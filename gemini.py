import os
from google import genai
from google.genai import types
import pathlib
import httpx
import json


client = genai.Client(api_key="AIzaSyBUuHznqkOzK4yrNiqFnVsbj-EIf3Zbfco")

# Retrieve and encode the PDF byte
def upload_pdf(file):
    # Upload the PDF using the File API
    sample_file = client.files.upload(
        file=file,
    )
    return sample_file

def get_gemini_response(sample_file, query):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[sample_file, query],
        config=types.GenerateContentConfig(
            response_mime_type= 'application/json'
        )
    )
    return json.loads(response.text)


    
