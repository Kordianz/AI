import sqlite3
import json
from uuid import uuid4
from datetime import datetime
import os
import faiss
import numpy as np
import yaml
from OpenAIService import OpenAIService

# Ustawienie ścieżek do katalogów na notatki,messages embeddings i memories
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT_DIR)

EMBEDDINGS_DIR = os.path.join(ROOT_DIR, 'embeddings')
NOTATKI_DIR = os.path.join(ROOT_DIR, 'notatki')
MEMORIES_DIR = os.path.join(ROOT_DIR, 'wspomnienia')
os.makedirs(NOTATKI_DIR, exist_ok=True)
os.makedirs(EMBEDDINGS_DIR, exist_ok=True)
os.makedirs(MEMORIES_DIR, exist_ok=True)
DB_PATH = os.path.join(ROOT_DIR, 'context.db')

# Inicjalizacja instancji serwisu OpenAI
service = OpenAIService()

class ContextService:
    """Klasa zapewniająca zapis i odczyt konktestu, całych rozmów itd."""
    def __init__(self):
        self.db_path = DB_PATH
        self._initialize_db()

    def _initialize_db(self):
        # Połączenie z bazą danych i tworzenie tabeli
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    message_uuid TEXT PRIMARY KEY,
                    conversation_uuid TEXT,
                    date TEXT,
                    role TEXT,
                    content TEXT,
                    keywords TEXT
                )
            ''')
            conn.commit()

    def save_message(self, role, content,  conversation_uuid=None):
        """Zapis konwersacji do bazy danych"""
        # Generowanie UUID i daty
        id_mesage = str(uuid4())
        id_conv = conversation_uuid or str(uuid4())
        date = datetime.now().isoformat()    
        if isinstance(content, dict):
            # Jeśli content jest słownikiem, używamy klucza 'content'
            value = content.get('content', '')  # Używamy `.get()` by uniknąć błędu, gdyby klucz nie istniał
        else:
            # Jeśli content nie jest słownikiem, zakładamy, że jest tekstem
            value = content   
        # print(id_mesage, id_conv, date, role, content)
        # Zapis do bazy danych
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO conversations (message_uuid, conversation_uuid, date, role, content)
                VALUES (?, ?, ?, ?, ?)
            ''', (id_mesage, id_conv, date, role, value))
            conn.commit()
         # Metadane, które będą zapisywane razem z notatką
        metadata = {
            'uuid': id_mesage,
            'date': date,
            'role': role
    }
        index_path = os.path.join(EMBEDDINGS_DIR, 'message_faiss.index')
        metadata_path = os.path.join(EMBEDDINGS_DIR, 'message_metadata.jsonl')
        response = service.embedding(content)
        embedding = np.array(response, dtype='float32')
        embedding = embedding / np.linalg.norm(embedding)

        if os.path.exists(index_path):
            index = faiss.read_index(index_path)
        else:
            dimension = len(embedding)
            index = faiss.IndexFlatIP(dimension)    
        index.add(np.array([embedding]))
        faiss.write_index(index, index_path) 
        with open(metadata_path, 'a', encoding='utf-8') as f:
            
            f.write(json.dumps(metadata, ensure_ascii=False) + '\n')   
        return id_mesage

    
    def get_existing_messages(self, conversation_id):
         """Pobieranie wiadomosci z konwersacji"""
         print("get_existing_messages", conversation_id)
         with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT role,content FROM conversations WHERE conversation_uuid = ? order by date
            ''', (conversation_id,))
            rows = cursor.fetchall()
            if rows:
                dane = [dict(row) for row in rows]
                # print(dane)
                return dane
            return None
        
    def get_similar_messages(self, message_embedding):
        """wyszukiwanie wiadomości zapisanych w faiss"""
        top_k = 5
        
        query_embedding = np.array(message_embedding, dtype='float32')
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        
        # Ścieżki do indeksu FAISS i metadanych
        index_path = os.path.join(EMBEDDINGS_DIR, 'message_faiss.index')
        metadata_path = os.path.join(EMBEDDINGS_DIR, 'message_metadata.jsonl')
        if not os.path.exists(index_path):
            print("Indeks FAISS nie istnieje. Nie można wyszukać podobnych wiadomości.")
            return []
        index = faiss.read_index(index_path)
        D, I = index.search(np.array([query_embedding]), top_k)
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata_list = [json.loads(line) for line in f if line.strip()]
        results = []
        for idx in I[0]:
            if idx < len(metadata_list):
                meta = metadata_list[idx]
                # Pobranie wiadomości z bazy danych na podstawie `message_uuid`
                message_data = self.get_message_by_uuid(meta['uuid'])
                if message_data:
                    results.append({
                        'uuid': meta['uuid'],
                        'role': message_data['role'],
                        'content': message_data['content'],
                        'similarity': D[0][I[0].tolist().index(idx)]
                    })

        return results
    
    def get_message_by_uuid(self, message_uuid):
        """
        Pobranie wiadomości z bazy danych na podstawie `message_uuid`.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT role, content FROM conversations WHERE message_uuid = ?
            ''', (message_uuid,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None



    # Funkcja do zapisywania notatki oraz obliczania jej embeddingu
    # Notatki zapisywane są w formacie markdown wraz z metadanymi (np. datą, UUID i słowami kluczowymi)
    def save_note_and_embedding(self, content, keywords=[]):
        # Generowanie UUID dla notatki oraz aktualnej daty
        note_uuid = str(uuid4())
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
    def search_similar_notes(self,query, top_k=5):
        # Generowanie embeddingu dla zapytania
        # response = service.embedding(query)
        query_embedding = np.array(query, dtype='float32')
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
        final = []
        for note in results:
            #     print(f"Znaleziono notatkę UUID: {note['uuid']}, plik: {note['filename']}")
                with open('notatki/' + note['filename'], 'r', encoding='utf-8') as file:
                    content = file.read()
                    final.append(content)
        return final    
    
    def get_relevant_context(self, similar_messages, similar_notes):
        """pobieranie kontekstu do odpowiedzi"""
        print("--------get relevant--------------------------------")
        context = ""
        for message in similar_messages:
            print("message", message['content'])
            context+=message['content']+"\n"
        for note in similar_notes:
            note_parts = note.split('---')
            metadata = yaml.safe_load(note_parts[1].strip())        
            # Treść notatki znajduje się w trzeciej części
            content = note_parts[2].strip()
            # Pobieramy 'keywords' z metadanych
            keywords = metadata.get('keywords', [])

            # Tworzymy nowy fragment kontekstu tylko z kluczowymi słowami i treścią
            context += "Keywords: " + ", ".join(keywords) + "\n"
            context += "Content: " + content + "\n\n"
        print("context-----------------------------", context,"\n\n\n---------koniec context-----")
        return context
    
    def save_memory(self, memory, conversation_uuid):
        """
        Zapis pamięci do pliku Markdown oraz obliczanie jej embeddingu.
        """
        title = memory.get('title')
        content = memory.get('content')
        keywords = memory.get('keywords', [])

        if not content or not title:
            print("Brak wystarczających danych do zapisania pamięci.")
            return None

        memory_uuid = str(uuid4())
        date_str = datetime.now().strftime('%Y-%m-%d')
        filename = f'{date_str}_{memory_uuid}.md'
        filepath = os.path.join(MEMORIES_DIR, filename)

        # Metadane pamięci
        metadata = {
            'uuid': memory_uuid,
            'title': title,
            'date': date_str,
            'keywords': keywords,
            'conversation_uuid': conversation_uuid
        }

        # Zapis pamięci oraz metadanych do pliku Markdown
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('---\n')
            yaml.dump(metadata, f, default_flow_style=False, allow_unicode=True)
            f.write('---\n')
            f.write(content)

        # Generowanie embeddingu dla pamięci
        response = service.embedding(content)
        embedding = np.array(response, dtype='float32')
        embedding = embedding / np.linalg.norm(embedding)

        # Zapis embeddingu do indeksu FAISS
        index_path = os.path.join(EMBEDDINGS_DIR, 'memory_faiss.index')
        metadata_path = os.path.join(EMBEDDINGS_DIR, 'memory_metadata.jsonl')

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
                'uuid': memory_uuid,
                'filename': filename,
                'keywords': keywords,
                'conversation_uuid': conversation_uuid
            }
            f.write(json.dumps(json_record, ensure_ascii=False) + '\n')

        print(f'Pamięć zapisana z UUID: {memory_uuid}')
        return memory_uuid

    def get_similar_memories(self, memory_content, top_k=5):
        """
        Wyszukiwanie pamięci podobnych do przekazanego `memory_content`.
        Korzysta z FAISS oraz metadanych z plików.
        """
        # Generowanie embeddingu dla `memory_content`
        response = service.embedding(memory_content)
        query_embedding = np.array(response, dtype='float32')
        query_embedding = query_embedding / np.linalg.norm(query_embedding)

        # Ścieżki do indeksu FAISS oraz metadanych
        index_path = os.path.join(EMBEDDINGS_DIR, 'memory_faiss.index')
        metadata_path = os.path.join(EMBEDDINGS_DIR, 'memory_metadata.jsonl')

        # Sprawdzanie, czy indeks FAISS istnieje
        if not os.path.exists(index_path):
            print("Indeks FAISS nie istnieje. Nie można wyszukać podobnych pamięci.")
            return []

        # Wczytywanie indeksu FAISS
        index = faiss.read_index(index_path)

        # Przeszukiwanie indeksu FAISS, aby znaleźć embeddingi najbardziej podobne do zapytania
        D, I = index.search(np.array([query_embedding]), top_k)

        # Wczytywanie metadanych pamięci z pliku JSONL
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata_list = [json.loads(line) for line in f if line.strip()]

        # Zbieranie wyników wyszukiwania
        results = []
        for idx in I[0]:
            if idx < len(metadata_list):
                meta = metadata_list[idx]
                results.append({
                    'uuid': meta['uuid'],
                    'filename': meta['filename'],
                    'keywords': meta['keywords'],
                    'conversation_uuid': meta.get('conversation_uuid'),
                    'similarity': D[0][I[0].tolist().index(idx)]
                })

        return results
