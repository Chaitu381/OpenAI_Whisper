import os
import time
import whisper
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration
# Configuration
INPUT_DIR = r"D:\code\Whisper\media_files"  # Directory to watch
OUTPUT_DIR = r"D:\code\Whisper\new_media_files"  # Directory to save transcriptions
SUPPORTED_EXT = {'.mp3', '.wav', '.mp4', '.mkv', '.mov', '.flv', '.aac', '.m4a'}
MODEL_SIZE = "small"  # Choose from tiny, base, small, medium, large

# Load Whisper model once
model = whisper.load_model(MODEL_SIZE)

class MediaHandler(FileSystemEventHandler):
    def on_created(self, event):
        """Handle new file creation events"""
        if not event.is_directory:
            self.process_file(event.src_path)

    def on_moved(self, event):
        """Handle file movement events"""
        if not event.is_directory:
            self.process_file(event.dest_path)

    def process_file(self, file_path):
        """Process supported media files"""
        ext = os.path.splitext(file_path)[1].lower()
        if ext in SUPPORTED_EXT:
            process_media_file(file_path)

def get_output_path(input_path):
    """Generate output path maintaining directory structure"""
    relative_path = os.path.relpath(input_path, INPUT_DIR)
    output_path = os.path.join(OUTPUT_DIR, relative_path)
    output_path = os.path.splitext(output_path)[0] + '.txt'
    return output_path

def process_media_file(input_path):
    """Process a single media file and save transcription"""
    output_path = get_output_path(input_path)
    
    # Skip already processed files
    if os.path.exists(output_path):
        print(f"Skipping already processed file: {input_path}")
        return
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        # Transcribe using Whisper
        result = model.transcribe(input_path)
        
        # Save transcription
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result['text'])
        
        print(f"Successfully processed: {input_path}")
    except Exception as e:
        print(f"Error processing {input_path}: {str(e)}")

def scan_existing_files():
    """Process existing files in the input directory"""
    print(f"Scanning directory: {INPUT_DIR}")  # Debugging statement
    for root, dirs, files in os.walk(INPUT_DIR):
        print(f"Found {len(files)} files in {root}")  # Debugging statement
        for file in files:
            file_path = os.path.join(root, file)
            print(f"Processing file: {file_path}")  # Debugging statement
            process_media_file(file_path)

def start_monitoring():
    """Start watching for new files"""
    event_handler = MediaHandler()
    observer = Observer()
    observer.schedule(event_handler, INPUT_DIR, recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    # Create output directory structure
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Initial processing of existing files
    print("Processing existing files...")
    scan_existing_files()
    
    # Start real-time monitoring
    print("Starting real-time monitoring...")
    start_monitoring()