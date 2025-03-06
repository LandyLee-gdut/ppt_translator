import gradio as gr
import os
import time
import tempfile
import shutil
from pdf_utils import convert_pdf_to_images, batch_convert_pdfs, cleanup_temp_images
from qwen_utils import batch_process_images, MODELSCOPE_API_KEY
from pdf_generator import images_to_pdf, natural_sort_key
import glob

# Global variables
TEMP_DIR = "temp_uploads"
OUTPUT_DIR = "outputs"

# Ensure directories exist
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Check for API key
if not MODELSCOPE_API_KEY:
    print("WARNING: MODELSCOPE_API_KEY environment variable not set.")
    print("The application may not function correctly without an API key.")

def process_pdf(pdf_file, progress=gr.Progress()):
    """
    Process a PDF file: convert to images, translate text, and generate a new PDF.
    
    Args:
        pdf_file: Gradio file upload object
        progress (gr.Progress): Gradio progress tracker
        
    Returns:
        tuple: (success message, output PDF path, list of image paths)
    """
    if pdf_file is None:
        return "No file uploaded. Please upload a PDF file.", None, []
    
    # Extract file name without extension
    file_name = os.path.splitext(os.path.basename(pdf_file.name))[0]
    
    # Create a temp file with a safe name
    temp_pdf_path = os.path.join(TEMP_DIR, f"{file_name}.pdf")
    
    # Save the uploaded file - pdf_file is a TemporaryFile in Gradio 4.0+
    # Copy file content to our destination
    with open(temp_pdf_path, "wb") as f:
        # For Gradio 4.0+, we need to read the content differently
        if hasattr(pdf_file, 'name'):
            # This is for directly accessing the file path
            shutil.copyfile(pdf_file.name, temp_pdf_path)
        else:
            # Fallback for other Gradio versions
            f.write(pdf_file.read())
    
    progress(0.1, desc="PDF file received")
    
    try:
        # Step 1: Convert PDF to images
        progress(0.2, desc="Converting PDF to images...")
        img_dir = os.path.join("imgs", file_name)
        image_paths = convert_pdf_to_images(temp_pdf_path, img_dir)
        progress(0.4, desc=f"Converted {len(image_paths)} pages to images")
        
        # Step 2: Process each image for translation
        progress(0.5, desc="Translating text in images...")
        translated_paths = batch_process_images(image_paths, pdf_name=file_name, output_dir=OUTPUT_DIR)
        progress(0.8, desc="Translation completed")
        
        # Step 3: Combine translated images into a PDF
        output_subdir = os.path.join(OUTPUT_DIR, file_name)
        output_pdf_path = os.path.join(output_subdir, f"{file_name}_translated.pdf")
        
        # Sort the translated paths using natural sorting for correct page ordering
        translated_paths = sorted(translated_paths, key=natural_sort_key)
        
        images_to_pdf(translated_paths, output_pdf_path)
        progress(1.0, desc="PDF generation completed")
        
        message = f"Successfully processed '{file_name}.pdf'. Translated {len(image_paths)} pages."
        
        # Return paths relative to the app for display
        return message, output_pdf_path, translated_paths
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error processing PDF: {str(e)}", None, []
    finally:
        # Clean up the temporary PDF file
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)

# Helper function to handle file downloading
def prepare_download(file_path):
    """
    Prepare a file for download by returning its path
    
    Args:
        file_path (str): Path to the file to be downloaded
        
    Returns:
        str or None: The file path if it exists, None otherwise
    """
    if file_path and os.path.exists(file_path):
        return file_path
    return None

def create_interface():
    """Create and configure the Gradio interface"""
    
    with gr.Blocks(title="PDF Translator") as app:
        gr.Markdown("""
        # PDF Translator
        
        Upload a PDF file to translate the text from Chinese to English.
        
        The application will:
        1. Convert the PDF to images
        2. Identify and translate the text
        3. Generate a new PDF with translated text
        """)
        
        # Show API key warning if needed
        if not MODELSCOPE_API_KEY:
            gr.Markdown("""
            ⚠️ **WARNING: No API Key Detected** ⚠️
            
            Please set your MODELSCOPE_API_KEY environment variable before using this application.
            Without an API key, the translation functionality will not work.
            
            ```bash
            export MODELSCOPE_API_KEY="your-api-key-here"  # For Linux/macOS
            set MODELSCOPE_API_KEY=your-api-key-here  # For Windows
            ```
            """)
        
        with gr.Row():
            with gr.Column(scale=1):
                # Use type="filepath" for Gradio 4.0+
                pdf_input = gr.File(label="Upload a PDF file", file_types=[".pdf"], type="filepath")
                translate_btn = gr.Button("Translate PDF", variant="primary")
            
            with gr.Column(scale=2):
                output_message = gr.Textbox(label="Status", interactive=False)
                
        with gr.Tabs():
            with gr.TabItem("Translated PDF"):
                # Store the path to the generated PDF
                pdf_output_path = gr.State()
                pdf_output_visible = gr.Textbox(label="Translated PDF Ready", interactive=False)
                
                # Use a standard File component for downloads
                pdf_download = gr.File(label="Download Translated PDF", interactive=False)
                
            with gr.TabItem("Page Preview"):
                gallery = gr.Gallery(
                    label="Translated Pages", 
                    show_label=True, 
                    elem_id="gallery",
                    columns=[2], 
                    height="auto"
                )
        
        # Define a function to update the download component when translation is complete
        def update_download(message, output_pdf_path, images):
            if output_pdf_path and os.path.exists(output_pdf_path):
                download_name = os.path.basename(output_pdf_path)
                status_message = f"Translation complete. PDF ready for download: {download_name}"
                return message, status_message, output_pdf_path, images
            else:
                return message, "Translation failed or PDF not generated", None, images
        
        # Handle the translation process
        translate_btn.click(
            fn=process_pdf, 
            inputs=[pdf_input], 
            outputs=[output_message, pdf_output_path, gallery]
        ).then(
            fn=update_download,
            inputs=[output_message, pdf_output_path, gallery],
            outputs=[output_message, pdf_output_visible, pdf_download, gallery]
        )
        
        # Add information about the app
        gr.Markdown("""
        ### About
        
        This application uses AI to translate text in PDF documents from Chinese to English.
        The translation is performed using Qwen-VL model with API integration.
        """)
    
    return app

if __name__ == "__main__":
    # Create and launch the interface
    app = create_interface()
    app.launch(share=True)  # Set share=False in production
