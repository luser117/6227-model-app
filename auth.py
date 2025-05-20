import streamlit as st

def check_login():
    st.sidebar.title("登入驗證")
    username = st.sidebar.text_input("使用者名稱")
    password = st.sidebar.text_input("密碼", type="password")

    if username == "luser" and password == "6227model":
        return True
    elif username and password:
        st.sidebar.error("帳號或密碼錯誤")

    return False
