import os
import time
import queue
import hashlib
from threading import Thread, Event

import cv2
import numpy as np
import pyautogui
from mss import mss
from PySide6.QtCore import (
    QObject, Qt, Property, Slot, Signal, QThread, QTimer, QPoint, QAbstractListModel,
    QModelIndex
)
from PySide6.QtGui import QImage, QGuiApplication
from PySide6.QtWidgets import QFileDialog
from PIL import Image

from screenvivid import config
from screenvivid import transforms
from screenvivid.utils.general import generate_video_path

class UndoRedoManager:
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []

    def do_action(self, action, undo_action):
        self.undo_stack.append(undo_action)
        self.redo_stack.clear()
        action()

    def undo(self):
        if self.undo_stack:
            action = self.undo_stack.pop()
            self.redo_stack.append(action[0])
            action[1]()

    def redo(self):
        if self.redo_stack:
            action = self.redo_stack.pop()
            self.undo_stack.append(action)
            action[0]()

    def can_undo(self):
        return len(self.undo_stack) > 0

    def can_redo(self):
        return len(self.redo_stack) > 0


class ClipTrack:
    def __init__(self, x, width, clip_len):
        self.x = x
        self.width = width
        self.clip_len = clip_len

    def to_dict(self):
        return {"x": self.x, "width": self.width, "clip_len": self.clip_len}

class ClipTrackModel(QAbstractListModel):
    xChanged = Signal()
    widthChanged = Signal()
    clipLenChanged = Signal()
    canUndoChanged = Signal(bool)
    canRedoChanged = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._clips = [ClipTrack(0, 0, 0)]
        self._clicked_events = []
        self._video_fps = config.DEFAULT_FPS
        self.undo_redo_manager = UndoRedoManager()

    def rowCount(self, parent=QModelIndex()):
        return len(self._clips)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._clips):
            return None

        clip = self._clips[index.row()]
        if role == Qt.UserRole:
            return {"x": clip.x, "width": clip.width, "clip_len": clip.clip_len}
        return None

    def roleNames(self):
        return {Qt.UserRole: b"clipData"}

    @Slot(int, result="QVariant")
    def get_clip(self, index):
        if self._clips and index < len(self._clips):
            return self._clips[index].to_dict()

    @Slot(float)
    def set_fps(self, fps):
        self._video_fps = fps

    @Slot()
    def cut_clip(self):
        if self._clicked_events:
            index, position = self._clicked_events
            if 0 <= index < len(self._clips):
                clip = self._clips[index]
                if position < clip.width:
                    # Store the original state for undo
                    original_clip = ClipTrack(clip.x, clip.width, clip.clip_len)

                    def do_cut():
                        # Create a new clip
                        new_clip = ClipTrack(clip.x + position, clip.width - position, (clip.width - position) / config.DEFAULT_PIXELS_PER_FRAME / self._video_fps)

                        # Update the current clip
                        clip.width = position
                        clip.clip_len = clip.width / config.DEFAULT_PIXELS_PER_FRAME / self._video_fps

                        # Inset the new one
                        self._clips.insert(index + 1, new_clip)

                        # Notify
                        self.layoutChanged.emit()
                        self._update_undo_redo_signals()

                    def undo_cut():
                        # Restore the original clip
                        self._clips[index].x = original_clip.x
                        self._clips[index].width = original_clip.width
                        self._clips[index].clip_len = original_clip.clip_len

                        # Remove the new clip that was added
                        if index + 1 < len(self._clips):
                            self._clips.pop(index + 1)

                        # Notify
                        self.layoutChanged.emit()
                        self._update_undo_redo_signals()

                    # Perform the cut action and add it to the undo/redo manager
                    self.undo_redo_manager.do_action(do_cut, (do_cut, undo_cut))

        # Reset the clicked events after cutting
        self.reset_cut_clip_data()

    @Slot(int)
    def delete_clip(self, index):
        self.reset_cut_clip_data()

        if self._clips and len(self._clips) > 1 and index == 0 or index == len(self._clips) - 1:
            deleted_clip = self._clips[index]
            def do_delete():
                self._clips.pop(index)
                self._update_clip_positions()
                self.layoutChanged.emit()
                self._update_undo_redo_signals()

            def undo_delete():
                self._clips.insert(index, deleted_clip)
                self._update_clip_positions()
                self.layoutChanged.emit()
                self._update_undo_redo_signals()

            self.undo_redo_manager.do_action(do_delete, (do_delete, undo_delete))

    def _update_clip_positions(self):
        x = 0
        for clip in self._clips:
            clip.x = x
            x = clip.x + clip.width

    def _update_undo_redo_signals(self):
        self.canUndoChanged.emit(self.undo_redo_manager.can_undo())
        self.canRedoChanged.emit(self.undo_redo_manager.can_redo())

    @Slot()
    def undo(self):
        self.undo_redo_manager.undo()
        self._update_undo_redo_signals()

    @Slot()
    def redo(self):
        self.undo_redo_manager.redo()
        self._update_undo_redo_signals()

    @Property(bool, notify=canUndoChanged)
    def canUndo(self):
        return self.undo_redo_manager.can_undo()

    @Property(bool, notify=canRedoChanged)
    def canRedo(self):
        return self.undo_redo_manager.can_redo()

    @Slot(int, float)
    def set_video_len(self, index, length):
        if self._clips:
            self._clips[index].width = length * self._video_fps * config.DEFAULT_PIXELS_PER_FRAME
            self._clips[index].clip_len = length
            self.widthChanged.emit()

    @Slot(int, float)
    def set_cut_clip_data(self, index, x):
        self._clicked_events = [index, x]

    @Slot()
    def reset_cut_clip_data(self):
        self._clicked_events = []

