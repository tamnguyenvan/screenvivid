import os
import time
import io
import cv2
import queue
import subprocess
import threading
import numpy as np
from PIL import Image
from PySide6.QtCore import Signal, QThread
from screenvivid.utils.general import get_os_name, get_ffmpeg_path
from screenvivid.utils.logging import logger

class VideoReaderThread(QThread):
    frame_ready = Signal(np.ndarray)

    def __init__(self, video_processor, frame_queue, stop_flag, export_params):
        super().__init__()
        self.video_processor = video_processor
        self.frame_queue = frame_queue
        self.stop_flag = stop_flag
        self.export_params = export_params

    def run(self):
        output_size = tuple(self.export_params.get("output_size"))

        current_frame = self.video_processor.current_frame
        self.video_processor.video.set(cv2.CAP_PROP_POS_FRAMES, self.video_processor.start_frame)
        self.video_processor.current_frame = self.video_processor.start_frame

        total_frames = self.video_processor.end_frame - self.video_processor.start_frame
        for i in range(total_frames):
            if self.stop_flag.is_set():
                break

            ret, frame = self.video_processor.video.read()
            if ret:
                # Get processed frame (in RGB format)
                processed_frame = self.video_processor.process_frame(frame)
                self.video_processor.current_frame += 1

                # Resize frame if necessary
                if processed_frame.shape[:2] != output_size:
                    processed_frame = cv2.resize(processed_frame, output_size)

                # Push the processed frame to the queue
                self.frame_queue.put(processed_frame)
            else:
                break

        self.video_processor.video.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
        self.video_processor.current_frame = current_frame

        # Signal that the reading is done
        self.frame_queue.put(None)

class FFmpegWriterThread(QThread):
    progress = Signal(float)
    finished = Signal()

    def __init__(self, frame_queue, stop_flag, export_params):
        super().__init__()
        self.frame_queue = frame_queue
        self.stop_flag = stop_flag
        self.export_params = export_params

    def _get_ffmpeg_command(self, ffmpeg_path, output_path, fps, output_size):
        os_name = get_os_name()

        # Base command parameters common to all platforms
        base_cmd = [
            ffmpeg_path,
            '-f', 'image2pipe',
            '-framerate', str(fps),
            '-s', f"{output_size[0]}x{output_size[1]}",
            '-vcodec', 'mjpeg',  # Using MJPEG for input pipe
            '-i', '-'
        ]

        if os_name == "macos":
            # macOS specific - using VideoToolbox hardware acceleration
            output_cmd = [
                '-c:v', 'h264_videotoolbox',
                '-vf', 'format=yuv420p',
                '-preset', 'fast'
            ]
        elif os_name == "linux":
            # Linux specific - using libx264 or NVIDIA hardware acceleration if available
            output_cmd = [
                '-c:v', 'libx264',  # or 'h264_nvenc' if NVIDIA GPU is available
                '-preset', 'ultrafast',
                '-crf', '23',
                '-vf', 'format=yuv420p',
                '-movflags', '+faststart'
            ]
        else:  # windows
            # Windows specific - using NVIDIA hardware acceleration if available
            output_cmd = [
                '-c:v', 'h264_nvenc',  # NVIDIA GPU encoding
                '-preset', 'p1',  # Lower latency preset
                '-qp', '23',  # Quality parameter
                '-vf', 'format=yuv420p',
                '-movflags', '+faststart'
            ]

        # Combine commands and add output path
        return base_cmd + output_cmd + ['-y', output_path]

    def run(self):
        format = self.export_params.get("format", "mp4")
        fps = self.export_params.get("fps")
        output_size = tuple(self.export_params.get("output_size"))
        output_file = self.export_params.get("output_path", "output_video")
        icc_profile = self.export_params.get("icc_profile", None)
        total_frames = self.export_params.get("total_frames")

        # Determine output path
        video_dir = "Videos" if get_os_name() != "macos" else "Movies"
        output_dir = os.path.join(os.path.expanduser("~"), f"{video_dir}/ScreenVivid")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{output_file}.{format}")

        ffmpeg_path = get_ffmpeg_path()

        # FFmpeg command setup - changed pixel format to bgr24
        cmd = self._get_ffmpeg_command(ffmpeg_path, output_path, fps, output_size)
        logger.debug(f"FFmpeg export command: {' '.join(cmd)}")

        # Start FFmpeg process with larger pipe buffer
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=50*1024*1024  # 50MB buffer
        )
        icc_data = None
        if icc_profile:
            with open(icc_profile, "rb") as f:
                icc_data = f.read()

        frame_count = 0
        try:
            while not self.stop_flag.is_set():
                try:
                    frame = self.frame_queue.get(timeout=0.5)
                    if frame is None:
                        break

                    # Convert frame to PIL Image
                    image = Image.fromarray(frame)

                    # Use context manager for proper buffer cleanup
                    with io.BytesIO() as buffer:
                        try:
                            # Save image to buffer
                            image.save(buffer, format="JPEG", quality=95, icc_profile=icc_data)
                            image_bytes = buffer.getvalue()

                            # Check if process is still running
                            if process.poll() is None:
                                process.stdin.write(image_bytes)
                                process.stdin.flush()
                            else:
                                logger.error("FFmpeg process terminated early.")
                                break

                        except Exception as e:
                            logger.error(f"Error processing frame {frame_count}: {e}")
                            continue
                        finally:
                            # Ensure image is closed to free up memory
                            image.close()

                    frame_count += 1
                    self.progress.emit(frame_count / total_frames * 100)
                    self.frame_queue.task_done()

                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Error in write loop: {e}")
                    break

        finally:
            # Proper cleanup
            try:
                if process.poll() is None:
                    process.stdin.close()
                    process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
            finally:
                self.finished.emit()

class ExportThread(QThread):
    progress = Signal(float)
    finished = Signal()

    def __init__(self, video_processor, export_params):
        super().__init__()
        self.video_processor = video_processor
        self.export_params = export_params
        # Increased queue size for better buffering
        self.frame_queue = queue.Queue(maxsize=90)  # Buffer 3 second at 30fps
        self._stop_flag = threading.Event()

        self.export_params["total_frames"] = self.video_processor.end_frame - self.video_processor.start_frame

        self.reader_thread = VideoReaderThread(video_processor, self.frame_queue, self._stop_flag, export_params)
        self.writer_thread = FFmpegWriterThread(self.frame_queue, self._stop_flag, export_params)

        self.writer_thread.progress.connect(self.progress.emit)
        self.writer_thread.finished.connect(self.finished.emit)

    def stop(self):
        self._stop_flag.set()
        self.reader_thread.quit()
        self.writer_thread.quit()

    def run(self):
        self.reader_thread.start()
        self.writer_thread.start()

        self.reader_thread.wait()
        self.writer_thread.wait()

        self.finished.emit()