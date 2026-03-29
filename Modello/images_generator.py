#Script che ho utilizzato per generare il mio dataset con le immagini 
# e con i corrispettivi label
import cv2
import numpy as np
import pandas as pd
import os
import random

IMG_SIZE = 128      # Dimensione immagine 
#IMAGES_PER_TYPE = 5000  # numero di immagini per ogni tipologia -> in tutto 20000 immagini
#OUTPUT_DIR = "dataset_training"  #contiene le immagini per il mio allenamento 
#LABEL_FILE = "labels_training.csv" #contiene i label corrispondenti alle immagini che ho generato 
IMAGES_PER_TYPE = 10 # Usate per il testing
OUTPUT_DIR = "dataset_testing" 
LABEL_FILE = "labels_testing.csv"

# Crea la cartella se non esiste
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Lista per memorizzare i dati (NomeFile, Steering, Speed) effettivi
dataset_labels = []

print(f"Inizio generazione di {IMAGES_PER_TYPE * 4} immagini:")

# funzione per disegnare 
def draw_lines(img, angle_deg, thickness, is_horizontal=False):
    """Disegna due linee bianche con angolo e spessore dati."""
    color = (255, 255, 255) # Bianco puro
    center_x, center_y = IMG_SIZE // 2, IMG_SIZE // 2
    
    if is_horizontal:
        #STOP : due linee orizzontali parallele
        offset = 15
        cv2.line(img, (20, center_y - offset), (IMG_SIZE - 20, center_y - offset), color, thickness)
        cv2.line(img, (20, center_y + offset), (IMG_SIZE - 20, center_y + offset), color, thickness)
    else:
        # Caso standard: linee verticali o inclinate
        length = 90
        dist_tra_linee = 35
        
        # Calcolo coordinate basato sulla trigonometria
        rad = np.deg2rad(angle_deg)
        dx = int(length * np.sin(rad))
        dy = int(length * np.cos(rad))
        
        # Linea 1 (Sinistra)
        x1, y1 = (center_x - dist_tra_linee) + dx, center_y - dy
        x2, y2 = (center_x - dist_tra_linee) - dx, center_y + dy
        cv2.line(img, (x1, y1), (x2, y2), color, thickness)
        
        # Linea 2 (Destra)
        x3, y3 = (center_x + dist_tra_linee) + dx, center_y - dy
        x4, y4 = (center_x + dist_tra_linee) - dx, center_y + dy
        cv2.line(img, (x3, y3), (x4, y4), color, thickness)

# Definizione dei tipi
types = [
    {'name': 'DRITTO', 'angle_base': 0, 'horiz': False},
    {'name': 'SINISTRA', 'angle_base': -35, 'horiz': False}, # Inclinazione sinistra
    {'name': 'DESTRA', 'angle_base': 35, 'horiz': False},   # Inclinazione destra
    {'name': 'STOP', 'angle_base': 0, 'horiz': True}        # Orizzontale
]

img_id = 0 

for t in types:
    print(f"Generazione tipo: {t['name']}")
    for i in range(IMAGES_PER_TYPE):
        
        # Crea sfondo colorato casuale che ho utilizzato per fare data augmentation
        bg_color = [random.randint(10, 220), random.randint(10, 220), random.randint(10, 220)]
        img = np.full((IMG_SIZE, IMG_SIZE, 3), bg_color, dtype=np.uint8)
        
        # Spessore (Mappato alla Velocità)
        thickness = random.randint(2, 14) # spessore tra 2px e 14px
        
        # Il valore target della velocità  è normalizzato tra 0.1 e 1.0
        # 0.1 come minimo invece di 0 per non far confondere il modello con lo STOP
        speed_target = np.interp(thickness, [2, 14], [0.1, 1.0])
        
        # Inclinazione (Mappato allo Steering)
        if t['horiz']:
            # Caso STOP
            angle_final = 0
            steering_target = 0.0
            speed_target = 0.0 # per lo stop ho deciso di settare la velocità a 0.0
        else:
            # Caso in cui ci deve essere un movimento
            #aggiungiamo una variazione casuale del nostro angolo per aggiungere rumore
            variation = random.uniform(-20.0, 20.0) 
            angle_final = t['angle_base'] + variation
            #normalizziamo il nostro steering a:
            #-45 -> -1 SX
            #+45 -> +1 DX
            steering_target = np.interp(angle_final, [-45, 45], [-1.0, 1.0])
        
        # Disegno effettivo delle mie linee
        draw_lines(img, angle_final, thickness, is_horizontal=t['horiz'])
        
        # salvataggio dei file come: TIPO_ID_VEL_STEER.png 
        # ho sostituito i "." con p per evitare possibili problemi con i nomi dei file 
        vel = str(round(speed_target, 2)).replace('.', 'p')
        ste = str(round(steering_target, 2)).replace('.', 'p')
        img_name = f"{t['name']}_{img_id}_v{vel}_s{ste}.png"
        
        cv2.imwrite(os.path.join(OUTPUT_DIR, img_name), img) # salvo l'img nella mia dir
        
        
        # salvo i valori effettivi nella mia lista -> nome_img, steering, speed , className
        dataset_labels.append([img_name, steering_target, speed_target, t['name']])
        img_id += 1

#salvo nel mio csv
df = pd.DataFrame(dataset_labels, columns=['file_name', 'steering_target', 'speed_target', 'type_label'])
df.to_csv(LABEL_FILE, index=False)

print(f"\nHo completato la generazione delle mie immagini")
print(f"Sono state generate {len(dataset_labels)} immagini in '{OUTPUT_DIR}'")
print(f"Il file con i miei label originali è stato salvato in '{LABEL_FILE}'")