class WindowController(QObject):

    topChanged = Signal(int)
    leftChanged = Signal(int)
    widthChanged = Signal()
    heightChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._window_geometry = None

    @Property(int, notify=topChanged)
    def top(self):
        return self._window_geometry.top()

    @Property(int, notify=leftChanged)
    def left(self):
        return self._window_geometry.left()

    @Property(int, notify=widthChanged)
    def width(self):
        return self._window_geometry.width()

    @Property(int, notify=heightChanged)
    def height(self):
        return self._window_geometry.height()

    @Slot(result="QPoint")
    def get_window_position(self):
        screen = QGuiApplication.primaryScreen()
        available_geometry = screen.availableGeometry()

        self._window_geometry = available_geometry
        return QPoint(available_geometry.x(), available_geometry.y())


class VideoRecorder(QObject):
    def __init__(self, output_path: str = None):
        super().__init__()
        self._output_path = output_path if output_path and os.path.exists(output_path) else generate_video_path()
        self._region = None
        self._video_recording_thread = VideoRecordingThread(self._output_path)

    @Property(str)
    def output_path(self):
        return self._output_path

    @output_path.setter
    def output_path(self, value):
        self._output_path = value

    @Property(dict)
    def mouse_events(self):
        return self._video_recording_thread.mouse_events

    @Property(list)
    def region(self):
        return self._region

    @region.setter
    def region(self, region):
        self._region = region

    @Slot()
    def start_recording(self):
        self._video_recording_thread.set_region(self._region)
        self._video_recording_thread.start_recording()

    @Slot()
    def stop_recording(self):
        self._video_recording_thread.stop_recording()

    @Slot()
    def cancel_recording(self):
        self.stop_recording()
        if os.path.exists(self._output_path):
            os.remove(self._output_path)


