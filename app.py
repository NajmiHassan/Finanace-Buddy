# app.py
import streamlit as st
from welcome import welcome_screen
from dashboard import chat_page
from quizzes import generate_quiz



# Main function to control the page navigation
def main():
    if "page" not in st.session_state:
        st.session_state["page"] = "welcome"

    # Sidebar for navigation
    with st.sidebar:
        if st.session_state["page"] != "welcome":
            if st.button("Dashboard"):
                st.session_state["page"] = "dashboard"
            if st.button("Quizzes"):
                st.session_state["page"] = "quizzes"

    if st.session_state["page"] == "welcome":
        welcome_screen()
    elif st.session_state["page"] == "dashboard":
        chat_page()
    elif st.session_state["page"] == "quizzes":
        generate_quiz()
    

if __name__ == "__main__":
    main()
