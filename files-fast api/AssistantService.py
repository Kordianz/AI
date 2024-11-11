import sqlite3
import json
from uuid import uuid4
from datetime import datetime
import os
import faiss
import numpy as np
from OpenAIService import OpenAIService



class AssistantService:
    """ Klasa obliczająca odpowiedź na podstawie kontekstu"""
    def __init__(self):
        self.service = OpenAIService()
    def answer(self, thread):
        print(thread)
        odpowiedz = self.service.completion(thread)

        return odpowiedz
    
    def add_system_message(self, thread, relevant_context):
        base_system_m =  "Jesteś asystentem który odpowiada na pytania wykorzystując wcześniejsze rozmowy i notatki."
        new_system_m = base_system_m
        if len(relevant_context) > 0:
            new_system_m += "\nPoniżej znajduje się kontekst do odpowiedzi:\n"+relevant_context
            
        else:
            new_system_m += "\nNie dostarczono kontekstu."
        
        sm =  [{"role": "system", "content": new_system_m}] 
          
        return sm + thread 
    
    def learn(self, messages):
        system_prompt = """As an Adaptive Learning Analyzer with human-like memory tagging, your task is to scan AI-User conversations, extract key insights, and generate structured learning data. Your primary objective is to produce a JSON object containing _thoughts, keywords, content, and title based on your analysis, emphasizing memorable and useful tags.

            Core Rules:
            - Always return a valid JSON object, nothing else.
            - Analyze only the most recent AI-User exchange.
            - When the user speaks about himself, ALWAYS add a tag 'adam' to the keywords.
            - When you have existing information, skip learning and set 'content' and 'title' to null.
            - Learn from user messages unless explicitly asked to remember the conversation.
            - Provide ultra-concise self-reflection in the _thoughts field.
            - Extract memorable, specific keywords for the keywords field:
            * Use lowercase for all tags
            * Split compound concepts into individual tags (e.g., "krakow_location" becomes ["krakow", "location"])
            * Prefer specific terms over generic ones (e.g., "tesla" over "car")
            * Omit unhelpful descriptors (e.g., "black_matte" as a color)
            * Focus on key concepts, names, and unique identifiers
            * Use mnemonic techniques to create more memorable tags
            * Limit to 3-7 tags per entry
            - Rephrase user information as if it's your own knowledge in the content field
            - Set content to null if no specific, useful information needs saving.
            - Never store trivial information (e.g., chitchat, greetings).
            - Don't process document information unless explicitly requested.
            - Focus on future-relevant information, mimicking human selective attention.
            - Maintain your base behavior; this analysis doesn't override your core functionality.
            - Generate a slugified, ultra-concise title for potential filename use.

            Examples of expected behavior:

            USER: I live in Krakow, it's a beautiful city in southern Poland.
            AI: {
            "_thoughts": "User shared living location and brief description",
            "keywords": ["krakow", "poland", "city", "south"],
            "content": "The user lives in Krakow, a city in southern Poland described as beautiful",
            "title": "place-of-living"
            }

            USER: I just bought a Tesla Model S in matte black.
            AI: {
            "_thoughts": "User mentioned recent car purchase",
            "keywords": ["tesla", "model-s", "purchase"],
            "content": "The user recently bought a Tesla Model S",
            "title": "tesla-ownership"
            }

            USER: My favorite programming languages are Python and JavaScript.
            AI: {
            "_thoughts": "User expressed programming language preferences",
            "keywords": ["python", "javascript", "coding", "preferences"],
            "content": "The user's favorite programming languages are Python and JavaScript",
            "title": "programming-languages"
            }

            USER: Hey, how's it going?
            AI: {
            "_thoughts": "Generic greeting, no significant information",
            "keywords": [],
            "content": null,
            "title": null
            }

            USER: Remember this: The speed of light is approximately 299,792,458 meters per second.
            AI: {
            "_thoughts": "User shared scientific fact about light speed",
            "keywords": ["light", "speed", "physics", "science"],
            "content": "The speed of light is approximately 299,792,458 meters per second",
            "title": "speed-of-light"
            }"""
        learning_prompt = [
            {"role": "system", "content": system_prompt},
            *[msg for msg in messages if msg["role"] != "system"]
        ]

        try:
            result = self.service.completion(learning_prompt)
            memory = result

            if not memory or memory.lower() == "false":
                return None

            try:
                parsed_memory = json.loads(memory)
                title = parsed_memory.get("title")
                keywords = parsed_memory.get("keywords")
                content = parsed_memory.get("content")

                if not content:
                    return None

                return {"title": title, "keywords": keywords, "content": content}
            except json.JSONDecodeError as parse_error:
                print(f"Error parsing learn result: {parse_error}")
                return None
        except Exception as error:
            print(f"Error in learn method: {error}")
            return None
