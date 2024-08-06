import requests
import os
import base64


def save_images_and_markdown(pdf, output_folder):
    """
    Saves images and markdown text extracted from a PDF document.

    Parameters:
    pdf (dict): The parsed PDF data containing text and images.
    output_folder (str): The folder to save the markdown text and images.
    """
    # Create a folder for the output
    os.makedirs(output_folder, exist_ok=True)

    # Save markdown text
    markdown_text = pdf.get('text', '')
    with open(os.path.join(output_folder, 'output.md'), 'w', encoding='utf-8') as f:
        f.write(markdown_text)

    # Save images
    images = pdf.get('images', [])
    for img in images:
        # Decode base64 image
        image_bytes = base64.b64decode(img["image"])

        # Save image
        with open(os.path.join(output_folder, img["image_name"]), 'wb') as f:
            f.write(image_bytes)

def parse_and_save_pdf(url, file_path):
    """
    Parses a PDF document by sending it to a specified URL and saves the extracted data.

    Parameters:
    url (str): The URL to send the PDF document for parsing.
    file_path (str): The path to the PDF document to be parsed.
    """
    try:
        # Open the file in binary mode
        with open(file_path, 'rb') as file:
            # Make the POST request with the file
            response = requests.post(url, files={'file': file})

        if response.status_code == 200:
            # Save markdown and images
            response_data = response.json()
            output_folder = os.path.splitext(os.path.basename(file_path))[0]
            # Save the markdown and images to the result_folder
            output_folder = os.path.join("/home/alalulu/workspace/ericsson-bot/omniparse/result_folder", output_folder)
            save_images_and_markdown(response_data, output_folder)
            print("Markdown and images saved successfully.")
        else:
            print(f"Error: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error processing file {file_path}: {e}")

def process_files_from_folder(doc_folder, parse_service_url, result_folder):
    
    # list all subfolder names in the result_folder
    subfolders = [f.path for f in os.scandir(result_folder) if f.is_dir()]

    # Walk through the directory and its subdirectories
    for root, dirs, files in os.walk(doc_folder):
        for file in files:
            if file.endswith('.pdf') or file.endswith('.docx') or file.endswith('.pptx'):
                # check if there is a subfolder has same name as the file name
                # if yes, skip the file
                file_name = os.path.splitext(file)[0]
                if any(file_name in subfolder for subfolder in subfolders):
                    continue
                # if the size of the file is over 15Mb, skip the file
                file_size = os.path.getsize(os.path.join(root, file))
                if file_size > 15 * 1024 * 1024:
                    continue
                file_path = os.path.join(root, file)
                print(f"----------Start processing file: {file_path} -------------------")
                try:
                    parse_and_save_pdf(parse_service_url, file_path)
                except Exception as e:
                    print(f"Failed to process file {file_path}: {e}")
                print(f"Processed file: {file_path}")

if __name__ == "__main__":
    # Define the URL and the file path
    url = "http://localhost:5200/parse_document/docs"
    # file_path = "/home/alalulu/workspace/ericsson-bot/omniparse/SI_Documents/serdes_spectra.docx"
    result_folder = "/home/alalulu/workspace/ericsson-bot/omniparse/result_folder"
    # Parse the PDF and save the extracted data
    # parse_and_save_pdf(url, file_path)
    folder_path = "/home/alalulu/workspace/ericsson-bot/omniparse/SI_Documents"
    process_files_from_folder(folder_path, url, result_folder)
