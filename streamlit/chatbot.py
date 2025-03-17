import openai
import json
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import threading
import os
import tempfile
import sys

import streamlit as st
from st_pages import Page, show_pages, hide_pages
from streamlit_extras.switch_page_button import switch_page
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from login import connect_db
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import cgv
from cgv import cgv_ticketing, login_to_cgv, search_movies, select_movie, choose_seat, process_payment
import restaurant
from restaurant import resta
import train_ticket
from train_ticket import ktx_reservation, get_user_input

# Layout
# st.set_page_config(
#     page_title="Talk to Any Website!",
#     layout="wide",
#     initial_sidebar_state="expanded",
#     page_icon="🗣️"
#     )

show_pages([
    Page("main_page.py","Main"),
    Page("login.py","Login"),
    Page("chatbot.py","Chatbot"),
])

hide_pages(['Main', 'Login', 'Chatbot'])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_file_path(filename):
    return os.path.join(BASE_DIR, filename)

# WebDriver Manager (Singleton)
class WebDriverManager:
    _driver = None

    @classmethod
    def get_driver(cls):
        if cls._driver is None:
            options = webdriver.ChromeOptions()
            service = Service(executable_path=get_file_path('./chromedriver'))  # Adjust path to chromedriver
            cls._driver = webdriver.Chrome(service=service, options=options)
        return cls._driver

    @classmethod
    def quit_driver(cls):
        if cls._driver:
            cls._driver.quit()
            cls._driver = None
##################################

# Train info
user_info_train = {}



