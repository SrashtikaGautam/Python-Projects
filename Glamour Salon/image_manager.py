import os
import shutil
from PIL import Image
import glob

class ImageManager:
    def __init__(self, gallery_path="gallery"):
        self.gallery_path = gallery_path
        self.ensure_gallery_directory()
        
    def ensure_gallery_directory(self):
        """Ensure the gallery directory exists"""
        if not os.path.exists(self.gallery_path):
            os.makedirs(self.gallery_path)
            
    def get_local_images(self):
        """Get all images from the local gallery directory and subdirectories"""
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.webp']
        images = set()  # Use set to avoid duplicates
        
        for extension in image_extensions:
            # Check subdirectories only (avoid root directory)
            pattern = os.path.join(self.gallery_path, '**', extension)
            images.update(glob.glob(pattern, recursive=True))
            # Also check for uppercase extensions in subdirectories
            pattern = os.path.join(self.gallery_path, '**', extension.upper())
            images.update(glob.glob(pattern, recursive=True))
            
        return list(images)
    
    def categorize_image(self, image_path):
        """Categorize image based on filename prefix"""
        filename = os.path.basename(image_path).lower()
        
        if filename.startswith('interior_'):
            return 'Interior'
        elif filename.startswith('service_'):
            return 'Services'
        elif filename.startswith('transformation_'):
            return 'Transformations'
        elif filename.startswith('team_'):
            return 'Team'
        else:
            return 'General'
    
    def resize_image(self, image_path, max_width=800, max_height=600):
        """Resize image to fit within specified dimensions while maintaining aspect ratio"""
        try:
            with Image.open(image_path) as img:
                # Calculate new dimensions maintaining aspect ratio
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                # Save the resized image
                name, ext = os.path.splitext(image_path)
                resized_path = f"{name}_resized{ext}"
                img.save(resized_path, optimize=True, quality=85)
                return resized_path
        except Exception as e:
            print(f"Error resizing image {image_path}: {e}")
            return image_path
    
    def get_image_info(self, image_path):
        """Get image information including dimensions and category"""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                format = img.format
                
            category = self.categorize_image(image_path)
            filename = os.path.basename(image_path)
            
            return {
                'path': image_path,
                'filename': filename,
                'category': category,
                'width': width,
                'height': height,
                'format': format
            }
        except Exception as e:
            print(f"Error getting image info for {image_path}: {e}")
            return None

def main():
    """Main function for testing the ImageManager"""
    manager = ImageManager()
    
    # Get all images
    images = manager.get_local_images()
    
    print(f"Found {len(images)} images in gallery:")
    for image in images:
        info = manager.get_image_info(image)
        if info:
            print(f"  - {info['filename']} ({info['category']}) - {info['width']}x{info['height']}")

if __name__ == "__main__":
    main()