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
from screenvivid.utils.general import safe_delete

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
    zoomChanged = Signal()
    zoomEffectsChanged = Signal()

    def __init__(self, frame_provider):
        super().__init__()
        self.video_processor = VideoProcessor()
        self.video_thread = VideoThread(self.video_processor)
        self.frame_provider = frame_provider
        self.export_thread = None
        self.is_exporting = False

        self.video_processor.frameProcessed.connect(self.on_frame_processed)
        self.video_processor.playingChanged.connect(self.on_playing_changed)
        self.video_processor.zoomChanged.connect(self.on_zoom_changed)
        self.video_processor.zoomEffectsChanged.connect(self.on_zoom_effects_changed)

        self.undo_redo_manager = UndoRedoManager()
        self.video_path = None
        self.is_recording_video = True

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

    @Property(bool, notify=playingChanged)
    def is_playing(self):
        return self.video_processor.is_playing

    @Property(list, notify=outputSizeChanged)
    def output_size(self):
        return self.video_processor.output_size

    @Property(list, notify=zoomEffectsChanged)
    def zoom_effects(self):
        return self.video_processor.zoom_effects

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
        self.video_path = path
        self.is_recording_video = metadata["recording"]
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

    @Slot()
    def clean(self):
        self.video_processor.clean()
        if self.is_recording_video:
            safe_delete(self.video_path)

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

    def on_zoom_changed(self):
        self.zoomChanged.emit()
        
    def on_zoom_effects_changed(self):
        self.zoomEffectsChanged.emit()

    @Slot(int, int, dict)
    def add_zoom_effect(self, start_frame, end_frame, zoom_params):
        """Add a zoom effect between start and end frames"""
        def do_add_zoom():
            self.video_processor.add_zoom_effect(start_frame, end_frame, zoom_params)

        def undo_add_zoom():
            self.video_processor.remove_zoom_effect(start_frame, end_frame)

        self.undo_redo_manager.do_action(do_add_zoom, (do_add_zoom, undo_add_zoom))
        
    @Slot(int, int)
    def remove_zoom_effect(self, start_frame, end_frame):
        """Remove a zoom effect between start and end frames"""
        def do_remove_zoom():
            self.video_processor.remove_zoom_effect(start_frame, end_frame)

        def undo_remove_zoom():
            # Assuming we have a way to get back the zoom parameters
            zoom_effect = self.video_processor.get_removed_zoom_effect(start_frame, end_frame)
            if zoom_effect:
                self.video_processor.add_zoom_effect(start_frame, end_frame, zoom_effect['params'])

        self.undo_redo_manager.do_action(do_remove_zoom, (do_remove_zoom, undo_remove_zoom))

    @Property(int, notify=currentFrameChanged)
    def current_frame(self):
        return self.video_processor.current_frame

    @Property(int, notify=currentFrameChanged)
    def absolute_current_frame(self):
        # This returns the absolute frame number including the start_frame offset
        return self.video_processor.start_frame + self.video_processor.current_frame

    @Slot(int, int, int, int, dict)
    def update_zoom_effect(self, old_start_frame, old_end_frame, new_start_frame, new_end_frame, params):
        """Update an existing zoom effect with new parameters"""
        def do_update_zoom():
            self.video_processor.update_zoom_effect(old_start_frame, old_end_frame, new_start_frame, new_end_frame, params)

        def undo_update_zoom():
            # Get the old effect that was replaced
            old_params = params.copy()
            self.video_processor.update_zoom_effect(new_start_frame, new_end_frame, old_start_frame, old_end_frame, old_params)

        self.undo_redo_manager.do_action(do_update_zoom, (do_update_zoom, undo_update_zoom))

class VideoLoadingError(Exception):
    pass

