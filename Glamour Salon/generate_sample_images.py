import os
from PIL import Image, ImageDraw, ImageFont
import random

def generate_sample_image(width=800, height=600, color=None, text=None, filename="sample.jpg"):
    """Generate a sample image with optional text"""
    # Create a new image with random color if not specified
    if color is None:
        color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
    
    image = Image.new('RGB', (width, height), color)
    draw = ImageDraw.Draw(image)
    
    # Add text if provided
    if text:
        try:
            # Try to use a nice font
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Calculate text position (centered)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Draw text with contrasting color
        text_color = (255 - color[0], 255 - color[1], 255 - color[2])
        draw.text((x, y), text, fill=text_color, font=font)
    
    # Save the image
    image.save(filename)
    print(f"Generated {filename}")

def generate_sample_gallery():
    """Generate sample images for the gallery"""
    # Create gallery directory if it doesn't exist
    if not os.path.exists("gallery"):
        os.makedirs("gallery")
    
    # Generate sample images with different prefixes for categorization
    samples = [
        ("interior_salon.jpg", (200, 150, 200), "Salon Interior"),
        ("interior_reception.jpg", (150, 200, 150), "Reception Area"),
        ("service_haircut.jpg", (200, 150, 150), "Haircut Service"),
        ("service_coloring.jpg", (150, 150, 200), "Hair Coloring"),
        ("service_manicure.jpg", (200, 200, 150), "Manicure Station"),
        ("service_facial.jpg", (150, 200, 200), "Facial Treatment"),
        ("transformation_before_after_1.jpg", (200, 100, 150), "Hair Transformation"),
        ("transformation_before_after_2.jpg", (100, 200, 150), "Makeup Transformation"),
        ("team_stylist_1.jpg", (150, 100, 200), "Senior Stylist"),
        ("team_stylist_2.jpg", (200, 150, 100), "Color Specialist"),
        ("team_manager.jpg", (100, 150, 200), "Salon Manager"),
    ]
    
    for filename, color, text in samples:
        full_path = os.path.join("gallery", filename)
        generate_sample_image(800, 600, color, text, full_path)

def main():
    """Main function to generate sample images"""
    print("Generating sample gallery images...")
    generate_sample_gallery()
    print("Sample gallery images generated successfully!")

if __name__ == "__main__":
    main()