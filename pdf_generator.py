import os
import re
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from PIL import Image
import glob

def natural_sort_key(s):
    """
    Sort strings with embedded numbers in natural order.
    Example: ['page1.png', 'page2.png', 'page10.png'] will sort correctly
    instead of ['page1.png', 'page10.png', 'page2.png']
    
    Args:
        s (str): String to be sorted
        
    Returns:
        list: List of string and int elements for sorting
    """
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', s)]

def get_image_dimensions(image_path):
    """
    Get the dimensions of an image.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        tuple: (width, height) of the image
    """
    with Image.open(image_path) as img:
        return img.size

def images_to_pdf(image_paths, output_pdf_path, page_size=None):
    """
    Convert a list of images into a single PDF file.
    
    Args:
        image_paths (list): List of paths to image files
        output_pdf_path (str): Path where the PDF will be saved
        page_size (tuple, optional): Custom page size as (width, height) in points
                                     If None, will use the size of each image
    
    Returns:
        str: Path to the created PDF file
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)
    
    # Sort image paths using natural sort to handle page numbers correctly
    image_paths = sorted(image_paths, key=natural_sort_key)
    print(f"Sorted image paths for PDF generation: {[os.path.basename(p) for p in image_paths]}")
    
    # Create a canvas for PDF
    if page_size:
        c = canvas.Canvas(output_pdf_path, pagesize=page_size)
    else:
        # Use the first image's dimensions as default
        if image_paths:
            width, height = get_image_dimensions(image_paths[0])
            c = canvas.Canvas(output_pdf_path, pagesize=(width, height))
        else:
            c = canvas.Canvas(output_pdf_path, pagesize=A4)
    
    # Process each image
    for img_path in image_paths:
        if not os.path.exists(img_path):
            print(f"Warning: Image not found: {img_path}")
            continue
            
        img_width, img_height = get_image_dimensions(img_path)
        
        # If no custom page size, set page size to match image
        if not page_size:
            c.setPageSize((img_width, img_height))
        
        # Draw image on the canvas (at 0,0 with image's full width/height)
        c.drawImage(img_path, 0, 0, width=img_width, height=img_height)
        c.showPage()
    
    # Save the PDF
    c.save()
    print(f"PDF created successfully at: {output_pdf_path}")
    return output_pdf_path

def batch_images_to_pdf(base_dir, output_dir="outputs"):
    """
    Process multiple directories of images, creating a PDF for each directory.
    
    Args:
        base_dir (str): Base directory containing subdirectories with images
        output_dir (str): Directory where PDFs will be saved
        
    Returns:
        dict: Mapping of directory names to output PDF paths
    """
    results = {}
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each subdirectory in the base directory
    for dir_name in os.listdir(base_dir):
        dir_path = os.path.join(base_dir, dir_name)
        
        # Skip if not a directory
        if not os.path.isdir(dir_path):
            continue
            
        # Get all images in the directory
        image_files = []
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            image_files.extend(glob.glob(os.path.join(dir_path, ext)))
        
        if not image_files:
            print(f"No images found in {dir_path}")
            continue
            
        # Create output subdirectory if it doesn't exist
        output_subdir = os.path.join(output_dir, dir_name)
        os.makedirs(output_subdir, exist_ok=True)
        
        # Create PDF file path
        pdf_path = os.path.join(output_subdir, f"{dir_name}.pdf")
        
        # Convert images to PDF
        results[dir_name] = images_to_pdf(image_files, pdf_path)
    
    return results

if __name__ == "__main__":
    # Test with a sample directory
    test_dir = "imgs"
    if os.path.exists(test_dir):
        pdfs = batch_images_to_pdf(test_dir, "outputs")
        print(f"Created PDFs: {pdfs}")
    else:
        print(f"Test directory {test_dir} not found")
