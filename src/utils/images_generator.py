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

    center_x, center_y = img_size // 2, img_size // 2

    p1_base = (center_x - line_spacing, center_y - line_length/2)
    p2_base = (center_x - line_spacing, center_y + line_length/2)

    p3_base = (center_x + line_spacing, center_y - line_length/2)
    p4_base = (center_x + line_spacing, center_y + line_length/2)

    points = [p1_base, p2_base, p3_base, p4_base]
    rotated_points = []

    rad = np.deg2rad(angle_deg)
    sin_a = np.sin(rad)
    cos_a = np.cos(rad)

    for p_base in points:
        px, py = p_base[0] - center_x, p_base[1] - center_y
        
        rotated_x = px * cos_a - py * sin_a
        rotated_y = px * sin_a + py * cos_a
        
        final_x = int(rotated_x + center_x)
        final_y = int(rotated_y + center_y)
        
        rotated_points.append((final_x, final_y))

    img = np.zeros((img_size, img_size, 3), dtype=np.uint8)
    img[:] = bg_color
    white = (255, 255, 255)
    cv2.line(img, rotated_points[0], rotated_points[1], white, thickness)
    cv2.line(img, rotated_points[2], rotated_points[3], white, thickness)

    return img

def add_noise(image, noise_percentage):
    if not (0 <= noise_percentage <= 100):
        raise ValueError("La percentuale di rumore deve essere compresa tra 0 e 100.")

    noisy_image = np.copy(image)
    h, w, _ = noisy_image.shape
    num_pixels = h * w
    num_noisy_pixels = int(num_pixels * (noise_percentage / 100.0))

    y_coords = np.random.randint(0, h, num_noisy_pixels)
    x_coords = np.random.randint(0, w, num_noisy_pixels)

    noisy_image[y_coords, x_coords] = (0, 0, 0)

    return noisy_image

def add_black_stripe(image, width, angle_deg, position_xy):
    striped_image = np.copy(image)
    h, w, _ = striped_image.shape
    black = (0, 0, 0)

    x, y = position_xy
    if not (0 <= x < w and 0 <= y < h):
        raise ValueError(f"La posizione (x, y) deve essere all'interno delle dimensioni dell'immagine ({w}x{h}).")

    angle_rad = np.deg2rad(angle_deg)

    length = int(max(h, w) * 1.5)
    p1_x = int(x - length * np.cos(angle_rad))
    p1_y = int(y - length * np.sin(angle_rad))
    p2_x = int(x + length * np.cos(angle_rad))
    p2_y = int(y + length * np.sin(angle_rad))

    cv2.line(striped_image, (p1_x, p1_y), (p2_x, p2_y), black, width)

    return striped_image
