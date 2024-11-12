import os
import base64
from PIL import Image, ImageOps
from io import BytesIO
from OpenAIService import OpenAIService

service = OpenAIService()
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT_DIR)
IMAGES_DIR = os.path.join(ROOT_DIR, "images")

def process_images():
    for filename in os.listdir(IMAGES_DIR):
        if not filename.startswith('resized'):
            image_path = os.path.join(IMAGES_DIR, filename)
            image = Image.open(image_path)
            image = ImageOps.contain(image, (2024, 2024))
            image.save(os.path.join(IMAGES_DIR, 'resized_' + filename))
            image_bytes = BytesIO()
            image.save(image_bytes, format='PNG')
            image_bytes.seek(0)
            base64_image = base64.b64encode(image_bytes.read()).decode('utf-8')
            return base64_image



testPrompt = [
            {
                "role": "system",
                "content": "You are a helpful assistant that can answer questions and help with tasks."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{process_images()}",
                            "detail": "high"
                        }
                    },
                    {
                        "type": "text",
                        "text": "opisz zdjęcie, rozpisz co widzisz w poszczególnych kartach. Wypisz tytułu i treść, oraz inne informacje w nich zawarte"
                    },
                ]
            }
        ];

        

print(service.vision_completion(testPrompt))


