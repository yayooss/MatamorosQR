import json
import os

FILE = "buffer.json"

def guardar_json(buffer):
    data = {k: list(v) for k, v in buffer.items()}

    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)

def cargar_json():
    if not os.path.exists(FILE):
        return {}

    with open(FILE, "r") as f:
        return json.load(f)
