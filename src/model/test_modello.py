import tensorflow as tf
import numpy as np
import cv2
import os

MODEL_PATH = "models/modello_bosch.h5"  # Il mio modello 
TEST_DIR = "src/data/dataset_testing"           # la mia cartella con il testing

#carico il modello 
if not os.path.exists(MODEL_PATH):
    print(f"ERRORE: Non trovo il file {MODEL_PATH}")
    exit()

model = tf.keras.models.load_model(MODEL_PATH, compile=False)
print(f"Modello {MODEL_PATH} caricato con successo!")

# Funzione per processare l'immagine (la stessa usata per l'allenamento)
def prepara_immagine(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    img = cv2.resize(img, (128, 128))
    img = img / 255.0
    img = np.expand_dims(img, axis=(0, -1)) # Formato (1, 128, 128, 1)
    return img

# Test su tutte le immagini nella cartella di test
print(f"\n{'FILE':<30} | {'STEER':<10} | {'SPEED':<10}")
print("-" * 55)

immagini_test = [f for f in os.listdir(TEST_DIR) if f.endswith('.png')]

for file_name in sorted(immagini_test):
    path = os.path.join(TEST_DIR, file_name)
    img_input = prepara_immagine(path)
    
    if img_input is not None:
        # Il modello restituisce steering e speed
        pred = model.predict(img_input, verbose=0)
        
        steer = pred[0][0][0]
        speed = pred[1][0][0]
        
        # Formattazione del mio output per leggerlo bene
        print(f"{file_name:<30} | {steer:>8.4f} | {speed:>8.4f}")

print("-" * 55)
