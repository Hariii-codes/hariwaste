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
            "You are WasteWorks AI Assistant, a specialized waste management analysis expert with deep knowledge of recycling processes, material science, and environmental impacts.\n\n"
            "Analyze this waste image in detail and provide the following information in a well-structured, clear format with HTML formatting:\n\n"
            "1. Is it recyclable? (Yes/No) - Provide a confident answer and explain your reasoning in detail. Consider regional variation in recyclability.\n"
            "2. Is it e-waste? (Yes/No) - Provide a confident answer and explain why it is or isn't electronic waste. Include information about hazardous components if present.\n"
            "3. Primary material composition - Specifically identify as one of: Plastic, Paper, Metal, Glass, Organic, Textile, Electronic, Mixed/Other. Choose the most dominant material and include specific subcategories (e.g., PET plastic, corrugated cardboard).\n"
            "4. Recycling preparation instructions - Provide detailed steps on how to prepare this item for recycling (cleaning, disassembly, separating components, removing labels/caps, etc.). Format this as an ordered list with clear steps.\n"
            "5. Environmental impact - Explain the environmental consequences if this item is improperly disposed of. Include decomposition time, pollution potential, and resource loss. Format this with bullet points.\n"
            "6. Disposal recommendations - Recommend the most eco-friendly disposal method based on the item's composition. Suggest specific facilities or programs when applicable. Use bold formatting for key recommendations.\n\n"
            "Format each section with HTML for better readability. Use <h4> for section headings, <ul> and <ol> for lists, <strong> for emphasis, and <p> for paragraphs. Keep responses concise but informative.\n\n"
            "Respond with a confident analysis even with partial visibility or unclear images. Format your response as clearly labeled sections with detailed explanations for each point."
        )
        
        response = model.generate_content(
            [prompt, image],
            generation_config={
                "max_output_tokens": 1000,
                "temperature": 0.3,
                "top_p": 0.95,
                "top_k": 40
            }
        )
        
        # Parse the response text
        analysis_text = response.text
        
        # Extract key information more robustly
        is_recyclable = False
        is_ewaste = False
        material = "Unknown"
        recycling_instructions = ""
        environmental_impact = ""
        disposal_recommendations = ""
        
        # More robust parsing strategy that's less dependent on specific formatting
        analysis_lower = analysis_text.lower()
        
        # Check for recyclability
        recyclable_indicators = ["1. is it recyclable", "recyclable:", "recyclability:"]
        for indicator in recyclable_indicators:
            if indicator in analysis_lower:
                # Look for a Yes/No response within 100 characters after the indicator
                segment = analysis_lower[analysis_lower.find(indicator):analysis_lower.find(indicator) + 100]
                is_recyclable = "yes" in segment and not ("no" in segment and segment.find("no") < segment.find("yes"))
                break
        
        # Check for e-waste
        ewaste_indicators = ["2. is it e-waste", "e-waste:", "electronic waste:"]
        for indicator in ewaste_indicators:
            if indicator in analysis_lower:
                # Look for a Yes/No response within 100 characters after the indicator
                segment = analysis_lower[analysis_lower.find(indicator):analysis_lower.find(indicator) + 100]
                is_ewaste = "yes" in segment and not ("no" in segment and segment.find("no") < segment.find("yes"))
                break
        
        # Extract material using a more flexible approach
        material_indicators = ["3. primary material", "material composition:", "primary material:"]
        for indicator in material_indicators:
            if indicator in analysis_lower:
                # Get the 150 characters after the indicator to find material
                material_section = analysis_lower[analysis_lower.find(indicator):analysis_lower.find(indicator) + 150]
                
                # Look for specific materials
                materials = {
                    "plastic": "Plastic",
                    "paper": "Paper",
                    "cardboard": "Paper",
                    "metal": "Metal",
                    "aluminum": "Metal",
                    "steel": "Metal",
                    "glass": "Glass",
                    "organic": "Organic",
                    "food": "Organic",
                    "textile": "Textile",
                    "fabric": "Textile",
                    "clothing": "Textile",
                    "electronic": "Electronic",
                    "battery": "Electronic"
                }
                
                # Find the first material mentioned
                for key, value in materials.items():
                    if key in material_section:
                        material = value
                        break
                
                break
        
        # Extract recycling instructions
        try:
            if "4. recycling preparation" in analysis_lower:
                start = analysis_lower.find("4. recycling preparation")
                next_section = analysis_lower.find("5.", start)
                if next_section == -1:  # If there's no next section
                    next_section = len(analysis_lower)
                recycling_instructions = analysis_text[start:next_section].strip()
            elif "preparation" in analysis_lower:
                start = analysis_lower.find("preparation")
                end = analysis_lower.find("\n\n", start)
                if end == -1:
                    end = len(analysis_lower)
                recycling_instructions = analysis_text[start:end].strip()
        except:
            recycling_instructions = "No specific preparation instructions available."
            
        # Extract environmental impact
        try:
            if "5. environmental impact" in analysis_lower:
                start = analysis_lower.find("5. environmental impact")
                next_section = analysis_lower.find("6.", start)
                if next_section == -1:
                    next_section = len(analysis_lower)
                environmental_impact = analysis_text[start:next_section].strip()
        except:
            environmental_impact = "Environmental impact analysis not available."
            
        # Extract disposal recommendations
        try:
            if "6. disposal" in analysis_lower:
                start = analysis_lower.find("6. disposal")
                next_section = analysis_lower.find("\n\n", start + 15)
                if next_section == -1:
                    next_section = len(analysis_lower)
                disposal_recommendations = analysis_text[start:next_section].strip()
        except:
            disposal_recommendations = "Specific disposal recommendations not available."
        
        # Format the result with additional information
        result = {
            "full_analysis": analysis_text,
            "is_recyclable": is_recyclable,
            "is_ewaste": is_ewaste,
            "material": material,
            "recycling_instructions": recycling_instructions,
            "environmental_impact": environmental_impact,
            "disposal_recommendations": disposal_recommendations
        }
        
        return result
    
    except Exception as e:
        logging.error(f"Error in image analysis: {e}")
        return {
            "error": str(e),
            "full_analysis": "Analysis failed",
            "is_recyclable": False,
            "is_ewaste": False,
            "material": "Unknown",
            "recycling_instructions": "Could not analyze the image.",
            "environmental_impact": "Could not analyze the image.",
            "disposal_recommendations": "Could not analyze the image."
        }
