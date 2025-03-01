import os
import cv2
import numpy
import logging
from PIL import Image
from config import (
    STATIC_STICKER_MAX_SIZE,
    STATIC_STICKER_WIDTH,
    STATIC_STICKER_HEIGHT,
    STATIC_STICKER_FORMAT,
    ANIMATED_STICKER_MAX_SIZE,
    ANIMATED_STICKER_WIDTH,
    ANIMATED_STICKER_HEIGHT,
    ANIMATED_STICKER_FORMAT,
    ANIMATED_STICKER_FPS,
    ANIMATED_STICKER_MAX_DURATION,
    STATIC_EMOJI_MAX_SIZE,
    STATIC_EMOJI_WIDTH,
    STATIC_EMOJI_HEIGHT,
    STATIC_EMOJI_FORMAT,
    ANIMATED_EMOJI_MAX_SIZE,
    ANIMATED_EMOJI_WIDTH,
    ANIMATED_EMOJI_HEIGHT,
    ANIMATED_EMOJI_FORMAT,
    ANIMATED_EMOJI_FPS,
    ANIMATED_EMOJI_MAX_DURATION,
    STATIC_IMAGE_FORMATS,
    ANIMATED_IMAGE_FORMATS
)

logger = logging.getLogger(__name__)

class MediaProcessor:
    def __init__(self, file_path: str, is_sticker: bool = True):
        self.file_path = file_path
        self.is_sticker = is_sticker
        self.is_animated = self._check_if_animated()
        self.temp_files = []
        
    def __del__(self):
        """Cleanup temporary files"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                logger.error(f"Error removing temp file {temp_file}: {e}")
    
    def _check_if_animated(self) -> bool:
        """Check if file is animated (video or GIF)"""
        file_ext = os.path.splitext(self.file_path)[1].lower()
        
        if file_ext in ANIMATED_IMAGE_FORMATS:
            if file_ext == '.gif':
                # Check if a GIF is animated
                try:
                    with Image.open(self.file_path) as img:
                        return getattr(img, 'is_animated', False)
                except Exception as e:
                    logger.error(f"Error checking if GIF is animated: {e}")
                    return False
            return True
            
        return False
    
    def get_target_params(self):
        """Get target parameters based on file type and destination"""
        if self.is_sticker:
            if self.is_animated:
                return {
                    'max_size': ANIMATED_STICKER_MAX_SIZE,
                    'width': ANIMATED_STICKER_WIDTH,
                    'height': ANIMATED_STICKER_HEIGHT,
                    'format': ANIMATED_STICKER_FORMAT,
                    'fps': ANIMATED_STICKER_FPS,
                    'max_duration': ANIMATED_STICKER_MAX_DURATION
                }
            else:
                return {
                    'max_size': STATIC_STICKER_MAX_SIZE,
                    'width': STATIC_STICKER_WIDTH,
                    'height': STATIC_STICKER_HEIGHT,
                    'format': STATIC_STICKER_FORMAT
                }
        else:
            if self.is_animated:
                return {
                    'max_size': ANIMATED_EMOJI_MAX_SIZE,
                    'width': ANIMATED_EMOJI_WIDTH,
                    'height': ANIMATED_EMOJI_HEIGHT,
                    'format': ANIMATED_EMOJI_FORMAT,
                    'fps': ANIMATED_EMOJI_FPS,
                    'max_duration': ANIMATED_EMOJI_MAX_DURATION
                }
            else:
                return {
                    'max_size': STATIC_EMOJI_MAX_SIZE,
                    'width': STATIC_EMOJI_WIDTH,
                    'height': STATIC_EMOJI_HEIGHT,
                    'format': STATIC_EMOJI_FORMAT
                }
    
    def check_size_requirements(self) -> bool:
        """Check if file meets size requirements"""
        file_size = os.path.getsize(self.file_path) / 1024  # Convert to KB
        target_params = self.get_target_params()
        return file_size <= target_params['max_size']
    
    def process_static_image(self) -> str:
        """Process static image file according to requirements"""
        target_params = self.get_target_params()
        
        try:
            img = Image.open(self.file_path)
            logger.info(f"Opened image: {self.file_path}")
            logger.info(f"Original size: {img.size}")
            
            # Convert RGBA to RGB if needed
            if img.mode == 'RGBA' and target_params['format'] != 'PNG':
                logger.info("Converting RGBA to RGB")
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background

            # Get current dimensions
            width, height = img.size
            logger.info(f"Current dimensions: {width}x{height}")
            
            # Check if we need to resize
            max_side = max(width, height)
            target_size = target_params['width']  # 512 for stickers
            
            if max_side != target_size:
                # Calculate scaling ratio to make the larger side exactly 512
                ratio = target_size / max_side
                
                # Calculate new dimensions
                new_width = width * ratio
                new_height = height * ratio
                
                # Round to nearest integer
                new_width_int = round(new_width)
                new_height_int = round(new_height)
                
                logger.info(f"Calculated dimensions before rounding: {new_width}x{new_height}")
                logger.info(f"Rounded dimensions: {new_width_int}x{new_height_int}")
                
                # Check if rounding caused the larger side to exceed 512
                if max(new_width_int, new_height_int) > target_size:
                    # If exceeded, we'll use floor instead of round for the larger side
                    if new_width_int > new_height_int:
                        new_width_int = int(new_width)
                        # Recalculate height with the exact same ratio
                        new_height_int = round(new_width_int * (height / width))
                    else:
                        new_height_int = int(new_height)
                        # Recalculate width with the exact same ratio
                        new_width_int = round(new_height_int * (width / height))
                
                logger.info(f"Final dimensions after adjustment: {new_width_int}x{new_height_int}")
                # Resize image using high-quality Lanczos resampling
                img = img.resize((new_width_int, new_height_int), Image.Resampling.LANCZOS)
            
            # Save processed image
            output_path = f"{os.path.splitext(self.file_path)[0]}_processed.{target_params['format'].lower()}"
            self.temp_files.append(output_path)
            logger.info(f"Saving to: {output_path}")
            
            if target_params['format'] == 'PNG':
                img.save(output_path, 'PNG', optimize=True)
            else:
                img.save(output_path, target_params['format'], quality=95, method=6)
            
            logger.info(f"Saved file size: {os.path.getsize(output_path)} bytes")
            return output_path
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            import traceback
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            return self.file_path
    
    def process_animated(self) -> str:
        """Process animated file (video or GIF) according to requirements"""
        target_params = self.get_target_params()
        file_ext = os.path.splitext(self.file_path)[1].lower()
        
        try:
            if file_ext == '.gif':
                return self._process_animated_gif(target_params)
            else:
                return self._process_video(target_params)
        except Exception as e:
            logger.error(f"Error processing animated file: {str(e)}")
            return self.file_path

    def _process_animated_gif(self, target_params: dict) -> str:
        """Convert GIF to WEBM"""
        try:
            # Create a temporary directory for frames
            temp_dir = f"temp_frames_{os.path.basename(self.file_path)}"
            os.makedirs(temp_dir, exist_ok=True)
            self.temp_files.append(temp_dir)
            logger.info(f"Created temp directory: {temp_dir}")
            
            # Open GIF
            img = Image.open(self.file_path)
            frame_count = 0
            frames = []
            logger.info(f"Original GIF dimensions: {img.width}x{img.height}")
            
            # Calculate new dimensions (keep proportions)
            ratio = min(
                target_params['width']/img.width,
                target_params['height']/img.height
            )
            new_width = int(img.width * ratio)
            new_height = int(img.height * ratio)
            
            logger.info(f"Target dimensions: {new_width}x{new_height}")
            
            # Extract and save frames
            try:
                while True:
                    # Limit the number of frames
                    if frame_count >= target_params['fps'] * target_params['max_duration']:
                        break
                        
                    # Save the frame
                    frame_path = os.path.join(temp_dir, f"frame_{frame_count:04d}.png")
                    
                    frame = img.copy()
                    frame = frame.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    frame.save(frame_path)
                    frames.append(frame_path)
                    
                    frame_count += 1
                    img.seek(img.tell() + 1)
            except EOFError:
                pass
            
            logger.info(f"Extracted {frame_count} frames")
            
            if not frames:
                raise ValueError("No frames extracted from GIF")
            
            # Create WEBM from frames
            output_path = f"{os.path.splitext(self.file_path)[0]}_processed.{target_params['format'].lower()}"
            logger.info(f"Creating WEBM file: {output_path}")
            
            # Open the first frame to get the dimensions
            first_frame = cv2.imread(frames[0])
            height, width = first_frame.shape[:2]
            
            # Create a video writer
            fourcc = cv2.VideoWriter_fourcc(*'VP90')
            out = cv2.VideoWriter(
                output_path,
                fourcc,
                target_params['fps'],
                (width, height)
            )
            
            # Recording frames
            for frame_path in frames:
                frame = cv2.imread(frame_path)
                out.write(frame)
            
            out.release()
            logger.info(f"Initial WEBM created, size: {os.path.getsize(output_path)/1024:.2f}KB")
            
            # Check the file size and reduce the bitrate if necessary
            while os.path.getsize(output_path) / 1024 > target_params['max_size']:
                # Reduce bitrate by 20% at each iteration
                bitrate = int(os.path.getsize(output_path) * 0.8)
                logger.info(f"Reducing bitrate to {bitrate} bytes")
                
                out = cv2.VideoWriter(
                    output_path,
                    fourcc,
                    target_params['fps'],
                    (width, height),
                    params=[
                        cv2.VIDEOWRITER_PROP_QUALITY, 95,
                        cv2.VIDEOWRITER_PROP_BITRATE, bitrate
                    ]
                )
                
                for frame_path in frames:
                    frame = cv2.imread(frame_path)
                    out.write(frame)
                
                out.release()
                logger.info(f"Current file size: {os.path.getsize(output_path)/1024:.2f}KB")
            
            logger.info(f"Final file size: {os.path.getsize(output_path)/1024:.2f}KB")
            return output_path
            
        except Exception as e:
            logger.error(f"Error processing GIF: {str(e)}")
            import traceback
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            return self.file_path

    def _process_video(self, target_params: dict) -> str:
        """Process video file to WEBM"""
        try:
            # Open the video
            cap = cv2.VideoCapture(self.file_path)
            logger.info("Opened video file")
            
            # Get video parameters
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            logger.info(f"Original video dimensions: {width}x{height}")
            
            # Calculate new dimensions (keep proportions)
            ratio = min(
                target_params['width'] / width,
                target_params['height'] / height
            )
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            
            logger.info(f"Target dimensions: {new_width}x{new_height}")
            
            # Create output file
            output_path = f"{os.path.splitext(self.file_path)[0]}_processed.{target_params['format'].lower()}"
            logger.info(f"Output path: {output_path}")
            
            # Create a video writer
            fourcc = cv2.VideoWriter_fourcc(*'VP90')
            out = cv2.VideoWriter(
                output_path,
                fourcc,
                target_params['fps'],
                (new_width, new_height)
            )
            
            frame_count = 0
            max_frames = int(target_params['fps'] * target_params['max_duration'])
            logger.info(f"Processing frames (max {max_frames} frames)")
            
            # Process each frame
            while cap.isOpened() and frame_count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Resize frame
                frame = cv2.resize(frame, (new_width, new_height))
                out.write(frame)
                frame_count += 1
            
            logger.info(f"Processed {frame_count} frames")
            
            # Freeing up resources
            cap.release()
            out.release()
            
            # Check the file size and reduce the bitrate if necessary
            initial_size = os.path.getsize(output_path) / 1024
            logger.info(f"Initial file size: {initial_size:.2f}KB")
            
            while os.path.getsize(output_path) / 1024 > target_params['max_size']:
                # Reduce bitrate by 20% at each iteration
                bitrate = int(os.path.getsize(output_path) * 0.8)
                logger.info(f"Reducing bitrate to {bitrate} bytes")
                
                cap = cv2.VideoCapture(self.file_path)
                out = cv2.VideoWriter(
                    output_path,
                    fourcc,
                    target_params['fps'],
                    (new_width, new_height),
                    params=[
                        cv2.VIDEOWRITER_PROP_QUALITY, 95,
                        cv2.VIDEOWRITER_PROP_BITRATE, bitrate
                    ]
                )
                
                frame_count = 0
                while cap.isOpened() and frame_count < max_frames:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    frame = cv2.resize(frame, (new_width, new_height))
                    out.write(frame)
                    frame_count += 1
                
                cap.release()
                out.release()
                
                current_size = os.path.getsize(output_path) / 1024
                logger.info(f"Current file size: {current_size:.2f}KB")
            
            final_size = os.path.getsize(output_path) / 1024
            logger.info(f"Final file size: {final_size:.2f}KB")
            return output_path
            
        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            import traceback
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            return self.file_path
    
    def process(self) -> tuple[str, bool]:
        """Process media file and return path to processed file and whether it was modified"""
        try:
            logger.info("Starting process method")
            # Checking supported formats
            file_ext = os.path.splitext(self.file_path)[1].lower()
            logger.info(f"File extension: {file_ext}")
            logger.info(f"Supported formats: {STATIC_IMAGE_FORMATS + ANIMATED_IMAGE_FORMATS}")
            
            if file_ext not in STATIC_IMAGE_FORMATS + ANIMATED_IMAGE_FORMATS:
                logger.error(f"Unsupported format: {file_ext}")
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            # Get target parameters
            target_params = self.get_target_params()
            current_ext = os.path.splitext(self.file_path)[1].lower()
            target_ext = f".{target_params['format'].lower()}"
            
            # Check if format conversion is needed
            needs_format_conversion = current_ext != target_ext
            
            # Process file if format conversion needed or it's animated
            if needs_format_conversion or self.is_animated:
                logger.info("Format conversion needed or file is animated")
                if self.is_animated:
                    logger.info("Processing animated file")
                    return self.process_animated(), True
                else:
                    logger.info("Processing static image for format conversion")
                    return self.process_static_image(), True
            
            # For static images, first check and adjust resolution if needed
            if not self.is_animated:
                img = Image.open(self.file_path)
                width, height = img.size
                max_side = max(width, height)
                target_size = target_params['width']
                
                if max_side != target_size:
                    logger.info("Resolution adjustment needed")
                    return self.process_static_image(), True
                
                # If resolution is correct, check file size
                if not self.check_size_requirements():
                    logger.info("File needs optimization for size")
                    return self.process_static_image(), True
            
            logger.info("No processing needed")
            return self.file_path, False
            
        except Exception as e:
            logger.error(f"Error in process method: {str(e)}")
            import traceback
            logger.error(f"Process method traceback: {traceback.format_exc()}")
            return self.file_path, False 