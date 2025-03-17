from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# File path for chromedriver
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_file_path(filename):
    return os.path.join(BASE_DIR, filename)

# Initialize Selenium driver
def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    service = Service(get_file_path("./chromedriver.exe"))
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(5)
    return driver


# Search for trains
def search_train(driver, user_info):
    # Navigate to the foreign reservation page
    driver.get("https://www.letskorail.com/ebizbf/EbizbfForeign_pr16100.do?gubun=1")
    time.sleep(2)  # Allow time for the page to load

    # Input departure station
    departure_input = driver.find_element(
        By.XPATH, "/html/body/div[2]/div[2]/div/form/div[2]/div[1]/table/tbody/tr[4]/td/div[1]/input[1]"
    )
    departure_input.clear()
    departure_input.send_keys(user_info["departure_station"])
    time.sleep(1)

    # Input arrival station
    arrival_input = driver.find_element(
        By.XPATH, "/html/body/div[2]/div[2]/div/form/div[2]/div[1]/table/tbody/tr[4]/td/div[2]/input[1]"
    )
    arrival_input.clear()
    arrival_input.send_keys(user_info["arrival_station"])
    time.sleep(1)

    # Input travel date
    date_input = Select(driver.find_element(By.ID, "slt_y01"))
    date_input.select_by_value(user_info["travel_date"][:4])  # Year
    time.sleep(1)

    month_input = Select(driver.find_element(By.ID, "slt_m01"))
    month_input.select_by_value(user_info["travel_date"][5:7])  # Select by the exact value (e.g., "11")
    time.sleep(1)

    day_input = Select(driver.find_element(By.ID, "slt_d01"))
    day_input.select_by_value(user_info["travel_date"][8:])  # Day
    time.sleep(1)

    time_input = Select(driver.find_element(By.ID, "slt_h01"))
    time_input.select_by_value(user_info["departure_time"])
    time.sleep(1)

    # Select train type
    train_type_dropdown = driver.find_element(
        By.XPATH, '//*[@id="selTrain"]'
    )
    train_type_dropdown.send_keys(user_info["train_type"])
    time.sleep(1)

    # Input number of adults
    adult_input = Select(driver.find_element(
        By.XPATH, "/html/body/div[2]/div[2]/div/form/div[2]/div[1]/table/tbody/tr[8]/td/select[1]"
    ))
    adult_input.select_by_value(user_info["adults"])
    time.sleep(1)

    # Input number of children
    child_input = Select(driver.find_element(
        By.XPATH, '/html/body/div[2]/div[2]/div/form/div[2]/div[1]/table/tbody/tr[8]/td/select[2]'
    ))
    child_input.select_by_value(user_info["children"])
    time.sleep(1)

    # Submit the form to search for trains
    search_button = driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div/form/div[2]/div[1]/ul/li/a/img')
    search_button.click()
    time.sleep(5)  # Wait for search results to load

    # Check for available trains
    try:
        # Locate the results table
        table = driver.find_element(By.CLASS_NAME, "table_st02")
        rows = table.find_elements(By.TAG_NAME, "tr")  # Get all rows in the table

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) == 0:  # Skip rows without data
                continue

            # Extract train details
            train_type = cells[2].text.strip()  # Train type (e.g., KTX, ITX-Saemaeul)
            dep_time = cells[5].text.strip()  # Departure time (e.g., 12:25)
            arr_time = cells[6].text.strip()  # Arrival time (e.g., 15:06)

            # Check availability (First class and Economy class)
            first_class_avail = "btn_slt01_on.gif" in cells[7].get_attribute("innerHTML")
            economy_class_avail = "btn_slt01_on.gif" in cells[8].get_attribute("innerHTML")

            # Debugging: Print extracted details
            print(f"Train Type: {train_type}, Dep. Time: {dep_time}, Arr. Time: {arr_time}, "
                  f"First Class Available: {first_class_avail}, Economy Class Available: {economy_class_avail}")

            # Match user preferences
            if user_info["train_type"] in train_type and dep_time >= user_info["departure_time"]:
                if user_info["seat_class"] == "2" and first_class_avail:  # First class
                    print("Selecting First Class seat...")
                    # Re-locate First Class button
                    first_class_img = cells[7].find_element(By.TAG_NAME, "img")
                    first_class_btn = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//img[@name="btnRsv2_5"]/parent::a'))
                    )
                    driver.execute_script("arguments[0].click();", first_class_btn)
                    return True
                elif user_info["seat_class"] == "1" and economy_class_avail:  # Economy class
                    print("Selecting Economy Class seat...")
                    # Re-locate Economy Class button
                    economy_class_img = cells[8].find_element(By.TAG_NAME, "img")
                    economy_class_btn = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//img[@name="btnRsv1_5"]/parent::a'))
                    )
                    driver.execute_script("arguments[0].click();", economy_class_btn)
                    return True

        print("No matching trains found or seats unavailable.")
        return False

    except Exception as e:
        print(f"An error occurred while searching for trains: {e}")
        return False

