import requests
import json

TOGETHER_API_KEY = "d93db5061957c8d023d73785327e15a09cbfc86230c3fb46d57f14f4af9d9e21"  # You'll need to set this in your environment variables
API_URL = "https://api.together.xyz/inference"

def classify_severity(complaint_text):
    """
    Classify the severity of a complaint using Together AI's LLM.
    """
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    # Prompt engineering for severity classification
    prompt = f"""Analyze this complaint and classify its severity as High, Medium, or Low. 
    Also provide a brief analysis of key concerns and recommended actions.
    
    Complaint: {complaint_text}
    
    Provide the response in the following JSON format:
    {{
        "severity": "High/Medium/Low",
        "analysis": "Brief analysis here"
    }}
    """

    data = {
        "model": "togethercomputer/llama-2-70b-chat",
        "prompt": prompt,
        "max_tokens": 300,
        "temperature": 0.7
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()
        
        # Parse the LLM response to extract JSON
        llm_response = response.json()['output']['choices'][0]['text']
        result = json.loads(llm_response)
        
        return {
            "severity": result["severity"],
            "confidence": 0.9,  # Together AI doesn't provide confidence scores directly
            "analysis": result["analysis"]
        }
    except Exception as e:
        print(f"Error in classification: {str(e)}")
        return {
            "severity": "Medium",  # Default fallback
            "confidence": 0.5,
            "analysis": "Error in automated analysis. Please review manually."
        }

def analyze_complaint(complaint_text):
    """
    Perform detailed analysis of the complaint using Together AI.
    """
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""Analyze this complaint in detail:
    {complaint_text}
    
    Provide:
    1. Key concerns
    2. Priority level
    3. Recommended immediate actions
    4. Potential risks
    
    Format the response in clear bullet points."""

    data = {
        "model": "togethercomputer/llama-2-70b-chat",
        "prompt": prompt,
        "max_tokens": 500,
        "temperature": 0.7
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['output']['choices'][0]['text']
    except Exception as e:
        print(f"Error in analysis: {str(e)}")
        return "Error performing detailed analysis. Please review manually."