class VideoRecordingThread:
    def __init__(self, output_path: str = None, start_delay: float = 0.5):
        self._output_path = output_path
        self._start_delay = start_delay
        self._region = None
        self._record_thread = None
        self._mouse_track_thread = None
        self._mouse_events = {"move": {}, "click": [], "cursors_map": {}}
        self._writer = None
        self._frame_index = 0
        self._frame_width = None
        self._frame_height = None
        self._is_stopped = Event()
        self._is_stopped.set()
        self._fps = config.DEFAULT_FPS or 30
        self._maximum_fps = 200
        self._monitor = {}

        # self._frame_queue = queue.Queue(maxsize=300)
        # self._processing_thread = None

    @property
    def mouse_events(self):
        return self._mouse_events

    def start_recording(self):
        if not self._output_path:
            raise ValueError("Output path is not specified")

        self._is_stopped.clear()
        self._record_thread = Thread(target=self._recording)
        self._record_thread.start()

        # self._mouse_track_thread = Thread(target=self._mouse_track)
        # self._mouse_track_thread.start()

    def stop_recording(self):
        self._is_stopped.set()
        if self._record_thread is not None:
            self._record_thread.join()

        # if self._mouse_track_thread is not None:
        #     self._mouse_track_thread.join()

    def cancel_recording(self):
        self.stop_recording()
        if self._output_path and os.path.exists(self._output_path):
            os.remove(self._output_path)

    @property
    def mouse_events(self):
        return self._mouse_events

    def _recording(self):
        try:
            time.sleep(self._start_delay)

            interval = 1 / self._fps
            self._frame_index = 0

            stream = mss()
            if not self._region:
                self._monitor = stream.monitors[0]
            else:
                self._monitor = {
                    "left": self._region[0],
                    "top": self._region[1],
                    "width": self._region[2],
                    "height": self._region[3],
                }

            # Start process_thread
            # self._processing_thread = Thread(target=self._process_frames)
            # self._processing_thread.start()

            while not self._is_stopped.is_set():
                t0 = time.time()
                frame = np.array(stream.grab(self._monitor))
                if frame is None:
                    break

                # try:
                #     self._frame_queue.put(frame, block=False)
                # except queue.Full:
                #     pass

                frame = np.array(frame)
                frame = frame[:, :, :3]
                frame_height, frame_width = frame.shape[:2]

                if self._writer is None:
                    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                    self._writer = cv2.VideoWriter(self._output_path, fourcc, self._fps, (frame_width, frame_height))
                    self._frame_width = frame_width
                    self._frame_height = frame_height

                self._get_mouse_data()

                self._frame_index += 1
                self._writer.write(frame)

                t1 = time.time()

                read_time = t1 - t0
                sleep_duration = max(0.001, interval - read_time)
                time.sleep(sleep_duration)

            # self._frame_queue.put(None)
            # self._processing_thread.join()
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if self._writer is not None:
                self._writer.release()
                self._writer = None

    def _get_mouse_data(self):
        x, y = pyautogui.position()
        if (
            self._frame_width
            and self._frame_height
            and self._monitor
            and self._monitor["left"] <= x < self._monitor["left"] + self._monitor["width"]
            and self._monitor["top"] <= y < self._monitor["top"] + self._monitor["height"]
        ):
            relative_x = (x - self._monitor["left"]) / self._frame_width
            relative_y = (y - self._monitor["top"]) / self._frame_height

            # cursor shape
            # cursor_id = self._get_cursor()
            cursor_id = ''

            self._mouse_events["move"][self._frame_index] = (relative_x, relative_y, self._frame_index, cursor_id)

    # def _get_cursor(self):
    #     cursor_image = get_cursor_image()
    #     t0 = time.time()
    #     cursor_id = hashlib.sha256(cursor_image.tobytes()).hexdigest()
    #     if cursor_id not in self._mouse_events["cursors_map"]:
    #         self._mouse_events["cursors_map"][cursor_id] = cursor_image
    #     return cursor_id

    # def _mouse_track(self):
    #     while not self._is_stopped.is_set():
    #         x, y = pyautogui.position()
    #         if (
    #             self._frame_width
    #             and self._frame_height
    #             and self._monitor
    #             and self._monitor["left"] <= x < self._monitor["left"] + self._monitor["width"]
    #             and self._monitor["top"] <= y < self._monitor["top"] + self._monitor["height"]
    #         ):
    #             relative_x = (x - self._monitor["left"]) / self._frame_width
    #             relative_y = (y - self._monitor["top"]) / self._frame_height
    #             self._mouse_events["move"][self._frame_index] = (relative_x, relative_y, self._frame_index)
    #         time.sleep(0.5 / self._fps)

    # def _process_frames(self):
    #     while not self._is_stopped.is_set():
    #         frame = self._frame_queue.get()
    #         if frame is None:
    #             break

    #         frame = np.array(frame)
    #         frame = frame[:, :, :3]
    #         frame_height, frame_width = frame.shape[:2]

    #         if self._writer is None:
    #             fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    #             self._writer = cv2.VideoWriter(self._output_path, fourcc, self._fps, (frame_width, frame_height))
    #             self._frame_width = frame_width
    #             self._frame_height = frame_height

    #         self._get_mouse_data()

    #         self._frame_index += 1
    #         self._writer.write(frame)

    def set_region(self, region):
        self._region = region


