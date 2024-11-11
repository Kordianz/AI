# Nazwa Projektu: Serwis Transkrypcji Audio z Azure OpenAI

## Opis
Ten projekt to serwis do transkrypcji plików audio z wykorzystaniem Azure OpenAI. Umożliwia on przetwarzanie plików audio, generowanie ich transkrypcji oraz późniejsze zadawanie pytań dotyczących zawartości przetworzonych plików. Projekt ten jest częścią kursu **AI DEVS 3**.

Projekt jest zbudowany przy użyciu języka Python, a do interakcji z API Azure OpenAI wykorzystuje klasę `OpenAIService`. Przetwarzanie plików audio odbywa się z użyciem technologii Whisper, a gotowe transkrypcje są zapisywane lokalnie, aby umożliwić późniejsze ich przeszukiwanie i analizę.

## Funkcje
- **Transkrypcja Audio**: Automatyczne generowanie transkrypcji dla plików audio, takich jak MP3, WAV, M4A, czy OGG.
- **Zarządzanie Plikami Audio**: Przetwarzanie wszystkich plików audio znajdujących się w określonym katalogu oraz zapisywanie transkrypcji do plików tekstowych.
- **Interaktywne Pytania**: Możliwość zadawania pytań dotyczących zawartości transkrybowanych plików i uzyskiwanie odpowiedzi na podstawie kontekstu.

## Struktura Projektu
- `OpenAIService.py`: Definiuje klasę `OpenAIService`, która obsługuje interakcję z API Azure OpenAI. Klasa ta jest odpowiedzialna za generowanie embeddingów, odpowiedzi oraz transkrypcji plików audio z użyciem modelu Whisper.
- `audio_transcribe.py`: Zawiera klasę `AudioTranscriptionService`, która zarządza procesem transkrypcji plików audio. W tym pliku znajdują się funkcje do przetwarzania katalogu z plikami audio, zarządzania ścieżkami do plików oraz interaktywne przetwarzanie danych.

## Wymagane Biblioteki
- **Python 3.8+**
- **Azure OpenAI**: Integracja do generowania transkrypcji i embeddingów.
- **pathlib**: Do zarządzania ścieżkami plików.
- **dotenv**: Do ładowania zmiennych środowiskowych z pliku `.env`.

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
5. Uruchom serwis transkrypcji audio:
   ```sh
   python audio_transcribe.py
   ```

## Użycie
- **Transkrypcja Plików Audio**: Skopiuj pliki audio do katalogu `plikiaudio`. Serwis automatycznie przetworzy te pliki, tworząc transkrypcje w katalogu `transkrypcje`.
- **Interaktywne Pytania**: Po przetworzeniu wszystkich plików można używać trybu interaktywnego do zadawania pytań na temat treści transkrypcji.

## Wkład
Jeśli chcesz wnieść swój wkład do projektu, prosimy o tworzenie pull requestów lub zgłaszanie problemów w sekcji Issues. Każdy feedback jest mile widziany!

## Licencja
Ten projekt jest dostępny na licencji MIT. Szczegóły znajdują się w pliku `LICENSE`.

