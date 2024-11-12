

```
# Projekt: Przetwarzanie Obrazów i Generacja Opisów za pomocą Azure OpenAI

Ten projekt został stworzony w ramach nauki na kursie **AI Devs 3**. Celem jest integracja z usługą Azure OpenAI do przetwarzania obrazów oraz generowania opisów i odpowiedzi na podstawie przesłanych zdjęć.

## Opis

Repozytorium zawiera skrypt, który:
- Przetwarza obrazy, zmieniając ich rozmiar i konwertując do formatu zgodnego z Azure OpenAI.
- Korzysta z usługi Azure OpenAI do generowania opisów i odpowiadania na pytania na podstawie podanych promptów i obrazów.

## Zawartość

- **OpenAIService.py** – Moduł obsługi API Azure OpenAI. Pozwala na:
  - Generowanie odpowiedzi (tekstowych) na podstawie promptów.
  - Tworzenie embeddingów dla przesłanych danych.
  - Transkrypcję plików audio.
  
- **vision.py** – Skrypt przetwarzający obrazy oraz wysyłający zapytania do Azure OpenAI Vision. Używa klasy `OpenAIService` do uzyskania opisów obrazu na podstawie przesłanych promptów.

## Wymagania

- Python 3.x
- Azure OpenAI
- Plik `.env` z kluczami API oraz danymi konfiguracyjnymi dla Azure OpenAI.

## Instrukcja Uruchomienia

1. Skopiuj repozytorium:
   ```bash
   git clone https://github.com/twoj_login/nazwa_repozytorium.git
   ```
2. Zainstaluj wymagane biblioteki:
   ```bash
   pip install -r requirements.txt
   ```
3. Utwórz plik `.env` i dodaj klucze API dla usług Azure OpenAI.
4. Uruchom skrypt `vision.py`, aby przetworzyć obrazy i uzyskać opisy:
   ```bash
   python vision.py
   ```

## Przykłady Użycia

W folderze `images` można umieścić obrazy, które zostaną przetworzone przez skrypt. Skrypt wygeneruje opisy obrazów na podstawie przesłanych promptów.

## Uwagi

Projekt ten jest tworzony w ramach nauki i testowania integracji z usługą Azure OpenAI, więc może zawierać uproszczenia i wymaga dalszego rozwijania.

