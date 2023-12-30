import streamlit as st
import requests
import base64
import os
from PIL import Image
import hmac

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the passward is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

# Page title
st.title('🏠 Property Vision')

api_key = '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'

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

MAX_TOKENS = 200
MODEL = "gpt-4-vision-preview"

with open('example.txt', 'r') as file:
    example1 = file.read()

def send_message(text, image_files=None):
    
    next_message = {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": text
            }
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
    return response.json()["choices"][0]["message"]

def load_image(image_file):
	img = Image.open(image_file)
	return img
     
# File upload
uploadedfile = st.file_uploader('Upload an image', type='jpeg', accept_multiple_files=True)

encoded_images = []

for uploaded_file in uploadedfile:
    eimage = base64.b64encode(uploaded_file.read()).decode('utf-8')
    encoded_images.append(eimage)

# Form input and query
result = []
with st.form('myform', clear_on_submit=True):
    submitted = st.form_submit_button('Submit', disabled=not(uploadedfile))
    if submitted:
        with st.spinner('Calculating...'):
            text = (
                "You are an estate agent. I'm going to send you images of a house. Your task is to write a description "
                "of the house in 500 words or less. Explain the key elements that you see in the picture. Your "
                "tone should be positive,friendly and professional"
            )

            response = send_message(text=text, image_files=encoded_images)
            result.append(response["content"])

if len(result):
    st.info(result)

    for im in uploadedfile:
        st.image(load_image(im))

