# Nazwa Projektu: Adaptacyjny Asystent Czatowy z Azure OpenAI

## Opis
Ten projekt ma cel edukacyjny, w oparciu o lekcję z AI DEV 3 testuję różne możliwości zapisywania rozmów i tworzenia wspomnień przez LLM.

Ten projekt to adaptacyjny asystent czatowy zasilany przez Azure OpenAI. Celem projektu jest inteligentne generowanie odpowiedzi na pytania użytkowników, przy jednoczesnym wykorzystaniu historii wcześniejszych rozmów oraz odpowiedniego kontekstu. Asystent korzysta z embeddingów, aby zwiększyć świadomość kontekstową, przechowuje notatki, oraz zapamiętuje wcześniejsze rozmowy.

Projekt jest stworzony przy użyciu języka Python i korzysta z wielu usług, takich jak FastAPI do budowy REST API, Azure OpenAI do generowania odpowiedzi i embeddingów oraz SQLite do lokalnego przechowywania historii rozmów. W celu wyszukiwania podobieństw w zapisanych notatkach i kontekście rozmów wykorzystano również FAISS.

## Funkcje
- **Adaptacyjne Generowanie Odpowiedzi**: Wykorzystanie Azure OpenAI do generowania odpowiedzi na pytania użytkowników z uwzględnieniem kontekstu poprzednich rozmów.
- **Zarządzanie Kontekstem**: Przechowywanie rozmów użytkowników i przywoływanie odpowiednich wiadomości jako kontekst dla kolejnych interakcji.
- **Pamięć i Nauka**: Projekt umożliwia naukę na podstawie interakcji z użytkownikiem poprzez przechowywanie istotnych informacji, słów kluczowych oraz metadanych do przyszłego wykorzystania.
- **Przechowywanie Notatek**: Obsługa zapisywania notatek użytkowników oraz embeddingów związanych z nimi, co pozwala na udzielanie bardziej wzbogaconych odpowiedzi kontekstowych.

## Struktura Projektu
- `OpenAIService.py`: Definiuje klasę `OpenAIService`, która obsługuje interakcję z API Azure OpenAI. Klasa ta generuje odpowiedzi, tworzy embeddingi oraz transkrybuje pliki audio.
- `AssistantService.py`: Zawiera klasę `AssistantService`, która zarządza tworzeniem odpowiedzi w oparciu o kontekstowe prompty, analizuje rozmowy i uczy się na podstawie interakcji.
- `ContextService.py`: Implementuje klasę `ContextService`, odpowiedzialną za przechowywanie danych rozmów oraz embeddingów w bazie danych, a także za wyszukiwanie podobnych rozmów i notatek z użyciem FAISS.
- `main.py`: Główny punkt wejścia aplikacji, który definiuje endpointy FastAPI, obsługuje przychodzące żądania czatowe i zarządza cyklem życia rozmowy, w tym przywoływaniem kontekstu, zapisywaniem wiadomości oraz generowaniem odpowiedzi.

## Wymagane Biblioteki
- **Python 3.8+**
- **FastAPI**: Framework do budowania API.
- **Azure OpenAI**: Integracja do generowania odpowiedzi i embeddingów.
- **FAISS**: Biblioteka do wyszukiwania podobieństw.

## Instalacja i Uruchomienie
1. Sklonuj repozytorium na lokalną maszynę:
   ```sh
   git clone <URL repozytorium>
   ```
2. Przejdź do katalogu projektu:
   ```sh
   cd nazwa_projektu
   ```
3. Utwórz i aktywuj wirtualne środowisko:
   ```sh
   python -m venv venv
   source venv/bin/activate  # dla systemów Unix
   venv\Scripts\activate  # dla systemów Windows
   ```
4. Zainstaluj wymagane zależności:
   ```sh
   pip install -r requirements.txt
   ```
5. Uruchom aplikację:
   ```sh
   uvicorn main:app --reload
   ```
6. Aplikacja będzie dostępna pod adresem `http://127.0.0.1:8000`.

## Użycie
Aplikacja udostępnia endpoint `/chat/`, który przyjmuje zapytania użytkownika oraz, opcjonalnie, identyfikator konwersacji. Dzięki temu możliwe jest kontynuowanie wcześniejszych rozmów, przywoływanie kontekstu i generowanie bardziej trafnych odpowiedzi.

## Wkład
Jeśli chcesz wnieść swój wkład do projektu, prosimy o tworzenie pull requestów lub zgłaszanie problemów w sekcji Issues. Każdy feedback jest mile widziany!

## Licencja
Ten projekt jest dostępny na licencji MIT. Szczegóły znajdują się w pliku `LICENSE`.

