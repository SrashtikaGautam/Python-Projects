import os
import shutil
from image_manager import ImageManager

def organize_gallery():
    """Organize gallery images into category subdirectories"""
    manager = ImageManager()
    images = manager.get_local_images()
    
    # Create category directories
    categories = ['Interior', 'Services', 'Transformations', 'Team', 'General']
    for category in categories:
        category_path = os.path.join(manager.gallery_path, category.lower())
        if not os.path.exists(category_path):
            os.makedirs(category_path)
    
    # Move images to appropriate category directories
    for image_path in images:
        info = manager.get_image_info(image_path)
        if info:
            category_dir = os.path.join(manager.gallery_path, info['category'].lower())
            dest_path = os.path.join(category_dir, info['filename'])
            
            # Only move if not already in the correct directory
            if os.path.dirname(image_path) != category_dir:
                shutil.move(image_path, dest_path)
                print(f"Moved {info['filename']} to {info['category']} category")

def main():
    """Main function to organize the gallery"""
    print("Organizing gallery images...")
    organize_gallery()
    print("Gallery organization complete!")

if __name__ == "__main__":
    main()