from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
import difflib

name = ""                 ## ex) "표세호"
birth = ""            ## ex) "20000101"
phonenumber = ""      ## ex) "12341234"
city = ""              ## ex) "서울특별시"
gu = ""                   ## ex) "관악구"
purpose = "주민등록등본 발급"


driver = webdriver.Chrome()

driver.maximize_window()

driver.get('https://www.gov.kr/portal/main/nologin')


def login():
    # 로그인 버튼 클릭

    driver.implicitly_wait(2)

    login = driver.find_element(by=By.XPATH, value = '/html/body/div[2]/div[3]/div[1]/div/div/ul/li[4]/a')
    login.click()

    # 간편인증 로그인 버튼 선택
    login_button = driver.find_element(by=By.XPATH, value = '/html/body/div[10]/div[3]/div/ul/li[1]/a')
    login_button.click()

    # 카카오톡 버튼 선택
    # 카카오톡이 포함된 li 요소를 XPath로 찾기
    kakao_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//li//p[text()='카카오톡']"))
    )

    # 해당 요소 클릭
    kakao_element.click()

    # kakao = driver.find_element(by=By.XPATH, value = '/html/body/div[2]/div[1]/div/div[1]/div/div[1]/div/div[1]/ul/li[7]/label/a')
    # kakao.click()

    nameBox = driver.find_element(by=By.XPATH, value = '/html/body/div[2]/div[1]/div/div[1]/div/div[2]/section/form/div[1]/div[1]/ul/li[1]/div[2]/input')
    nameBox.send_keys(name)
    time.sleep(1)

    birthBox = driver.find_element(by=By.XPATH, value = '/html/body/div[2]/div[1]/div/div[1]/div/div[2]/section/form/div[1]/div[1]/ul/li[2]/div[2]/input')
    birthBox.send_keys(birth)

    time.sleep(1)

    phoneBox = driver.find_element(by=By.XPATH, value = '/html/body/div[2]/div[1]/div/div[1]/div/div[2]/section/form/div[1]/div[1]/ul/li[4]/div[2]/input')
    phoneBox.send_keys(phonenumber)

    consent_button = driver.find_element(by=By.XPATH, value ='/html/body/div[2]/div[1]/div/div[1]/div/div[2]/section/form/dl[1]/dt/label/input')
    consent_button.click()

    send_button = driver.find_element(by=By.XPATH, value = '/html/body/div[2]/div[1]/div/div[1]/div/div[2]/section/form/div[2]/button[2]')
    send_button.click()

    # 사용자가 직접 인증 완료 버튼을 클릭한 후 페이지 URL이 변경될 때까지 기다림
    current_url = driver.current_url
    WebDriverWait(driver, 300).until(
        lambda driver: driver.current_url != current_url  # URL이 변경될 때까지 기다림
    )


# 유사도 비교 함수
def get_similarity(text1, text2):
    return difflib.SequenceMatcher(None, text1, text2).ratio()

def residential():
# 검색창에 주민등록등본 입력

    search_box = driver.find_element(By.XPATH, value = '/html/body/div[5]/section[2]/div/div[1]/div[3]/div[3]/form/input[3]')
    search_box.send_keys(purpose)

    search_button = driver.find_element(By.XPATH, value = '/html/body/div[5]/section[2]/div/div[1]/div[3]/div[3]/form/button')
    search_button.click()

    # ul 요소 찾기
    ul_element = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div/div[4]/form/div/div/div/div/div/div[3]/div[2]/ul')

    # li 요소들 찾기
    li_elements = ul_element.find_elements(By.TAG_NAME, 'li')

    # 목표 텍스트
    target_text = purpose

    # 가장 유사한 항목 찾기
    best_match = None
    best_similarity = 0

    # li 요소들 순회
    for li in li_elements:
        # li 요소의 a 태그 아래 텍스트 가져오기 (span과 일반 텍스트 포함)
        a_element = li.find_element(By.TAG_NAME, 'a')
        full_text = a_element.text  # 전체 텍스트를 추출
        
        # 유사도 계산
        similarity = get_similarity(full_text, target_text)
        
        # 유사도가 가장 높은 항목 업데이트
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = a_element

    # 가장 유사한 항목 클릭
    if best_match:
        print(f"가장 유사한 항목: {best_match.text} (유사도: {best_similarity})")
        best_match.click()
    
    # 발급하기 클릭
    print_button = driver.find_element(by=By.XPATH, value='/html/body/div[7]/div[2]/div[2]/div/div/span/a')
    print_button.click()

    # city select 요소 찾기
    city_dropdown = driver.find_element(By.XPATH, '/html/body/div[9]/form[2]/div[1]/div[1]/div[1]/div[1]/select')

    # 드롭다운 클릭하여 활성화
    city_dropdown.click()

    # 대기하여 드롭다운에서 '시' 선택 가능할 때까지 기다림
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//option[text()='서울특별시']")))

    # Select 객체 생성
    select_city = Select(city_dropdown)

    # 텍스트로 '시' 선택
    select_city.select_by_visible_text(city)

    # gu select 요소 찾기
    gu_dropdown = driver.find_element(By.XPATH, '/html/body/div[9]/form[2]/div[1]/div[1]/div[1]/div[2]/select')

    # 드롭다운 클릭하여 활성화
    gu_dropdown.click()

    # 대기하여 드롭다운에서 '구' 선택 가능할 때까지 기다림
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//option[text()='서초구']")))

    # Select 객체 생성
    select_gu = Select(gu_dropdown)

    # 텍스트로 '구' 선택
    select_gu.select_by_visible_text(gu)

    # 신청버튼 클릭
    enroll_button = driver.find_element(by=By.XPATH, value='/html/body/div[9]/div[4]/button[2]')
    enroll_button.click()

    time.sleep(2)
    # 문서출력 버튼 클릭
    print_button = driver.find_element(by=By.XPATH, value='/html/body/div[7]/div[2]/div[2]/div/div/div[1]/table/tbody/tr/td[4]/p[2]/span/a')
    print_button.click()

    # 새 창으로 전환
    time.sleep(2)  # 팝업 창이 열리는 시간을 기다립니다.
    driver.switch_to.window(driver.window_handles[1])  # 두 번째 창으로 전환

    # 인쇄 버튼 클릭 (팝업 창 내의 인쇄 버튼)
    print_in_popup_button = driver.find_element(By.XPATH, '/html/body/div[6]/header/div[2]/div[3]/ul/li/a')
    print_in_popup_button.click()


login()

residential()

time.sleep(400)

# # 브라우저 종료
driver.quit()