# Handle the passenger information page
def fill_passenger_information(driver, passenger_info):
    try:
        # Input first and last name
        driver.find_element(By.NAME, "txtCustFirstNm").send_keys(passenger_info["first_name"])
        driver.find_element(By.NAME, "txtCustLastNm").send_keys(passenger_info["last_name"])

        # Select gender
        gender_value = passenger_info["gender"]  # "M" for Male, "F" for Female

        # Locate the radio button by its value attribute and click it
        gender_radio = driver.find_element(By.XPATH, f"//input[@name='selSexDvCd' and @value='{gender_value}']")
        gender_radio.click()

        # Input password and confirm password
        driver.find_element(By.NAME, "txtCustPw").send_keys(passenger_info["password"])
        driver.find_element(By.NAME, "txtCustPw2").send_keys(passenger_info["password"])

        # Select nationality
        nationality_select = Select(driver.find_element(By.NAME, "selNationCd"))
        nationality_select.select_by_value(passenger_info["nationality_code"])  # e.g., "US" for the USA

        # Input email
        driver.find_element(By.NAME, "txtEmailAddr").send_keys(passenger_info["email"])

        # Agree to terms and conditions
        driver.find_element(By.NAME, "chkAgree").click()

        # Click the Next button
        next_button = driver.find_element(By.XPATH, "//a[@href='javascript:infochk();']")
        next_button.click()
        time.sleep(3)  # Wait for the next page to load

    except Exception as e:
        print(f"Error while filling passenger information: {e}")
        return False
    return True


# Handle the ticket payment information page
def payment(driver, payment_option, card_details=None):
    try:
        if payment_option == "overseas_card":
            # Select Overseas Issued Credit Card
            driver.find_element(By.ID, "ipt_rdpi01").click()
            print("Selected: (Credit card) issued overseas.")

            # Click Next button for overseas card
            next_button = driver.find_element(By.XPATH, "//img[@alt='Next']")
            next_button.click()
            print("Clicked Next button for overseas card.")
            time.sleep(3)  # Wait for the next page to load

        elif payment_option == "korean_card":
            # Select Korea Issued Credit Card
            driver.find_element(By.ID, "ipt_rdpi02").click()
            print("Selected: (Credit card) issued in Korea.")

            # Fill in card details
            if card_details is None:
                raise ValueError("Card details must be provided for Korean-issued cards.")

            # Fill credit card number
            card_number_parts = card_details["card_number"].split("-")  # Ensure the number is split into 4 parts
            driver.find_element(By.NAME, "txtCardNo1").send_keys(card_number_parts[0])
            driver.find_element(By.NAME, "txtCardNo2").send_keys(card_number_parts[1])
            driver.find_element(By.NAME, "txtCardNo3").send_keys(card_number_parts[2])
            driver.find_element(By.NAME, "txtCardNo4").send_keys(card_number_parts[3])

            # Select expiration date
            month_select = Select(driver.find_element(By.NAME, "ExpMonth_1"))
            month_select.select_by_value(card_details["expiration_month"])
            year_select = Select(driver.find_element(By.NAME, "ExpYear_1"))
            year_select.select_by_value(card_details["expiration_year"])

            # Enter credit card PIN
            driver.find_element(By.NAME, "txtCCardPwd_1").send_keys(card_details["pin"])

            # Enter resident registration number
            driver.find_element(By.NAME, "txtJuminNo2_1").send_keys(card_details["id_number"])

            # Click Next button for Korean card
            next_button = driver.find_element(By.XPATH, "//img[@alt='Next']")
            next_button.click()
            print("Clicked Next button for Korean card.")
            time.sleep(3)  # Wait for the next page to load

        else:
            raise ValueError("Invalid payment option provided.")

    except Exception as e:
        print(f"Error while selecting payment method: {e}")
        return False
    return True

# Update the ktx_reservation function
def ktx_reservation(user_info_train):
    # Get user information
    user_info = user_info_train

    # Initialize Selenium driver
    driver = init_driver()

    try:
        # Search for trains and reserve
        if not search_train(driver, user_info):
            print("Reservation process terminated.")
            return

        # Fill passenger information
        if not fill_passenger_information(driver, passenger_info):
            print("Failed to fill passenger information.")
            return

        # Select payment method & Proceed payment
        if not payment(driver, payment_info["payment_option"]):
            print("Payment process failed.")
            return

        print("Your KTX reservation is successfully completed!")
    finally:
        driver.quit()
        print("Browser closed.")
