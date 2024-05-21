import streamlit as st
import cv2
import pytesseract
from PIL import Image
import os
import subprocess
import openai
import boto3
import re
import ast
import pandas as pd

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Initialize session state to keep track of the active input type
if 'input_type' not in st.session_state:
    st.session_state.input_type = None
if 'text_input' not in st.session_state:
    st.session_state.text_input = ""
if 'image_input' not in st.session_state:
    st.session_state.image_input = None
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = ""
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'more_info_shown' not in st.session_state:
    st.session_state.more_info_shown = False

# Define callback functions to handle button clicks
def enable_text_input():
    st.session_state.input_type = 'text'
    st.session_state.image_input = None
    st.session_state.extracted_text = ""
    st.session_state.submitted = False
    st.session_state.more_info_shown = False

def enable_image_input():
    st.session_state.input_type = 'image'
    st.session_state.text_input = ""
    st.session_state.extracted_text = ""
    st.session_state.submitted = False
    st.session_state.more_info_shown = False

# Function to extract text from image using Tesseract
def extract_text_from_image(image):
    images = Image.open(image)
    text = pytesseract.image_to_string(images)
    return text

# Display welcome note and instructions
image = Image.open(r"C:\Users\Prashant Ronad\Downloads\WhatsApp Image 2024-05-19 at 03.36.11_7664e05d.jpg")
max_size = (100, 150)  # Define the maximum size

st.image(image, use_column_width=True)
st.markdown("<h1 style='text-align: left; font-size:50px;color: orange;'>Welcome to ClinText</h1>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: left; font-size:25px;font-weight:bold; color: white;'>Choose your input form</h1>", unsafe_allow_html=True)

# Create the input box with buttons at the center
col1, col2, col3 = st.columns([3, 1, 3])

with col1:
    # Add empty space above the text input box
    st.markdown("<div style='margin-top: 100px;'></div>", unsafe_allow_html=True)
    
    if st.session_state.input_type == 'text':
        st.session_state.text_input = st.text_area('Enter text here:', value=st.session_state.text_input, height=150)
    elif st.session_state.input_type == 'image':
        st.session_state.image_input = st.file_uploader('Upload an image:', type=['jpg', 'png', 'jpeg'])
    
    # Add empty space below the text input box
    st.markdown("<div style='margin-bottom: 100px;'></div>", unsafe_allow_html=True)

with col2:
    text_button = st.button('Text', on_click=enable_text_input)

with col3:
    image_button = st.button('Image', on_click=enable_image_input)

# Process the uploaded image and extract text if an image is uploaded
if st.session_state.input_type == 'image' and st.session_state.image_input:
    st.session_state.extracted_text = extract_text_from_image(st.session_state.image_input)

text = ""
# Display the current input or the extracted text
if st.session_state.input_type == 'text' and st.session_state.text_input:
    st.write('Text input:')
    text = st.session_state.text_input
    st.write(text)
elif st.session_state.input_type == 'image' and st.session_state.extracted_text:
    st.write('Extracted text from image:')

    text = st.session_state.extracted_text
    st.write(text)

