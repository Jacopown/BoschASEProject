import cv2
import numpy as np
import pandas as pd
import os
import random
import argparse
from src.utils.images_generator import generate_colors, generate_image

TYPES = [
    {'name': 'DRITTO', 'angle_range': [-5, 5]},
    {'name': 'SINISTRA', 'angle_range': [-55, -6]}, # Inclinazione sinistra
    {'name': 'DESTRA', 'angle_range': [6, 55]},   # Inclinazione destra
    {'name': 'STOP', 'angle_range': [-95, -85]}        # Orizzontale
]

def generate_dataset(dataset_size, output_dir = "../../datasetset/", is_test=False):
    output_dir = os.path.abspath(output_dir) # Ensure output_dir is an absolute path
    img_id = 0 
    images_per_type = dataset_size // len(TYPES)  # Calcola quante immagini generare per ogni tipo
    dataset_labels = []

    for t in TYPES:
        print(f"Generazione tipo: {t['name']}")
        bg_colors = generate_colors(images_per_type, is_test) # Genera colori per il training set
        for bg_color in bg_colors:
            
            # Spessore (Mappato alla Velocità)
            thickness = random.randint(2, 14) # spessore tra 2px e 14px
            
            # Il valore target della velocità  è normalizzato tra 0.1 e 1.0
            # 0.1 come minimo invece di 0 per non far confondere il modello con lo STOP
            speed_target = np.interp(thickness, [2, 14], [0.1, 1.0])
            
            lines_angle = random.uniform(t['angle_range'][0], t['angle_range'][1])

            if abs(lines_angle) > 55:
                steering_target = 0.0 # Per il tipo STOP, la velocità è sempre 0
            else:
                steering_target = np.interp(lines_angle, [-55, 55], [-1.0, 1.0])
            
            # Disegno effettivo delle mie linee
            img = generate_image(lines_angle, thickness, bg_color) # sfondo nero
            
            # salvataggio dei file come: TIPO_ID_VEL_STEER.png 
            # ho sostituito i "." con p per evitare possibili problemi con i nomi dei file 
            vel = str(round(speed_target, 2)).replace('.', 'p')
            ste = str(round(steering_target, 2)).replace('.', 'p')
            img_name = f"{t['name']}_{img_id}_v{vel}_s{ste}.png"
            
            cv2.imwrite(os.path.join(output_dir, img_name), img) # salvo l'img nella mia dir
            
            # salvo i valori effettivi nella mia lista -> nome_img, steering, speed , className
            dataset_labels.append([img_name, steering_target, speed_target, t['name']])
            img_id += 1

    #salvo nel mio csv
    df = pd.DataFrame(dataset_labels, columns=['file_name', 'steering_target', 'speed_target', 'type_label'])
    df.to_csv(os.path.join(output_dir, "labels.csv"), index=False)
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a dataset of images.')
    parser.add_argument('-s', '--dataset_size', type=int, required=True,
                        help='Total number of images to generate.')
    parser.add_argument('-o', '--output_dir', type=str, required=True,
                        help='Directory to save the dataset. Defaults to data/ folder')
    parser.add_argument('-t', '--is_test', action='store_true',
                        help='Flag to indicate if this is for testing.')
    args = parser.parse_args()

    # Ensure output_dir is an absolute path
    args.output_dir = os.path.abspath(args.output_dir)

    # Crea la cartella se non esiste
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    generate_dataset(args.dataset_size, args.output_dir, args.is_test)
