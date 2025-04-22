#!/usr/bin/env python3
import os
import datetime
import PySimpleGUI as sg
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def search_and_screenshot(driver, brand, query_type, output_folder):
    """
    Perform a Google search for the given brand and query type,
    take screenshots of search results labeled as sponsored or ads,
    and save them to the specified output folder.
    """
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    query = f"{brand} {query_type}"

    for page in range(5):
        start = page * 10
        url = f"https://www.google.com/search?q={query}&hl=en&start={start}"
        driver.get(url)
        driver.implicitly_wait(5)

        xpaths = [
            "//*[contains(text(),'Sponsored')],",
            "//*[contains(text(),'Ad') and not(contains(text(),'AdSense'))]",
        ]
        sponsored_elements = []
        for xpath in xpaths:
            sponsored_elements.extend(driver.find_elements(By.XPATH, xpath))

        for idx, element in enumerate(sponsored_elements, start=1):
            try:
                filename = f"{date_str}_{brand}_{query_type}_p{page+1}_{idx}.png"
                filepath = os.path.join(output_folder, filename)
                element.screenshot(filepath)
            except Exception as e:
                print(f"Failed to screenshot element: {e}")

def main():
    # (Optional) suppress Tk deprecation warning in macOS
    os.environ['TK_SILENCE_DEPRECATION'] = '1'

    # Layout of the GUI
    layout = [
        [sg.Text("Enter brand names (one per line):")],
        [sg.Multiline(key='-BRANDS-', size=(40, 10))],
        [sg.Text("Select output folder:"), sg.Input(key='-FOLDER-'), sg.FolderBrowse()],
        [sg.Button("Run"), sg.Button("Exit")],
    ]

    # Create the Window without an external icon to avoid image-loading errors
    window = sg.Window(
        title="Brand Ad Screenshot Tool",
        layout=layout,
        icon=None,
        finalize=True
    )

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break

        if event == 'Run':
            brands = [b.strip() for b in values['-BRANDS-'].splitlines() if b.strip()]
            output_folder = values['-FOLDER-']

            if not brands or not output_folder:
                sg.popup_error("Please enter at least one brand and select an output folder.")
                continue

            sg.popup("Processing started. This may take a few minutes...")

            options = Options()
            options.add_argument('--headless')
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )

            for brand in brands:
                for q in ['coupon', 'deal']:
                    search_and_screenshot(driver, brand, q, output_folder)

            driver.quit()
            sg.popup("Processing completed!")

    window.close()

if __name__ == "__main__":
    main()
