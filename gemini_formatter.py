"""
Format and clean Gemini AI output for better display in the application.
This module removes HTML tags, numbering, and other formatting that
makes the AI output less readable in the UI.
"""

import re
from bs4 import BeautifulSoup

def clean_text(text):
    """
    Remove HTML tags and clean text for better readability
    
    Args:
        text: Text string that might contain HTML tags
        
    Returns:
        Clean text without HTML tags
    """
    if not text:
        return ""
        
    # Use BeautifulSoup to remove HTML
    soup = BeautifulSoup(text, 'html.parser')
    clean = soup.get_text()
    
    # Remove numbered list patterns (1., 2., etc.)
    clean = re.sub(r'^\s*\d+\.\s*', '', clean, flags=re.MULTILINE)
    
    # Remove extra whitespace
    clean = re.sub(r'\s+', ' ', clean).strip()
    
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
    formatted = {}
    
    # Copy original fields
    formatted.update(response_dict)
    
    # Clean specific text fields
    if 'full_analysis' in response_dict:
        formatted['full_analysis'] = clean_text(response_dict['full_analysis'])
    
    if 'recycling_instructions' in response_dict:
        # Remove headings like "How to recycle:" 
        text = clean_text(response_dict['recycling_instructions'])
        text = re.sub(r'^(How to recycle:|Recycling Instructions:)\s*', '', text, flags=re.IGNORECASE)
        formatted['recycling_instructions'] = text
    
    if 'environmental_impact' in response_dict:
        # Remove headings like "Environmental Impact:"
        text = clean_text(response_dict['environmental_impact'])
        text = re.sub(r'^(Environmental Impact:|Impact:)\s*', '', text, flags=re.IGNORECASE)
        formatted['environmental_impact'] = text
    
    if 'disposal_recommendations' in response_dict:
        # Remove headings and numbering
        text = clean_text(response_dict['disposal_recommendations'])
        text = re.sub(r'^(Disposal Recommendations:|Best Disposal Method:)\s*', '', text, flags=re.IGNORECASE)
        formatted['disposal_recommendations'] = text
    
    # Generate summary based on available information if not already there
    if not response_dict.get('summary') and response_dict.get('full_analysis'):
        # Get material information
        material_type = "Unknown"
        if response_dict.get('material'):
            material_type = response_dict.get('material')
        elif 'material_detection' in response_dict and response_dict['material_detection'].get('primary_material'):
            material_type = response_dict['material_detection']['primary_material'].capitalize()
            
        # Determine item description from full analysis
        full_analysis_lower = response_dict.get('full_analysis', '').lower()
        item_description = "Waste item"
        if "bottle" in full_analysis_lower:
            item_description = "Plastic bottle"
        elif "container" in full_analysis_lower:
            item_description = "Container"
        elif "packaging" in full_analysis_lower:
            item_description = "Packaging material"
        elif "bag" in full_analysis_lower:
            item_description = "Bag"
        elif "cup" in full_analysis_lower:
            item_description = "Cup"
        elif "box" in full_analysis_lower:
            item_description = "Box"
        elif "device" in full_analysis_lower or "electronic" in full_analysis_lower:
            item_description = "Electronic device"
        
        # Determine recyclability
        recyclable = "Not recyclable"
        if response_dict.get('is_recyclable'):
            recyclable = "Recyclable"
            
        # Create bullet point summary
        formatted['summary'] = f"• The image shows a {item_description}.\n• It is primarily made of {material_type}.\n• This item is {recyclable}."
    elif 'summary' in response_dict:
        formatted['summary'] = response_dict['summary']
    
    return formatted

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
    result = {
        "full_analysis": raw_text,
        "recycling_instructions": "",
        "environmental_impact": "",
        "disposal_recommendations": "",
        "summary": ""
    }
    
    # Extract recycling instructions
    recycling_match = re.search(
        r'(?:recycling instructions:|how to recycle:)(.*?)(?=environmental impact:|$)', 
        raw_text, 
        re.IGNORECASE | re.DOTALL
    )
    if recycling_match:
        result["recycling_instructions"] = recycling_match.group(1).strip()
    
    # Extract environmental impact
    impact_match = re.search(
        r'(?:environmental impact:|impact:)(.*?)(?=disposal|best disposal method|$)', 
        raw_text, 
        re.IGNORECASE | re.DOTALL
    )
    if impact_match:
        result["environmental_impact"] = impact_match.group(1).strip()
    
    # Extract disposal recommendations
    disposal_match = re.search(
        r'(?:disposal recommendations:|best disposal method:)(.*?)(?=\Z)', 
        raw_text, 
        re.IGNORECASE | re.DOTALL
    )
    if disposal_match:
        result["disposal_recommendations"] = disposal_match.group(1).strip()
    
    # Create a concise summary in bullet points
    material_type = ""
    if "plastic" in raw_text.lower():
        material_type = "Plastic"
    elif "paper" in raw_text.lower():
        material_type = "Paper"
    elif "metal" in raw_text.lower():
        material_type = "Metal"
    elif "glass" in raw_text.lower():
        material_type = "Glass"
    elif "fabric" in raw_text.lower() or "textile" in raw_text.lower():
        material_type = "Textile"
    elif "electronic" in raw_text.lower() or "e-waste" in raw_text.lower():
        material_type = "Electronic"
    else:
        material_type = "Mixed materials"
    
    # Extract an item description
    item_description = "Waste item"
    if "bottle" in raw_text.lower():
        item_description = "Plastic bottle"
    elif "container" in raw_text.lower():
        item_description = "Container"
    elif "packaging" in raw_text.lower():
        item_description = "Packaging material"
    elif "bag" in raw_text.lower():
        item_description = "Bag"
    elif "cup" in raw_text.lower():
        item_description = "Cup"
    elif "box" in raw_text.lower():
        item_description = "Box"
    elif "device" in raw_text.lower() or "electronic" in raw_text.lower():
        item_description = "Electronic device"
    
    # Determine recyclability
    recyclable = "Not recyclable"
    if "recyclable: yes" in raw_text.lower() or "is recyclable" in raw_text.lower():
        recyclable = "Recyclable"
    
    # Format the bullet point summary
    result["summary"] = f"• The image shows a {item_description}.\n• It is primarily made of {material_type}.\n• This item is {recyclable}."
    
    return result