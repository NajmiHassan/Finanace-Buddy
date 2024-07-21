import streamlit as st
from together import Together
from typing import List, Dict
import pandas as pd
import matplotlib.pyplot as plt
import os
import re  # For regular expression matching to extract amounts

# Get API key from environment variable
api_key = os.getenv("TOGETHER_API_KEY")
if not api_key:
   st.error("TOGETHER API KEY is not set. Please set the TOGETHER_API_KEY environment variable.")
   st.stop()
   api_key = st.text_input("OpenAI API Key", type="password")
   #raise ValueError("TOGETHER API KEY environment variable not set.")

# Set up Together client
client = Together(api_key=api_key)

# Pre-defined Personal Finance Lessons
lessons = {
    "1": "Introduction to Personal Finance",
    "2": "Budgeting Basics",
    "3": "Saving for the Future",
    "4": "Managing Debt",
    "5": "Understanding Investments",
    "6": "Planning for Retirement",
    "7": "Navigating Taxes",
    "8": "Protecting Your Assets with Insurance",
    "9": "Estate Planning: Securing Your Legacy",
    "10": "Achieving Your Financial Goals"
}

# Function to generate a response from LLaMA 2
def generate_response(prompt: str, dialog: List[Dict]) -> str:
    dialog.append({"role": "user", "content": prompt})
    try:
        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3-70B-Instruct-Turbo",
            messages=dialog,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            top_k=50,
            repetition_penalty=1.1,
        )
        ai_response = response.choices[0].message.content.strip()
        dialog.append({"role": "assistant", "content": ai_response})
        return ai_response
    except Exception as e:
        return f"Error generating response: {e}"

# Function to get chapter description from LLaMA 3
def get_chapter_description(chapter):
    prompt = f"Please provide a concise description of the key topics covered in the Personal Finance chapter titled '{lessons[chapter]}'."
    return generate_response(prompt, [{"role": "system", "content": "You are a personal finance expert."}])

# Function to get subtopics for a chapter
def get_subtopics(chapter):
    prompt = f"Please provide the subtopics for the chapter titled '{lessons[chapter]}'."
    response = generate_response(prompt, [{"role": "system", "content": "You are a personal finance expert."}])
    subtopics = {str(i+1): topic for i, topic in enumerate(response.split('\n'))}
    return subtopics

# Function to display a financial dashboard
def display_dashboard(expenses):
    st.header("Financial Dashboard")

    # Prepare data for visualization
    categories = list(expenses.keys())
    amounts = list(expenses.values())

    # Display bar chart
    st.subheader("Expense Breakdown")
    expenses_df = pd.DataFrame(list(expenses.items()), columns=["Category", "Amount"])
    st.bar_chart(expenses_df.set_index("Category"))

    # Display pie chart
    st.subheader("Expense Distribution")
    fig, ax = plt.subplots()
    ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(fig)

# Main Streamlit App
st.title("Finance AI")
st.subheader("Helping You with Personal Finances")

# Sidebar for Navigation
with st.sidebar:
    st.subheader("Choose an Option")
    option = st.selectbox("", ["Monthly Budget Planner", "Personal Finance Tutor", "Test Your Knowledge", "Visualize Your Finances"])

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "question_count" not in st.session_state:
    st.session_state.question_count = 0
if "expenses" not in st.session_state:
    st.session_state.expenses = {}
if "current_chapter" not in st.session_state:
    st.session_state.current_chapter = "1"

# Display Logic for Monthly Budget Planner
if option == "Monthly Budget Planner":
    if "budget_messages" not in st.session_state:
        st.session_state.budget_messages = []
    if "budget_question_count" not in st.session_state:
        st.session_state.budget_question_count = 0
    if "expenses" not in st.session_state:
        st.session_state.expenses = {}
    if "new_budget" not in st.session_state:  
        st.session_state.new_budget = False
    if "financial_goals" not in st.session_state:
        st.session_state.financial_goals = {}

    st.subheader("Monthly Budget Planner Chatbot")

    if not st.session_state.new_budget:
        user_input = st.chat_input("Enter your monthly budget plan:")
        if user_input:
            st.session_state.new_budget = True
            st.session_state.budget_messages.append({"role": "user", "content": user_input})
            budget_plan = user_input
            response = generate_response(budget_plan, st.session_state.budget_messages)
            st.session_state.budget_messages.append({"role": "assistant", "content": response})
            st.session_state.financial_goals = response

    if st.session_state.new_budget:
        if st.session_state.budget_question_count == 0:
            st.session_state.budget_messages.append({"role": "assistant", "content": "Do you have a budget plan?"})
        else:
            st.session_state.budget_messages.append({"role": "assistant", "content": "Please share your budget plan."})
            budget_input = st.chat_input("Share your budget plan:")
            if budget_input:
                st.session_state.budget_messages.append({"role": "user", "content": budget_input})
                response = generate_response(budget_input, st.session_state.budget_messages)
                st.session_state.budget_messages.append({"role": "assistant", "content": response})
                st.session_state.financial_goals = response
                st.session_state.new_budget = True

    chat_container = st.container()
    with chat_container:
        for message in st.session_state.budget_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

