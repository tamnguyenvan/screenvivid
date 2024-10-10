import os
import io
import time
import queue
import subprocess
from threading import Thread, Event

from PIL import Image
import pyautogui
from PySide6.QtCore import QObject, Property, Slot, Signal

from screenvivid import config
from screenvivid.models.utils.cursor import get_cursor_state, CursorLoaderThread
from screenvivid.models.screen_capture import get_screen_capture_class
from screenvivid.utils.general import (
    generate_video_path, get_os_name, get_ffmpeg_path, generate_temp_file
)
from screenvivid.utils.logging import logger

class ScreenRecorderModel(QObject):
    outputPathChanged = Signal()
    regionChanged = Signal()
    iccProfileChanged = Signal()
    devicePixelRatio = Signal()

    def __init__(self, output_path: str = None):
        super().__init__()
        self._output_path = output_path if output_path and os.path.exists(output_path) else generate_video_path()
        self._region = None
        self._screen_recording_thread = ScreenRecordingThread(self._output_path)

    @Property(str)
    def output_path(self):
        return self._output_path

    @output_path.setter
    def output_path(self, value):
        self._output_path = value
        self.outputPathChanged.emit()

    @Property(dict)
    def mouse_events(self):
        return self._screen_recording_thread.mouse_events

    @Property(list)
    def region(self):
        return self._region

    @region.setter
    def region(self, region):
        self._region = region
        self.regionChanged.emit()

    @Property(str)
    def icc_profile(self):
        return self._screen_recording_thread.icc_profile

    @icc_profile.setter
    def icc_profile(self, value):
        self._screen_recording_thread.icc_profile = value
        self.icc_profile.emit()

    @Property(float)
    def device_pixel_ratio(self):
        return self._screen_recording_thread.device_pixel_ratio

    @device_pixel_ratio.setter
    def device_pixel_ratio(self, value):
        self._screen_recording_thread.device_pixel_ratio = value
        self.devicePixelRatio.emit()

    @Slot()
    def start_recording(self):
        self._screen_recording_thread.set_region(self._region)
        self._screen_recording_thread.start_recording()

    @Slot()
    def stop_recording(self):
        self._screen_recording_thread.stop_recording()

    @Slot()
    def cancel_recording(self):
        self.stop_recording()
        if os.path.exists(self._output_path):
            os.remove(self._output_path)

