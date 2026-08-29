import time
import os
import hashlib
from PyQt6.QtCore import QThread, pyqtSignal
from classifier import classify_content

IMAGES_DIR = "clips_images"

def get_file_hash(file_path):
    # calculate md5 hash of image content to detect exact duplicates
    hasher = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()
    except Exception:
        return None

class ClipboardListener(QThread):
    new_clip = pyqtSignal(str, str)

    def __init__(self, clipboard):
        super().__init__()
        self.clipboard = clipboard

    def run(self):
        last_content = ""
        last_img_hash = ""
        
        while True:
            try:
                mime_data = self.clipboard.mimeData()
                handled = False
                
                # Check for direct images from clipboard
                if mime_data.hasImage():
                    image = self.clipboard.image()
                    if not image.isNull():
                        if not os.path.exists(IMAGES_DIR):
                            os.makedirs(IMAGES_DIR)
                        
                        # save to a temporary check file first
                        temp_path = os.path.join(IMAGES_DIR, "temp_check.png")
                        image.save(temp_path, "PNG")
                        
                        current_img_hash = get_file_hash(temp_path)
                        
                        if current_img_hash and current_img_hash != last_img_hash:
                            last_img_hash = current_img_hash
                            final_path = os.path.join(IMAGES_DIR, f"clip_{int(time.time())}.png")
                            os.rename(temp_path, final_path)
                            
                            self.new_clip.emit(final_path, "image")
                            handled = True
                        else:
                            # cleanup temp if it's a duplicate
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                            handled = True # already processed, skip spam

                # Check for image files / paths copied from system
                if not handled and mime_data.hasUrls():
                    for url in mime_data.urls():
                        local_path = url.toLocalFile()
                        if local_path and any(local_path.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".bmp", ".webp"]):
                            if local_path != last_content and os.path.exists(local_path):
                                current_img_hash = get_file_hash(local_path)
                                if current_img_hash != last_img_hash:
                                    last_img_hash = current_img_hash
                                    last_content = local_path
                                    
                                    # copy to our storage
                                    if not os.path.exists(IMAGES_DIR):
                                        os.makedirs(IMAGES_DIR)
                                    final_path = os.path.join(IMAGES_DIR, f"clip_{int(time.time())}.png")
                                    
                                    import shutil
                                    shutil.copy(local_path, final_path)
                                    
                                    self.new_clip.emit(final_path, "image")
                                    handled = True
                                    break

                # Fallback to text / code / links
                if not handled:
                    text = self.clipboard.text().strip()
                    if text and text != last_content:
                        if text.startswith("file://") or any(text.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg"]):
                            clean_path = text.replace("file://", "")
                            if os.path.exists(clean_path):
                                current_img_hash = get_file_hash(clean_path)
                                if current_img_hash != last_img_hash:
                                    last_img_hash = current_img_hash
                                    last_content = text
                                    
                                    if not os.path.exists(IMAGES_DIR):
                                        os.makedirs(IMAGES_DIR)
                                    final_path = os.path.join(IMAGES_DIR, f"clip_{int(time.time())}.png")
                                    
                                    import shutil
                                    shutil.copy(clean_path, final_path)
                                    
                                    self.new_clip.emit(final_path, "image")
                                    handled = True
                        
                        if not handled:
                            last_content = text
                            category = classify_content(text)
                            self.new_clip.emit(text, category)
                            
            except Exception:
                pass
            
            time.sleep(1)