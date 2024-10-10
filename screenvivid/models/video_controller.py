import time

import cv2
import numpy as np
import pyautogui
from PySide6.QtCore import QObject, Property, Slot, Signal, QThread, QTimer
from PySide6.QtGui import QImage

from screenvivid.models.utils import transforms
from screenvivid.models.utils.manager.undo_redo import UndoRedoManager
from screenvivid.models.export import ExportThread
from screenvivid.utils.logging import logger

class VideoControllerModel(QObject):
    frameReady = Signal()
    playingChanged = Signal(bool)
    currentFrameChanged = Signal(int)

    exportProgress = Signal(float)
    exportFinished = Signal()
    paddingChanged = Signal()
    insetChanged = Signal()
    borderRadiusChanged = Signal()
    aspectRatioChanged = Signal()
    backgroundChanged = Signal()
    devicePixelRatioChanged = Signal()
    cursorScaleChanged = Signal()
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

    @Property(int)
    def start_frame(self):
        return self.video_processor.start_frame

    @Property(int)
    def end_frame(self):
        return self.video_processor.end_frame

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
            self.aspectRatioChanged.emit()

    @Property(float, notify=aspectRatioChanged)
    def aspect_ratio_float(self):
        return self.video_processor.aspect_ratio_float

    @Property(float, notify=paddingChanged)
    def padding(self):
        return self.video_processor.padding

    @padding.setter
    def padding(self, value):
        if self.video_processor.padding != value:
            self.video_processor.padding = value
            self.paddingChanged.emit()

    @Property(int, notify=insetChanged)
    def inset(self):
        return self.video_processor.inset

    @inset.setter
    def inset(self, inset):
        if self.video_processor.inset != inset:
            self.video_processor.inset = inset
            self.insetChanged.emit()

    @Property(int, notify=borderRadiusChanged)
    def border_radius(self):
        return self.video_processor.border_radius

    @border_radius.setter
    def border_radius(self, value):
        if self.video_processor.border_radius != value:
            self.video_processor.border_radius = value
            self.borderRadiusChanged.emit()

    @Property(dict, notify=backgroundChanged)
    def background(self):
        return self.video_processor.background

    @background.setter
    def background(self, value):
        if self.video_processor.background != value:
            self.video_processor.background = value
            self.backgroundChanged.emit()

    @Property(float, notify=devicePixelRatioChanged)
    def device_pixel_ratio(self):
        return self.video_processor.device_pixel_ratio

    @device_pixel_ratio.setter
    def device_pixel_ratio(self, value):
        if self.video_processor.device_pixel_ratio != value:
            self.video_processor.device_pixel_ratio = value
            self.devicePixelRatioChanged.emit()

    @Property(float, notify=cursorScaleChanged)
    def cursor_scale(self):
        return self.video_processor.cursor_scale

    @cursor_scale.setter
    def cursor_scale(self, value):
        if self.video_processor.cursor_scale != value:
            self.video_processor.cursor_scale = value
            self.cursorScaleChanged.emit()

    @Property(list, notify=outputSizeChanged)
    def output_size(self):
        return self.video_processor.output_size

    @Slot(int)
    def trim_left(self, start_frame):
        def do_trim_left():
            self.video_processor.append_start_frame(start_frame)

        def undo_trim_left():
            self.video_processor.pop_start_frame()

        self.undo_redo_manager.do_action(do_trim_left, (do_trim_left, undo_trim_left))

    @Slot(int)
    def trim_right(self, end_frame):
        def do_trim_right():
            self.video_processor.append_end_frame(end_frame)

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
        self._padding = 0.1
        self._inset = 0
        self._border_radius = 20
        self._background = {"type": "wallpaper", "value": 1}
        self._device_pixel_ratio = 1.0
        self._cursor_scale = 1.0
        self._transforms = None
        self._mouse_events = []
        self._region = None
        self._x_offset = None
        self._y_offset = None
        self._cursors_map = dict()

    @property
    def aspect_ratio(self):
        return self._aspect_ratio

    @aspect_ratio.setter
    def aspect_ratio(self, value):
        self._aspect_ratio = value
        self._transforms["aspect_ratio"] = transforms.AspectRatio(
            aspect_ratio=value,
            screen_size=self._transforms["aspect_ratio"].screen_size
        )

    @property
    def aspect_ratio_float(self):
        if self._transforms and self._transforms.get("aspect_ratio"):
            return self._transforms["aspect_ratio"].aspect_ratio_float
        return 16 / 9

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
        self._transforms["border_shadow"] = transforms.BorderShadow(border_radius=value)

    @property
    def background(self):
        return self._background

    @background.setter
    def background(self, value):
        self._background = value
        self._transforms["background"] = transforms.Background(background=value)

    @property
    def device_pixel_ratio(self):
        return self._device_pixel_ratio

    @device_pixel_ratio.setter
    def device_pixel_ratio(self, value):
        self._device_pixel_ratio = value

    @property
    def cursor_scale(self):
        return self._cursor_scale

    @cursor_scale.setter
    def cursor_scale(self, value):
        self._cursor_scale = value

        self._transforms["cursor"] = transforms.Cursor(
            move_data=self._mouse_events,
            cursors_map=self._cursors_map,
            offsets=(self._x_offset, self._y_offset),
            scale=value
        )

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
            self._region = metadata.get("region", []) if metadata else []

            if self._region:
                x_offset, y_offset = self._region[:2]
            else:
                x_offset, y_offset = None, None
            self._x_offset = x_offset
            self._y_offset = y_offset
            screen_width, screen_height = pyautogui.size()
            screen_size = int(screen_width * self._device_pixel_ratio), int(screen_height * self._device_pixel_ratio)
            self._transforms = transforms.Compose({
                "aspect_ratio": transforms.AspectRatio(self._aspect_ratio, screen_size),
                "cursor": transforms.Cursor(move_data=self._mouse_events, cursors_map=self._cursors_map, offsets=(x_offset, y_offset), scale=self._cursor_scale),
                "padding": transforms.Padding(padding=self.padding),
                # "inset": transforms.Inset(inset=self.inset, color=(0, 0, 0)),
                "border_shadow": transforms.BorderShadow(border_radius=self.border_radius),
                "background": transforms.Background(background=self._background),
            })

            # Get first frame
            self.jump_to_frame(0)
            return True
        except VideoLoadingError:
            return False

    def get_frame(self):
        try:
            t0 = time.time()
            if self.start_frame + self.current_frame >= self.end_frame - 1:
                self.pause()
                return

            success, frame = self.video.read()
            if not success:
                return

            processed_frame = self.process_frame(frame)
            self.frameProcessed.emit(processed_frame)
            self.current_frame += 1
            t1 = time.time()
            logger.debug(f"Render FPS: {t1 - t0}")
            return processed_frame
        except Exception as e:
            logger.error(e)
            return

    @Slot()
    def play(self):
        self.is_playing = True
        self.play_timer.start(1000 / self.fps)
        # self.play_timer.start(1)

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

    def jump_to_frame(self, target_frame):
        internal_target_frame = min(self.start_frame + target_frame, self.end_frame)
        if self.video.isOpened() and self.start_frame <= internal_target_frame <= self.end_frame:
            self.video.set(cv2.CAP_PROP_POS_FRAMES, internal_target_frame)
            ret, frame = self.video.read()
            if ret:
                processed_frame = self.process_frame(frame)
                self.current_frame = target_frame
                self.frameProcessed.emit(processed_frame)

    def get_current_frame(self):
        if self.video is not None and self.video.isOpened():
            current_position = self.current_frame
            if current_position >= self.total_frames:
                current_position -= 1
                self.video.set(cv2.CAP_PROP_POS_FRAMES, current_position)

            ret, frame = self.video.read()

            if ret:
                processed_frame = self.process_frame(frame)

                self.video.set(cv2.CAP_PROP_POS_FRAMES, current_position)
                self.frameProcessed.emit(processed_frame)
                self.current_frame = current_position

    def process_next_frame(self):
        self.get_frame()

    def process_frame(self, frame):
        result = self._transforms(input=frame, start_frame=self.start_frame + self.current_frame)
        result = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        return result

class VideoThread(QThread):
    def __init__(self, video_processor):
        super().__init__()
        self.video_processor = video_processor

    def run(self):
        self.video_processor.play()
