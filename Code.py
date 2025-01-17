import tkinter as tk
from tkinter import filedialog
from pdf2image import convert_from_path
import pytesseract
import os
from PIL import Image
from docx import Document
from docx.shared import Pt, Inches

# Global variable to hold the current language setting
current_language = 'eng'
# Set paths for Tesseract and Poppler (adjust based on your bundled structure)
tesseract_exe_path = os.path.join(os.path.dirname(__file__), 'tesseract.exe')
poppler_path = os.path.join(os.path.dirname(__file__), 'poppler\\bin')

# Configure pytesseract to use the bundled Tesseract
pytesseract.pytesseract.tesseract_cmd = tesseract_exe_path

# Configure pdf2image to use the bundled Poppler
convert_from_path.poppler_path = poppler_path

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("JPEG files", "*.jpg;*.jpeg")])
    if file_path:
        file_path_label.config(text=file_path)
        process_button.config(state=tk.NORMAL)
    else:
        file_path_label.config(text="No file selected")

def change_language():
    global current_language
    if current_language == 'eng':
        current_language = 'ara'
        language_button.config(text="Set to English")
    else:
        current_language = 'eng'
        language_button.config(text="Set to Arabic")
    result_text.insert(tk.END, f"Language set to: {current_language}\n")

def process_file():
    file_path = file_path_label.cget("text")
    if not file_path or file_path == "No file selected":
        result_text.insert(tk.END, "Please select a file first.\n")
        return
    
    try:
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()
        
        if file_extension in ['.pdf']:
            ocr_text = process_pdf(file_path)
        elif file_extension in ['.jpg', '.jpeg']:
            ocr_text = pytesseract.image_to_string(Image.open(file_path), lang=current_language, config='--psm 6')
        else:
            result_text.insert(tk.END, "Unsupported file type.\n")
            return

        # Prompt user for custom file name and path
        save_path = filedialog.asksaveasfilename(defaultextension=".docx", filetypes=[("Word Document", "*.docx")])
        if not save_path:
            result_text.insert(tk.END, "No save location selected.\n")
            return

        doc = Document()
        doc.styles['Normal'].font.name = 'Times New Roman'
        doc.styles['Normal'].font.size = Pt(14)
        
        # Simple paragraph detection based on line breaks
        paragraphs = ocr_text.split('\n\n')
        for paragraph in paragraphs:
            if paragraph.strip():  # Check if paragraph is not just whitespace
                doc.add_paragraph(paragraph)

        try:
            doc.save(save_path)
            result_text.insert(tk.END, f"Text saved to '{os.path.basename(save_path)}' in {os.path.dirname(save_path)}\n")
        except Exception as e:
            result_text.insert(tk.END, f"Error saving text document: {str(e)}\n")
        
    except Exception as e:
        result_text.insert(tk.END, f"An error occurred: {str(e)}\n")

def process_pdf(pdf_path):
    images = convert_from_path(pdf_path)
    result_text = ""
    for i, image in enumerate(images):
        image_path = f"temp_page_{i}.png"
        image.save(image_path, 'PNG')
        page_text = pytesseract.image_to_string(image_path, lang=current_language, config='--psm 6')
        result_text += page_text + "\n\n"  # Add extra line breaks for paragraph separation
        os.remove(image_path)  # Remove temporary image after processing
    return result_text

# Create the main window
root = tk.Tk()
root.title("File Text Extraction Tool")

# Select file button
select_button = tk.Button(root, text="Select File", command=select_file)
select_button.pack(pady=10)

# Display selected file path
file_path_label = tk.Label(root, text="No file selected")
file_path_label.pack()

# Process button, initially disabled
process_button = tk.Button(root, text="Extract Text", command=process_file, state=tk.DISABLED)
process_button.pack(pady=10)

# Language toggle button
language_button = tk.Button(root, text="Set to Arabic", command=change_language)
language_button.pack(pady=10)

# Text area for displaying results
result_text = tk.Text(root, wrap=tk.WORD, width=80, height=20)
result_text.pack(padx=10, pady=10)

# Start the GUI
root.mainloop()