import cv2
import numpy as np
import math
import random

def generate_colors(n, is_test=False):
    reserved_radius= 40.0
    colors = []
    
    center = (127.5, 127.5, 127.5)
    black = (0, 0, 0)
    white = (255, 255, 255)
    
    boundary_radius = 156.0 
    
    while len(colors) < n:
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        
        dist_to_black = math.sqrt((r - black[0])**2 + (g - black[1])**2 + (b - black[2])**2)
        dist_to_white = math.sqrt((r - white[0])**2 + (g - white[1])**2 + (b - white[2])**2)
        
        if dist_to_black < reserved_radius or dist_to_white < reserved_radius:
            continue
            
        dist_to_center = math.sqrt((r - center[0])**2 + (g - center[1])**2 + (b - center[2])**2)
        
        if is_test:
            if dist_to_center > boundary_radius:
                colors.append((r, g, b))
        else:
            if dist_to_center <= boundary_radius:
                colors.append((r, g, b))
                
    return colors

def generate_image(angle_deg, thickness, bg_color, img_size=128, line_length = 90, line_spacing = 35):
    """Disegna due linee parallele sull'immagine fornita, ruotate di un angolo specifico."""

    # 1. Definiamo i punti per due linee VERTICALI di base
    center_x, center_y = img_size // 2, img_size // 2

    # Punti per la linea di sinistra (prima della rotazione)
    p1_base = (center_x - line_spacing, center_y - line_length/2)
    p2_base = (center_x - line_spacing, center_y + line_length/2)

    # Punti per la linea di destra (prima della rotazione)
    p3_base = (center_x + line_spacing, center_y - line_length/2)
    p4_base = (center_x + line_spacing, center_y + line_length/2)

    points = [p1_base, p2_base, p3_base, p4_base]
    rotated_points = []

    # 2. Applichiamo la formula di rotazione 2D a tutti e 4 i punti
    # Converti l'angolo in radianti per le funzioni trigonometriche
    rad = np.deg2rad(angle_deg)
    sin_a = np.sin(rad)
    cos_a = np.cos(rad)

    for p_base in points:
        # Sposta il punto all'origine per la rotazione
        px, py = p_base[0] - center_x, p_base[1] - center_y
        
        # Applica la matrice di rotazione 2D
        rotated_x = px * cos_a - py * sin_a
        rotated_y = px * sin_a + py * cos_a
        
        # Riporta il punto alla sua posizione originale
        final_x = int(rotated_x + center_x)
        final_y = int(rotated_y + center_y)
        
        rotated_points.append((final_x, final_y))

    # 3. Disegna le due linee usando i punti ruotati
    img = np.zeros((img_size, img_size, 3), dtype=np.uint8) # Immagine nera di base
    img[:] = bg_color # Imposta il colore di sfondo
    white = (255, 255, 255) # Bianco puro
    cv2.line(img, rotated_points[0], rotated_points[1], white, thickness)
    cv2.line(img, rotated_points[2], rotated_points[3], white, thickness)

    return img
