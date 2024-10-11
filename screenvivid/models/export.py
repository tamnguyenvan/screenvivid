import os
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


# Codec-specific configurations
codec_params = {
    "mpeg4": {
        "codec": "mpeg4",
        "params": {
            "q:v": "2",         # Highest quality (2-31, lower is better)
            "trellis": "2",     # Compression quality
            "mbd": "rd",        # macroblock decision: rate distortion
            "flags": "+mv4",    # Enable 4MV (4 motion vectors per macroblock)
            "pix_fmt": "yuv420p",
            "movflags": "+faststart"
        }
    },
    "h264": {
        "codec": "libx264",
        "params": {
            "preset": "ultrafast",
            "crf": "23",        # Constant Rate Factor (18-28, lower is better)
            "tune": "zerolatency",
            "pix_fmt": "yuv420p",
            "movflags": "+faststart"
        }
    }
}

# Platform-specific overrides and additions
platform_specific = {
    "windows": {
        "default_codec": "mpeg4",
        "params": {
            "max_muxing_queue_size": "1024"  # Windows-specific buffer size
        }
    },
    "macos": {
        "default_codec": "h264",
        "h264": {
            "codec": "h264_videotoolbox",  # Use hardware acceleration on macOS
            "params": {
                "allow_sw": "1",
                "q": "23"      # Quality parameter for VideoToolbox
            }
        }
    },
    "linux": {
        "default_codec": "h264"
    }
}

def get_codec_config(os_name, requested_codec=None):
    """
    Get codec configuration for specified OS and codec.

    Args:
        os_name (str): Operating system name ('windows', 'macos', 'linux')
        requested_codec (str, optional): Specific codec to use. If None, uses platform default.

    Returns:
        dict: Combined codec configuration
    """
    # Get platform settings
    platform = platform_specific.get(os_name, {})

    # Determine which codec to use
    codec_name = requested_codec or platform.get('default_codec', 'h264')

    # Start with base codec configuration
    if codec_name not in codec_params:
        raise ValueError(f"Unsupported codec: {codec_name}")

    config = {
        "codec": codec_params[codec_name]["codec"],
        "params": dict(codec_params[codec_name]["params"])
    }

    # Apply platform-specific codec override if exists
    if codec_name in platform:
        if "codec" in platform[codec_name]:
            config["codec"] = platform[codec_name]["codec"]
        if "params" in platform[codec_name]:
            config["params"].update(platform[codec_name]["params"])

    # Apply platform-specific general params if exists
    if "params" in platform:
        config["params"].update(platform["params"])

    return config


class FFmpegWriterThread(QThread):
    progress = Signal(float)
    finished = Signal()

    def __init__(self, frame_queue, stop_flag, export_params):
        super().__init__()
        self.frame_queue = frame_queue
        self.stop_flag = stop_flag
        self.export_params = export_params

    def _get_ffmpeg_command(self, ffmpeg_path, output_path, fps, output_size, codec_config):
        os_name = get_os_name()
        width, height = output_size
        adjusted_width = (width + 1) & ~1
        adjusted_height = (height + 1) & ~1

        # Get codec configuration from export_params or use default
        requested_codec = self.export_params.get("codec")
        codec_config = get_codec_config(os_name, requested_codec)

        # Allow override of codec parameters from export_params
        if "codec_params" in self.export_params:
            codec_config["params"].update(self.export_params["codec_params"])

        # Base command parameters
        base_cmd = [
            ffmpeg_path,
            '-f', 'image2pipe',
            '-framerate', str(fps),
            '-s', f"{output_size[0]}x{output_size[1]}",
            '-vcodec', 'mjpeg',
            '-i', '-',
            '-vf', f'scale={adjusted_width}:{adjusted_height}'
        ]

        # Build output command from configuration
        output_cmd = ['-c:v', codec_config["codec"]]
        for key, value in codec_config["params"].items():
            output_cmd.extend([f'-{key}', str(value)])

        return base_cmd + output_cmd + ['-y', output_path]

    def run(self):
        format = self.export_params.get("format", "mp4")
        fps = self.export_params.get("fps")
        output_size = tuple(self.export_params.get("output_size"))
        output_file = self.export_params.get("output_path", "output_video")
        icc_profile = self.export_params.get("icc_profile", None)
        total_frames = self.export_params.get("total_frames")
        codec_config = self.export_params.get("codec_config", {})

        # Determine output path
        video_dir = "Videos" if get_os_name() != "macos" else "Movies"
        output_dir = os.path.join(os.path.expanduser("~"), f"{video_dir}/ScreenVivid")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{output_file}.{format}")

        ffmpeg_path = get_ffmpeg_path()

        # FFmpeg command setup - changed pixel format to bgr24
        cmd = self._get_ffmpeg_command(ffmpeg_path, output_path, fps, output_size, codec_config)
        logger.debug(f"FFmpeg export command: {' '.join(cmd)}")

        # Start FFmpeg process with larger pipe buffer
        if get_os_name() == "windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=10*1024*1024,
                creationflags=subprocess.CREATE_NO_WINDOW,
                startupinfo=startupinfo
            )
        else:
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=10*1024*1024,
            )
        icc_data = None
        try:
            if icc_profile:
                with open(icc_profile, "rb") as f:
                    icc_data = f.read()

            frame_count = 0
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