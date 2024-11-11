from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from openai import AzureOpenAI
import os
import faiss
import numpy as np
import uuid
from datetime import datetime
import json
import yaml
import requests
import json
from OpenAIService import OpenAIService
from ContextService import ContextService
from AssistantService import AssistantService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Starting the application")
# Ustawienie ścieżki głównego katalogu do folderu, w którym znajduje się obecny skrypt
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT_DIR)



# Inicjalizacja instancji serwisu OpenAI
service = OpenAIService()
context_service = ContextService()
assistant_service = AssistantService()

# Przykład użycia funkcji do zapisywania notatki
# note_uuid = save_note_and_embedding(
#     content="To jest treść mojej notatki o uczeniu maszynowym.",
#     keywords=["uczenie maszynowe", "sztuczna inteligencja"]
# )

# # Przykład użycia funkcji do wyszukiwania podobnych notatek
# similar_notes = search_similar_notes("Chcę dowiedzieć się o AI", top_k=3)
# for note in similar_notes:
#     print(f"Znaleziono notatkę UUID: {note['uuid']}, plik: {note['filename']}")
#     with open('notatki/' + note['filename'], 'r', encoding='utf-8') as file:
#         print('otwieram plik', file.read())
app = FastAPI(
    title="webSearch",
    description="Przepisany przykład websearch ze szkolenia AI DEVS 3",
    version="1.0.0"
)

@app.post("/chat/")
def chat(request):
    """endpoint chatu
    Przyjmuje w requeście prompt od usera i ewentualnie id konwersacji.
    """
    # print(request)
    data = json.loads(request)
    message = {"role": "user", "content": data.get("message")}
    conversation_id = data.get("conversation_id")
    thread = None 
    if conversation_id:
        existing_messages = context_service.get_existing_messages(conversation_id)
        thread = existing_messages+[message]
    else: 
        conversation_id = str(uuid.uuid4())
        thread = message
    print("--------------------------------------------------")
    print("wątek test: ", thread,"\n\n\n")
    
    if not message:
        raise HTTPException(status_code=400, detail="Brak promptu od użytkownika")
    message_embedding = service.embedding(message)
    
    similar_messages = context_service.get_similar_messages(message_embedding)
    print("--------------------------------------------------")
    
    similar_notes = context_service.search_similar_notes(message_embedding)
    print("--------------------------------------------------")
    

    relevant_context = context_service.get_relevant_context(similar_messages, similar_notes)
    print("-------------relevant context----------------")
    print(relevant_context)
    
    thread = assistant_service.add_system_message(thread, relevant_context)
    print("---------Thread-------------------------")
    print(thread)
    
    context_service.save_message('user',message,conversation_id)
    
    assistant_content = assistant_service.answer(thread)
    context_service.save_message('assistant',assistant_content,conversation_id)
    para = [{"role": "user", "content": message['content']},{"role": "assistant", "content": assistant_content}]
    memory = assistant_service.learn(para)
    
    # mem = {"messages": para,
    #        "keywords": memory.get("keywords", []) if isinstance(memory, dict) else [],
    #        "conversation_uuid": conversation_id}
    
    
    
    # saved_conversation_id = ContextService.save_conversation(mem)
    if memory:
        context_service.save_memory(memory,conversation_id)

    return {"answer": assistant_content, "conversation_id": conversation_id}


   
