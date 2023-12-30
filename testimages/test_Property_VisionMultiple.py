import streamlit as st
import requests
import base64
import os

# Page title
st.set_page_config(page_title='🦜🔗 Property Vision App')
st.title('🏠🔗 Property Vision')

api_key = os.environ.get('OPENAI_API_KEY')

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

MAX_TOKENS = 200
MODEL = "gpt-4-vision-preview"


def send_message(text, image_files=None):
    
    next_message = {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": text
            },
        ]
    }

    if image_files:
        for encoded_image in encoded_images:
            image_json = {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{encoded_image}"
                }
            }
            next_message["content"].append(image_json)

    messages = [next_message]

    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": MAX_TOKENS
    }
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload
    )
    response_content = response.json()["choices"][0]["message"]["content"]
    cleaned_content = response_content.replace('\n\n', ' ').replace('[', '').replace(']', '')
    return cleaned_content

# File upload
uploadedfile = st.file_uploader('Upload an image', type='jpeg', accept_multiple_files=True)

encoded_images = []

for uploaded_file in uploadedfile:
    eimage = base64.b64encode(uploaded_file.read()).decode('utf-8')
    encoded_images.append(eimage)

# Form input and query
result = []
with st.form('myform', clear_on_submit=True):
    openai_api_key = st.text_input('OpenAI API Key', type='password', disabled=not (uploadedfile))
    submitted = st.form_submit_button('Submit', disabled=not(uploadedfile))
    if submitted and openai_api_key.startswith('sk-'):
        with st.spinner('Calculating...'):
            text = (
                "You are an estate agent. I'm going to send you multiple images of a property. Your task is to write a description for the marketing campaign"
                "in 500 words or less. Explain the key elements of the property that you see in the pictures. Your "
                "tone should be positive and friendly"
            )

            response = send_message(text=text, image_files=encoded_images)
            result.append(response["content"])
            del openai_api_key

if len(result):
    st.info(response)