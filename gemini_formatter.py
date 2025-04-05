"""
Format and clean Gemini AI output for better display in the application.
This module removes HTML tags, numbering, and other formatting that
makes the AI output less readable in the UI.
"""

import re
import logging

def clean_text(text):
    """
    Remove HTML tags and clean text for better readability
    
    Args:
        text: Text string that might contain HTML tags
        
    Returns:
        Clean text without HTML tags
    """
    # Remove HTML tags
    clean = re.sub(r'<[^>]*>', '', text)
    
    # Remove extra whitespace
    clean = re.sub(r'\s+', ' ', clean).strip()
    
    # Convert Markdown-style headers to plain headers
    clean = re.sub(r'#{1,6}\s+([^\n]+)', r'\1:', clean)
    
    return clean

def format_gemini_response(response_dict):
    """
    Format the response from Gemini AI to clean up sections
    and remove unwanted elements.
    
    Args:
        response_dict: Dictionary containing the Gemini AI response
        
    Returns:
        Updated dictionary with cleaned and formatted text
    """
    try:
        # Clean up the full analysis text
        if "full_analysis" in response_dict:
            response_dict["full_analysis"] = clean_text(response_dict["full_analysis"])
        
        # Clean up other text fields
        for field in ["recycling_instructions", "environmental_impact", "disposal_recommendations"]:
            if field in response_dict:
                response_dict[field] = clean_text(response_dict[field])
        
        return response_dict
    
    except Exception as e:
        logging.error(f"Error formatting Gemini response: {str(e)}")
        return response_dict  # Return original if formatting fails

def extract_sections_from_raw_text(raw_text):
    """
    Extract different sections from a single raw text response.
    Useful when Gemini returns a single block of text that needs
    to be split into appropriate sections.
    
    Args:
        raw_text: The full text response from Gemini
        
    Returns:
        Dictionary with extracted sections
    """
    sections = {}
    
    # Extract recyclability information (Point 1)
    recyclable_match = re.search(r'(?:1\.?|Is this item recyclable\??)[^\n]*?(Yes|No)', raw_text, re.IGNORECASE)
    if recyclable_match:
        sections["recyclable"] = recyclable_match.group(1)
    
    # Extract material information (Point 2)
    material_match = re.search(r'(?:2\.?|What material is it made of\??)[^\n]*?(Plastic|Metal|Paper|Glass|Wood|Fabric|Textile|Rubber|Ceramic|Mixed|Unknown|Composite)', raw_text, re.IGNORECASE)
    if material_match:
        sections["material"] = material_match.group(1)
    else:
        # Try a more general pattern if specific materials aren't found
        material_match = re.search(r'(?:2\.?|What material is it made of\??)[^\n]*?:?\s*([^\.,:;\n]+)', raw_text, re.IGNORECASE)
        if material_match:
            sections["material"] = material_match.group(1).strip()
    
    # Extract e-waste information (Point 3)
    ewaste_match = re.search(r'(?:3\.?|Is it e-waste\??)[^\n]*?(Yes|No)', raw_text, re.IGNORECASE)
    if ewaste_match:
        sections["ewaste"] = ewaste_match.group(1)
    
    # Extract recycling instructions (Point 4)
    recycling_match = re.search(r'(?:4\.?|Recycling Instructions:?|Provide detailed recycling instructions)[^\n]*?\n(.*?)(?:\n\s*[5-6]\.|\n\s*Environmental Impact|\n\s*Recommendations|\Z)', raw_text, re.DOTALL | re.IGNORECASE)
    if recycling_match:
        sections["recycling_instructions"] = recycling_match.group(1).strip()
    
    # Extract environmental impact (Point 5)
    impact_match = re.search(r'(?:5\.?|Environmental Impact:?|Explain the environmental impact)[^\n]*?\n(.*?)(?:\n\s*6\.|\n\s*Recommendations|\Z)', raw_text, re.DOTALL | re.IGNORECASE)
    if impact_match:
        sections["environmental_impact"] = impact_match.group(1).strip()
    
    # Extract disposal recommendations (Point 6)
    recommendations_match = re.search(r'(?:6\.?|Recommendations:?|Give practical recommendations)[^\n]*?\n(.*?)(?:\Z)', raw_text, re.DOTALL | re.IGNORECASE)
    if recommendations_match:
        sections["disposal_recommendations"] = recommendations_match.group(1).strip()
    
    return sections