import streamlit as st
import base64
import os
from dotenv import load_dotenv
from openai import OpenAI
import tempfile

OPENAI_API_KEY = st.secrets["openai"]["api_key"]

client = OpenAI(api_key=OPENAI_API_KEY)

sample_prompt = """You are a medical practitioner and an expert in analyzing medical-related images working for a very reputed hospital. You will be provided with images and you need to identify anomalies, diseases, or health issues. Generate the result in a detailed manner, including all findings, next steps, recommendations, etc. Respond only if the image is related to the human body and health issues. You must answer but also write a disclaimer saying, "Consult with a Doctor before making any decisions."

Remember, if certain aspects are not clear from the image, it's okay to state 'Unable to determine based on the provided image.'

Now analyze the image and answer the above questions in the same structured manner defined above."""

# Initialize session state variables
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'result' not in st.session_state:
    st.session_state.result = None

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def call_gpt4_model_for_analysis(filename: str, sample_prompt=sample_prompt):
    base64_image = encode_image(filename)
    
    messages = [
        {
            "role": "user",
            "content":[
                {
                    "type": "text", "text": sample_prompt
                    },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                        "detail": "high"
                        }
                    }
                ]
            }
        ]

    response = client.chat.completions.create(
        model = "gpt-4-vision-preview",
        messages = messages,
        max_tokens = 1500
        )

    return response.choices[0].message.content

def chat_eli(query):
    eli5_prompt = "You have to explain the below piece of information to a five years old. \n" + query
    messages = [
        {
            "role": "user",
            "content": eli5_prompt
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
        max_tokens=1500
    )

    return response.choices[0].message.content

st.title("SkinView")

with st.expander("About this App"):
    st.write("""
    Welcome to SkinView! This application leverages the power of GPT-4 to analyze medical images related to skin conditions. 
    Upload an image and receive a detailed analysis including findings, next steps, and recommendations. 
    Please consult with a doctor before making any decisions based on the analysis.
    """)

uploaded_file = st.file_uploader("Upload an Image (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])

# Temporary file handling
if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        st.session_state['filename'] = tmp_file.name

    st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)

# Process button
if st.button('Analyze Image'):
    if 'filename' in st.session_state and os.path.exists(st.session_state['filename']):
        with st.spinner('Analyzing image...'):
            st.session_state['result'] = call_gpt4_model_for_analysis(st.session_state['filename'])
        st.markdown(st.session_state['result'], unsafe_allow_html=True)
        os.unlink(st.session_state['filename'])  

# ELI5 Explanation
if 'result' in st.session_state and st.session_state['result']:
    st.info("Option to simplify the explanation.")
    if st.radio("ELI5 - Explain Like I'm 5", ('No', 'Yes')) == 'Yes':
        with st.spinner('Simplifying explanation...'):
            simplified_explanation = chat_eli(st.session_state['result'])
        st.markdown(simplified_explanation, unsafe_allow_html=True)

# Footer
st.markdown("""
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f1f1f1;
        color: black;
        text-align: center;
        padding: 10px;
    }
    </style>
    <div class="footer">
        <p>by Rajwardhan Shinde(GitHub: Fatey96).MIT License Copyright (c) 2024 Fatey96.</p>
    </div>
    """, unsafe_allow_html=True)
