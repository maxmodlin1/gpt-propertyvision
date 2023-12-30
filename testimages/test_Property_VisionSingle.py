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

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

def send_message(text, image_encode=None):

    next_message = {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": text
            },
        ]
    }
    if image_encode:
        image_json = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image_encode}"
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

    # print(f'Response status code: {response.status_code}')
    # print(f'Response headers: {response.headers}')
    # print(f'Response body: {response.json()}')

    return response.json()["choices"][0]["message"]

# File upload
uploadedfile = st.file_uploader('Upload an image', type='jpeg')
# Query text

# Form input and query
result = []
with st.form('myform', clear_on_submit=True):
    openai_api_key = st.text_input('OpenAI API Key', type='password', disabled=not (uploadedfile))
    submitted = st.form_submit_button('Submit', disabled=not(uploadedfile))
    if submitted and openai_api_key.startswith('sk-'):
        with st.spinner('Calculating...'):
            text = (
                "You are an estate agent. I'm going to send you an image of a house. Your task is to write a description "
                "of the house in 50 words or less. Explain the key elements of the house that you see in the picture. Your "
                "tone should be positive and friendly"
            )

            im = encode_image(uploadedfile)
            response = send_message(text=text, image_encode=im)
            result.append(response["content"])
            del openai_api_key

if len(result):
    st.info(response)