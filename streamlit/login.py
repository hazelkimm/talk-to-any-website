import psycopg2
import pandas as pd

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import base64

import streamlit as st
from st_pages import Page, show_pages, hide_pages
from streamlit_extras.switch_page_button import switch_page

##### Streamlit Layout
st.set_page_config(
    page_title="Talk to Any Website!",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🗣️"
    )

show_pages([
    Page("main_page.py","Main"),
    Page("login.py","Login"),
    Page("chatbot.py","Chatbot"),
])

hide_pages(['Chatbot'])

##### 암호화 관련
def generate_and_save_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()

    # Save private key
    with open("private_key.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Save public key
    with open("public_key.pem", "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

def load_keys():
    with open("private_key.pem", "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )
    with open("public_key.pem", "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())
    return private_key, public_key

try:
    private_key, public_key = load_keys()
except FileNotFoundError:
    generate_and_save_keys()
    private_key, public_key = load_keys()

# 암호화
def encrypt_pwd(password):
    password_bytes = password.encode('utf-8')
    encrypted_password = public_key.encrypt(
        password_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    encrypted_password_b64 = base64.b64encode(encrypted_password).decode('utf-8')
    return encrypted_password_b64

# 복호화
def decrypt_pwd(encrypted_password_b64):
    encrypted_password = base64.b64decode(encrypted_password_b64)
    decrypted_password = private_key.decrypt(
        encrypted_password,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    decrypted_password_str = decrypted_password.decode('utf-8')
    return decrypted_password_str


##### DB 관련
IP = "175.113.110.253"
# IP = "10.67.0.24"

def connect_db():
    return psycopg2.connect(
        dbname="pikamander",
        user="pikamander",
        password="team6",
        host=IP,
        port="5432"
    )

def run_db(sql:str,sql_type):
    if sql_type not in ['select', 'update', 'insert']: raise Exception("sql_type should be 'select' or 'update' or 'insert'")

    conn = connect_db()
    if sql_type == 'select':
        reaction = None
        try:
            reaction = pd.read_sql(sql,conn)

        except psycopg2.Error as e:
            print("DB error: ", e)

        finally:
            conn.close()
    
        return reaction
    
    elif sql_type == 'update' or sql_type == 'insert':
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()

        except psycopg2.Error as e:
            print("DB error: ", e)
            conn.rollback()

        finally:
            conn.close()

def add_user(user_id, name, age, sex, cgv_id, cgv_pwd, address, 
             leftright, aisle_seat, frontback, 
             password, korail_id, korail_pwd, naver_id, naver_pwd):
    conn = connect_db()
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO users (user_id, name, age, sex, cgv_id, cgv_pwd, address, 
              leftright, aisle_seat, frontback, 
              password, korail_id, korail_pwd, naver_id, naver_pwd) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (user_id, name, age, sex, cgv_id, encrypt_pwd(cgv_pwd), address, leftright, aisle_seat, frontback, 
          encrypt_pwd(password), korail_id, encrypt_pwd(korail_pwd), naver_id, encrypt_pwd(naver_pwd)))

    # c.execute('''
    #     INSERT INTO users (user_id, name, age, sex, cgv_id, cgv_pwd, address, 
    #           leftright, aisle_seat, frontback, 
    #           password, korail_id, korail_pwd, naver_id, naver_pwd) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    # ''', (user_id, name, age, sex, cgv_id, cgv_pwd, address, leftright, aisle_seat, frontback, 
    #       password, korail_id, korail_pwd, naver_id, naver_pwd))

    conn.commit()
    conn.close()

def check_user(user_id, password):
    conn = connect_db()
    c = conn.cursor()

    c.execute('''
        SELECT password FROM users WHERE user_id = %s
    ''', (user_id, ))

    result = c.fetchone()
    conn.close()

    if result is None:
        return False

    return password == decrypt_pwd(result[0])
    # return password == result[0]

def find_user_info(user_id):
    sql = f"SELECT name, age, sex, cgv_id, cgv_pwd, address, leftright, aisle_seat, frontback, korail_id, korail_pwd, naver_id, naver_pwd, password FROM users WHERE user_id = '{user_id}'"
    user_table = run_db(sql, 'select')

    name = user_table.loc[0, 'name']
    age = user_table.loc[0, 'age']
    sex = user_table.loc[0, 'sex']
    cgv_id = user_table.loc[0, 'cgv_id']
    cgv_pwd = user_table.loc[0, 'cgv_pwd']
    address = user_table.loc[0, 'address']
    leftright = user_table.loc[0, 'leftright']
    aisle_seat = user_table.loc[0, 'aisle_seat']
    frontback = user_table.loc[0, 'frontback']
    korail_id = user_table.loc[0, 'korail_id']
    korail_pwd = user_table.loc[0, 'korail_pwd']
    naver_id = user_table.loc[0, 'naver_id']
    naver_pwd = user_table.loc[0, 'naver_pwd']
    password = user_table.loc[0, 'password']

    return name, age, sex, cgv_id, decrypt_pwd(cgv_pwd), address, leftright, aisle_seat, frontback, korail_id, decrypt_pwd(korail_pwd), naver_id, decrypt_pwd(naver_pwd), decrypt_pwd(password)
    # return name, age, sex, cgv_id, cgv_pwd, address, leftright, aisle_seat, frontback, korail_id, korail_pwd, naver_id, naver_pwd, password

def user_info_update(user_id, name, age, sex, cgv_id, cgv_pwd, address, 
                     leftright, aisle_seat, frontback, 
                     korail_id, korail_pwd, naver_id, naver_pwd, password):
    sql = f"UPDATE users SET name = '{name}', age = '{age}', sex = '{sex}', cgv_id = '{cgv_id}', cgv_pwd = '{encrypt_pwd(cgv_pwd)}', address = '{address}', leftright = '{leftright}', aisle_seat = '{aisle_seat}', frontback = '{frontback}', korail_id = '{korail_id}', korail_pwd = '{encrypt_pwd(korail_pwd)}', naver_id = '{naver_id}', naver_pwd = '{encrypt_pwd(naver_pwd)}', password = '{encrypt_pwd(password)}' WHERE user_id = '{user_id}'"
    # sql = f"UPDATE users SET name = '{name}', age = '{age}', sex = '{sex}', cgv_id = '{cgv_id}', cgv_pwd = '{cgv_pwd}', address = '{address}', leftright = '{leftright}', aisle_seat = '{aisle_seat}', frontback = '{frontback}', korail_id = '{korail_id}', korail_pwd = '{korail_pwd}', naver_id = '{naver_id}', naver_pwd = '{naver_pwd}', password = '{password}' WHERE user_id = '{user_id}'"
    run_db(sql, 'update')



# 로그인 페이지를 보여주는 함수
def show_login():
    st.title("Login")
    user_id = st.text_input("ID")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            if check_user(user_id, password):
                st.session_state.logged_in = True
                st.session_state.user_id = user_id
                switch_page('Main')
            else:
                st.warning("Incorrect ID or password")
        except:
            st.warning("Incorrect ID or password2")

# 회원가입 페이지를 보여주는 함수
def show_signup():
    st.title("Sign up")
    new_user_id = st.text_input("ID")
    new_password = st.text_input("Password", type="password")
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        new_name = st.text_input("Your name")
        new_age = st.number_input("Your age", min_value=0, max_value=120)
        new_sex = st.selectbox("Your sex", options=["Male", "Female"])
        new_address = st.text_input("Your address")

    with col2:
        new_cgv_id = st.text_input("Your CGV ID")
        new_cgv_pwd = st.text_input("Your CGV password", type="password")
        new_leftright = st.selectbox("Your preferred seat in the movie theater (Left or Right)", options=['Left', 'Middle', 'Right'])
        new_frontback = st.selectbox("Your preferred seat in the movie theater (Front or Back)", options=['Front', 'Middle', 'Back'])
        new_aisle_seat = st.checkbox("Your preferred seat in the movie theater (Aisle seat)")

    with col3:
        new_korail_id = st.text_input("Your Korail ID")
        new_korail_pwd = st.text_input("Your Korail password", type="password")
        new_naver_id = st.text_input("Your Naver ID")
        new_naver_pwd = st.text_input("Your Naver password", type="password")

    st.divider()
    if st.button("Sign Up"):
        if new_user_id == '':
            st.warning("Enter the ID")
        if new_password == '':
            st.warning("Enter the password")
        
        try:
            if check_user(new_user_id, new_password): 
                st.warning("This ID is already taken")
            else:
                add_user(new_user_id, new_name, new_age, new_sex, 
                         new_cgv_id, new_cgv_pwd, new_address, 
                         new_leftright, new_aisle_seat, new_frontback,
                         new_password, new_korail_id, new_korail_pwd, new_naver_id, new_naver_pwd)  # add_user 함수를 호출하여 사용자 정보를 데이터베이스에 저장
                st.success("You have successfully signed up")
        except:
            st.warning("This ID is already taken2")



##### 페이지 출력

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "Login"

if st.session_state.logged_in and (st.session_state.page != 'mypage') and (st.session_state.page != 'update_info'):
    switch_page('Main')

else:
    if st.session_state.page == "Login":
        show_login()
        col1, col2, _, _, _, _, _, _, _, _ = st.columns(10)
        if col2.button('Main'):
            switch_page('Main')
        if col1.button("Sign Up"):
            st.session_state.page = "signup"
            switch_page('Login')
    
    elif st.session_state.page == "signup":
        show_signup()
        col1, col2, _, _, _, _, _ = st.columns(7)
        if col2.button('Main'):
            st.session_state.page = "Login"
            switch_page('Main')
        if col1.button("Back to Login"):
            st.session_state.page = "Login"
            switch_page('Login')

    elif st.session_state.page == 'mypage':
        user_id = st.session_state.user_id
        name, age, sex, cgv_id, cgv_pwd, address, leftright, aisle_seat, frontback, korail_id, korail_pwd, naver_id, naver_pwd, password = find_user_info(user_id)

        st.title('My Page')
        st.divider()

        st.metric('Name', f'👤 {name}')

        col1, col2, col3 = st.columns([1, 1, 5])
        col1.metric('Age', age)
        col2.metric('Sex', sex)
        col3.metric('Address', address)
        st.divider()

        col1, col2, col3 = st.columns(3)
        with col1:
            sub_col1, sub_col2 = st.columns([1, 3])
            sub_col1.metric('Account', '🍿')
            sub_col2.code(cgv_id, language='markdown')
            sub_col1.write('')
            sub_col2.text_input('', type='password', value=cgv_pwd, key='cgv')

        with col2:
            sub_col1, sub_col2 = st.columns([1, 3])        
            sub_col1.metric('Account', '🚅')
            sub_col2.code(korail_id, language='markdown')
            sub_col1.write('')
            sub_col2.text_input('', type='password', value=korail_pwd, key='korail')

        with col3:
            sub_col1, sub_col2 = st.columns([1, 3])        
            sub_col1.metric('Account', '🍽️')
            sub_col2.code(naver_id, language='markdown')
            sub_col1.write('')
            sub_col2.text_input('', type='password', value=naver_pwd, key='naver')

        st.divider()
        col1, col2, col3 = st.columns([1, 1, 5])
        col1.metric('LR', leftright.capitalize())
        col2.metric('FB', frontback.capitalize())
        if aisle_seat:
            col3.metric('Aisle?', 'O')
        else:
            col3.metric('Aisle?', 'X')

        st.divider()
        col1, col2, _, _, _, _, col7, col8 = st.columns(8)
        if col7.button('Update Info'):
            st.session_state.page = 'update_info'
            switch_page('Login')
        if col8.button('Logout'):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.page = 'Login'
            switch_page('Login')


    elif st.session_state.page == 'update_info':
        name, age, sex, cgv_id, cgv_pwd, address, leftright, aisle_seat, frontback, korail_id, korail_pwd, naver_id, naver_pwd, password = find_user_info(st.session_state.user_id)
        
        st.title("Update Info")
        st.write("ID")
        new_user_id = st.code(st.session_state.user_id, language="markdown")
        new_password = st.text_input("Password", type="password", value=password)
        st.divider()

        col1, col2, col3 = st.columns(3)
        with col1:
            new_name = st.text_input("Your name", value=name)
            new_age = st.number_input("Your age", min_value=0, max_value=120, value=age)
            new_sex = st.selectbox("Your sex", options=["Male", "Female"], index=["Male", "Female"].index(sex))
            new_address = st.text_input("Your address", value=address)

        with col2:
            new_cgv_id = st.text_input("Your CGV ID", value=cgv_id)
            new_cgv_pwd = st.text_input("Your CGV password", type="password", value=cgv_pwd)
            new_leftright = st.selectbox("Your preferred seat in the movie theater (Left or Right)", options=['Left', 'Middle', 'Right'], index=['left', 'middle', 'right'].index(leftright.lower()))
            new_frontback = st.selectbox("Your preferred seat in the movie theater (Front or Back)", options=['Front', 'Middle', 'Back'], index=['front', 'middle', 'back'].index(frontback.lower()))
            new_aisle_seat = st.checkbox("Your preferred seat in the movie theater (Aisle seat)", value=aisle_seat)

        with col3:
            new_korail_id = st.text_input("Your Korail ID", value=korail_id)
            new_korail_pwd = st.text_input("Your Korail password", type="password", value=korail_pwd)
            new_naver_id = st.text_input("Your Naver ID", value=naver_id)
            new_naver_pwd = st.text_input("Your Naver password", type="password", value=naver_pwd)


        col1, col2, _, _, _, _, _, _, _, _ = st.columns(10)
        if col1.button('Update'):
            try:
                user_info_update(st.session_state.user_id, new_name, new_age, new_sex, new_cgv_id, new_cgv_pwd, new_address, new_leftright, new_aisle_seat, new_frontback, new_korail_id, new_korail_pwd, new_naver_id, new_naver_pwd, new_password)
            except:
                st.warning('Error in update')
            else:
                st.success('You have successfully updated information')
        if col2.button('Main'):
            switch_page('Main')

