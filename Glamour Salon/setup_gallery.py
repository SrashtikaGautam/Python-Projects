import os
import subprocess
import sys

def setup_gallery():
    """Setup the gallery by generating sample images"""
    print("Setting up Glamour Salon gallery...")
    
    # Check if gallery directory exists
    if not os.path.exists("gallery"):
        print("Creating gallery directory...")
        os.makedirs("gallery")
    
    # Check if we have any images in the gallery
    image_files = [f for f in os.listdir("gallery") if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    
    if not image_files:
        print("No images found in gallery. Generating sample images...")
        try:
            # Run the generate_sample_images script
            subprocess.run([sys.executable, "generate_sample_images.py"], check=True)
            print("Sample images generated successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error generating sample images: {e}")
            return False
        except FileNotFoundError:
            print("generate_sample_images.py not found. Please make sure it exists in the current directory.")
            return False
    else:
        print(f"Found {len(image_files)} images in gallery. Skipping sample image generation.")
    
    # Organize the gallery
    print("Organizing gallery...")
    try:
        # Run the organize_gallery script
        subprocess.run([sys.executable, "organize_gallery.py"], check=True)
        print("Gallery organized successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error organizing gallery: {e}")
        return False
    except FileNotFoundError:
        print("organize_gallery.py not found. Please make sure it exists in the current directory.")
        return False
    
    print("Gallery setup complete!")
    return True

def main():
    """Main function to setup the gallery"""
    if setup_gallery():
        print("\nGallery is ready for use!")
        print("You can now run the main application with: streamlit run app.py")
    else:
        print("\nGallery setup failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()