class VideoController(QObject):
    frameReady = Signal()
    playingChanged = Signal(bool)
    currentFrameChanged = Signal(int)

    exportProgress = Signal(float)
    exportFinished = Signal()
    aspectRatioChanged = Signal(str)
    frameWidthChanged = Signal()
    frameHeightChanged = Signal()
    canUndoChanged = Signal(bool)
    canRedoChanged = Signal(bool)
    outputSizeChanged = Signal()
    fpsChanged = Signal(int)

    def __init__(self, frame_provider):
        super().__init__()
        self.video_processor = VideoProcessor()
        self.video_thread = VideoThread(self.video_processor)
        self.frame_provider = frame_provider
        self.export_thread = None
        self.is_exporting = False

        self.video_processor.frameProcessed.connect(self.on_frame_processed)
        self.video_processor.playingChanged.connect(self.on_playing_changed)

        self.undo_redo_manager = UndoRedoManager()

    @Property(int, notify=fpsChanged)
    def fps(self):
        return self.video_processor.fps

    @Property(int)
    def total_frames(self):
        return self.video_processor.total_frames

    @Property(float)
    def video_len(self):
        return self.video_processor.video_len

    @Property(int, notify=frameWidthChanged)
    def frame_width(self):
        return self.video_processor.frame_width

    @Property(int, notify=frameHeightChanged)
    def frame_height(self):
        return self.video_processor.frame_height

    @Property(str, notify=aspectRatioChanged)
    def aspect_ratio(self):
        return self.video_processor.aspect_ratio

    @aspect_ratio.setter
    def aspect_ratio(self, aspect_ratio):
        if self.video_processor.aspect_ratio != aspect_ratio:
            self.video_processor.aspect_ratio = aspect_ratio
            self.aspectRatioChanged.emit(aspect_ratio)

    @Property(int)
    def padding(self):
        return self.video_processor.padding

    @padding.setter
    def padding(self, value):
        self.video_processor.padding = value

    @Property(int)
    def inset(self):
        return self.video_processor.inset

    @inset.setter
    def inset(self, inset):
        self.video_processor.inset = inset

    @Property(int)
    def border_radius(self):
        return self.video_processor.border_radius

    @border_radius.setter
    def border_radius(self, value):
        self.video_processor.border_radius = value

    @Property(dict)
    def background(self):
        return self.video_processor.background

    @background.setter
    def background(self, value):
        self.video_processor.background = value

    @Property(list, notify=outputSizeChanged)
    def output_size(self):
        return self.video_processor.output_size

    @Slot(int)
    def trim_left(self, start_frame):
        def do_trim_left():
            self.video_processor.append_start_frame(start_frame)
            self.video_processor.jump_to_frame(0)

        def undo_trim_left():
            self.video_processor.pop_start_frame()
            self.video_processor.jump_to_frame(0)

        self.undo_redo_manager.do_action(do_trim_left, (do_trim_left, undo_trim_left))

    @Slot(int)
    def trim_right(self, end_frame):
        def do_trim_right():
            self.video_processor.append_end_frame(end_frame)
            self.video_processor.jump_to_frame(max(0, end_frame - 5))

        def undo_trim_right():
            self.video_processor.pop_end_frame()

        self.undo_redo_manager.do_action(do_trim_right, (do_trim_right, undo_trim_right))

    def _update_undo_redo_signals(self):
        self.canUndoChanged.emit(self.undo_redo_manager.can_undo())
        self.canRedoChanged.emit(self.undo_redo_manager.can_redo())

    @Slot()
    def undo(self):
        self.undo_redo_manager.undo()
        self._update_undo_redo_signals()

    @Slot()
    def redo(self):
        self.undo_redo_manager.redo()
        self._update_undo_redo_signals()

    @Slot(str, dict, result="bool")
    def load_video(self, path, metadata):
        return self.video_processor.load_video(path, metadata)

    @Slot()
    def toggle_play_pause(self):
        self.video_processor.toggle_play_pause()

    def on_playing_changed(self, is_playing):
        self.playingChanged.emit(is_playing)

    @Slot()
    def play(self):
        if not self.video_thread.isRunning():
            self.video_thread.start()
        else:
            self.video_processor.play()

    @Slot()
    def pause(self):
        self.video_processor.pause()

    @Slot()
    def next_frame(self):
        self.video_processor.next_frame()

    @Slot()
    def prev_frame(self):
        self.video_processor.prev_frame()

    @Slot(int)
    def jump_to_frame(self, target_frame):
        self.video_processor.jump_to_frame(target_frame)

    @Slot()
    def get_current_frame(self):
        self.video_processor.get_current_frame()

    @Slot(dict)
    def export_video(self, export_params):
        if self.is_exporting:
            return
        self.is_exporting = True
        self.export_thread = ExportThread(self.video_processor, export_params)
        self.export_thread.progress.connect(self.update_export_progress)
        self.export_thread.finished.connect(self.on_export_finished)
        self.export_thread.start()

    @Slot()
    def cancel_export(self):
        if self.export_thread and self.export_thread.isRunning():
            self.export_thread.stop()
            self.export_thread.wait()
            self.is_exporting = False
            self.exportFinished.emit()

    def update_export_progress(self, progress):
        self.exportProgress.emit(progress)

    def on_export_finished(self):
        self.is_exporting = False
        self.exportFinished.emit()

    def on_frame_processed(self, frame):
        height, width = frame.shape[:2]
        bytes_per_line = width * 3
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.currentFrameChanged.emit(self.video_processor.current_frame)
        self.frame_provider.updateFrame(q_image)
        self.frameReady.emit()