class VideoProcessor(QObject):
    frameProcessed = Signal(np.ndarray)
    playingChanged = Signal(bool)
    zoomChanged = Signal()
    zoomEffectsChanged = Signal()

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
        
        # Zoom effects storage
        self._zoom_effects = []
        self._removed_zoom_effects = []

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
        logger.debug(f"Jumping to frame {target_frame} (absolute)")
        
        # Ensure we stay within valid frame range
        internal_target_frame = max(self.start_frame, min(self.end_frame, target_frame))
        logger.debug(f"Adjusted target frame: {internal_target_frame}")
        
        # Calculate relative frame (for internal tracking)
        relative_frame = internal_target_frame - self.start_frame
        logger.debug(f"Relative frame position: {relative_frame}")
        
        # Set video position
        if self.video.isOpened():
            self.video.set(cv2.CAP_PROP_POS_FRAMES, internal_target_frame)
            ret, frame = self.video.read()
            if ret:
                processed_frame = self.process_frame(frame)
                self.current_frame = relative_frame
                self.frameProcessed.emit(processed_frame)
                logger.debug(f"Successfully jumped to frame {target_frame}, current_frame={self.current_frame}")
            else:
                logger.error(f"Failed to read frame at position {internal_target_frame}")
        else:
            logger.error("Cannot jump to frame - video is not open")

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
        # Get absolute frame number 
        current_absolute_frame = self.start_frame + self.current_frame
        logger.info(f"Processing frame {current_absolute_frame}")

        # First apply standard transforms
        result = self._transforms(input=frame, start_frame=current_absolute_frame)
        
        # Then check for and apply zoom effect (BEFORE color conversion)
        zoom_effect = self.get_active_zoom_effect(current_absolute_frame)
        if zoom_effect:
            logger.info(f"🔍 APPLYING ZOOM EFFECT: {zoom_effect}")
            
            try:
                # Extract zoom parameters
                x = float(zoom_effect['x'])
                y = float(zoom_effect['y']) 
                scale = float(zoom_effect['scale'])
                progress = float(zoom_effect['progress'])
                
                # Get the transition point (default to 0.5 for smooth in/out)
                transition_point = float(zoom_effect.get('transitionPoint', 0.5))
                
                logger.info(f"Zoom params: x={x}, y={y}, scale={scale}, progress={progress}, transition={transition_point}")
                
                # Apply easing function for custom zoom transition
                if progress <= transition_point and transition_point > 0:
                    # Zoom in phase - scale from 1.0 to target scale
                    # Normalize progress to 0-1 range for this phase
                    normalized_progress = progress / transition_point
                    current_scale = 1.0 + (scale - 1.0) * normalized_progress
                elif progress > transition_point and transition_point < 1.0:
                    # Zoom out phase - scale from target scale back to 1.0
                    # Normalize progress to 0-1 range for this phase
                    normalized_progress = (progress - transition_point) / (1.0 - transition_point)
                    current_scale = scale - (scale - 1.0) * normalized_progress
                else:
                    # Exactly at transition point or fallback
                    current_scale = scale
                
                logger.info(f"Applied scale: {current_scale}")
                
                # Get frame dimensions
                h, w = result.shape[:2]
                
                # CORRECTED ZOOM IMPLEMENTATION:
                # 1. Calculate the region size based on zoom level (smaller with more zoom)
                region_w = int(w / current_scale)
                region_h = int(h / current_scale)
                
                # 2. Calculate the center point in pixels
                center_x = int(w * x)
                center_y = int(h * y)
                
                # 3. Calculate crop region centered on target point
                x1 = max(0, center_x - region_w // 2)
                y1 = max(0, center_y - region_h // 2)
                
                # 4. Make sure we don't exceed frame boundaries
                if x1 + region_w > w:
                    x1 = w - region_w
                if y1 + region_h > h:
                    y1 = h - region_h
                
                # 5. Ensure x1 and y1 are not negative
                x1 = max(0, x1)
                y1 = max(0, y1)
                
                # 6. Calculate the final crop coordinates
                x2 = min(w, x1 + region_w)
                y2 = min(h, y1 + region_h)
                
                logger.info(f"Crop region: ({x1},{y1}) to ({x2},{y2})")
                
                # 7. Safety check before cropping
                if y2 > y1 and x2 > x1 and y1 >= 0 and y2 <= h and x1 >= 0 and x2 <= w:
                    # 8. Extract the region
                    crop_region = result[y1:y2, x1:x2].copy()
                    
                    # 9. Resize back to full frame size - this creates the zoom effect
                    result = cv2.resize(crop_region, (w, h), interpolation=cv2.INTER_LANCZOS4)
                    logger.info(f"✅ Zoom applied successfully!")
                else:
                    logger.error(f"❌ Invalid crop region: ({x1},{y1})-({x2},{y2}) for frame size {w}x{h}")
            
            except Exception as e:
                logger.error(f"❌ Error applying zoom: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
        
        # Finally, convert to RGB and return
        return cv2.cvtColor(result, cv2.COLOR_BGR2RGB)

    def clean(self):
        try:
            if self.video:
                self.video.release()
        except:
            logger.warning(f"Failed to release video capture")

    @property
    def zoom_effects(self):
        return self._zoom_effects
    
    def add_zoom_effect(self, start_frame, end_frame, zoom_params):
        """
        Add a zoom effect to the video
        
        Parameters:
        - start_frame: Start frame for the zoom effect
        - end_frame: End frame for the zoom effect
        - zoom_params: Dictionary with zoom parameters (x, y, scale, etc.)
        """
        zoom_effect = {
            'start_frame': start_frame,
            'end_frame': end_frame,
            'params': zoom_params
        }
        
        # Check if this overlaps with an existing zoom effect
        for i, effect in enumerate(self._zoom_effects):
            if (start_frame <= effect['end_frame'] and end_frame >= effect['start_frame']):
                # Overlapping effect, replace it
                self._zoom_effects[i] = zoom_effect
                self.zoomEffectsChanged.emit()
                return
        
        # Add new effect
        self._zoom_effects.append(zoom_effect)
        self._zoom_effects.sort(key=lambda x: x['start_frame'])
        self.zoomEffectsChanged.emit()
    
    def remove_zoom_effect(self, start_frame, end_frame):
        """Remove a zoom effect that matches the given frame range"""
        for i, effect in enumerate(self._zoom_effects):
            if effect['start_frame'] == start_frame and effect['end_frame'] == end_frame:
                removed = self._zoom_effects.pop(i)
                self._removed_zoom_effects.append(removed)
                self.zoomEffectsChanged.emit()
                return True
        return False
    
    def get_removed_zoom_effect(self, start_frame, end_frame):
        """Get a previously removed zoom effect for undo operations"""
        for i, effect in enumerate(self._removed_zoom_effects):
            if effect['start_frame'] == start_frame and effect['end_frame'] == end_frame:
                return self._removed_zoom_effects.pop(i)
        return None
    
    def get_active_zoom_effect(self, frame):
        """
        Get the active zoom effect for the current frame, if any.
        
        Args:
            frame: Absolute frame number
            
        Returns:
            Dictionary with zoom effect parameters or None if no active effect
        """
        # Print clear debug info about available zoom effects
        logger.info(f"Checking for zoom effect at frame {frame}")
        logger.info(f"Number of zoom effects: {len(self._zoom_effects)}")
        
        for i, effect in enumerate(self._zoom_effects):
            start = effect['start_frame']
            end = effect['end_frame']
            logger.info(f"Zoom effect #{i}: frames {start}-{end}, params: {effect['params']}")
            
            if start <= frame <= end:
                # Calculate how far we are through the effect (0.0 to 1.0)
                total_frames = end - start
                progress = 0 if total_frames == 0 else (frame - start) / total_frames
                
                logger.info(f"⭐ FOUND active zoom effect #{i} with progress {progress:.2f}")
                
                # Add progress to the effect data for animation calculation
                effect_data = effect['params'].copy()
                effect_data['progress'] = progress
                return effect_data
        
        logger.info(f"No active zoom effect found for frame {frame}")
        return None

    def update_zoom_effect(self, old_start_frame, old_end_frame, new_start_frame, new_end_frame, params):
        """Update an existing zoom effect with new start/end frames and parameters"""
        # Find the existing effect
        for i, effect in enumerate(self._zoom_effects):
            if effect['start_frame'] == old_start_frame and effect['end_frame'] == old_end_frame:
                # Update with new values
                updated_effect = {
                    'start_frame': new_start_frame,
                    'end_frame': new_end_frame,
                    'params': params
                }
                self._zoom_effects[i] = updated_effect
                self._zoom_effects.sort(key=lambda x: x['start_frame'])
                self.zoomEffectsChanged.emit()
                logger.info(f"Updated zoom effect: {old_start_frame}-{old_end_frame} → {new_start_frame}-{new_end_frame}")
                return True
        
        logger.warning(f"Could not find zoom effect to update: {old_start_frame}-{old_end_frame}")
        return False

class VideoThread(QThread):
    def __init__(self, video_processor):
        super().__init__()
        self.video_processor = video_processor

    def run(self):
        self.video_processor.play()
