import google.generativeai as genai
import PIL.Image
import os
import logging

# Configure Google Gemini AI with API key
api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyAI-BJRT0oVhWMRie6Sjl39F1z9U2SAcnI")
genai.configure(api_key=api_key)

def analyze_waste(image_path):
    """
    Analyze waste image using Google Gemini AI
    
    Args:
        image_path: Path to the uploaded image
        
    Returns:
        Dictionary containing analysis results
    """
    try:
        # Open image using PIL
        image = PIL.Image.open(image_path)
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Configure the model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Generate content with a detailed prompt
        prompt = (
            "Analyze this waste image in detail. Provide the following information:\n"
            "1. Is it recyclable? Answer with Yes or No and explain why.\n"
            "2. Is it e-waste? Answer with Yes or No and explain why.\n"
            "3. What is its primary material composition? (e.g., plastic, paper, metal, glass, organic, etc.)\n"
            "4. If it's recyclable, how should it be prepared for recycling?\n"
            "5. Are there any special disposal considerations?\n\n"
            "Format your response clearly with sections for each question."
        )
        
        response = model.generate_content(
            [prompt, image],
            generation_config={
                "max_output_tokens": 500,
                "temperature": 0.4,
            }
        )
        
        # Parse the response text
        analysis_text = response.text
        
        # Extract key information
        is_recyclable = "yes" in analysis_text.lower().split("1. is it recyclable?")[1].split("\n")[0].lower()
        is_ewaste = "yes" in analysis_text.lower().split("2. is it e-waste?")[1].split("\n")[0].lower()
        
        # Try to extract material
        material = "Unknown"
        try:
            material_section = analysis_text.lower().split("3. what is its primary material composition?")[1].split("\n")[0]
            if "plastic" in material_section:
                material = "Plastic"
            elif "paper" in material_section:
                material = "Paper"
            elif "metal" in material_section:
                material = "Metal"
            elif "glass" in material_section:
                material = "Glass"
            elif "organic" in material_section:
                material = "Organic"
            elif "textile" in material_section or "fabric" in material_section:
                material = "Textile"
            elif "electronic" in material_section:
                material = "Electronic"
            else:
                material = "Mixed/Other"
        except:
            pass
        
        # Format the result
        result = {
            "full_analysis": analysis_text,
            "is_recyclable": is_recyclable,
            "is_ewaste": is_ewaste,
            "material": material
        }
        
        return result
    
    except Exception as e:
        logging.error(f"Error in image analysis: {e}")
        return {
            "error": str(e),
            "full_analysis": "Analysis failed",
            "is_recyclable": False,
            "is_ewaste": False,
            "material": "Unknown"
        }