class VideoLoadingError(Exception):
    pass

class VideoProcessor(QObject):
    frameProcessed = Signal(np.ndarray)
    playingChanged = Signal(bool)

    def __init__(self):
        super().__init__()
        self.video = None
        self._is_playing = False
        self._start_frames = []
        self._end_frames = []
        self._current_frame = 0
        self._total_frames = 0
        self._max_frame = 0
        self.play_timer = QTimer()
        self.play_timer.timeout.connect(self.process_next_frame)

        self._aspect_ratio = "Auto"
        self._padding = 100
        self._inset = 0
        self._border_radius = 14
        self._background = {"type": "wallpaper", "value": 1}
        self._transforms = None
        self._mouse_events = []

    @property
    def aspect_ratio(self):
        return self._aspect_ratio

    @aspect_ratio.setter
    def aspect_ratio(self, aspect_ratio):
        self._aspect_ratio = aspect_ratio
        self._transforms["aspect_ratio"] = transforms.AspectRatio(aspect_ratio=aspect_ratio)

    @property
    def padding(self):
        return self._padding

    @padding.setter
    def padding(self, value):
        self._padding = value
        self._transforms["padding"] = transforms.Padding(padding=value)

    @property
    def inset(self):
        return self._inset

    @inset.setter
    def inset(self, inset):
        self._inset = inset
        self._transforms["inset"] = transforms.Inset(inset=inset)

    @property
    def border_radius(self):
        return self._border_radius

    @border_radius.setter
    def border_radius(self, value):
        self._border_radius = value
        self._transforms["border_shadow"] = transforms.BorderShadow(radius=value)

    @property
    def background(self):
        return self._background

    @background.setter
    def background(self, value):
        self._background = value
        self._transforms["background"] = transforms.Background(background=value)

    @property
    def total_frames(self):
        return self._total_frames

    @total_frames.setter
    def total_frames(self, value):
        self._total_frames = value

    @property
    def start_frame(self):
        return sum(self._start_frames) if self._start_frames else 0

    @property
    def start_frames(self):
        return self._start_frames

    def append_start_frame(self, start_frame):
        self._start_frames.append(start_frame)

    def pop_start_frame(self):
        if self._start_frames:
            return self._start_frames.pop()

    @property
    def end_frame(self):
        if self._end_frames:
            return self._end_frames[-1]
        else:
            return self.total_frames

    @property
    def end_frames(self):
        return self._end_frames

    def append_end_frame(self, end_frame):
        self._end_frames.append(end_frame)

    def pop_end_frame(self):
        if self._end_frames:
            return self._end_frames.pop()

    @property
    def mouse_events(self):
        return self._mouse_events

    @mouse_events.setter
    def mouse_events(self, value):
        self._mouse_events = value

    @property
    def current_frame(self):
        return self._current_frame

    @current_frame.setter
    def current_frame(self, current_frame):
        self._current_frame = current_frame

    @property
    def is_playing(self):
        return self._is_playing

    @is_playing.setter
    def is_playing(self, value):
        if self._is_playing != value:
            self._is_playing = value
            self.playingChanged.emit(value)

    @property
    def output_size(self):
        ar = self._transforms["aspect_ratio"]
        return ar.calculate_output_resolution(
            ar.aspect_ratio,
            self.frame_width,
            self.frame_height
        )[:2]

    # @Slot(str)
    def load_video(self, path, metadata):
        try:
            self.video = cv2.VideoCapture(path)

            self.fps = int(self.video.get(cv2.CAP_PROP_FPS))
            self.frame_width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.frame_height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.total_frames = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
            self.video_len = self.total_frames / self.fps if self.fps > 0 else 0
            self.current_frame = 0
            self._start_frames.append(0)
            self._end_frames.append(self.total_frames)

            self._mouse_events = metadata.get("mouse_events", {}).get("move", {}) if metadata else {}
            self._cursors_map = metadata.get("mouse_events", {}).get("cursors_map", {}) if metadata else {}
            region = metadata.get("region", []) if metadata else []
            if region:
                x_offset, y_offset = region[:2]
            else:
                x_offset, y_offset = None, None
            self._transforms = transforms.Compose({
                "aspect_ratio": transforms.AspectRatio(self._aspect_ratio),
                "cursor": transforms.Cursor(move_data=self._mouse_events, cursors_map=self._cursors_map, offsets=(x_offset, y_offset)),
                "padding": transforms.Padding(padding=self.padding),
                "inset": transforms.Inset(inset=self.inset, color=(0, 0, 0)),
                "border_shadow": transforms.BorderShadow(radius=self.border_radius),
                "background": transforms.Background(background=self._background),
            })

            # Get first frame
            # self.get_frame()
            self.jump_to_frame(0)
            return True
        except VideoLoadingError:
            return False

    def get_frame(self):
        try:

            if self.start_frame + self.current_frame >= self.end_frame - 1:
                self.pause()
                return

            success, frame = self.video.read()
            if not success:
                return

            processed_frame = self.process_frame(frame)
            self.frameProcessed.emit(processed_frame)
            self.current_frame += 1
            return processed_frame
        except:
            return

    @Slot()
    def play(self):
        self.is_playing = True
        self.play_timer.start(1000 / self.fps)

    @Slot()
    def pause(self):
        self.is_playing = False
        self.play_timer.stop()

    @Slot()
    def toggle_play_pause(self):
        if self.is_playing:
            self.pause()
        else:
            self.play()

    @Slot()
    def next_frame(self):
        self.pause()
        # if self.video.isOpened():
        #     ret, frame = self.video.read()
        #     if ret:
        #         processed_frame = self.process_frame(frame)
        #         self.frameProcessed.emit(processed_frame)
        #         self.current_frame += 1
        self.get_frame()

    @Slot()
    def prev_frame(self):
        self.pause()
        if self.video.isOpened() and self.current_frame > 0:
            self.current_frame -= 1
            self.video.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
            ret, frame = self.video.read()
            if ret:
                processed_frame = self.process_frame(frame)
                self.frameProcessed.emit(processed_frame)

    # @Slot(int)
    def jump_to_frame(self, target_frame):
        internal_target_frame = self.start_frame + target_frame
        if self.video.isOpened() and self.start_frame <= internal_target_frame < self.end_frame:
            self.video.set(cv2.CAP_PROP_POS_FRAMES, internal_target_frame)
            ret, frame = self.video.read()
            if ret:
                processed_frame = self.process_frame(frame)
                self.current_frame = target_frame
                self.frameProcessed.emit(processed_frame)

    # @Slot()
    def get_current_frame(self):
        if self.video is not None and self.video.isOpened():
            current_position = int(self.video.get(cv2.CAP_PROP_POS_FRAMES))
            if current_position >= self.total_frames:
                current_position -= 1
                self.video.set(cv2.CAP_PROP_POS_FRAMES, current_position)

            ret, frame = self.video.read()

            if ret:
                processed_frame = self.process_frame(frame)

                self.video.set(cv2.CAP_PROP_POS_FRAMES, current_position)
                self.frameProcessed.emit(processed_frame)
                self.current_frame = current_position
                current_position = int(self.video.get(cv2.CAP_PROP_POS_FRAMES))

    def process_next_frame(self):
        # if self.video.isOpened():
        #     ret, frame = self.video.read()
        #     if ret:
        #         processed_frame = self.process_frame(frame)
        #         self.frameProcessed.emit(processed_frame)
        #         self.current_frame += 1
        #     else:
        #         self.pause()
        self.get_frame()

    def process_frame(self, frame):
        transformed_result = self._transforms(input=frame, start_frame=self.current_frame)
        output_frame = transformed_result["input"]

        output_frame = cv2.cvtColor(output_frame, cv2.COLOR_BGR2RGB)
        return output_frame


