#!/usr/bin/env python3
# AUTO-EXTRACT FROM GEMINI API
import requests
import json

GEMINI_API_KEY = "AIzaSyBqAbzJdyg7sP5tIhCddWk4Q1EEmSZSCT4"

# Prompt Gemini to recall the conversation
prompt = '''
Please provide a complete summary of our conversation in this session.
Include:
1. All tasks discussed
2. All code generated
3. All documents created
4. All data and details shared
5. Any updated information

Format as JSON with categories:
- conversations
- code_blocks
- documents
- tasks
- updated_data
'''

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
headers = {"Content-Type": "application/json"}
payload = {"contents": [{"parts": [{"text": prompt}]}]}

response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    data = response.json()
    if "candidates" in data:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        print("EXTRACTED DATA:")
        print(text)

        with open("gemini_auto_extracted.txt", "w") as f:
            f.write(text)
        print("\nSaved to: gemini_auto_extracted.txt")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
