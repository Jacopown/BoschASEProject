import pandas as pd
import numpy as np
import cv2
import os
import tensorflow as tf
from tensorflow.keras import layers, models, Input
from sklearn.model_selection import train_test_split

IMG_SIZE = 128
CSV_PATH = "labels_training.csv"
IMG_DIR = "dataset_training"

#funzione che carica i miei file 
def load_dataset(csv_path, img_dir):
    if not os.path.exists(csv_path):
        print(f"ERRORE! Il file {csv_path} non esiste!")
        return None, None, None
    
    df = pd.read_csv(csv_path) #leggo il mio file csv 
    images = []
    steerings = []
    speeds = []
      
    for idx, row in df.iterrows():
        img_path = os.path.join(img_dir, row['file_name'])
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            continue
            
        img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
        img = img / 255.0
        img = np.expand_dims(img, axis=-1)
        
        images.append(img)
        steerings.append(row['steering_target'])
        speeds.append(row['speed_target'])

    print(f"Immagini caricate con successo: {len(images)}")
    return np.array(images), np.array(steerings), np.array(speeds)

# caricamento effettivo 
X, y_steer, y_speed = load_dataset(CSV_PATH, IMG_DIR)

if X is not None and len(X) > 0:
    # Divido in Training (80%) e Validazione (20%)
    X_train, X_val, y_s_train, y_s_val, y_v_train, y_v_val = train_test_split(
        X, y_steer, y_speed, test_size=0.2, random_state=42
    )

    #funzione con cui definisco il mio modello a "Y"
    def build_model():
        inputs = Input(shape=(IMG_SIZE, IMG_SIZE, 1))
        
        # tronco comune -> serve al modello a comprendere cosa c'è nell'immagine
        x = layers.Conv2D(24, (5, 5), strides=(2, 2), activation='relu')(inputs) #individua i bordi delle linee
        x = layers.Conv2D(36, (5, 5), strides=(2, 2), activation='relu')(x) # individua le forme e orientamento della linea
        x = layers.Conv2D(48, (5, 5), strides=(2, 2), activation='relu')(x) # individua strutture più complesse 
        x = layers.Flatten()(x)
        x = layers.Dense(100, activation='relu')(x)
        
        # testa 1 -> per lo steering
        steer_out = layers.Dense(50, activation='relu')(x) # elabora ciò che abbiamo ottenuto dal tronco comune e capisce la direzione
        steer_out = layers.Dense(1, name='steering_output')(steer_out) #restituisce in output un numero che rappresenta il nostro angolo  
        
        # testa 2 -> per la velocità
        speed_out = layers.Dense(50, activation='relu')(x) #cerca di capire lo spessore delle linee per determinare la velocità
        speed_out = layers.Dense(1, name='speed_output')(speed_out)#restituisce in output un numero che rappresenta la nostra velocità
        
        return models.Model(inputs=inputs, outputs=[steer_out, speed_out])

    model = build_model() # il mio modello vero e proprio 

    # compilazione del modello
    model.compile(
        optimizer='adam',
        loss={'steering_output': 'mse', 'speed_output': 'mse'},
        metrics={'steering_output': 'mae', 'speed_output': 'mae'}
    )

    # training del modello 
    print("\nInizio dell'allenamento reale...")
    model.fit(
        X_train, 
        {'steering_output': y_s_train, 'speed_output': y_v_train},
        validation_data=(X_val, {'steering_output': y_s_val, 'speed_output': y_v_val}),
        epochs=20, 
        batch_size=32
    )

    #salvo il mio modello 
    model.save("modello_bosch.h5")
    print("\nIl modello è stato creato e salvato con successo!")
else:
    print("Errore: Dataset non caricato. Controlla i percorsi delle immagini.")