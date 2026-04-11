#!/usr/bin/env python3
import os
import sys

# Set dummy credentials
os.environ['HF_TOKEN'] = 'dummy-token'
os.environ['API_KEY'] = 'dummy-key'

sys.path.insert(0, '.')

print("Debugging inference setup...")
print("HF_TOKEN:", os.getenv('HF_TOKEN'))
print("API_KEY:", os.getenv('API_KEY'))

try:
    from openai import OpenAI
    print("OpenAI import successful")
    
    # Try to create client
    API_BASE_URL = os.getenv("API_BASE_URL", "https://openrouter.ai/api/v1")
    MODEL_NAME = os.getenv("MODEL_NAME", "openai/gpt-oss-20b:free")
    API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY", "")
    
    print(f"API_BASE_URL: {API_BASE_URL}")
    print(f"MODEL_NAME: {MODEL_NAME}")
    print(f"API_KEY length: {len(API_KEY)}")
    
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    print("OpenAI client created successfully")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
