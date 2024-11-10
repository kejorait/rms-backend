import base64
import logging
import os
import subprocess
import threading
import uuid

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.remote_connection import LOGGER
from webdriver_manager.chrome import ChromeDriverManager

from helper import constants
from models.app_setting import AppSetting


# Printing functions for Windows
def print_pdf_windows(pdf_path, printer_name, sumatra_path="C:\\Program Files\\SumatraPDF\\SumatraPDF.exe"):
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"The PDF file does not exist: {pdf_path}")
    if not os.path.isfile(sumatra_path):
        raise FileNotFoundError(f"The SumatraPDF executable does not exist: {sumatra_path}")

    try:
        print(f"Printing to {printer_name} using SumatraPDF")
        # Command to print the PDF
        command = [
            sumatra_path,
            "-print-to", printer_name,
            "-print-settings", "portrait,fit",
            pdf_path
        ]
        # Run the command
        subprocess.run(command, check=True)
        print("Print job sent successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while printing: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def print_html(html_content, download_dir, print_settings):
    LOGGER.setLevel(logging.WARNING)
    # Suppress specific libraries' logging to CRITICAL level
    logging.getLogger("webdriver_manager").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)
    logging.getLogger("multipart").setLevel(
        logging.CRITICAL
    )  # Add multipart library suppression

    # Redirect all logs to os.devnull to capture stdout/stderr logs completely
    null_handler = logging.FileHandler(os.devnull)
    logging.getLogger().addHandler(null_handler)

    # Suppress root logger to prevent any other DEBUG/INFO outputs
    logging.basicConfig(level=logging.CRITICAL)

    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument(
        "--window-size=1280,720"
    )  # Set window size for headless mode
    chrome_options.add_argument("--log-level=3")  # Suppresses logging to console
    chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-logging"]
    )  # Suppresses DevTools warnings
    chrome_options.add_argument("--proxy-server='direct://'")
    chrome_options.add_argument("--proxy-bypass-list=*")

    # Initialize Chrome WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Convert HTML content to a base64-encoded data URL
    html_base64 = base64.b64encode(html_content.encode("utf-8")).decode("utf-8")
    data_url = f"data:text/html;base64,{html_base64}"

    # Load the HTML content in the browser
    driver.get(data_url)

    # Get the height of the body element
    body_height_px = driver.execute_script("return document.body.scrollHeight;")

    # Assuming 96 pixels per inch (standard screen resolution)
    pixels_per_inch = 96
    height_in_inches = body_height_px / pixels_per_inch
    
    # Use Chrome DevTools Protocol to generate PDF
    pdf_base64 = driver.execute_cdp_cmd(
        "Page.printToPDF",
        {
            "printBackground": True,
            "paperWidth": float(print_settings["paper_width"]),  # A4 width in inches
            "paperHeight": float(height_in_inches * 1.5),  # A4 height in inches
            "marginTop": 0,
            "marginBottom": 0,
            "marginLeft": 0,
            "marginRight": 0,
            "landscape": False,
        },
    )

    # Set PDF file path
    pdf_path = os.path.join(download_dir, f"{uuid.uuid4()}.pdf")

    # Decode and save the PDF file
    with open(pdf_path, "wb") as f:
        f.write(base64.b64decode(pdf_base64["data"]))

    # Close the driver
    driver.quit()

    # Check if the PDF file was created successfully
    if os.path.exists(pdf_path):
        print_pdf_windows(pdf_path, print_settings["printer"])
        # print_pdf_windows(pdf_path, print_settings["printer"])
        
    # delete the pdf file
    os.remove(pdf_path)

# Define your HTML content
def generateKitchenBillHtml(bill):
    # Generate the HTML content for the bill
    html_content = f'''
       <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8" />
            <meta
            name="viewport"
            content="width=device-width, initial-scale=1.0"
            />
            <link
            href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;700&display=swap"
            rel="stylesheet"
            />
            <title>Document</title>
        </head>
        <body>
            <div
            style="
                padding-right: 3.5rem;
                display: flex;
                flex-direction: column;
                width: 300px;
                font-family: 'Poppins', sans-serif;
            "
            >
            <div style="padding-bottom: 1rem">
                <p
                style="
                    text-align: center;
                    font-size: 1.4375rem; /* Updated from 1.125rem */
                    font-weight: 500;
                    text-decoration: underline;
                "
                >
                Orders
                </p>
                <p style="font-size: 1.6875rem;">Table: {bill["table_nm"]}</p> <!-- Updated from 1.1875rem -->
                <p style="font-size: 1.3125rem;">{bill["created_dt"]}</p> <!-- Updated from 0.8125rem -->
            </div>

            <table style="table-layout: fixed; font-size: 1.3125rem; width: 100%; margin: 0 auto"> <!-- Updated from 0.8125rem -->
                <thead>
                <tr>
                    <th
                    style="
                        text-align: center;
                        font-size: 1.3125rem; /* Updated from 0.8125rem */
                        padding: 0.5rem;
                        border-bottom: 1px solid black;
                        width: 20%;
                        font-weight: 500;
                    "
                    >
                    QTY
                    </th>
                    <th
                    style="
                        text-align: left;
                        font-size: 1.3125rem; /* Updated from 0.8125rem */
                        padding-left: 0.5rem;
                        padding-top: 0.5rem;
                        padding-bottom: 0.5rem;
                        border-bottom: 1px solid black;
                        width: 80%;
                        font-weight: 500;
                    "
                    >
                    ITEM
                    </th>
                </tr>
                </thead>
                <tbody>
                {"".join(f"""
                            <tr>
                            <td style="text-align: center; font-size: 1.6875rem; font-weight: 700; padding: 0.25rem;">{item['qty']}</td> <!-- Updated from 1.1875rem -->
                            <td style="font-size: 1.6875rem; font-weight: 700; text-align: left; padding-left: 0.5rem;">{item['menu_nm']}</td> <!-- Updated from 1.1875rem -->
                            </tr>""" for item in bill["menu_items"])}
                </tbody>
            </table>
            <hr style="border-color: black; border-style: dashed; width: 100%" />
            </div>
        </body>
        </html>
        '''

    return html_content


