import os
import time
import uuid
import json
import pdfkit

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Windows printing function (for reference)
def print_pdf_windows(pdf_path, printer_name):
    import win32print
    import win32api
    win32api.ShellExecute(0, "print", pdf_path, f'/d:"{printer_name}"', ".", 0)

# Linux printing function
def print_pdf_linux(pdf_path, printer_name):
    import cups
    conn = cups.Connection()
    
    if printer_name not in conn.getPrinters():
        raise ValueError(f"Printer '{printer_name}' not found.")

    conn.printFile(printer_name, pdf_path, "Print Job", {})

# def print_html(html_content, download_dir, printer_name):
#     # Set up Chrome options
#     chrome_options = Options()
#     chrome_options.add_argument('--headless')  # Run in headless mode
#     chrome_options.add_argument('--disable-gpu')
#     chrome_options.add_argument('--no-sandbox')
    
#     # Set the custom download directory and printing options
#     prefs = {
#         "download.default_directory": download_dir,
#         "download.prompt_for_download": False,
#         "directory_upgrade": True,
#         "safebrowsing.enabled": True,
#         "printing.print_preview_sticky_settings.appState": json.dumps({
#             "recentDestinations": [{
#                 "id": "Save as PDF",
#                 "origin": "local",
#                 "account": "",
#                 "isOwned": True,
#                 "capabilities": {
#                     "paperSize": {
#                         "height": 6 * 72,  # height in points
#                         "width": 4 * 72,   # width in points
#                         "marginTop": 0,
#                         "marginBottom": 0,
#                         "marginLeft": 0,
#                         "marginRight": 0,
#                         "landscape": False,
#                     }
#                 },
#             }],
#             "selectedDestinationId": "Save as PDF",
#             "version": 2,
#             "isLandscape": False,
#             "marginsType": 0,  # No margins
#         })
#     }
#     chrome_options.add_experimental_option("prefs", prefs)

#     # Create a new instance of the Chrome driver
#     service = Service(ChromeDriverManager().install())
#     driver = webdriver.Chrome(service=service, options=chrome_options)

#     # Set the content of the page
#     driver.get("data:text/html;charset=utf-8," + html_content)

#     # Wait for the content to load
#     time.sleep(2)

#     # Set PDF file path
#     pdf_path = os.path.join(download_dir, f"{uuid.uuid4()}.pdf")

#     # Trigger the print to PDF
#     try:
#         driver.execute_script('window.print();')
#     except Exception as e:
#         print(f"Error triggering print: {e}")
    
#     # Wait for a moment to allow the PDF to be saved
#     time.sleep(2)

#     # Close the browser
#     driver.quit()
    
#     print(f"Download Dir: {download_dir}")
#     print(f"PDF saved at: {pdf_path}")
#     print(f"Printer name: {printer_name}")
#     print("path exists ",os.path.exists(pdf_path))
#     # Check if the PDF file was created
#     if os.path.exists(pdf_path):
#         print(f"PDF saved at: {pdf_path}")
#         try:
#             # Uncomment the appropriate line based on your OS
#             # print_pdf_windows(pdf_path, printer_name)  # For Windows
#             print_pdf_linux(pdf_path, printer_name)      # For Linux
#         except Exception as e:
#             print(f"Error printing PDF: {e}")
#     else:
#         print("PDF not saved.")


def print_html(html_content, download_dir, printer_name):
    # Ensure the download directory exists
    os.makedirs(download_dir, exist_ok=True)

    # Set PDF file path
    pdf_path = os.path.join(download_dir, f"{uuid.uuid4()}.pdf")

    # Convert HTML to PDF
    try:
        pdfkit.from_string(html_content, pdf_path)
        print(f"PDF saved at: {pdf_path}")
        
        # Print the PDF
        print_pdf_linux(pdf_path, printer_name)
    except Exception as e:
        print(f"Error creating PDF: {e}")
# Example usage
if __name__ == "__main__":
    # Get current directory
    current_directory = os.getcwd()
    download_directory = current_directory + "/bill_pdfs"
    # Ensure the directory exists
    printer_name = "Microsoft Print to PDF"
    os.makedirs(download_directory, exist_ok=True)
    # Generate the HTML content for the bill
    html_content = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Print Test</title>
    </head>
    <body>
        <h1>Hello, World!</h1>
        <p>This is a test print from Python using Selenium.</p>
    </body>
    </html>
    '''

    # Ensure the download directory exists
    os.makedirs(download_directory, exist_ok=True)

    # Run the print function
    print_html(html_content, download_directory, printer_name)
