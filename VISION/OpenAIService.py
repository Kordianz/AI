from openai import AzureOpenAI
from dotenv import load_dotenv
import os


# Ładowanie zmiennych środowiskowych z pliku .env
load_dotenv()

# Klasa do obsługi usługi OpenAI, której używamy do generowania odpowiedzi i embeddingów

class OpenAIService:
    def __init__(self):
        # Inicjalizacja klienta Azure OpenAI z kluczami API i innymi ustawieniami
        self.client = AzureOpenAI(
                        api_key=os.getenv("get_oai_key"),  # Pobranie klucza API ze zmiennych środowiskowych
                        api_version="2024-02-15-preview",
                        azure_endpoint=os.getenv("get_oai_base")  # Pobranie adresu endpointu z pliku .env
                        )
        self.audioclient = AzureOpenAI(
                        api_key=os.getenv("get_oai_keyaudio"),  # Pobranie klucza API ze zmiennych środowiskowych
                        api_version="2024-06-01",
                        azure_endpoint=os.getenv("get_oai_baseaudio")  # Pobranie adresu endpointu z pliku .env
                        )
        self.visionclient = AzureOpenAI(
                        api_key=os.getenv("get_vision_key"),  # Pobranie klucza API ze zmiennych środowiskowych
                        api_version="2024-06-01",
                        azure_endpoint=os.getenv("get_vision_base")  # Pobranie adresu endpointu z pliku .env
                        )

    # Metoda do generowania odpowiedzi na podstawie podanych promptów
    def completion(self, prompts):
        # print("\n\n prompt:", prompts)
        try:
            response = self.client.chat.completions.create(
                model=os.getenv("get_model"),
                messages=prompts                
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print("Error in OpenAI completion:", e)
            raise e
    def vision_completion(self, prompts):
        # print("\n\n prompt:", prompts)
        try:
            response = self.visionclient.chat.completions.create(
                model=os.getenv("get_vision_model"),
                messages=prompts,
                max_tokens=4000                
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print("Error in OpenAI completion:", e)
            raise e
    # Metoda do tworzenia embeddingów dla podanych danych (np. notatki)
    def embedding(self, data):
        try:
            response = self.client.embeddings.create(
                input=data,
                model=os.getenv("get_embed_model")
            )
            return response.data[0].embedding
        except Exception as e:
            print("Error in OpenAI completion:", e)
            raise e
        
    def transcribe_audio(self, audio_file):
        """Transkrybuje plik audio używając Azure OpenAI Whisper"""
        try:
            response = self.audioclient.audio.transcriptions.create(
                model=os.getenv("get_modelaudio"),
                file=audio_file,
                response_format="text"
            )
            return response
        except Exception as e:
            print(f"Błąd podczas transkrypcji: {str(e)}")
            return None     