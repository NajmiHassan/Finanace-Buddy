import os
import streamlit as st
from together import Together
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the Together client
client = Together(api_key=os.environ.get('TOGETHER_API_KEY'))

def chat_page():
    st.title("You Teacher in the Finance world")
    st.write("Ask any finance-related questions below:")
    user_question = st.text_area("Your question")
    if st.button("Submit"):
        st.write(f"Your question: {user_question}")

        # Modify the prompt to instruct the model to provide financial advice
        prompt = f"You are a financial teacher. Please answer the following question in a clear and concise manner, focusing on providing financial advice and explanations: {user_question}"

        # Call the Llama 3 model
        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3-70B-Instruct-Turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        answer = response.choices[0].message.content
        st.write(f"Answer: {answer}")
