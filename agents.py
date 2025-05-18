import os
from mistralai import Mistral
from datetime import datetime

# Configure the Mistral API client
client = Mistral(api_key="91TejAXA6KcZhGrJmHv1qQyn0V4gt3Gf")
MODEL = "mistral-large-latest"

class CrewAIAgent:
    """Base class for CrewAI agents."""
    def execute(self, *args, **kwargs):
        raise NotImplementedError("Each agent must implement the execute method.")

class IncidentDetailsExtractorAgent(CrewAIAgent):
    def execute(self, description):
        prompt = f"""
        Extract the following details from the description if available. 
        Only return the extracted information in this exact format, nothing else:
        Date of Incident: [date if found, otherwise leave blank]
        Time of Incident: [time if found, otherwise leave blank]
        Place of Incident: [place(a place like a location,area,and not like undeterministic road or home or car like that exact map place) if found, otherwise leave blank]
        
        Description: {description}
        """
        chat_response = client.chat.complete(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1
        )
        return chat_response.choices[0].message.content.strip()

class DetailedDescriptionGeneratorAgent(CrewAIAgent):
    def execute(self, description):
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
        chat_response = client.chat.complete(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1
        )
        return chat_response.choices[0].message.content.strip()

class ComplaintTypeAndLawsDetectorAgent(CrewAIAgent):
    def execute(self, description):
        prompt = f"""
        Analyze the incident description and provide:
        1. Type of Complaint: [complaint type]
        
        2. Sections Invoked:
        Based on the nature of the complaint, list the most relevant and applicable sections of Indian law that apply to this case.
        Format each section as:
        Section [number] of [law code] ([brief description])
        
        For example:
        Section 375 of the IPC (Definition of Rape)
        Section 376 of the IPC (Punishment for Rape)
        
        Include any relevant acts if applicable, formatted as:
        Relevant provisions of [Act name], if [condition].
        
        List at least 3-4 most relevant sections.
        
        3. Immediate Next Steps:
        [List 1-2 concrete action items based on Indian legal procedures as short and simple points]
        
        Description: {description}
        """
        chat_response = client.chat.complete(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1
        )
        return chat_response.choices[0].message.content.strip()

def parse_extracted_details(extracted_text):
    details_dict = {}
    for line in extracted_text.split('\n'):
        if ': ' in line:
            key, value = line.split(': ', 1)
            details_dict[key.strip()] = value.strip()
    return details_dict

def process_incident(description, name, contact, email, address):
    # First, check if we have all required details
    extractor_agent = IncidentDetailsExtractorAgent()
    extracted_details = extractor_agent.execute(description)
    details_dict = parse_extracted_details(extracted_details)
    
    # Check for missing information
    missing_info = {
        'date': not details_dict.get('Date of Incident'),
        'time': not details_dict.get('Time of Incident'),
        'place': not details_dict.get('Place of Incident')
    }
    
    if any(missing_info.values()):
        return {
            'status': 'incomplete',
            'missing_info': missing_info,
            'current_details': details_dict
        }
    
    # Only if we have all required information, proceed with other agents
    detailed_description = DetailedDescriptionGeneratorAgent().execute(description)
    complaint_analysis = ComplaintTypeAndLawsDetectorAgent().execute(description)
    
    structured_complaint = generate_structured_complaint(
        name,
        contact,
        email,
        address,
        details_dict['Date of Incident'],
        details_dict['Time of Incident'],
        details_dict['Place of Incident'],
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
    
    return f"{original_description}\n\nAdditional Details: {'. '.join(updates)}." if updates else original_description

def generate_structured_complaint(name, contact, email, permanent_address, date, time, place, detailed_description, complaint_analysis):
    complaint_template = f"""
                                    OFFICIAL COMPLAINT REPORT


COMPLAINANT INFORMATION
----------------------
Name:                   {name}
Contact Number:         {contact}
Email Address:         {email}
Permanent Address:     {permanent_address}


INCIDENT DETAILS
---------------
Date:                  {date}
Time:                  {time}
Location:              {place}


DETAILED DESCRIPTION
-------------------
{detailed_description}


LEGAL ANALYSIS AND RECOMMENDATIONS
--------------------------------
1. Type of Complaint: {complaint_analysis.split('1. Type of Complaint: ')[1].split('2. Sections Invoked:')[0].strip()}

2. Sections Invoked:
{complaint_analysis.split('2. Sections Invoked:')[1].split('3. Immediate Next Steps:')[0].strip()}

3. Immediate Next Steps:
{complaint_analysis.split('3. Immediate Next Steps:')[1].strip()}


DECLARATION
----------
I, {name}, hereby declare that the information provided above is true and accurate 
to the best of my knowledge and belief.

Date of Filing:        {datetime.now().strftime('%B %d, %Y')}
Place:                 {place}

[Filed under Section 156(3) of Criminal Procedure Code, 1973]
"""
    return complaint_template