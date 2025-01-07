import os
import google.generativeai as genai
from datetime import datetime

# Configure the API key
genai.configure(api_key=os.getenv("API_KEY"))

# Initialize model
model = genai.GenerativeModel("gemini-1.5-pro")

def extract_incident_details(description):
    prompt = f"""
    Extract the following details from the description if available. 
    Only return the extracted information in this exact format, nothing else:
    Date of Incident: [date if found, otherwise leave blank]
    Time of Incident: [time if found, otherwise leave blank]
    Place of Incident: [place if found, otherwise leave blank]
    
    Description: {description}
    """
    response = model.generate_content(prompt)
    return response.text.strip()

def generate_detailed_description(description):
    prompt = f"""
    Provide a detailed and comprehensive description of the incident in a short concise paragraph based on the given input.
    Include:
    - Chronological sequence of events
    - All relevant details about what happened
    - Names and roles of people involved (if mentioned)
    - Any evidence or witnesses mentioned
    - Impact on the victim/complainant
    
    Keep the tone professional and factual.
    Original description: {description}
    """
    response = model.generate_content(prompt)
    return response.text.strip()

def analyze_complaint(description):
    prompt = f"""
    Analyze the incident description and provide:
    1. Type of Complaint: [complaint type]
    
    2. Sections Invoked:
    Based on the nature of the complaint, list the most relevant and applicable sections of Indian law that apply to this case.
    Format each section as:
    * **Section [number] of [law code]** ([brief description])
    
    For example:
    * **Section 375 of the IPC** (Definition of Rape)
    * **Section 376 of the IPC** (Punishment for Rape)
    
    Include any relevant acts if applicable, formatted as:
    * Relevant provisions of **[Act name]**, if [condition].
    
    List at least 3-4 most relevant sections.
    
    3. Immediate Next Steps:
    [List 1-2 concrete action items based on Indian legal procedures as short and simple points]
    
    Description: {description}
    """
    response = model.generate_content(prompt)
    return response.text.strip()

def generate_structured_complaint(name, contact, email, permanent_address, date, time, place, detailed_description, complaint_analysis):
    complaint_template = f"""
========= COMPLAINT REPORT =========

PERSONAL DETAILS
Name: {name}
Contact: {contact}
Email: {email}
Permanent Address: {permanent_address}

INCIDENT DETAILS
Date: {date}
Time: {time}
Place: {place}

DETAILED DESCRIPTION OF INCIDENT
{detailed_description}

COMPLAINT ANALYSIS
{complaint_analysis}

DECLARATION
I hereby declare that the information provided above is true and accurate to the best of my knowledge and belief.

Date: {datetime.now().strftime('%Y-%m-%d')}

[Under Section 156(3) of Criminal Procedure Code, 1973]
================================
    """
    return complaint_template

def process_incident(description, name, contact, email, address):
    # Extract initial details
    extracted_details = extract_incident_details(description)
    details_dict = {}
    for line in extracted_details.split('\n'):
        if ': ' in line:
            key, value = line.split(': ', 1)
            details_dict[key] = value.strip()
    
    # Check for missing information
    missing_info = {
        'date': not details_dict.get('Date of Incident'),
        'time': not details_dict.get('Time of Incident'),
        'place': not details_dict.get('Place of Incident')
    }
    
    if any(missing_info.values()):
        # Return what information is missing
        return {
            'status': 'incomplete',
            'missing_info': missing_info,
            'current_details': details_dict
        }
    
    # If all information is present, generate the complaint
    detailed_description = generate_detailed_description(description)
    complaint_analysis = analyze_complaint(description)
    structured_complaint = generate_structured_complaint(
        name,
        contact,
        email,
        address,
        details_dict.get('Date of Incident', ''),
        details_dict.get('Time of Incident', ''),
        details_dict.get('Place of Incident', ''),
        detailed_description,
        complaint_analysis
    )

    return {
        'status': 'complete',
        'structured_complaint': structured_complaint,
        'details': details_dict,
        'analysis': complaint_analysis
    }

def update_incident_details(original_description, date=None, time=None, place=None):
    # Create an updated description with the provided details
    updates = []
    if date:
        updates.append(f"The incident occurred on {date}")
    if time:
        updates.append(f"at {time}")
    if place:
        updates.append(f"at {place}")
    
    if updates:
        updated_description = f"{original_description}\n\nAdditional Details: {'. '.join(updates)}."
    else:
        updated_description = original_description
    
    return updated_description