# Submit button
if st.session_state.input_type:
    if st.button('Submit'):
        st.session_state.submitted = True
        st.session_state.more_info_shown = False  # Reset more info shown state

        api_key = "Your-gpt-api-key"
        openai.api_key = api_key

        # Create a prompt for GPT-3.5-turbo to analyze the text
        prompt = (
            f"Given the following medical text, determine if there is enough medically relevant information to proceed with analysis. "
            f"If the information is sufficient, respond with 'sufficient information for analysis'. "
            f"If not, respond with 'not enough information'.\n\n"
            f"Text:\n{text}"
        )

        # Call GPT API to analyze the text
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a medical assistant skilled in analyzing medical texts for relevance and completeness."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract the generated text from the response
        analysis_result = response.choices[0].message.content

        # Function to mask sensitive information
        def mask_sensitive_info(text):
            text = re.sub(r'\b[A-Z][a-z]*\b', '[NAME]', text)
            text = re.sub(r'\b\d{1,2}/\d{1,2}/\d{2,4}\b', '[DATE]', text)
            text = re.sub(r'\b\d{1,2}-\d{1,2}-\d{2,4}\b', '[DATE]', text)
            return text

        # Define the prompt to extract medical concepts
        masked_text = mask_sensitive_info(text)
        prompt = f"Extract symptoms, diagnosis, and treatment from the following medical record:\n\n{masked_text}\n\nFormat: {{'symptoms': [], 'diagnosis': [], 'treatment':[]}}"

        # Call ChatGPT
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant specialized in the medical domain."},
                {"role": "user", "content": prompt}
            ]
        )

        # Return the generated text
        generated_entities = ast.literal_eval(completion.choices[0].message.content)

        def detect_entities(text):
            # Initialize the Comprehend Medical client
            client = boto3.client(
                service_name='comprehendmedical',
                region_name='us-east-1',
                aws_access_key_id='your-access-key',
                aws_secret_access_key='your-secrect-access-key'
            )

            # Detect entities in the provided text
            result = client.detect_entities(Text=text)

            # Extract the entities from the result
            entities = result['Entities']

            # Return the detected entities
            return entities

        # Example usage
        entities = detect_entities(text)
        filtered_entities = [{'Text': item['Text'], 'Traits': item['Traits'], 'Score': item['Score']} for item in entities if item['Traits']]

        # Create a prompt for GPT API
        def generate_prompt(gpt_response, comprehend_medical_response):
            # Format the responses into strings
            gpt_str = f"GPT response:\nSymptoms: {', '.join(gpt_response['symptoms'])}\nDiagnosis: {', '.join(gpt_response['diagnosis'])}\nTreatment: {', '.join(gpt_response['treatment'])}\n"
            comprehend_str = "Comprehend Medical response:\n" + "\n".join(
                [f"Text: {item['Text']}, Traits: {', '.join([trait['Name'] for trait in item['Traits']])}, Score: {item['Score']:.2f}" for item in comprehend_medical_response]
            )

            # Combine the formatted responses into a prompt
            prompt = (
                f"{gpt_str}\n{comprehend_str}\n\n"
                "Based on the above responses from GPT and Comprehend Medical, provide a final description of the patient's symptoms, diagnosis, and treatment."
            )

            return prompt

        # Generate the prompt
        prompt = generate_prompt(generated_entities, filtered_entities)

        # Call GPT API to generate a final summary
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a medical assistant skilled in summarizing complex medical information."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract the generated text from the response
        final_summary = response.choices[0].message.content

        prompt = (
            f"Convert the following final_summary to a dictionary which contains key value pairs of symptoms, diagnosis, and treatment each in list"
            f"final summary:\n{final_summary}"
        )

        # Call GPT API to analyze the text
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a medical assistant skilled in analyzing medical texts for relevance and completeness."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract the generated text from the response
        data = ast.literal_eval(response.choices[0].message.content)

        # Determine the maximum length of the lists
        max_length = max(len(data["symptoms"]), len(data["diagnosis"]), len(data["treatment"]))

        # Extend the lists to ensure they all have the same length
        symptoms = data["symptoms"] + [""] * (max_length - len(data["symptoms"]))
        diagnosis = data["diagnosis"] + [""] * (max_length - len(data["diagnosis"]))
        treatment = data["treatment"] + [""] * (max_length - len(data["treatment"]))

        # Create DataFrame
        df = pd.DataFrame({
            "Symptoms": symptoms,
            "Diagnosis": diagnosis,
            "Treatment": treatment
        })

        # Display results
        st.write(analysis_result)
        st.write(final_summary)
        st.dataframe(df)

    # Display the "More Info" button only after submission
    if st.session_state.submitted:
        if st.button('More Info'):
            st.session_state.more_info_shown = True
            prompt = (
                f"If the age is not availble in text print give the age and other info for more info"
                f"If the age is given analyze the text, according to the age identify percentage of danger, lethality and spreading...give percentages mandatorily even though they arent accurate"
                f"Dont reveal the age or any personal info in your response"
                f"Text:\n{text}"
                )

            # Call GPT API to analyze the text
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a medical assistant skilled in analyzing medical texts for relevance and completeness."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract the generated text from the response
            analysis_result_2 = response.choices[0].message.content

            st.write(analysis_result_2)