# Define your HTML content
def generateFinalBill(bill, print_settings):
    # Generate the HTML content for the bill
    html_content = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;700&display=swap" rel="stylesheet" />
            <title>Document</title>
        </head>
        <body>
            <div style="padding-right: 3.5rem; display: flex; flex-direction: column; text-align: center; width: 300px; font-family: 'Poppins', sans-serif;">
                <div style="padding-bottom: 1rem; display: flex; justify-content: center">
                    <img style="width: 80px" src="data:image/jpeg;base64, {print_settings["logo_base64"]}" alt="Logo"/>
                </div>
                <p style="font-size: 0.75rem">{print_settings["address"]}</p>
                <div style="display: flex; justify-content: center; padding-top: 1rem; padding-bottom: 1rem">
                    <hr style="border-color: black; border-style: dashed; width: 100%" />
                </div>

                <div style="padding-bottom: 1rem">
                    <p style="font-size: 0.875rem; font-weight: 500; text-decoration: underline">Receipt</p>
                    <p style="font-size: 0.875rem">{bill["table_nm"]}</p>
                </div>

                <table style="table-layout: fixed; font-size: 0.75rem; width: 100%; margin: 0 auto">
                    <thead>
                        <tr>
                            <th style="text-align: center; font-size: 0.75rem; padding: 0.5rem; border-bottom: 1px solid black; width: 20%;">QTY</th>
                            <th style="text-align: left; font-size: 0.75rem; padding-left: 0.5rem; padding-top: 0.5rem; padding-bottom: 0.5rem; border-bottom: 1px solid black; width: 60%;">ITEM</th>
                            <th style="text-align: right; font-size: 0.75rem; padding: 0.5rem; border-bottom: 1px solid black; width: 40%;">PRICE</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join(f"""
                        <tr>
                            <td style="padding: 0.25rem">{item['qty']}</td>
                            <td style="text-align: left; padding-left: 0.5rem">{item['menu_nm']}</td>
                            <td style="text-align: right">Rp {format(int(item['total']), ',')}</td>
                        </tr>""" for item in bill['data'])}
                    </tbody>
                </table>

                <div style="display: flex; justify-content: center; padding-top: 0.25rem; padding-bottom: 0.25rem;">
                    <hr style="border-color: black; border-style: dashed; width: 100%" />
                </div>

                <table style="table-layout: fixed; width: 100%">
                    <tr>
                        <td style="width: 16.666%"></td>
                        <td style="font-size: 0.75rem; text-align: left; padding: 0.25rem">Subtotal</td>
                        <td style="font-size: 0.75rem; text-align: right">Rp {format(int(bill['subtotal'] if 'subtotal' in bill else 0), ',')}</td>
                    </tr>
                    <tr>
                        <td style="width: 16.666%"></td>
                        <td style="font-size: 0.75rem; text-align: left; padding: 0.25rem">Service</td>
                        <td style="font-size: 0.75rem; text-align: right">Rp {format(int(bill['service'] if 'service' in bill else 0), ',')}</td>
                    </tr>
                    <tr>
                        <td style="width: 16.666%"></td>
                        <td style="font-size: 0.75rem; text-align: left; padding: 0.25rem">PB1</td>
                        <td style="font-size: 0.75rem; text-align: right">Rp {format(int(bill['pb1'] if 'pb1' in bill else 0), ',')}</td>
                    </tr>
                    <tr>
                        <td style="width: 16.666%"></td>
                        <td style="font-size: 0.75rem; text-align: left; padding: 0.25rem; font-weight: bold; white-space: nowrap;">Dining Total</td>
                        <td style="font-size: 0.75rem; text-align: right; font-weight: bold">Rp {format(int(bill['dining_total'] if 'dining_total' in bill else 0), ',')}</td>
                    </tr>
                </table>

                <div style="display: flex; justify-content: center; padding-top: 0.25rem; padding-bottom: 0.25rem;">
                    <hr style="border-color: black; border-style: dashed; width: 100%" />
                </div>
                
                <table style="table-layout: fixed; font-size: 0.75rem; width: 100%; margin: 0 auto">
                    <thead>
                    <tr>
                        <th
                        style="
                            text-align: left;
                            font-size: 0.75rem;
                            padding-left: 0.5rem;
                            padding-top: 0.5rem;
                            padding-bottom: 0.5rem;
                            border-bottom: 1px solid black;
                            width: 20%;
                        "
                        >
                        START
                        </th>
                        <th
                        style="
                            text-align: left;
                            font-size: 0.75rem;
                            padding-left: 0.5rem;
                            padding-top: 0.5rem;
                            padding-bottom: 0.5rem;
                            border-bottom: 1px solid black;
                            width: 20%;
                        "
                        >
                        END
                        </th>
                        <th
                        style="
                            text-align: left;
                            font-size: 0.75rem;
                            padding-left: 0.5rem;
                            padding-top: 0.5rem;
                            padding-bottom: 0.5rem;
                            border-bottom: 1px solid black;
                            width: 20%;
                        "
                        >
                        Time(Min)
                        </th>
                        <th
                        style="
                            text-align: right;
                            font-size: 0.75rem;
                            padding: 0.5rem;
                            border-bottom: 1px solid black;
                            width: 40%;
                        "
                        >
                        PRICE
                        </th>
                    </tr>
                    </thead>
                    <tbody>
                    {"".join(f"""
                        <tr>
                            <td style="text-align: left; padding: 0.25rem; padding-left: 0.5rem">{item['session_created_dt'].strftime("%H:%M")}</td>
                            <td style="text-align: left; padding-left: 0.5rem">{item['session_closed_dt'].strftime("%H:%M")}</td>
                            <td style="text-align: left; padding-left: 0.5rem">{item['session_time_minutes']}</td>
                            <td style="text-align: right">Rp {format(int(item['session_price']), ',')}</td>
                        </tr>""" for item in bill['sessionList'])}
                    <!-- Add more rows as needed -->
                    </tbody>
                </table>

                <table style="table-layout: fixed; width: 100%">
                    <tr>
                    <td style="width: 16.666%"></td>
                    <td
                        style="
                        font-size: 0.75rem;
                        text-align: left;
                        padding: 0.25rem;
                        font-weight: bold;
                        white-space: nowrap;
                        "
                    >
                        Billiard Total
                    </td>
                    <td style="font-size: 0.75rem; text-align: right; font-weight: bold">Rp {format(int(bill['blData']['total_amount']), ',')}</td>
                    </tr>
                </table>

                <div
                    style="
                    display: flex;
                    justify-content: center;
                    padding-top: 0.25rem;
                    padding-bottom: 0.25rem;
                    "
                >
                    <hr style="border-color: black; border-style: dashed; width: 100%" />
                </div>

                <table style="table-layout: fixed; width: 100%">
                    <tr>
                    <td style="width: 33.333%"></td>
                    <td style="font-size: 0.75rem; text-align: left; padding: 0.25rem; font-weight: bold">
                        Total
                    </td>
                    <td style="font-size: 0.75rem; text-align: right; padding: 0.25rem; font-weight: bold">
                        Rp {format(int(bill['total_amount']), ',')}
                    </td>
                    </tr>
                </table>
      
                <div style="padding-top: 1.5rem; padding-bottom: 1.5rem">
                    <div style="display: flex; flex-direction: column; align-items: center">
                        <p style="font-size: 0.75rem">{bill["time"].strftime("%d %B %Y | %H:%M")}</p>
                    </div>
                    <div style="display: flex; justify-content: center; padding-top: 0.25rem">
                        <p style="font-size: 0.75rem">Serviced by: {bill['created_by']}</p>
                    </div>
                    <div style="display: flex; justify-content: center; padding-top: 0.5rem">
                        <p style="font-size: 1rem">THANK YOU</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
    '''
    return html_content

def printBill(db, billType, printData):
    
    # Get the print settings from the database
    query = db.query(AppSetting)
    query = query.filter(AppSetting.is_delete == constants.NO)
    query = query.filter(AppSetting.is_inactive == constants.NO)
    query = query.filter(
        AppSetting.cd.in_(["printer", "paper_width", "paper_height", "logo_base64", "address", "zoom"])
    )
    print_query = query.all()
    print_settings = {setting.cd: setting.value for setting in print_query}

    # Get current directory
    current_directory = os.getcwd()
    download_directory = current_directory + "\\helper\\bill_pdfs"
    
    # Ensure the directory exists
    os.makedirs(download_directory, exist_ok=True)
    
    # Generate the HTML content for the bill
    # switch case for bill type
    
    if billType == "new_order":
        html_content = generateKitchenBillHtml(printData)
    elif billType == "payment":
        # html_content = generateFinalBill(printData, print_settings)
        if printData["html"]:
            html_content = printData["html"]
    # Run the print function

    def background_print():
        for i in range(printData["print_amount"]):
            # print(html_content)
            print_html(html_content, download_directory, print_settings)

    # Run the printing in a background thread
    print_thread = threading.Thread(target=background_print)
    print_thread.start()
