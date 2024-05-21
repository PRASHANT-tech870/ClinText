![WhatsApp Image 2024-05-19 at 03 36 16_a1e53e27](https://github.com/PRASHANT-tech870/ClinText/assets/56446798/cb5d34b6-8101-4d82-ae43-edff1bd73070)


<h1 style="text-align: left; font-size:50px;color: orange;">Welcome to ClinText</h1>


## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
   - [Running the Application](#running-the-application)
   - [Text Input Mode](#text-input-mode)
   - [Image Input Mode](#image-input-mode)


## Introduction

ClinText is a comprehensive tool designed to analyze medical texts, extract relevant information, and provide insights using advanced AI models. This project leverages optical character recognition (OCR) to extract text from images and integrates with OpenAI's GPT-3.5-turbo and AWS Comprehend Medical to analyze and summarize the extracted information.

## Features

- **Text and Image Input:** Users can input medical text directly or upload images containing text.
- **OCR with Tesseract:** Extracts text from images using Tesseract OCR.
- **Medical Text Analysis:** Analyzes the extracted text for medical relevance using GPT-3.5-turbo.
- **Entity Extraction:** Detects medical entities such as symptoms, diagnosis, and treatment using AWS Comprehend Medical.
- **Detailed Summaries:** Generates comprehensive summaries and additional insights based on the analysis.

## Installation

To run ClinText locally, follow these steps:

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/clintext.git
   cd clintext
2. **Create and activate a virtual environmen**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
3. **Install the required dependencies:**
   ```sh
   pip install -r requirements.txt
4. Set up Tesseract OCR:

   1. Download and install Tesseract OCR from [here](https://github.com/tesseract-ocr/tesseract).
   2. Update the pytesseract.pytesseract.tesseract_cmd variable in the script with the path to the Tesseract executable.
5. Configure OpenAI and AWS credentials:

   1. Set up your OpenAI API key.
   2. Set up your AWS credentials for Comprehend Medical.

## Usage
   **Running the Application**
   
To start the Streamlit application, run:
```sh
streamlit run app.py
```

  **Text Input Mode**
1. Click the Text button to enable text input mode.
2. Enter your medical text in the provided text area.
3. Click Submit to analyze the text.
4. View the results, including extracted entities and detailed summaries.

**Image Input Mode**
1. Click the Image button to enable image input mode.
2. Upload an image containing text.
3. Click Submit to analyze the extracted text.
4. View the results, including extracted entities and detailed summaries.

