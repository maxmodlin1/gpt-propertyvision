import streamlit as st
import requests
import base64
import os
from PIL import Image
import hmac
import json
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

api_key = st.secrets["api_key"]

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

MAX_TOKENS = 500
MODEL = "gpt-4-vision-preview"

def send_message(image_files=None):

    # with open('system_prompt.txt', 'r') as file:
    #     system_prompt = str(file.read().strip())

    # with open('user_prompt.txt', 'r') as file:
    #     assistant_prompt = str(file.read().strip())

    # with open('assistant_prompt.txt', 'r') as file:
    #     user_prompt = str(file.read().strip())

    system_message = {
      "role": "system",
      "content": "You are an AI assistant for a UK estate agency. Your role is to generate engaging and professional property descriptions based on the images and information provided. Your descriptions should highlight the key features of each property and appeal to potential buyers. Maintain a positive and professional tone throughout.\n"
    
    }

    assistant_message = {
    "role": "assistant",
    "content": [
        {
            "type": "text",
            "text": """
Here is a template prompt that you can use for 'gpt4-vision' to generate UK real estate property descriptions based on the images provided:

---

**Prompt for 'gpt4-vision' to Generate Real Estate Property Description:**

Dear gpt4-vision,

I am requesting you to analyze the set of images I have provided and craft a detailed UK real estate listing. Each set includes pictures of the property's exterior, interior, and any notable features or amenities. Please scrutinize all visual aspects to ensure the description is accurate and comprehensive. Follow the structure outlined below to maintain consistency and professionalism across all listings but don't call out each section explicitly.

**Required Structure for the Property Description:**

   1. Generate a captivating title that should include the property type, one standout feature, and the location but dont call out the word Title.
   2. Begin with an inviting opening that summarizes the property's appeal and its most enticing attributes.
   3. Describe the architectural style, landscaping, lot size, and any outdoor features such as pools, gardens, garages, or patios.
   4. Detail the layout, flooring types, natural light, room functions, and any high-end finishes or appliances.
            """
        }
    ]
}

    user_prompt = ("Write a property description based on the images I have sent you. The property is located in Broomhill, Glasgow and it has 2 bedrooms, 1 bathroom and is 1000 square foot.")
    
    user_message = {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": user_prompt
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
            user_message["content"].append(image_json)

    messages = [assistant_message,user_message]

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

    print("Response:", response)
    print("JSON:", response.json())
  
    r = response.json()["choices"][0]["message"]["content"]
    if r.startswith('["') and r.endswith('"]'):
        r = r[2:-2]  # Remove the first two and last two characters
    clean_text = (r.replace("{", "")
                 .replace("}", "")
                 .replace("[", "")
                 .replace("]", "")
                 .replace("\"", "")
                 .replace("\n\n", "")
                 .replace("[\"", "")
                 .replace("]\"", ""))
    return clean_text

def load_image(image_file):
	img = Image.open(image_file)
	return img

def encodeimages(uploadedfile):
    encoded_images = []
    for uploaded_file in uploadedfile:
        eimage = base64.b64encode(uploaded_file.read()).decode('utf-8')
        encoded_images.append(eimage)
        return encoded_images

# File upload
uploadedfile = st.file_uploader('Upload an image', type='jpeg', accept_multiple_files=True)
encoded_images = encodeimages(uploadedfile)

# Form input and query
result = []
with st.form('myform', clear_on_submit=True):
    submitted = st.form_submit_button('Submit', disabled=not(uploadedfile))
    if submitted:
        with st.spinner('Generating description...'):
            response = send_message(image_files=encoded_images)
            result.append(response)

if len(result):
    st.info(result)

    for im in uploadedfile:
        st.image(load_image(im))