elif option == "Personal Finance Tutor":
    st.subheader("Personal Finance Tutor Chatbot")

    # Initialize chat history if not already present
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Welcome message
    if not st.session_state.messages:
        st.session_state.messages.append({"role": "assistant", "content": "Welcome! Which topic related to personal finance would you like to learn about?"})

    # Display chat history in a chat-like format
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # User input for chatbot
    user_input = st.chat_input("Ask me about any topic related to personal finance:")

    if user_input:
        # Update chat history with user input
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Generate response from chatbot
        dialog_history = [{"role": "system", "content": "You are a personal finance tutor. Provide detailed, helpful responses to the user's questions."}]
        for message in st.session_state.messages:
            dialog_history.append(message)
        
        response_content = generate_response(user_input, dialog_history)
        
        # Update chat history with chatbot response
        st.session_state.messages.append({"role": "assistant", "content": response_content})

        # Clear the input field after submission
        st.session_state.user_input = ""  # Reset the user_input key in session state



# Display Logic for Test Your Knowledge
elif option == "Test Your Knowledge":
    st.subheader("Test Your Knowledge")

    # Initialize session state for quiz
    if "quiz_started" not in st.session_state:
        st.session_state.quiz_started = False
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_question" not in st.session_state:
        st.session_state.current_question = None

    # Display previous messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Start a new quiz if not already started
    if not st.session_state.quiz_started:
        # Generate and display the first question from LLaMA
        prompt = "Ask a question about personal finance. The question should be related to budgeting, saving, investing, or any other personal finance topic."
        dialog_history = [{"role": "system", "content": "You are a personal finance tutor. Ask questions to test the user's knowledge about personal finance."}]
        response_content = generate_response(prompt, dialog_history)
        
        # Update session state with the question
        st.session_state.current_question = response_content
        st.session_state.messages.append({"role": "assistant", "content": response_content})
        st.session_state.quiz_started = True

    # Handle user input for quiz answers
    user_input = st.chat_input("Your answer:")
    if user_input:
        # Update chat history with user answer
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Generate a response from LLaMA to check the user's answer
        check_prompt = f"Evaluate the following answer for the question: '{st.session_state.current_question}'. User's answer: '{user_input}'. Provide feedback and the correct answer if necessary."
        check_response = generate_response(check_prompt, [{"role": "system", "content": "You are a personal finance tutor. Evaluate the user's answer and provide feedback."}])
        
        # Update chat history with LLaMA's feedback
        st.session_state.messages.append({"role": "assistant", "content": check_response})

        # Generate and display the next question
        next_question_prompt = "Ask another question about personal finance."
        next_question_response = generate_response(next_question_prompt, [{"role": "system", "content": "You are a personal finance tutor. Continue asking questions to test the user's knowledge."}])
        
        st.session_state.current_question = next_question_response
        st.session_state.messages.append({"role": "assistant", "content": next_question_response})

 


# Display Logic for Visualize Your Finances
elif option == "Visualize Your Finances":
    st.subheader("Input Your Monthly Budget")

    # Input fields for income and expenses
    with st.form("budget_form"):
        income = st.number_input("Monthly Income:", min_value=0.0)

        # Initialize expenses if not in session state
        if "expenses" not in st.session_state:
            st.session_state.expenses = {}
            st.session_state.expenses[""] = 0.0  # Add initial empty expense

        # Add/update expenses
        expenses_to_update = st.session_state.expenses.copy()  # Create a copy to avoid iteration issues
        for i, (category, amount) in enumerate(expenses_to_update.items()):
            col1, col2 = st.columns(2)
            with col1:
                new_category = st.text_input(f"Category {i+1}:", value=category, key=f"category_{i}")
            with col2:
                new_amount = st.number_input(f"Amount {i+1}:", min_value=0.0, value=amount, key=f"amount_{i}")
            st.session_state.expenses[new_category] = new_amount  # Update in the session state

        # Add a new expense button
        if st.form_submit_button("Add Expense"):
            st.session_state.expenses[""] = 0.0  # Add a new empty expense

        # Visualize button (now within the form)
        submitted = st.form_submit_button("Visualize")

    # Visualization logic (outside the form)
    if submitted and income > 0 and st.session_state.expenses:
        # Remove empty expenses
        st.session_state.expenses = {k: v for k, v in st.session_state.expenses.items() if k.strip() and v > 0}

        # Calculate total expenses and remaining income
        total_expenses = sum(st.session_state.expenses.values())
        remaining_income = income - total_expenses

        # Create the data for the pie chart
        data = list(st.session_state.expenses.values()) + [remaining_income]
        labels = list(st.session_state.expenses.keys()) + ["Remaining"]

        # Create the pie chart
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(data, labels=labels, autopct="%1.1f%%", startangle=140)
        ax.axis("equal")

        # Display the chart
        st.pyplot(fig)

        # Display advice (if needed)
        if remaining_income < 0:
            st.warning("Warning: Your expenses exceed your income. You might want to reconsider your budget.")
        else:
            st.success(f"You have ${remaining_income:.2f} remaining this month!")


# Utility Functions
def generate_quiz(chapter, dialog):
    prompt = f"Generate a quiz with 5 questions based on the chapter titled '{lessons[chapter]}'."
    return generate_response(prompt, dialog)

def teach_topic(chapter, topic, dialog):
    prompt = f"Teach me about '{topic}' from the chapter titled '{lessons[chapter]}'."
    return generate_response(prompt, dialog)
