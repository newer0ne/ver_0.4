import yaml
from yaml.loader import SafeLoader
import datetime
import pandas as pd
import requests
from dotenv import load_dotenv
import os
import streamlit as st
import streamlit_authenticator as stauth
load_dotenv()


# Читаем настройки запроса
url = os.getenv('URL')
headers = {'Content-Type': 'application/json'}

st.set_page_config(
    page_title="НеНСИ", page_icon="🔍",  layout="wide"
)

def request_(text):
    response = requests.post(
        url, json=dict(text=f'{text}')
        )
    return response


# --- USER AUTHENTICTION ---

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

authenticator.login('Добро пожаловать в НеНСИ', 'main')

if st.session_state["authentication_status"]:
    authenticator.logout('Выйти из НеНСИ', 'main', key='unique_key')

    # --- Лог логирований --- 
    loginlog_username = st.session_state["username"]
    loginlog_time = datetime.datetime.now()
    formatted_time = loginlog_time.strftime("%d-%m-%Y %H:%M:%S")
    with open('login_log.txt', 'a') as file:
        file.write(f"Username: {loginlog_username} has loggined at {formatted_time}\n")
    
    # --- Заголовки ---
    st.title(':red[Не]НСИ ver. 0.3')
    st.header('Поиск узла по описанию 🔍')

    # --- Первый блок поиска ---
    query = st.text_input('''Введите описание
                        в текстовое поле ниже''')

    if not query:
        st.write('')
    else:
        with open('query_log.txt', 'a', encoding='utf-8') as file:
            file.write(f"Username: {loginlog_username} has looked: {query} at {formatted_time}\n")
        response = request_(query)
        st.subheader('Неточный поиск', divider='red')
        if response.status_code == 200:
            st.dataframe(pd.DataFrame(response.json()))
        else:
            print('Ошибка при отправке данных:', response.status_code)

    # --- Второй блок поиска ---
    st.header('Поиск узла по списку 🔍')
    uploaded_file = st.file_uploader("Добавьте Excel файл в формате .xlsx", type=["xls", "xlsx"])
    if uploaded_file is not None:
        allowed_extensions = ['.xls', '.xlsx']
        if '.' + uploaded_file.name.split('.')[-1] not in allowed_extensions:
            st.error('Ошибка: Недопустимый формат файла. Пожалуйста, загрузите файл в форматах xls или xlsx.')
        else:
            #st.write("Filename: ", uploaded_file.name)
            file = pd.read_excel(uploaded_file)
            list_cols = file[file.columns[0]].values.tolist()
            tab_variables = [st.empty() for _ in range(len(file[file.columns[0]]))]
            tab_variables = st.tabs(list_cols)
            # Добавляем прогресс-бар
            progress_bar = st.progress(0)
            # запускаем цикл наполнения таблиц по запросам к API
            for idx, value in enumerate(file[file.columns[0]].values):
                with tab_variables[idx]:
                    st.write(f"Результат неточного поиска для: {value}")
                    resposne_str = request_(value)
                    if resposne_str.status_code == 200:
                        st.dataframe(pd.DataFrame(resposne_str.json()))
                    else:
                        print('Ошибка при отправке данных:', resposne_str.status_code)

                progress_bar.progress((idx + 1) / len(list_cols))
elif st.session_state["authentication_status"] is False:
    st.error('Логин или пароль не верны, попробуйте ещё раз')
elif st.session_state["authentication_status"] is None:
    st.warning('Введите ваш логин без @rushydro.ru и пароль abc123')
    