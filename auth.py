import streamlit as st

def check_password():
    def password_entered():
        if st.session_state["username"] == "luser" and st.session_state["password"] == "6227model":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("使用者名稱", key="username")
        st.text_input("密碼", type="password", key="password", on_change=password_entered)
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("使用者名稱", key="username")
        st.text_input("密碼", type="password", key="password", on_change=password_entered)
        st.error("❌ 使用者名稱或密碼錯誤")
        return False
    else:
        return True
