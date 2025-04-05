"""
Simple material detection based on color analysis.
This module performs basic material detection using color distributions in images.
It's designed as a lightweight alternative to using heavier ML models for initial material classification.
"""

import cv2
import numpy as np
from collections import Counter
import logging

def detect_material(image_path):
    """
    Detect materials in an image based on color distribution analysis.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dictionary with detected materials and confidence scores
    """
    try:
        # Extract dominant colors
        dominant_colors = extract_dominant_colors(image_path)
        
        # Simple mapping of color characteristics to materials
        materials = {}
        
        # Check for clear, translucent plastic (light colors)
        light_colors = sum(1 for color in dominant_colors if sum(color) > 600)
        if light_colors >= 2:
            materials["plastic"] = min(0.7, light_colors * 0.2)
        
        # Check for dark plastics
        dark_colors = sum(1 for color in dominant_colors if sum(color) < 300)
        if dark_colors >= 2:
            materials["plastic"] = max(materials.get("plastic", 0), min(0.6, dark_colors * 0.15))
        
        # Check for cardboard/paper (browns)
        browns = sum(1 for color in dominant_colors if 
                    color[0] < 100 and color[1] < 120 and color[2] < 150 and 
                    color[0] > 40 and color[1] > 50)
        if browns >= 1:
            materials["paper/cardboard"] = min(0.75, browns * 0.25)
        
        # Check for metals (grays and silvers)
        grays = sum(1 for color in dominant_colors if 
                   abs(color[0] - color[1]) < 20 and 
                   abs(color[1] - color[2]) < 20 and
                   abs(color[0] - color[2]) < 20 and
                   color[0] > 50 and color[0] < 200)
        if grays >= 2:
            materials["metal"] = min(0.8, grays * 0.2)
        
        # Check for glass (clear colors with some reflections)
        glass_like = sum(1 for color in dominant_colors if 
                        sum(color) > 550 and 
                        max(color) - min(color) < 30)
        if glass_like >= 2:
            materials["glass"] = min(0.65, glass_like * 0.2)
        
        # If nothing detected, provide a fallback
        if not materials:
            materials["unknown"] = 0.4
            materials["mixed materials"] = 0.3
        
        # Sort by confidence and normalize
        result = {
            "materials": materials,
            "dominant_colors": [color.tolist() for color in dominant_colors]
        }
        
        return result
        
    except Exception as e:
        logging.error(f"Error in material detection: {str(e)}")
        return {"materials": {"unknown": 0.5}, "error": str(e)}


def extract_dominant_colors(image_path, num_colors=5):
    """
    Extract the dominant colors from an image using k-means clustering.
    
    Args:
        image_path: Path to the image file
        num_colors: Number of dominant colors to extract
        
    Returns:
        List of RGB colors in descending order of dominance
    """
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image from {image_path}")
    
    # Convert to RGB (from BGR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Reshape into a list of pixels
    pixels = image.reshape(-1, 3).astype(np.float32)
    
    # Use k-means to find dominant colors
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
    _, labels, centers = cv2.kmeans(
        pixels, 
        num_colors, 
        None,
        criteria, 
        10, 
        cv2.KMEANS_RANDOM_CENTERS
    )
    
    # Count the occurrences of each label
    count = Counter(labels.flatten())
    
    # Sort centers by frequency of occurrence
    sorted_colors = [centers[i] for i, _ in count.most_common(num_colors)]
    
    return sorted_colors