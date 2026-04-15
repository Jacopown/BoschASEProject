"""
This script generates a dataset of images with corresponding labels for training a model
to predict steering and speed based on visual input.

The script creates images featuring two white parallel lines on a colored background.
The angle of the lines corresponds to the steering angle, and their thickness
corresponds to the speed. The generated images are categorized into different types
(e.g., 'DRITTO', 'SINISTRA', 'DESTRA', 'STOP') based on the line angle.

The output is a directory containing the generated images and a 'labels.csv' file
that maps each image to its steering target, speed target, and type.
"""
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

def generate_dataset(dataset_size: int, output_dir: str = "../../datasetset/", is_test: bool = False) -> None:
    """
    Generates a dataset of images and a corresponding labels file.

    For each image type defined in TYPES, it generates a number of images,
    calculates the steering and speed targets, and saves the image and its
    metadata.

    Args:
        dataset_size (int): The total number of images to generate for the entire dataset.
        output_dir (str): The directory where the images and 'labels.csv' will be saved.
        is_test (bool): A flag indicating whether to generate a test set. This affects
                        the background color generation to ensure test colors are distinct
                        from training colors.

    Side Effects:
        - Creates the `output_dir` if it doesn't exist.
        - Saves `dataset_size` images in the specified `output_dir`.
        - Creates a 'labels.csv' file in `output_dir` with the columns:
          'file_name', 'steering_target', 'speed_target', 'type_label'.
    """
    output_dir = os.path.abspath(output_dir)
    img_id = 0 
    images_per_type = dataset_size // len(TYPES)  # Calcola quante immagini generare per ogni tipo
    dataset_labels = []

    for t in TYPES:
        print(f"Generazione tipo: {t['name']}")
        bg_colors = generate_colors(images_per_type, is_test) # Genera colori per il training set
        for bg_color in bg_colors:
            
            thickness = random.randint(2, 14) # spessore tra 2px e 14px
            
            speed_target = np.interp(thickness, [2, 14], [0.1, 1.0])
            
            lines_angle = random.uniform(t['angle_range'][0], t['angle_range'][1])

            if abs(lines_angle) > 55:
                steering_target = 0.0 # Per il tipo STOP, la velocità è sempre 0
            else:
                steering_target = np.interp(lines_angle, [-55, 55], [-1.0, 1.0])
            
            img = generate_image(lines_angle, thickness, bg_color) # sfondo nero
            
            vel = str(round(speed_target, 2)).replace('.', 'p')
            ste = str(round(steering_target, 2)).replace('.', 'p')
            img_name = f"{t['name']}_{img_id}_v{vel}_s{ste}.png"
            
            cv2.imwrite(os.path.join(output_dir, img_name), img) # salvo l'img nella mia dir
            
            dataset_labels.append([img_name, steering_target, speed_target, t['name']])
            img_id += 1

    df = pd.DataFrame(dataset_labels, columns=['file_name', 'steering_target', 'speed_target', 'type_label'])
    df.to_csv(os.path.join(output_dir, "labels.csv"), index=False)
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a dataset of images.')
    parser.add_argument('-s', '--dataset_size', type=int, required=True,
                        help='Total number of images to generate.')
    parser.add_argument('-o', '--output_dir', type=str, required=True,
                        help='Directory to save the dataset. Defaults to dataset/ folder')
    parser.add_argument('-t', '--is_test', action='store_true',
                        help='Flag to indicate if this is for testing.')
    args = parser.parse_args()

    args.output_dir = os.path.abspath(args.output_dir)

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    generate_dataset(args.dataset_size, args.output_dir, args.is_test)
