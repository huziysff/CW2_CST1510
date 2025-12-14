import os
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

load_dotenv()

class AIAssistant:
    def __init__(self):
        try:
            api_key = os.getenv("GROQ_API_KEY")
            
            if not api_key:
                self.client = None
                print("Error: GROQ_API_KEY not found in .env file")
                return

            self.client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=api_key
            )
        except Exception as e:
            print(f"Client Init Error: {e}")
            self.client = None

    def get_response(self, system_role, user_prompt, chat_history):
        """
        Sends the conversation to the AI and yields the response stream.
        """
        if not self.client:
            yield "Error: API Client failed to initialize. Check your .env file."
            return

        messages = [{"role": "system", "content": system_role}] + chat_history + [{"role": "user", "content": user_prompt}]

        try:
            stream = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Connection Error: {e}"