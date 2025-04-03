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
        "disposal_recommendations": ""
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
    
    return result