if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    col1, col2, col3 = st.sidebar.columns(3)
    if col1.button('My Page', key="my_page_button"):
        st.session_state.page = 'mypage'
        switch_page('Login')
    if col2.button('Logout', key="logout_button"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.page = 'Login'
        switch_page('Main')
else:
    if st.sidebar.button('Login', key="login_button"):
        switch_page('Login')

# st.markdown("""
# <style>
# .big-font {
#     font-size:80px !important;
# }
# </style>
# """, unsafe_allow_html=True)

# CSS 스타일을 추가
# CSS 스타일을 추가
st.markdown("""
<style>
/* 전체 페이지 레이아웃을 세로로 정렬 */
.css-1v3fvcr {
    display: flex;
    flex-direction: column;
    height: 100vh;
}

/* 채팅 메시지 영역을 확장 */
.css-1n76uvr {
    flex-grow: 1;
    overflow-y: auto;
    padding-bottom: 80px; /* 하단 여백 추가 */
}

/* 입력창 및 버튼 컨테이너 */
.chat-container {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: white;
    padding: 10px;
    box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.1);
    display: flex;
    gap: 10px; /* 입력창과 버튼 간격 */
    justify-content: center;
    align-items: center;
}

/* 입력창 스타일 */
input[type="text"] {
    flex-grow: 1;
    padding: 10px;
    border-radius: 8px;
    border: 1px solid #ccc;
    font-size: 16px;
}

/* 음성 버튼 스타일 */
.voice-button {
    padding: 10px;
    border: none;
    border-radius: 50%;
    background-color: #007bff;
    color: white;
    cursor: pointer;
    font-size: 18px;
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.voice-button:hover {
    background-color: #0056b3;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_lottiefile(filepath: str):
    with open(filepath,"r") as f:
        return json.load(f)

with st.sidebar:
    selected = option_menu('Talk to Any Website!', ['Main', 'Chatbot'],
        icons=['house', 'chat-dots'], menu_icon='robot', default_index=1)
    lottie = load_lottiefile("chatbot.json")
    st_lottie(lottie,key='loc')

if selected == 'Main':
    switch_page('Main')

if selected == 'Chatbot':
    client = openai.OpenAI()

    recognizer = sr.Recognizer()

    import pygame

    pygame.mixer.init()


    def speak(text, lang='en'):
        """Convert text to speech and play it using pygame."""
        try:
            # Convert text to lowercase before passing to gTTS
            text_to_speak = text.lower()

            # Generate TTS audio
            tts = gTTS(text=text_to_speak, lang=lang)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp_file_path = temp_file.name  # Save path
            temp_file.close()
            tts.save(temp_file_path)

            # Play audio using pygame
            pygame.mixer.music.load(temp_file_path)
            pygame.mixer.music.play()

            # Wait for playback to finish (non-blocking for Streamlit)
            def cleanup():
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)  # Avoid CPU overuse
                os.remove(temp_file_path)

            threading.Thread(target=cleanup, daemon=True).start()
        except Exception as e:
            print(f"Error during speech playback: {e}")




    # Function for capturing user input from voice
    def listen():
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print("You said: " + text)
            return text
        except sr.UnknownValueError:
            print("Could not understand audio")
            return "Could not understand audio"
        except sr.RequestError:
            print("Could not request results; check your network connection")
            return "Could not request results; check your network connection"

    

    # Macro function to handle specific task prompts
    def send_macro_command(task_description):
        return f"I need code for a macro that performs the following task: {task_description}"

    
    def extract_movie_name(user_message, available_movies):
        """
        Extracts the movie name from a user's message.
        Supports direct movie name match or ordinal references like 'first' or 'second'.

        Args:
            user_message (str): The user's input message.
            available_movies (list): List of available movie names.

        Returns:
            str: Extracted movie name, or None if not found.
        """
        user_message_lower = user_message.lower()

        # Direct match
        for movie in available_movies:
            if movie.lower() in user_message_lower:
                return movie

        # Ordinal references
        ordinal_map = {"first": 0, "second": 1, "third": 2}
        for word, index in ordinal_map.items():
            if word in user_message_lower and index < len(available_movies):
                return available_movies[index]

        return None


    import time


    if "user_info_train" not in st.session_state:
        st.session_state.user_info_train = {
            "travel_date": None,
            "departure_time": None,
            "departure_station": None,
            "arrival_station": None,
            "seat_class": None,  # "1" for Economy, "2" for First Class
            "train_type": None,
            "adults": None,
            "children": None,
        }

    # 질문과 키 매핑
    questions = []
    question_to_key = {}

    if "user_info_train" not in st.session_state:
        st.session_state.user_info_train = {key: None for key in question_to_key.values()}

    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0

    def handle_train_ticket_questions(user_message):
        """Train ticket 질문 처리"""
        current_index = st.session_state.current_question_index

        # 사용자의 응답을 user_info_train에 저장
        if current_index > 0:  # 첫 질문에는 응답 없음
            previous_question = questions[current_index - 1]
            key = question_to_key[previous_question]
            if user_message:  # 응답이 있는 경우에만 저장
                st.session_state.user_info_train[key] = user_message
            else:
                return "Please provide an answer before proceeding."

        # 다음 질문 진행
        if current_index < len(questions):
            current_question = questions[current_index]
            st.session_state.current_question_index += 1
            return current_question
        else:
            # 모든 질문이 완료되었을 때
            booking_summary = (
                "Thank you! Here is your booking information:\n" +
                "\n".join([f"{key.replace('_', ' ').capitalize()}: {value}\n" for key, value in st.session_state.user_info_train.items()])
            )
            # 상태 초기화 및 예약 프로세스 시작
            # st.session_state.current_question_index = 0  # 상태 초기화
            # st.session_state.user_info_train = {key: None for key in question_to_key.values()}  # 정보 초기화
            train_ticket.ktx_reservation(st.session_state.user_info_train)
            return booking_summary



    def chat_with_gpt(user_message):
        user_id = st.session_state.get('user_id', None)  # session_state에서 user_id 가져오기

        if not user_id:
            st.error("User not logged in")
            return
        user_message = user_message if user_message else ""
        assistant_response = ""

        prompt = None
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # 사용자 메시지를 세션 상태에 추가
        st.session_state.messages.append({"role": "user", "content": user_message}

        if "train ticket" in user_message.lower() or st.session_state.current_question_index >0:
            # 시스템 메시지로 GPT 역할 설정
            if "messages" not in st.session_state:
                st.session_state.messages = []

            # Define the system message separately
            system_message = {
                "role": "system",
                "content": "You are a helpful Train Ticket Booking Assistant. Your job is to help users book train tickets by gathering necessary details such as travel date, preferred departure time, departure station, destination station, seat class, train type, and number of adult and child passengers. You provide options based on their preferences and assist step-by-step in the booking process."
            }

            # If no predefined response, call OpenAI API
            try:
                # API 호출
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[system_message] + st.session_state.messages  # Always prepend the system message
                )
                gpt_response = response.choices[0].message.content

                # Add GPT's response to the conversation history
                st.session_state.messages.append({"role": "assistant", "content": gpt_response})

                speak(gpt_response)

            except Exception as e:
                st.error("Error communicating with OpenAI API. Please try again later.")
                print(f"OpenAI API error: {e}")


            ###################### 실시간 업뎃
          
            if st.session_state.current_question_index == 0:
                # 첫 번째 질문 시작
                # assistant_response = "Cool! Let me help you book a train ticket."
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                speak(assistant_response)

            # 다음 질문 처리
            next_question = handle_train_ticket_questions(user_message)
            st.session_state.messages.append({"role": "assistant", "content": next_question})
            speak(next_question)

            
     
        

        ##############원래 else문 #######################
        else:
            # If no predefined response, call OpenAI API
            try:
                # API 호출
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ]
                )
                gpt_response = response.choices[0].message.content  # Correct access
                speak(gpt_response)
                st.session_state.messages.append({"role": "assistant", "content": gpt_response})
            except Exception as e:
                st.error("Error communicating with OpenAI API. Please try again later.")
                print(f"OpenAI API error: {e}")
       #############################################

            system_message = {
                "role": "system",
                "content": "You are a helpful Booking Assistant. Your job is to help users book by gathering necessary details. You provide options based on their preferences and assist step-by-step in the booking process."
            }

            # If no predefined response, call OpenAI API
            try:
                # API 호출
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[system_message] + st.session_state.messages  # Always prepend the system message
                )
                gpt_response = response.choices[0].message.content

                # Add GPT's response to the conversation history
                st.session_state.messages.append({"role": "assistant", "content": gpt_response})

                # Display the GPT response
                speak(gpt_response)

            except Exception as e:
                st.error("Error communicating with OpenAI API. Please try again later.")
                print(f"OpenAI API error: {e}")

        log_conversation(user_id, user_message, "", "user")
        log_conversation(user_id, "", assistant_response, "assistant")
            #############################################################

    def log_conversation(user_id, user_speech, gpt_response, speaker):
        if not user_id:
            print("Log skipped: user_id is missing.")
            return

        # user_speech와 gpt_response가 None일 경우 기본값 처리
        user_speech = user_speech or ""
        gpt_response = gpt_response or ""

        connection = connect_db()
        try:
            with connection.cursor() as cursor:
                query = """
                    INSERT INTO gpt_log (user_id, interaction_time, user_speech, gpt_response, speaker)
                    VALUES (%s, %s, %s, %s, %s)
                """
                interaction_time = datetime.now()
                cursor.execute(query, (user_id, interaction_time, user_speech, gpt_response, speaker))
            connection.commit()
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            connection.close()

    # Initial greeting with speak function
    #초기화; 첫 실행 시 인사 메시지 출력
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        # speak("Hello, how can I assist you today?")

    # 메시지 리스트 초기화
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    st.title("🗣️ Talk to Any Website!")
    st.divider()
    voice = False

    
    col1, col2 = st.columns([8, 2])  # 메시지 입력창이 음성 버튼보다 넓게 설정

    with col1:  # 메시지 입력 창
        with st._bottom:
            user_message = st.chat_input("Talk to Any Website!", key="text_input")

    with col2:  # 음성 버튼
        with st._bottom:
            if st.button('', icon=":material/mic:", key='voice_button'):  # 음성 버튼
                voice_input = listen()
                user_message = voice_input if voice_input else ""

    # 메시지가 입력된 경우 처리
    if user_message:
        chat_with_gpt(user_message)

    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.write(message['content'])  

    if voice:
        user_message = voice_input
        voice = False
        chat_with_gpt(user_message)