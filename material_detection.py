"""
Simple material detection based on color analysis.
This module performs basic material detection using color distributions in images.
It's designed as a lightweight alternative to using heavier ML models for initial material classification.
"""

import cv2
import numpy as np
import logging
from PIL import Image

# Define material color profiles based on dominant color ranges
MATERIAL_COLOR_PROFILES = {
    "plastic": {
        "ranges": [
            # Clear plastic colors
            {"lower": [200, 200, 200], "upper": [255, 255, 255], "weight": 0.8},
            # Blue plastic colors
            {"lower": [50, 50, 100], "upper": [150, 150, 255], "weight": 0.7},
            # White plastic colors
            {"lower": [220, 220, 220], "upper": [255, 255, 255], "weight": 0.7},
        ],
        "brightness_range": [100, 250],  # Plastics tend to be bright
        "color_variance": [10, 60],  # Plastics have low to medium color variance
    },
    "paper": {
        "ranges": [
            # Brown paper colors
            {"lower": [50, 50, 20], "upper": [220, 180, 140], "weight": 0.8},
            # White paper colors
            {"lower": [200, 200, 200], "upper": [255, 255, 255], "weight": 0.9},
            # Yellowish paper colors
            {"lower": [180, 180, 100], "upper": [255, 255, 200], "weight": 0.7},
        ],
        "brightness_range": [130, 240],  # Paper tends to be moderately bright
        "color_variance": [5, 40],  # Paper has low color variance
    },
    "metal": {
        "ranges": [
            # Silver/gray metal colors
            {"lower": [100, 100, 100], "upper": [220, 220, 220], "weight": 0.9},
            # Gold/bronze metal colors
            {"lower": [100, 100, 20], "upper": [255, 220, 120], "weight": 0.7},
        ],
        "brightness_range": [80, 220],  # Metals have medium brightness
        "color_variance": [5, 30],  # Metals have low color variance
    },
    "glass": {
        "ranges": [
            # Clear glass colors
            {"lower": [220, 220, 220], "upper": [255, 255, 255], "weight": 0.8},
            # Green glass colors
            {"lower": [0, 100, 0], "upper": [100, 255, 100], "weight": 0.7},
            # Brown glass colors
            {"lower": [50, 10, 0], "upper": [180, 100, 50], "weight": 0.7},
        ],
        "brightness_range": [120, 255],  # Glass is often transparent/bright
        "color_variance": [3, 25],  # Glass has very low color variance
    },
    "fabric": {
        "ranges": [
            # Various fabric colors with wider ranges
            {"lower": [0, 0, 0], "upper": [255, 255, 255], "weight": 0.5},
        ],
        "brightness_range": [40, 220],  # Fabrics vary in brightness
        "color_variance": [40, 200],  # Fabrics have high color variance
    },
    "organic": {
        "ranges": [
            # Brown organic colors
            {"lower": [20, 10, 0], "upper": [150, 100, 50], "weight": 0.8},
            # Green organic colors
            {"lower": [0, 50, 0], "upper": [100, 200, 100], "weight": 0.9},
        ],
        "brightness_range": [20, 180],  # Organic materials tend to be darker
        "color_variance": [30, 200],  # Organic materials have high variance
    }
}

def detect_material(image_path):
    """
    Detect materials in an image based on color distribution analysis.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dictionary with detected materials and confidence scores
    """
    try:
        # Read the image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to load image at {image_path}")
        
        # Convert BGR to RGB (OpenCV uses BGR by default)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Resize for faster processing
        resized = cv2.resize(img_rgb, (300, 300))
        
        # Get image features
        brightness = np.mean(resized)
        color_variance = np.std(resized)
        
        # Get color distribution
        material_scores = {}
        
        for material, profile in MATERIAL_COLOR_PROFILES.items():
            score = 0
            
            # Brightness score
            b_min, b_max = profile["brightness_range"]
            if b_min <= brightness <= b_max:
                score += 0.3  # Weight for brightness match
            
            # Color variance score
            cv_min, cv_max = profile["color_variance"]
            if cv_min <= color_variance <= cv_max:
                score += 0.2  # Weight for variance match
            
            # Color range scores
            for color_range in profile["ranges"]:
                lower = np.array(color_range["lower"])
                upper = np.array(color_range["upper"])
                weight = color_range["weight"]
                
                # Create mask for this color range
                mask = cv2.inRange(resized, lower, upper)
                match_percentage = np.sum(mask) / mask.size
                
                score += match_percentage * weight * 5.0
            
            material_scores[material] = min(score, 1.0)  # Cap at 1.0
        
        # Sort materials by score
        sorted_materials = sorted(
            material_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Calculate percentage composition for top 3 materials
        total_score = sum(score for _, score in sorted_materials[:3]) or 1
        material_composition = {
            material: {
                "confidence": score,
                "percentage": round((score / total_score) * 100)
            }
            for material, score in sorted_materials[:3] if score > 0.1
        }
        
        primary_material = sorted_materials[0][0] if sorted_materials else "unknown"
        
        # Calculate recyclability based on material composition
        recyclable_materials = ["paper", "plastic", "glass", "metal"]
        recyclability_score = sum(
            material_composition[m]["percentage"] / 100 
            for m in material_composition if m in recyclable_materials
        )
        
        return {
            "primary_material": primary_material,
            "composition": material_composition,
            "recyclability_score": round(recyclability_score * 100),
            "analysis_method": "color_distribution",
        }
        
    except Exception as e:
        logging.error(f"Error in material detection: {str(e)}")
        return {
            "error": f"Failed to detect material: {str(e)}",
            "primary_material": "unknown",
            "composition": {},
            "recyclability_score": 0,
            "analysis_method": "failed"
        }


def extract_dominant_colors(image_path, num_colors=5):
    """
    Extract the dominant colors from an image using k-means clustering.
    
    Args:
        image_path: Path to the image file
        num_colors: Number of dominant colors to extract
        
    Returns:
        List of RGB colors in descending order of dominance
    """
    try:
        # Read image using PIL for better handling of various formats
        pil_img = Image.open(image_path)
        img = np.array(pil_img.convert('RGB'))
        
        # Reshape the image to be a list of pixels
        pixels = img.reshape(-1, 3)
        
        # Cluster the pixel intensities
        from sklearn.cluster import KMeans
        clt = KMeans(n_clusters=num_colors)
        clt.fit(pixels)
        
        # Get the colors and counts
        colors = clt.cluster_centers_.astype(int)
        labels = clt.labels_
        
        # Count labels to find frequency of each color
        counts = np.bincount(labels)
        
        # Sort colors by frequency
        sorted_idx = np.argsort(counts)[::-1]
        sorted_colors = colors[sorted_idx]
        
        return sorted_colors.tolist()
        
    except Exception as e:
        logging.error(f"Error extracting dominant colors: {str(e)}")
        return []