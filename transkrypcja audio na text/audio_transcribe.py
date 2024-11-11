import os
from OpenAIService import OpenAIService
from pathlib import Path

class AudioTranscriptionService:
    def __init__(self):
        self.openai_service = OpenAIService()
        self.input_dir = "plikiaudio"
        self.output_dir = "transkrypcje"
        
    def ensure_directories(self):
        """Tworzy wymagane katalogi jeśli nie istnieją"""
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
    def get_output_path(self, audio_path):
        """Generuje ścieżkę do pliku wyjściowego"""
        audio_filename = Path(audio_path).stem
        return os.path.join(self.output_dir, f"{audio_filename}.txt")
        
    def transcribe_audio(self, audio_path):
        """Transkrybuje plik audio używając Azure OpenAI Whisper"""
        try:
            with open(audio_path, "rb") as audio_file:
                transcript = self.openai_service.transcribe_audio(audio_file)
                return transcript
        except Exception as e:
            print(f"Błąd podczas transkrypcji: {str(e)}")
            return None

    def process_directory(self):
        """Przetwarza wszystkie pliki audio w katalogu"""
        self.ensure_directories()
        
        # Wspierane formaty audio
        audio_extensions = {'.mp3', '.wav', '.m4a', '.ogg'}
        
        for filename in os.listdir(self.input_dir):
            if Path(filename).suffix.lower() in audio_extensions:
                audio_path = os.path.join(self.input_dir, filename)
                output_path = self.get_output_path(audio_path)
                
                # Sprawdź czy transkrypcja już istnieje
                if os.path.exists(output_path):
                    print(f"Transkrypcja dla {filename} już istnieje, pomijam...")
                    continue
                
                print(f"Transkrybuję {filename}...")
                transcript = self.transcribe_audio(audio_path)
                
                if transcript:
                    # Zapisz transkrypcję do pliku
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(transcript)
                    print(f"Zapisano transkrypcję do {output_path}")
                else:
                    print(f"Nie udało się przetworzyć {filename}")

def main():
    service = AudioTranscriptionService()
    service.process_directory()
    
    # Po przetworzeniu wszystkich plików, możemy rozpocząć rozmowę
    while True:
        print("\nCo chcesz zrobić?")
        print("1. Wyświetl dostępne transkrypcje")
        print("2. Zadaj pytanie o transkrypcję")
        print("3. Zakończ")
        
        choice = input("\nWybierz opcję (1-3): ")
        
        if choice == "1":
            transkrypcje = os.listdir(service.output_dir)
            if not transkrypcje:
                print("Brak dostępnych transkrypcji!")
                continue
                
            print("\nDostępne transkrypcje:")
            for i, filename in enumerate(transkrypcje, 1):
                print(f"{i}. {filename}")
                
        elif choice == "2":
            transkrypcje = os.listdir(service.output_dir)
            if not transkrypcje:
                print("Brak dostępnych transkrypcji!")
                continue
                
            print("\nWybierz transkrypcję:")
            for i, filename in enumerate(transkrypcje, 1):
                print(f"{i}. {filename}")
                
            try:
                file_index = int(input("\nNumer transkrypcji: ")) - 1
                if 0 <= file_index < len(transkrypcje):
                    with open(os.path.join(service.output_dir, transkrypcje[file_index]), 'r', encoding='utf-8') as f:
                        transcript = f.read()
                    
                    question = input("\nTwoje pytanie: ")
                    response = service.openai_service.chat(f"""
                    Kontekst transkrypcji:
                    {transcript}
                    
                    Pytanie użytkownika:
                    {question}
                    """)
                    print("\nOdpowiedź:")
                    print(response)
                else:
                    print("Nieprawidłowy numer transkrypcji!")
            except ValueError:
                print("Wprowadź poprawny numer!")
                
        elif choice == "3":
            break
        else:
            print("Nieprawidłowa opcja!")

if __name__ == "__main__":
    main() 