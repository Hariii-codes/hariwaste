"""
Service for analyzing waste items using Google's Gemini AI.
"""

import os
import base64
import json
import logging
from PIL import Image
import google.generativeai as genai
from material_detection import detect_material
from gemini_formatter import format_gemini_response, extract_sections_from_raw_text, clean_text

# Configure Gemini AI
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logging.warning("GEMINI_API_KEY not found. Gemini AI features will not work.")

def analyze_waste(image_path):
    """
    Analyze waste image using Google Gemini AI and material detection
    
    Args:
        image_path: Path to the uploaded image
        
    Returns:
        Dictionary containing analysis results
    """
    try:
        # First, try the local material detection as a fallback
        material_detection_result = detect_material(image_path)
        
        # If Gemini API key is not available, return basic material detection results only
        if not GEMINI_API_KEY:
            logging.warning("Using local material detection only - Gemini API key not available")
            materials = material_detection_result.get("materials", {})
            top_material = max(materials.items(), key=lambda x: x[1])[0] if materials else "unknown"
            
            return {
                "is_recyclable": top_material in ["plastic", "paper/cardboard", "metal", "glass"],
                "is_ewaste": False,
                "material": top_material,
                "full_analysis": "Unable to perform full analysis without Gemini API key.",
                "recycling_instructions": "Basic recycling: Separate by material type.",
                "environmental_impact": "Unable to analyze environmental impact without AI service.",
                "disposal_recommendations": "Please consult local recycling guidelines.",
                "material_detection": material_detection_result
            }
        
        # Process image for Gemini
        img = Image.open(image_path)
        
        # Resize if image is too large
        max_size = 4000  # Max dimensions for Gemini
        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size))
        
        # Prepare the prompt for Gemini
        waste_prompt = """
        You are a waste management expert analyzing this image of waste.
        Analyze this image and determine:
        
        1. Is this item recyclable? (Yes/No)
        2. What material is it made of? (Plastic, Metal, Paper, Glass, etc.)
        3. Is it e-waste? (Yes/No)
        4. Provide detailed recycling instructions for this specific item.
        5. Explain the environmental impact if this item is not properly recycled.
        6. Give practical recommendations for proper disposal or alternative uses.

        Format your response with clear section headings for each point.
        If you cannot determine something with certainty, indicate this clearly.
        """
        
        # Set up the Gemini model
        model = genai.GenerativeModel(model_name="gemini-pro-vision")
        
        # Analyze the image with Gemini
        response = model.generate_content([waste_prompt, img])
        
        # Process the AI response
        ai_response = response.text
        
        # Extract sections from the raw text
        sections = extract_sections_from_raw_text(ai_response)
        
        # Get recyclability from the AI response
        is_recyclable = "yes" in sections.get("recyclable", "").lower()
        
        # Get the material type
        material = sections.get("material", "unknown").lower()
        
        # Determine if it's e-waste
        is_ewaste = "yes" in sections.get("ewaste", "").lower()
        
        # Build the complete analysis result
        result = {
            "is_recyclable": is_recyclable,
            "is_ewaste": is_ewaste,
            "material": material,
            "full_analysis": clean_text(ai_response),
            "recycling_instructions": sections.get("recycling_instructions", ""),
            "environmental_impact": sections.get("environmental_impact", ""),
            "disposal_recommendations": sections.get("disposal_recommendations", ""),
            "material_detection": material_detection_result
        }
        
        return result
        
    except Exception as e:
        logging.error(f"Error in waste analysis: {str(e)}")
        return {"error": str(e), "material_detection": material_detection_result if 'material_detection_result' in locals() else {}}