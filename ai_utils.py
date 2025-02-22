import os
from openai import OpenAI
import json
import time
import logging
import ollama  # Importing Ollama for local LLM execution

# OpenAI API Key setup (only needed for fallback)
# OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
# openai = OpenAI(api_key=OPENAI_API_KEY)

# Define Ollama model name (Change this if you want another model)
OLLAMA_MODEL = "llama2"  # Options: "mistral", "llama2", "gemma", etc.

def handle_rate_limit():
    """Handle rate limit by sleeping for a short duration."""
    time.sleep(1)  # Wait for 1 second before retrying

def generate_ollama_response(prompt, system_prompt, max_tokens=512):
    """Generate response using Ollama model with fallback to OpenAI."""
    try:
        # Using Ollama to generate response
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            options={"max_tokens": max_tokens, "temperature": 0.7}
        )

        return response['message']['content'].strip()
    except Exception as e:
        logging.error(f"Ollama model failed: {str(e)}. Falling back to OpenAI.")

        # Fallback to OpenAI if Ollama fails
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Failed to generate response: {str(e)}")

def generate_caption(topic):
    try:
        system_prompt = "You are an Instagram content creator known for engaging captions. Return your response in JSON format with a 'caption' key."
        user_prompt = f"Create an engaging Instagram caption about: {topic}. Make it conversational and include emojis."

        response = generate_ollama_response(user_prompt, system_prompt)
        try:
            result = json.loads(response)
            return result['caption']
        except json.JSONDecodeError:
            return response
    except Exception as e:
        raise Exception(f"Failed to generate caption: {str(e)}")

def generate_script(topic):
    try:
        system_prompt = "You are a professional YouTube script writer. Return your response in JSON format with a 'script' key."
        user_prompt = f"Create a YouTube video script about: {topic}. Include an intro, main points, and outro."

        response = generate_ollama_response(user_prompt, system_prompt, max_tokens=1024)
        try:
            result = json.loads(response)
            return result['script']
        except json.JSONDecodeError:
            return response
    except Exception as e:
        raise Exception(f"Failed to generate script: {str(e)}")
    
def generate_hashtags(base64_image):
    """Generate 10 relevant hashtags for an image using Ollama."""
    try:
        system_prompt = "You are a social media expert. Analyze the provided image and generate 10 trending hashtags."
        user_prompt = "Generate 10 relevant hashtags for this image. Return them in JSON format as an array."

        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
                {"role": "user", "content": f"Image (base64 format): {base64_image}"}
            ],
            options={"temperature": 0.7}
        )

        try:
            result = json.loads(response['message']['content'])  # Convert response to JSON
            return result.get('hashtags', response['message']['content'])  # Return hashtags or raw text
        except json.JSONDecodeError:
            return response['message']['content']  # If JSON fails, return text
        
    except Exception as e:
        raise Exception(f"Failed to generate hashtags: {str(e)}")
