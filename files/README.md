# FAISS Metadata Search - Przykład Implementacji

## Wprowadzenie

Ten projekt Ten projekt pokazuje, jak używać FAISS do przechowywania i przeszukiwania embeddingów,
które reprezentują notatki, oraz jak przechowywać metadane notatek w pliku JSON Lines (JSONL).
Obecna implementacja koncentruje się na podstawowej funkcjonalności,
z naciskiem na prostotę i czytelność, zamiast maksymalnej efektywności.
Jest to element mojej nauki na kursie AI DEVS, gdzie próbuję wykonać implementacje w pythonie przykładów które na kursie mamy w TypeScript.
To co tu jest to mały fragment mający na celu zrozumienie faiss i ogólnie wyszukiwania wektorowego.

## Struktura Projektu

W tej wersji projektu:
1. Generujemy **embeddingi** dla notatek za pomocą **Azure OpenAI**.
2. **Embeddingi** są zapisywane w indeksie FAISS.
3. Metadane notatek są przechowywane w pliku **JSONL**.
4. Gdy chcemy znaleźć podobne notatki, **embedding zapytania** jest porównywany z embeddingami z indeksu FAISS.
5. Indeksy zwrócone przez FAISS są używane do znalezienia odpowiednich notatek w pliku JSONL.