class VideoThread(QThread):
    def __init__(self, video_processor):
        super().__init__()
        self.video_processor = video_processor

    def run(self):
        self.video_processor.play()


class ExportThread(QThread):
    progress = Signal(float)
    finished = Signal()

    def __init__(self, video_processor, export_params):
        super().__init__()
        self.video_processor = video_processor
        self.export_params = export_params
        self.output_dir = os.path.join(os.path.expanduser("~"), "Videos/ScreenVivid")
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
        self._stop_flag = False

    def stop(self):
        self._stop_flag = True

    def run(self):
        format = self.export_params.get("format", "mp4")
        fps = self.export_params.get("fps", self.video_processor.fps)
        output_size = self.export_params.get("output_size")
        aspect_ratio = self.export_params.get("aspect_ratio", "auto")
        compression_level = self.export_params.get("compression_level", "high")
        output_file = self.export_params.get("output_path", "output_video")
        output_path = os.path.join(self.output_dir, output_file)

        # Set aspect ratio
        self.video_processor.aspect_ratio = aspect_ratio

        # Determine output file extension
        if format == "mp4":
            output_path += ".mp4"
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        elif format == "gif":
            output_path += ".gif"
            # For GIF, we"ll use a different approach

        # Create VideoWriter object (for mp4)
        if format == "mp4":
            out = cv2.VideoWriter(output_path, fourcc, fps, output_size)

        # Rewind video to start
        current_frame = self.video_processor.current_frame
        self.video_processor.video.set(cv2.CAP_PROP_POS_FRAMES, self.video_processor.start_frame)
        self.video_processor.current_frame = self.video_processor.start_frame

        frames = []
        total_frames = self.video_processor.end_frame - self.video_processor.start_frame

        for i in range(total_frames):
            if self._stop_flag:
                break
            ret, frame = self.video_processor.video.read()
            if ret:
                processed_frame = self.video_processor.process_frame(frame)
                self.video_processor.current_frame += 1

                # Resize frame if necessary
                if processed_frame.shape[:2] != output_size:
                    processed_frame = cv2.resize(processed_frame, output_size)

                if format == "mp4":
                    out.write(cv2.cvtColor(processed_frame, cv2.COLOR_RGB2BGR))
                elif format == "gif":
                    frames.append(Image.fromarray(processed_frame))

                if format == "gif" and i + 1 == total_frames:
                    break

                self.progress.emit((i + 1) / total_frames * 100)
            else:
                break

        self.video_processor.video.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
        self.video_processor.current_frame = current_frame

        if format == "mp4":
            out.release()
        elif format == "gif" and not self._stop_flag:
            frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=1000/fps, loop=0)
            self.progress.emit(100)

        self.finished.emit()
