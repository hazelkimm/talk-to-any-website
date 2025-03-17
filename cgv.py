from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import random
import psycopg2
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_file_path(filename):
    return os.path.join(BASE_DIR, filename)

# Connect to your PostgreSQL database
def connect_db():
    return psycopg2.connect(
        dbname="pikamander",
        user="pikamander",
        password="team6",
        # host="10.67.0.24",
        # host="192.168.45.13",
        # host="192.168.45.188",
        host="175.113.110.253",
        port="5432"
    )

# Retrieve user information from the database
def get_user_info(db_connection, user_id):
    with db_connection.cursor() as cursor:
        cursor.execute('SELECT cgv_id, cgv_pwd, leftright, frontback FROM "users" WHERE user_id = %s', (user_id,))
        user_data = cursor.fetchone()
        
    if user_data:
        return {
            'cgv_id': user_data[0],
            'cgv_pwd': user_data[1],
            # 'leftright': user_data[2],
            'leftright': 'left',
            # 'frontback': user_data[3],
            'frontback': 'middle',

        }
    return None

# DB 연결 및 사용자 정보 가져오기
def get_user_info_from_db(user_id):
    db_connection = connect_db()
    user_id = user_id  # 사용할 user_id (101로 고정)
    user_info = get_user_info(db_connection, user_id)
    db_connection.close()
    return user_info

def login_to_cgv(driver, user_id, user_info):
    driver.get('http://www.cgv.co.kr/user/login/?returnURL=http%3a%2f%2fwww.cgv.co.kr%2fticket%2fdefault.aspx')

    # DB에서 사용자 정보 가져오기 및 비밀번호 복호화
    user_info_from_db = get_user_info_from_db(user_id)
    user_info['cgv_pwd'] = user_info_from_db['cgv_pwd']

    # 로그인
    # 페이지가 로드될 때까지 기다리기
    # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    username = driver.find_element(By.XPATH, '//*[@id="txtUserId"]')
    password = driver.find_element(By.XPATH, '//*[@id="txtPassword"]')

    username.send_keys(user_info['cgv_id'])
    password.send_keys(user_info['cgv_pwd'])
    time.sleep(2)

    login = driver.find_element(By.XPATH, '//*[@id="submit"]')
    login.click()
    time.sleep(2)

    # driver.switch_to.frame('ticket_iframe')


# 시간 형식 변환 함수
def time_in_range(time_str, start, end):
    return start <= time_str <= end


# User에게 원하는 영화관과 시간 입력 받기
# location = input("원하시는 지역을 입력해주세요: ").strip()
# theater = input("원하시는 영화관을 입력해주세요: ").strip()
# date = input("관람을 원하시는 날짜를 입력해주세요 (ex. 4): ").strip()
# preferred_time = input("관람을 원하시는 시간대를 입력해주세요 (ex. 16:00-18:00): ").strip()
# preferred_genre = input("관람하고 싶으신 장르를 입력해주세요. (1. 드라마 2. 액션 3. 멜로.로맨스 4. 서스펜스): ").strip()
# num_people = input("관람하시는 인원을 입력해주세요: ").strip()
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def search_movies(driver, preferred_time):
    driver.get('http://www.cgv.co.kr/ticket/eng/newdefault.aspx')
    driver.add_cookie({'name': 'Language', 'value': 'en'})
    driver.refresh()
    wait = WebDriverWait(driver, 10)

def select_movie(driver, movie_name):
    movies = driver.find_elements(By.CLASS_NAME, "movie-title-class")  # Adjust class
    for movie in movies:
        if movie.text == movie_name:
            movie.click()
            return True
    return False

def choose_seat(driver, seat_preferences):
    seats = driver.find_elements(By.CLASS_NAME, "seat-class")  # Adjust class
    for seat in seats:
        if seat.get_attribute("data-preference") == seat_preferences:
            seat.click()
            return seat.get_attribute("id")
    return None

