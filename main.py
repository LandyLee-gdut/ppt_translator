import argparse
import os
import sys
import re
from pdf_utils import convert_pdf_to_images, cleanup_temp_images
from qwen_utils import batch_process_images, MODELSCOPE_API_KEY
from pdf_generator import images_to_pdf, natural_sort_key

def check_environment():
    """Check if all required environment variables are set"""
    if not MODELSCOPE_API_KEY:
        print("ERROR: MODELSCOPE_API_KEY environment variable not set.")
        print("Please set it using:")
        print("  export MODELSCOPE_API_KEY='your-api-key'  # on Linux/macOS")
        print("  set MODELSCOPE_API_KEY=your-api-key  # on Windows")
        return False
    return True

def main():
    # Verify environment setup
    if not check_environment():
        sys.exit(1)
        
    parser = argparse.ArgumentParser(description='Translate text in PDF files from Chinese to English')
    parser.add_argument('pdf_path', nargs='?', help='Path to the PDF file')
    parser.add_argument('-o', '--output', help='Output directory for the translated PDF', default='outputs')
    parser.add_argument('--web', action='store_true', help='Launch the web interface')
    
    args = parser.parse_args()
    
    # Launch web interface if requested or if no PDF path provided
    if args.web or not args.pdf_path:
        print("Launching web interface...")
        from gradio_app import create_interface
        app = create_interface()
        app.launch(share=False)  # Set share=False for more reliable operation
        return
    
    # Command line mode - requires pdf_path
    if not os.path.exists(args.pdf_path):
        print(f"Error: PDF file not found: {args.pdf_path}")
        sys.exit(1)
        
    # Get PDF file name
    pdf_name = os.path.splitext(os.path.basename(args.pdf_path))[0]
    
    # Create output directory if needed
    os.makedirs(args.output, exist_ok=True)
    output_subdir = os.path.join(args.output, pdf_name)
    os.makedirs(output_subdir, exist_ok=True)
    
    try:
        # Step 1: Convert PDF to images
        print(f"Converting PDF to images...")
        img_dir = os.path.join("imgs", pdf_name)
        image_paths = convert_pdf_to_images(args.pdf_path, img_dir)
        print(f"Converted {len(image_paths)} pages to images")
        
        # Step 2: Process each image for translation
        print(f"Translating text in images...")
        translated_paths = batch_process_images(image_paths, pdf_name=pdf_name, output_dir=args.output)
        print(f"Translation completed")
        
        # Step 3: Combine translated images into a PDF
        output_pdf_path = os.path.join(output_subdir, f"{pdf_name}_translated.pdf")
        
        # Sort the translated paths using natural sorting
        translated_paths = sorted(translated_paths, key=natural_sort_key)
        
        images_to_pdf(translated_paths, output_pdf_path)
        print(f"PDF generation completed")
        
        print(f"Successfully processed '{pdf_name}.pdf'. Translated {len(image_paths)} pages.")
        print(f"Output PDF: {output_pdf_path}")
        
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
