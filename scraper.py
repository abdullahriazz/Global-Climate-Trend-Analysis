import calendar
import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

df = pd.read_csv("city.csv")

chrome_options = Options()
# chrome_options.add_argument("--headless")  # Uncomment for headless mode
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
)

url = "https://www.wunderground.com/history"

day = "1"
data_list = []
csv_name = "2021 sept_dec.csv"

# Define columns and create empty CSV
columns = [
    "City",
    "Year",
    "Month",
    "Max Temperature",
    "Avg Temperature",
    "Min Temperature",
    "Dew Point",
    "Precipitation",
    "Snowdepth",
    "Wind",
    "Gust Wind",
    "Sea Level Pressure",
]

timeout = 20

for year in range(2021, 2023):
    for month_num in range(9, 13):
        for index, row in df.iterrows():
            while True:
                driver = webdriver.Remote(
                    command_executor="http://172.17.0.1:4447/wd/hub",
                    options=chrome_options,
                )
                print("Attempting to load")
                try:
                    driver.get(url)  # Attempt to load the URL
                    time.sleep(5)  # Wait for the page to load
                    print("Page loaded successfully!")  # Optional: Confirmation
                    try:
                        search_box = WebDriverWait(driver, timeout).until(
                            EC.presence_of_element_located(
                                (By.XPATH, '//*[@id="historySearch"]')
                            )
                        )
                        keys = row["City"]
                        search_box.click()
                        search_box.send_keys(keys)
                        # Wait for suggestions and select the first one
                        try:
                            WebDriverWait(driver, 10).until(
                                EC.presence_of_all_elements_located(
                                    (
                                        By.CSS_SELECTOR,
                                        "li.needsclick.needsfocus.defcon-.is-city",
                                    )
                                )
                            )
                            try:
                                suggestions = WebDriverWait(driver, timeout).until(
                                    EC.presence_of_all_elements_located(
                                        (
                                            By.CSS_SELECTOR,
                                            "li.needsclick.needsfocus.defcon-.is-city",
                                        )
                                    )
                                )
                                suggestions[0].click()

                                # Select month, day, and year
                                month = calendar.month_name[month_num]
                                Select(
                                    WebDriverWait(driver, timeout).until(
                                        EC.presence_of_element_located(
                                            (By.XPATH, '//*[@id="monthSelection"]')
                                        )
                                    )
                                ).select_by_visible_text(month)

                                Select(
                                    WebDriverWait(driver, timeout).until(
                                        EC.presence_of_element_located(
                                            (By.XPATH, '//*[@id="daySelection"]')
                                        )
                                    )
                                ).select_by_visible_text(day)

                                Select(
                                    WebDriverWait(driver, timeout).until(
                                        EC.presence_of_element_located(
                                            (By.XPATH, '//*[@id="yearSelection"]')
                                        )
                                    )
                                ).select_by_visible_text(str(year))

                                date_submit_button = WebDriverWait(
                                    driver, timeout
                                ).until(
                                    EC.element_to_be_clickable(
                                        (By.XPATH, '//*[@id="dateSubmit"]')
                                    )
                                )
                                driver.execute_script(
                                    "arguments[0].click();", date_submit_button
                                )

                                # Wait for any popups and close them
                                try:
                                    close_popup = WebDriverWait(driver, timeout).until(
                                        EC.element_to_be_clickable(
                                            (By.CSS_SELECTOR, "button.close-popup")
                                        )  # Adjust the selector as needed
                                    )
                                    driver.execute_script(
                                        "arguments[0].click();", close_popup
                                    )
                                except:
                                    print("No popup to close.")

                                # Wait for the monthly data link and click it
                                monthly = WebDriverWait(driver, timeout).until(
                                    EC.element_to_be_clickable(
                                        (
                                            By.XPATH,
                                            '//*[@id="inner-content"]/div[2]/div[1]/div[1]/div[1]/div/lib-link-selector/div/div/div/a[3]',
                                        )
                                    )
                                )
                                try:
                                    driver.execute_script(
                                        "arguments[0].click();", monthly
                                    )

                                    time.sleep(5)
                                    # Wait for the summary table to load
                                    table = WebDriverWait(driver, timeout).until(
                                        EC.presence_of_element_located(
                                            (By.CLASS_NAME, "summary-table")
                                        )
                                    )

                                    rows = table.find_elements(By.TAG_NAME, "tr")
                                    weather_data = {
                                        "City": keys,
                                        "Year": year,
                                        "Month": month,
                                    }

                                    # Extract weather data from the table
                                    for row in rows:
                                        cols = row.find_elements(By.TAG_NAME, "td")
                                        if len(cols) > 1:
                                            label = row.find_element(
                                                By.TAG_NAME, "th"
                                            ).text
                                            value = cols[1].text

                                            try:
                                                value = float(value)
                                            except ValueError:
                                                value = None

                                            if "Max Temperature" in label:
                                                weather_data["Max Temperature"] = value
                                            elif "Avg Temperature" in label:
                                                weather_data["Avg Temperature"] = value
                                            elif "Min Temperature" in label:
                                                weather_data["Min Temperature"] = value
                                            elif "Dew Point" in label:
                                                weather_data["Dew Point"] = value
                                            elif "Precipitation" in label:
                                                weather_data["Precipitation"] = value
                                            elif "Snowdepth" in label:
                                                weather_data["Snowdepth"] = value
                                            elif "Wind" == label:
                                                weather_data["Wind"] = value
                                            elif "Gust Wind" in label:
                                                weather_data["Gust Wind"] = value
                                            elif "Sea Level Pressure" in label:
                                                weather_data["Sea Level Pressure"] = (
                                                    value
                                                )
                                    driver.quit()
                                    break  # Exit the loop if successful
                                except:
                                    driver.quit()
                                    continue
                            except:
                                driver.quit()
                                continue
                        except:
                            driver.quit()
                            continue
                    except:
                        driver.quit()
                        continue
                except Exception as e:
                    print(f"Failed to load the page: {e}. Retrying in 2 seconds...")
                    time.sleep(2)  # Add a short delay before retrying
                    driver.quit()
                    continue

            # Append the weather data to the CSV
            pd.DataFrame([weather_data]).to_csv(csv_name, mode="a", header=False, index=False)