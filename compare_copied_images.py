from PIL import Image
import hashlib
from pathlib import Path

main_path = Path("/Users/quintenmeijboom/Documents")
dory_original = main_path / "Loes_dory.jpeg"
dory_copy = main_path / "Temp/Loes_dory.jpeg"


def image_pixel_hash(image_path: str) -> str:
    with Image.open(image_path) as img:
        # Converteer de afbeelding naar een consistent formaat, bijvoorbeeld RGB
        img_converted = img.convert("RGB")
        # Verkrijg de ruwe pixeldata
        pixel_bytes = img_converted.tobytes()
        # Maak een SHA256 hash van de pixeldata
        return hashlib.sha256(pixel_bytes).hexdigest()


if dory_original.exists() and dory_copy.exists():
    # Voorbeeld van gebruik:
    hash1 = image_pixel_hash(str(dory_original))
    hash2 = image_pixel_hash(str(dory_copy))

    if hash1 == hash2:
        print("De pixeldata zijn identiek.")
    else:
        print("De pixeldata verschillen.")
