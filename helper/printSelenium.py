import os
import time
import json
import uuid
import pdfkit
# import win32print
# import win32api
import cups

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# # Printing functions for Windows and Linux
# def print_pdf_windows(pdf_path,printer_name):
#     win32api.ShellExecute(0, "print", pdf_path, f'/d:"{printer_name}"', ".", 0)

# Linux printing function
def print_pdf_linux(pdf_path, printer_name):

    # Connect to CUPS
    conn = cups.Connection()
    
    # Check if the printer exists
    if printer_name not in conn.getPrinters():
        raise ValueError(f"Printer '{printer_name}' not found.")

    # Print the PDF file
    conn.printFile(printer_name, pdf_path, "Print Job", {})
    
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

# Define your HTML content
def generateKitchenBillHtml(bill):
    
    # Generate the HTML content for the bill
    html_content = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Kitchen Bill</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    text-align: center;
                    margin: 0; /* Remove default margin */
                    padding: 0; /* Remove default padding */
                }}

                .app-print-bill-container {{
                    padding-right: 3.5rem;
                    display: flex;
                    flex-direction: column;
                    text-align: center;
                    max-width: 600px; /* Adjust as needed */
                    margin: 0 auto; /* Center the container */
                }}

                .print-bill-main-container {{
                    width: 100%;
                    border: 1px solid #ddd;
                    padding: 1rem;
                    box-sizing: border-box; /* Ensure padding is included in width */
                }}

                .logo-container {{
                    display: flex;
                    justify-content: center;
                    padding-bottom: 1rem;
                }}

                .img-size {{
                    max-width: 100px;
                }}

                .text-xs {{
                    font-size: 0.75rem;
                }}

                .divider {{
                    border-top: 1px dashed black;
                    margin: 1rem 0;
                }}

                .receipt-header {{
                    padding-bottom: 1rem;
                }}

                .receipt-title {{
                    font-size: 0.875rem;
                    font-weight: 500;
                    text-decoration: underline;
                }}

                .table-name {{
                    font-size: 0.875rem;
                }}

                .receipt-table,
                .summary-table,
                .total-table {{
                    width: 100%;
                    margin: 0 auto;
                    border-collapse: collapse;
                }}

                .receipt-table th,
                .receipt-table td,
                .summary-table td,
                .total-table td {{
                    font-size: 0.75rem;
                    padding: 0.5rem;
                    border-bottom: 1px solid #333;
                }}

                .receipt-table th {{
                    text-align: center;
                    border-bottom: 1px solid #333;
                }}

                .receipt-table th:nth-child(2),
                .receipt-table td:nth-child(2) {{
                    text-align: left;
                    padding-left: 0.5rem;
                }}

                .receipt-table th:last-child,
                .receipt-table td:last-child {{
                    text-align: right;
                }}

                .summary-table td:nth-child(2),
                .total-table td:nth-child(2) {{
                    text-align: left;
                }}

                .summary-table td:last-child,
                .total-table td:last-child {{
                    text-align: right;
                }}

                .total-label,
                .total-amount {{
                    font-weight: bold;
                }}

                .footer {{
                    padding: 1rem 0;
                }}

                .timestamp,
                .serviced-by {{
                    font-size: 0.75rem;
                    margin: 0.25rem 0;
                }}

                .thank-you {{
                    font-size: 1rem;
                    margin-top: 1rem;
                    font-weight: bold;
                }}

                @media print {{
                    @page {{
                        margin: 0; /* Remove margin on the printed page */
                    }}

                    body {{
                        margin: 0; /* Ensure body has no margin when printing */
                    }}

                    .app-print-bill-container {{
                        width: auto; /* Allow container to take its own width */
                        height: auto; /* Allow container to take its own height */
                    }}

                    .print-bill-main-container {{
                        border: none; /* Optionally remove the border for print */
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="app-print-bill-container">
                <div class="print-bill-main-container">
                    <div class="receipt-header">
                        <p class="table-name">Table: {bill["table_nm"]}</p>
                    </div>

                    <table class="receipt-table">
                        <thead>
                            <tr>
                                <th>ITEM</th>
                                <th></th>
                                <th>QTY</th>
                            </tr>
                        </thead>
                        <tbody>
                            {"".join(f"""
                                <tr>
                                    <td>{item['menu_nm']}</td>
                                    <td></td>
                                    <td>{item['qty']}</td>
                                </tr>""" for item in bill["menu_items"])}
                        </tbody>
                    </table>

                    <div class="footer">
                        <p class="timestamp">{bill["created_dt"]}</p>
                        <p class="serviced-by">Serviced by: {bill["created_by"]}</p>
                        <p class="thank-you">THANK YOU</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        '''
    
    return html_content

def printKitchenBill(bill,printer_name):
    # Get current directory
    current_directory = os.getcwd()
    download_directory = current_directory + "/helper/bill_pdfs"
    # Ensure the directory exists
    os.makedirs(download_directory, exist_ok=True)
    # Generate the HTML content for the bill
    html_content = generateKitchenBillHtml(bill)
    # Run the print function
    print_html(html_content, download_directory,printer_name)
    