"""
This module provides functions for generating and manipulating images for the dataset.

It includes capabilities to:
- Generate random background colors, ensuring a distinction between training and test sets.
- Create a base image with two parallel white lines at a specified angle and thickness.
- Add random "salt-and-pepper" noise to an image.
- Superimpose a black stripe onto an image to simulate occlusions.
"""
import cv2
import numpy as np
import math
import random
from typing import List, Tuple

def generate_colors(n: int, is_test: bool = False) -> List[Tuple[int, int, int]]:
    """
    Generates a list of N random RGB colors, avoiding pure black and white.

    The color generation strategy depends on the `is_test` flag to ensure that
    the test dataset uses a different color distribution from the training set.
    Colors are sampled based on their distance from the center of the RGB cube.

    Args:
        n (int): The number of colors to generate.
        is_test (bool): If True, generates colors from an outer shell of the RGB color
                        space. If False, generates colors from an inner core.

    Returns:
        list: A list of N tuples, where each tuple represents an (R, G, B) color.
    """
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

def generate_image(angle_deg: float, thickness: int, bg_color: Tuple[int, int, int], img_size: int = 128, line_length: int = 90, line_spacing: int = 35) -> np.ndarray:
    """
    Generates an image containing two parallel white lines rotated at a specific angle.

    Args:
        angle_deg (float): The rotation angle of the lines in degrees.
        thickness (int): The thickness of the lines in pixels.
        bg_color (tuple): The (R, G, B) background color of the image.
        img_size (int): The height and width of the square image.
        line_length (int): The length of the lines in pixels.
        line_spacing (int): The perpendicular distance between the two lines.

    Returns:
        numpy.ndarray: The generated image as a NumPy array.
    """
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

def add_noise(image: np.ndarray, noise_percentage: float) -> np.ndarray:
    """
    Adds noise to an image by setting random pixels to black.

    Args:
        image (numpy.ndarray): The input image.
        noise_percentage (float): The percentage of pixels to turn into noise (0-100).

    Returns:
        numpy.ndarray: The image with added noise.
    
    Raises:
        ValueError: If `noise_percentage` is not between 0 and 100.
    """
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

def add_black_stripe(image: np.ndarray, width: int, angle_deg: float, position_xy: Tuple[int, int]) -> np.ndarray:
    """
    Adds a black stripe (line) over an image to simulate occlusion.

    Args:
        image (numpy.ndarray): The input image.
        width (int): The width (thickness) of the stripe in pixels.
        angle_deg (float): The angle of the stripe in degrees.
        position_xy (tuple): An (x, y) tuple defining a point that the stripe will pass through.

    Returns:
        numpy.ndarray: The image with the black stripe.
        
    Raises:
        ValueError: If the `position_xy` is outside the image bounds.
    """
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