def process_payment(driver, payment_details):
    driver.find_element(By.ID, "card_number").send_keys(payment_details['card_number'])
    driver.find_element(By.ID, "expiry_date").send_keys(payment_details['expiry_date'])
    driver.find_element(By.ID, "cvc").send_keys(payment_details['cvc'])
    driver.find_element(By.ID, "cardholder_name").send_keys(payment_details['cardholder_name'])

    driver.find_element(By.ID, "pay_button").click()
    time.sleep(5)  # Wait for payment confirmation
    return "Payment Complete!"


def cgv_ticketing():
    db_connection = connect_db()
    user_id = 'sehopyo'  # 사용할 user_id (101로 고정)
    user_infos = get_user_info_from_db(user_id)
    db_connection.close()
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    # options.add_argument('window-size=1920x1080')
    service = Service(executable_path=get_file_path('./chromedriver.exe'))
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(1)
    
    # Chrome 팝업창을 자동으로 확인하는 함수
    def handle_popup():
        try:
            # 팝업 대기 및 확인
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert.accept()  # 확인 버튼 클릭
        except:
            print("팝업이 나타나지 않았습니다.")



    ### 로그인
    login_to_cgv(driver, user_id, user_info)


    ### 예매 페이지로 이동
    # driver.get('http://www.cgv.co.kr/ticket/')
    driver.switch_to.frame('ticket_iframe')
    time.sleep(1)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    ### 영화 선택 (title)
    movies = soup.select('#movie_list > ul > li > a')
    titles = [movie['title'] for movie in movies if movie.has_attr('title')]
    # print(titles)
    title_idx = titles.index(user_info['title'])

    movie = driver.find_element(By.XPATH, f'//*[@id="movie_list"]/ul/li[{title_idx+1}]/a')
    movie.click()
    time.sleep(2)


    ### 영화타입 선택 (movie_type)
    if user_info['movie_type'] == '2D':
        movie_type = 'sbmt_digital'
    elif user_info['movie_type'] == 'IMAX':
        movie_type = 'sbmt_imax'
    elif user_info['movie_type'] == '4DX':
        movie_type = 'sbmt_4dx'
    elif user_info['movie_type'] == 'SOUNDX':
        movie_type = 'sbmt_soundx'
    elif user_info['movie_type'] == 'SCREENX':
        movie_type = 'sbmt_screenx'
    else:
        movie_type = 'sbmt_all'

    movieType = driver.find_element(By.XPATH, f'//*[@id="{movie_type}"]/a')
    movieType.click()
    time.sleep(1)


    ### 지역 선택 (location)
    locations = soup.select('#theater_area_list > ul > li > a')
    location_names = [location.get_text(strip=True) for location in locations]
    location_idx = next((i for i, location in enumerate(location_names) if location.startswith(user_info['location'])), -1)
        
    location = driver.find_element(By.XPATH, f'//*[@id="theater_area_list"]/ul/li[{location_idx+1}]/a')
    location.click()
    time.sleep(1)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')


    ### 영화관 선택 (theater)
    theaters = soup.select('#theater_area_list > ul > li.selected > div > ul > li > a')
    theater_names = [theater.get_text(strip=True) for theater in theaters]
    theater_idx = theater_names.index(user_info['theater'])
        
    theater = driver.find_element(By.XPATH, f'//*[@id="theater_area_list"]/ul/li[{location_idx+1}]/div/ul/li[{theater_idx+1}]/a')
    theater.click()
    time.sleep(1)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')


    ### 날짜 선택 (date)
    dates = soup.select('#date_list > ul > div > li > a')
    available_days = [date.find(class_='day').get_text(strip=True) for date in dates if not date.find(class_='sreader', string="선택불가")]
    # print(available_days)
    date_idx = available_days.index(user_info['date'])
        
    date = driver.find_element(By.XPATH, f'//*[@id="date_list"]/ul/div/li[{date_idx+2}]/a')
    date.click()
    time.sleep(1)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # # 사용자가 입력한 시간 범위
    # start_time = preferred_time[:5]  # 시작 시간
    # end_time = preferred_time[7:]    # 종료 시간
    start_time = user_info['start_time']
    end_time = user_info['end_time']

    ### 상영시간 선택 (movie_time)
    screens = soup.select('#ticket > div.steps > div.step.step1 > div.section.section-time > div.col-body > div.time-list.nano > div.content.scroll-y > div > span > span.floor')
    screens = [screen.get_text(strip=True) for screen in screens]
    screen_idx = next((i for i, screen in enumerate(screens) if screen.startswith(user_info['screen'])), -1)

    # 각 상영관에서 원하는 시간 범위에 맞는 영화 시간 선택
    selected = False
    for screen_idx, screen in enumerate(screens):
        # 해당 상영관의 상영 시간 가져오기
        times = soup.select(f'#ticket > div.steps > div.step.step1 > div.section.section-time > div.col-body > div.time-list.nano > div.content.scroll-y > div:nth-child({screen_idx+1}) > ul > li > a')
        
        # 상영 시간 리스트 생성
        time_texts = [time.select_one('.time > span').get_text(strip=True) for time in times]
        
        # 원하는 시간 범위에 맞는 상영 시간 검색
        for time_idx, time_text in enumerate(time_texts):
            if time_in_range(time_text, start_time, end_time):
                # 원하는 시간이 있으면 클릭
                movie_time = driver.find_element(By.XPATH, f'//*[@id="ticket"]/div[2]/div[1]/div[4]/div[2]/div[3]/div[1]/div[{screen_idx+1}]/ul/li[{time_idx+1}]/a')
                movie_time.click()
                time.sleep(1)
                selected = True
                break

        if selected:
            break  # 원하는 상영 시간을 찾으면 루프 종료
        
    ### 좌석선택 버튼 클릭
    seatBtn = driver.find_element(By.XPATH, '//*[@id="tnb_step_btn_right"]')
    seatBtn.click()
    time.sleep(2)


    ### 관람등급 안내 '동의하고 예매하기' 클릭
    notice = driver.find_element(By.XPATH, '/html/body/div[4]/div[3]/a[1]')
    notice.click()
    time.sleep(1)


    ### 인원선택
    num_people = int(user_info['num_people'])
    numOfPeople = driver.find_element(By.XPATH, f'//*[@id="nop_group_adult"]/ul/li[{num_people+1}]/a')
    numOfPeople.click()

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')


    ### 좌석선택

    # 상영관의 좌석 행 개수 세기
    rows = driver.find_elements(By.CSS_SELECTOR, '#seats_list > div > div.row')
    third = len(rows) // 3

    # 'front', 'middle', 'back' 중 사용자 선호 위치의 행들을 선택
    if user_info['seat_fmb'] == 'front':
        preferred_rows = rows[: third]
    elif user_info['seat_fmb'] == 'middle':
        preferred_rows = rows[third : 2*third]
    else:
        preferred_rows = rows[2*third :]

    # 위에서 고른 행들 중에서, 'left', 'middle', 'right' 모두 있는 행 선택 (A,B,C 블록 중 하나라도 없는 경우에는 그냥 제외시킴)
    selected_row = None
    if user_info['seat_fmb'] == 'back' or user_info['seat_fmb'] == 'middle':
        rows_to_check = reversed(preferred_rows)
    else:
        rows_to_check = preferred_rows

    for row in rows_to_check:
        seat_groups = row.find_elements(By.CSS_SELECTOR, 'div[class^="seat_group"]')
        if len(seat_groups) == 3:
            selected_row = row
            break

    # 'left', 'middle', 'right' 중 사용자 선호 위치의 좌석들 선택
    selected_seats = None
    if user_info['seat_lmr'] == 'left':
        selected_seats = selected_row.find_element(By.CLASS_NAME, 'seat_group.left')
        selected_seats = selected_seats.find_elements(By.CLASS_NAME, 'seat')
    elif user_info['seat_lmr'] == 'right':
        seat_groups = selected_row.find_elements(By.CLASS_NAME, 'seat_group')
        selected_seats = seat_groups[2].find_elements(By.CLASS_NAME, 'seat')
    else:
        seat_groups = selected_row.find_elements(By.CLASS_NAME, 'seat_group')
        selected_seats = seat_groups[1].find_elements(By.CLASS_NAME, 'seat')

    random.shuffle(selected_seats)

    # 사용자 선호 위치의 좌석들 중에서 예약 가능한 것 선택
    while True:
        for seat in selected_seats:
            try:
                seat.click()
                time.sleep(1)
                break

                '''
                예상 오류
                1. 예매완료 좌석(뺏김)
                    ->  1) 확인 버튼을 누르고
                        2) 방금 선택한 좌석을 다시 클릭해서 해제한 후
                        3) 1초 로딩 기다리고
                        4) 다음 좌석 선택 시도로 넘어가기  
                        
                    
                2. 선택불가, 예매 완료된 회색 좌석
                    클릭해서 아무 반응이 없는 상태로 다음 버튼을 누를 때
                    <관람인원과 선택 좌석 수가 동일하지 않습니다> 발생
                        
                    ->  1) 확인 버튼을 누르고
                        2) 다음 좌석 선택 시도로 넘어가기
                        
                        
                '''

            except:
                handle_popup()
                continue

        # 결제선택 빨강버튼
        seatBtn = driver.find_element(By.XPATH, '//*[@id="tnb_step_btn_right"]')
        seatBtn.click()
        time.sleep(2)


        ### 결제 화면

        ### 결제 정보 입력 (Payment Information Input)

        # Placeholder payment information
        payment_info = {
            'card_number': '1234-5678-9012-3456',  # Sample card number
            'expiry_date': '12/25',  # Sample expiry date
            'cvc': '123',  # Sample CVC
            'cardholder_name': 'John Doe'  # Sample cardholder name
        }

        try:
            # 카드 번호 입력
            card_number_field = driver.find_element(By.XPATH, '//*[@id="card_number"]')
            card_number_field.send_keys(payment_info['card_number'])

            # 만료 날짜 입력
            expiry_date_field = driver.find_element(By.XPATH, '//*[@id="expiry_date"]')
            expiry_date_field.send_keys(payment_info['expiry_date'])

            # CVC 입력
            cvc_field = driver.find_element(By.XPATH, '//*[@id="cvc"]')
            cvc_field.send_keys(payment_info['cvc'])

            # 카드 소유자 이름 입력
            cardholder_name_field = driver.find_element(By.XPATH, '//*[@id="cardholder_name"]')
            cardholder_name_field.send_keys(payment_info['cardholder_name'])

            print("Payment information entered successfully.")
        except Exception as e:
            print("Error entering payment information:", e)

        ### Terms Agreement and Payment Confirmation

        # 약관 동의 및 결제 진행
        try:
            # 약관 동의 체크박스 클릭
            terms_checkbox = driver.find_element(By.XPATH, '//*[@id="terms_agree"]')
            terms_checkbox.click()

            # 결제 버튼 클릭
            pay_button = driver.find_element(By.XPATH, '//*[@id="pay_button"]')
            pay_button.click()

            print("Payment submitted, waiting for confirmation...")
            time.sleep(5)  # Wait for processing; adjust as needed for the site's response time
        except Exception as e:
            print("Error submitting payment:", e)

        ### 결제 완료 확인 (Confirm Payment Completion)

        try:
            # 결제 완료 메시지 확인
            confirmation_message = driver.find_element(By.XPATH, '//*[@id="confirmation_message"]').text
            print("Payment confirmation received:", confirmation_message)
        except Exception as e:
            print("Failed to retrieve payment confirmation:", e)

        ### 마무리 (Finalization)

        # 모든 작업 완료 후 브라우저 닫기
        driver.quit()
        print("Process completed and browser closed.")

    # driver.close()


