#importing required libraries
import streamlit as st
import google.generativeai as genai

# Read API key from the file
#with open("/content/Key.txt", "r") as f:
#    key = f.read().strip()  # ✅ Using .strip() to remove any unwanted spaces/newlines

f = open("/content/Key.txt")
key = f.read()
genai.configure(api_key=key)


# Define system prompt for AI model
system_prompt = """
You are an AI Python Tutor. Check the provided code. If it's correct, say, 'The code is correct.'
If there's a bug, provide a bug report and fixed code.
"""

# Initialize AI model
model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=system_prompt)

# Streamlit UI layout
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.image("/content/PyCode4.jpg", width=100)

st.title("🔍 PyCode Reviewer")
st.markdown(
    "<h3 style='font-size:18px; color: #333; text-align:center;'>Submit your Python code for review and receive detailed feedback.</h3>",
    unsafe_allow_html=True
)

# Sidebar for instructions
st.sidebar.title("📋 Instructions")
st.sidebar.write(
    """
    1. Paste your Python code into the editor below.
    2. Click the "Review Code" button to analyze your code.
    3. Receive detailed feedback, bug identification, and suggested fixes.
    """
)

# Custom Styling
st.markdown(
    """
    <style>
    .stTextArea textarea {
        background-color: #f0f0f0;
        color: black;
        border: 1px solid #ccc;
    }
    .stButton>button {
        background-color: #80b3ff;
        color: black;
        border: none;
    }
    .stButton > button:active {
        background-color: #ff6666;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Text area for user input
user_prompt = st.text_area("Enter your code", placeholder="Type your code here")

# Button to review code
btn_click = st.button("Review Code")

if btn_click:
    if user_prompt.strip():
        try:
            response = model.generate_content(user_prompt)
            if response and hasattr(response, 'text'):
                st.write(response.text)  # Display AI response
            else:
                st.warning("No response received.")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please enter some code before reviewing!")
