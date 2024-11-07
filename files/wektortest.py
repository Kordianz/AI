from dotenv import load_dotenv
from openai import AzureOpenAI
import os
import faiss
import numpy as np
import uuid
from datetime import datetime
import json
import yaml

# Ustawienie ścieżki głównego katalogu do folderu, w którym znajduje się obecny skrypt
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT_DIR)

# Ustawienie ścieżek do katalogów na notatki, embeddings i memories
NOTATKI_DIR = os.path.join(ROOT_DIR, 'notatki')
EMBEDDINGS_DIR = os.path.join(ROOT_DIR, 'embeddings')

os.makedirs(NOTATKI_DIR, exist_ok=True)
os.makedirs(EMBEDDINGS_DIR, exist_ok=True)


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

    # Metoda do generowania odpowiedzi na podstawie podanych promptów
    def completion(self, prompts):
        try:
            response = self.client.chat.completions.create(
                model=os.getenv("get_model"),
                messages=prompts                
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

# Inicjalizacja instancji serwisu OpenAI
service = OpenAIService()

# Funkcja do zapisywania notatki oraz obliczania jej embeddingu
# Notatki zapisywane są w formacie markdown wraz z metadanymi (np. datą, UUID i słowami kluczowymi)
def save_note_and_embedding(content, keywords=[]):
    # Generowanie UUID dla notatki oraz aktualnej daty
    note_uuid = str(uuid.uuid4())
    date_str = datetime.now().strftime('%Y-%m-%d')
    filename = f'{date_str}_{note_uuid}.md'
    filepath = os.path.join(NOTATKI_DIR, filename)
    
    # Metadane, które będą zapisywane razem z notatką
    metadata = {
        'uuid': note_uuid,
        'date': date_str,
        'keywords': keywords
    }
        
    # Zapis notatki oraz jej metadanych do pliku markdown
    with open(filepath, 'w', encoding='utf-8') as f:        
        f.write('---\n')
        yaml.dump(metadata, f, default_flow_style=False, allow_unicode=True)
        f.write('\n---\n')
        f.write(content)
    
    # Generowanie embeddingu dla notatki za pomocą usługi OpenAI
    response = service.embedding(content)
    embedding = np.array(response, dtype='float32')
    
    # Normalizacja wektora embeddingu (do długości 1)
    embedding = embedding / np.linalg.norm(embedding)
    
    # Zapis embeddingu do indeksu FAISS
    index_path = os.path.join(EMBEDDINGS_DIR, 'notatki_faiss.index')
    metadata_path = os.path.join(EMBEDDINGS_DIR, 'notatki_metadata.jsonl')
    
    # Jeśli istnieje już indeks FAISS, wczytujemy go, w przeciwnym wypadku tworzymy nowy
    if os.path.exists(index_path):
        index = faiss.read_index(index_path)
    else:
        dimension = len(embedding)
        index = faiss.IndexFlatIP(dimension)
    
    # Dodawanie nowego embeddingu do indeksu FAISS i zapis indeksu
    index.add(np.array([embedding]))
    faiss.write_index(index, index_path)
    
    # Zapis metadanych do pliku JSONL (każdy rekord w osobnej linii)
    with open(metadata_path, 'a', encoding='utf-8') as f:
        json_record = {
            'uuid': note_uuid,
            'filename': filename,
            'keywords': keywords
        }
        f.write(json.dumps(json_record, ensure_ascii=False) + '\n')
    
    print(f'Notatka zapisana z UUID: {note_uuid}')
    return note_uuid

# Funkcja do wyszukiwania podobnych notatek na podstawie zapytania
# Używa FAISS do znalezienia embeddingów najbardziej zbliżonych do zapytania
def search_similar_notes(query, top_k=5):
    # Generowanie embeddingu dla zapytania
    response = service.embedding(query)
    query_embedding = np.array(response, dtype='float32')
    query_embedding = query_embedding / np.linalg.norm(query_embedding)
    
    # Ścieżki do indeksu FAISS i metadanych
    index_path = os.path.join(EMBEDDINGS_DIR, 'notatki_faiss.index')
    metadata_path = os.path.join(EMBEDDINGS_DIR, 'notatki_metadata.jsonl')
    
    # Sprawdzanie czy indeks FAISS istnieje
    if not os.path.exists(index_path):
        print("Indeks FAISS nie istnieje.")
        return []
    
    # Wczytywanie indeksu FAISS
    index = faiss.read_index(index_path)
    
    # Przeszukiwanie indeksu FAISS, aby znaleźć embeddingi najbardziej podobne do zapytania
    D, I = index.search(np.array([query_embedding]), top_k)
    
    # Wczytywanie metadanych notatek
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata_list = [json.loads(line) for line in f if line.strip()]
    
    # Zbieranie wyników wyszukiwania
    results = []
    for idx in I[0]:
        if idx < len(metadata_list):
            meta = metadata_list[idx]
            results.append(meta)
    
    return results

# Przykład użycia funkcji do zapisywania notatki
note_uuid = save_note_and_embedding(
    content="To jest treść mojej notatki o uczeniu maszynowym.",
    keywords=["uczenie maszynowe", "sztuczna inteligencja"]
)

# Przykład użycia funkcji do wyszukiwania podobnych notatek
similar_notes = search_similar_notes("Chcę dowiedzieć się o AI", top_k=3)
for note in similar_notes:
    print(f"Znaleziono notatkę UUID: {note['uuid']}, plik: {note['filename']}")
    with open('notatki/' + note['filename'], 'r', encoding='utf-8') as file:
        print('otwieram plik', file.read())
