from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_file_path(filename):
    return os.path.join(BASE_DIR, filename)

# Selenium 설정
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--disable-popup-blocking')  # 팝업 차단 설정
options.add_argument('--incognito') 
service = webdriver.chrome.service.Service(executable_path=get_file_path('./chromedriver'))
driver = webdriver.Chrome(service=service, options=options)
driver.implicitly_wait(1)

# 네이버 사이트 열기 & 로그인
driver.get("https://www.naver.com/")
login = driver.find_element(By.XPATH, '//*[@id="account"]/div/a')
login.click()
time.sleep(2)
login_id = driver.find_element(By.XPATH, '//*[@id="id"]')
login_id.send_keys(user_id) # id
login_pw = driver.find_element(By.XPATH, '//*[@id="pw"]')
login_pw.send_keys(user_pw) # pw
login_button = driver.find_element(By.XPATH, '//*[@id="log.login"]')
login_button.click()
time.sleep(20)

# 검색
search_box = driver.find_element(By.XPATH, '//*[@id="query"]')
enter_button = driver.find_element(By.XPATH, '//*[@id="sform"]/fieldset/button')
enter_button.click()
time.sleep(2)

# 식당 선택
restaurant = driver.find_element(By.XPATH, '//*[@id="place-main-section-root"]/section/div/div[5]/ul/li[1]/div[1]/a[1]')
driver.execute_script("arguments[0].removeAttribute('target');", restaurant)
restaurant.click()
time.sleep(20)

# 예약 선택
driver.switch_to.frame('entryIframe')
reservation = driver.find_element(By.XPATH, '//*[@id="app-root"]/div/div/div/div[2]/div[4]/div/span')
reservation.click()
time.sleep(2)

# 예약 유형 선택
reservation = driver.find_element(By.XPATH, '//*[@id="app-root"]/div/div/div/div[6]/div[2]/div/div[2]/ul/li[2]/div[2]/a/div[1]/div')
reservation.click()
time.sleep(2)

# 예약 날짜 선택
driver.execute_script("window.scrollTo(0, 400);")
reservation = driver.find_element(By.XPATH, '//*[@id="root"]/main/section[2]/div/div[3]/div[1]/div/div/button[2]')
reservation.click()
time.sleep(2)

# 예약 날짜 최종 선택
reservation = driver.find_element(By.XPATH, '//*[@id="root"]/main/section[2]/div/div[3]/div[1]/div/table/tbody/tr[1]/td[7]/button')
reservation.click()
time.sleep(2)

driver.execute_script("window.scrollTo(0, 400);")
reservation = driver.find_element(By.XPATH, '//*[@id="root"]/main/section[2]/div/div[3]/div[2]/div/ul[2]/li[15]/button')
reservation.click()
time.sleep(2)

driver.execute_script("window.scrollTo(0, 400);")
reservation = driver.find_element(By.XPATH, '//*[@id="root"]/main/div[4]/div/button')
reservation.click()
option1 = driver.find_element(By.XPATH, '//*[@id="extra0"]/option[2]')
option1.click()
option2 = driver.find_element(By.XPATH, '//*[@id="extra1"]/option[2]')
option2.click()
time.sleep(2)

reservation = driver.find_element(By.XPATH, '//*[@id="root"]/div[2]/div[4]/div/button[2]')
reservation.click()

driver.quit()