class ScreenRecordingThread:
    def __init__(self, output_path: str = None, start_delay: float = 0.5):
        self._output_path = output_path
        self._start_delay = start_delay
        self._region = None
        self._mouse_events = {"move": {}, "click": [], "cursors_map": {}}
        self._frame_index = 0
        self._frame_width = None
        self._frame_height = None
        self._is_stopped = Event()
        self._is_stopped.set()
        self._fps = config.DEFAULT_FPS or 24
        self._icc_profile = None
        self._device_pixel_ratio = 1.0

        # Queues for communication between threads
        self._image_queue = queue.Queue(maxsize=90)  # Buffer 3 seconds for FPS=30
        self._frame_index_queue = queue.Queue(maxsize=90)

        self._os_name = get_os_name()
        nonscale_screen_size = pyautogui.size()
        self._screen_size = [
            int(self._device_pixel_ratio * nonscale_screen_size[0]),
            int(self._device_pixel_ratio * nonscale_screen_size[1])
        ]

        self._ffmpeg_process = None
        self._capture_thread = None
        self._mouse_thread = None
        self._writer_thread = None

        self._cursor_loader = CursorLoaderThread()
        self._cursor_loader.start()
        self._prev_cursor_anim_state = {}

        # For time tracking
        self._start_time = None
        self._frame_timestamps = queue.Queue(maxsize=90)

    @property
    def mouse_events(self):
        return self._mouse_events

    @property
    def icc_profile(self):
        return self._icc_profile

    @icc_profile.setter
    def icc_profile(self, value):
        self._icc_profile = value

    @property
    def device_pixel_ratio(self):
        return self._device_pixel_ratio

    @device_pixel_ratio.setter
    def device_pixel_ratio(self, value):
        self._device_pixel_ratio = value

    def start_recording(self):
        if not self._output_path:
            raise ValueError("Output path is not specified")

        self._is_stopped.clear()

        # Start FFmpeg process
        cmd = self._get_ffmpeg_command()
        logger.debug(f"FFmpeg command: {cmd}")
        if self._os_name == "windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            self._ffmpeg_process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=50*1024*1024,
                creationflags=subprocess.CREATE_NO_WINDOW,
                startupinfo=startupinfo
            )
        else:
            self._ffmpeg_process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=50*1024*1024,
            )

        # Start all threads
        self._capture_thread = Thread(target=self._capture_screen)
        self._mouse_thread = Thread(target=self._process_mouse_events)
        self._writer_thread = Thread(target=self._write_frames)

        self._capture_thread.start()
        self._mouse_thread.start()
        self._writer_thread.start()

        self._fps_stats = {
            "capture": {"frames": 0, "start_time": None, "current_fps": 0},
            "mouse": {"frames": 0, "start_time": None, "current_fps": 0},
            "writer": {"frames": 0, "start_time": None, "current_fps": 0}
        }
        self._fps_update_interval = 1.0

    def _update_fps(self, thread_name: str):
        stats = self._fps_stats[thread_name]
        if stats["start_time"] is None:
            stats["start_time"] = time.time()

        stats["frames"] += 1
        elapsed_time = time.time() - stats["start_time"]

        if elapsed_time >= self._fps_update_interval:
            stats["current_fps"] = stats["frames"] / elapsed_time
            logger.debug(f"{thread_name} FPS: {stats['current_fps']:.2f}")
            stats["frames"] = 0
            stats["start_time"] = time.time()

    def stop_recording(self):
        self._is_stopped.set()

        # Wait for threads to finish
        if self._capture_thread:
            self._capture_thread.join()
        if self._mouse_thread:
            self._mouse_thread.join()
        if self._writer_thread:
            self._writer_thread.join()

        # Close FFmpeg process
        if self._ffmpeg_process and self._ffmpeg_process.poll() is None:
            self._ffmpeg_process.communicate(b"q")
            self._ffmpeg_process.wait()

        logger.debug(f"Stopped recording")

    def _capture_screen(self):
        """Thread 1: Capture screen and put data into queues"""
        logger.debug("Started capturing")
        target_interval = 1.0 / self._fps
        next_frame_time = time.time() + target_interval

        # ScreenCapture
        icc_profile_probe_tries = 0
        icc_profile_probe_max_tries = 3
        screen_capture = get_screen_capture_class()
        try:
            with screen_capture(self._region) as sct:
                while not self._is_stopped.is_set():
                    current_time = time.time()

                    # Đợi đến thời điểm chính xác để capture frame tiếp theo
                    if current_time < next_frame_time:
                        time.sleep(max(0, next_frame_time - current_time))
                        continue

                    screenshot_bytes, pixel_format = sct.capture()
                    if (
                        pixel_format in ("jpeg", "png")
                        and not self._icc_profile
                        and icc_profile_probe_tries < icc_profile_probe_max_tries
                    ):
                        # Extract icc profile
                        image = Image.open(io.BytesIO(screenshot_bytes))
                        icc_profile_data = image.info.get("icc_profile")
                        if icc_profile_data:
                            self._icc_profile = generate_temp_file(extensions=".icc")
                            logger.debug(f"ICC profile file: {self._icc_profile}")
                        icc_profile_probe_tries += 1

                    # Lưu timestamp của frame
                    frame_time = time.time()
                    self._image_queue.put((screenshot_bytes, frame_time))
                    self._frame_index_queue.put(self._frame_index)

                    self._frame_index += 1
                    self._update_fps("capture")

                    # Tính thời điểm cần capture frame tiếp theo
                    next_frame_time += target_interval

                    # Reset nếu bị lag quá nhiều
                    if time.time() > next_frame_time + target_interval:
                        next_frame_time = time.time() + target_interval

        except Exception as e:
            logger.error(f"Screen capture error: {e}")
        finally:
            # Signal write thread to stop
            self._image_queue.put((None, None))

    def _write_frames(self):
        """Thread 3: Write image bytes to FFmpeg stdin with precise timing"""
        logger.debug("Started ffmpeg writer")
        target_interval = 1.0 / self._fps

        # Initialize timing variables
        self._start_time = time.time()
        # next_frame_time = self._start_time + target_interval
        frame_count = 0

        try:
            while not self._is_stopped.is_set():
                try:
                    # Get frame data with timestamp
                    image_bytes, frame_time = self._image_queue.get(timeout=0.5)

                    if image_bytes is None:  # Stop signal
                        break

                    current_time = time.time()

                    # Calculate ideal time for this frame
                    ideal_time = self._start_time + (frame_count * target_interval)

                    # If we"re running behind, skip the delay
                    if current_time <= ideal_time:
                        sleep_time = ideal_time - current_time
                        if sleep_time > 0:
                            time.sleep(sleep_time)

                    # Write frame
                    if self._ffmpeg_process.poll() is None:
                        self._ffmpeg_process.stdin.write(image_bytes)
                        self._ffmpeg_process.stdin.flush()
                        self._update_fps("writer")
                        frame_count += 1
                    else:
                        logger.error("FFmpeg process is not running")
                        break

                    self._image_queue.task_done()

                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Frame writing error: {e}")
                    break

        finally:
            logger.debug(f"FFmpeg writer stopped. Wrote {frame_count} frames")
            actual_duration = time.time() - self._start_time
            actual_fps = frame_count / actual_duration if actual_duration > 0 else 0
            logger.debug(f"Average output FPS: {actual_fps:.2f}")

    def _process_mouse_events(self):
        """Thread 2: Process mouse events using frame_index"""
        logger.debug("Started mouse tracking thread")
        try:
            last_frame = -1
            while not self._is_stopped.is_set():
                try:
                    frame_index = self._frame_index_queue.get(timeout=0.5)

                    if frame_index is None:
                        continue

                    if frame_index > last_frame:
                        x, y = pyautogui.position()

                        # Scale by device pixel ratio
                        x *= self._device_pixel_ratio
                        y *= self._device_pixel_ratio

                        relative_x = (x - self._region[0]) / self._region[2]
                        relative_y = (y - self._region[1]) / self._region[3]

                        cursor_state, anim_step = self._get_cursor()
                        self._mouse_events["move"][frame_index] = (
                            relative_x,
                            relative_y,
                            frame_index,
                            cursor_state,
                            anim_step,
                        )

                        self._update_fps("mouse")

                    last_frame = frame_index
                    self._frame_index_queue.task_done()

                    # Tính toán thời gian sleep
                    time.sleep(0.001)

                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Mouse tracking error: {e}")
                    break

        finally:
            logger.debug("Mouse tracking thread stopped")

    def _get_ffmpeg_command(self):
        ffmpeg_path = get_ffmpeg_path()
        width, height = int(self._region[2]), int(self._region[3])
        adjusted_width = (width + 1) & ~1
        adjusted_height = (height + 1) & ~1

        if self._os_name == "macos":  # macOS
            cmd = [
                ffmpeg_path,
                "-f", "image2pipe",
                "-framerate", str(self._fps),
                "-vcodec", "mjpeg",  # MJPEG for macOS
                "-i", "-",
                "-vf", f"scale={adjusted_width}:{adjusted_height}",
                "-c:v", "h264_videotoolbox",  # Hardware acceleration for macOS
                "-pix_fmt", "yuv420p",
                "-preset", "fast",
                "-y",
                self._output_path
            ]
        elif self._os_name == "linux":  # Linux
            cmd = [
                ffmpeg_path,
                "-f", "rawvideo",
                "-framerate", str(self._fps),
                "-video_size", f"{width}x{height}",  # Explicitly specify video size
                "-pixel_format", "bgra",  # Use bgra for python-mss
                "-i", "-",
                "-vf", f"scale={adjusted_width}:{adjusted_height}",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-crf", "23",
                "-vsync", "1",  # Help maintain sync
                "-y",  # Overwrite output file if exists
                self._output_path
            ]
        else:  # Windows
            cmd = [
                ffmpeg_path,
                "-f", "rawvideo",
                "-framerate", str(self._fps),
                "-video_size", f"{width}x{height}",
                "-pixel_format", "bgra",
                "-i", "-",
                "-vf", f"scale={adjusted_width}:{adjusted_height}",
                "-c:v", "libx264",
                "-preset", "fast",
                "-qp", "23",
                "-vsync", "1",  # Help maintain sync
                "-y",
                self._output_path
            ]
        return cmd

    def _get_cursor(self):
        cursor_theme = None
        if self._os_name in ["linux", "macos"]:
            cursor_theme = self._cursor_loader.cursor_theme

        cursor_state, anim_info = get_cursor_state(cursor_theme)
        if self._os_name == "linux" and cursor_state not in self._mouse_events["cursors_map"]:
            self._mouse_events["cursors_map"][cursor_state] = self._cursor_loader.get_cursor(cursor_state)

        # Calculate anim step
        anim_step = 0
        if anim_info.get("is_anim", False):
            n_steps = anim_info.get("n_steps", 1)
            if cursor_state not in self._prev_cursor_anim_state:
                self._prev_cursor_anim_state[cursor_state] = {"frame": -1, "anim_step": 0}

            if self._prev_cursor_anim_state[cursor_state]["frame"] == self._frame_index - 1:
                # The previous frame was the same cursor state
                prev_anim_step = self._prev_cursor_anim_state[cursor_state]["anim_step"]
                self._prev_cursor_anim_state[cursor_state]["anim_step"] = (prev_anim_step + 1) % n_steps
            else:
                # The previous frame was not the same cursor state. So reset the anim step
                self._prev_cursor_anim_state[cursor_state]["anim_step"] = 0

            self._prev_cursor_anim_state[cursor_state]["frame"] = self._frame_index
            anim_step = self._prev_cursor_anim_state[cursor_state]["anim_step"]
        return cursor_state, anim_step

    def set_region(self, region):
        self._region = region