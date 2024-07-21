import streamlit as st

def welcome_screen():
    st.title("Welcome to the Finance Teaching AI")
    st.write("This AI will help you learn about finance through interactive lessons, quizzes, and daily tips.")
    user_name = st.text_input("Enter your name to get started:")
    if st.button("Start Learning"):
        st.session_state["user_name"] = user_name
        st.session_state["page"] = "dashboard"
