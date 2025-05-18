Women Complaint Generator & Management System
Overview
This project provides women with a streamlined platform to report incidents such as harassment or violence in a safe and accessible manner. The system utilizes artificial intelligence and location services to generate formal complaints, identify appropriate authorities, and deliver reports directly to relevant police stations. Additionally, it offers educational resources on women's rights and provides timely updates.
Key Features

AI-Powered Complaint Generator: Converts natural language descriptions into properly formatted legal complaints
Location-Based Routing: Automatically directs complaints to the nearest police station
Rights Information System: Identifies applicable constitutional rights related to the incident
Complaint Tracking: Enables users to monitor the status of their submitted complaints
Police Administration Dashboard: Provides officers with tools to view, forward, and manage complaints
Safety Map: Displays safe zones and active alerts in the user's vicinity
Multilingual Support: Presents rights information and government schemes in local languages

Installation Instructions
Prerequisites

Python 3.7 or higher
pip package manager

Step 1: Install Required Dependencies
Ensure Python and pip are installed on your system, then run:
bashpip install flask
If using a requirements file:
bashpip install -r requirements.txt
Step 2: Launch the Application
Open a terminal or command prompt and execute:
bashpython app.py
You should see output similar to:
* Running on http://127.0.0.1:5000/
Open your web browser and navigate to:
http://127.0.0.1:5000/
Project Structure
Women/
├── app.py                  # Main application file
├── agents.py               # AI agents for complaint processing
├── routes/                 # Backend routing logic
├── models/                 # Data models and database schemas
├── templates/              # HTML templates
├── static/                 # Static assets (CSS, JavaScript, images)
├── utils/                  # Utility functions and helpers
Project Background
This system was developed to address deficiencies in the current manual complaint filing process, which is often time-consuming, difficult to access, and confusing for many women. Our solution:

Accelerates the complaint registration process
Automatically references relevant legal frameworks
Uses geolocation technology to direct complaints to appropriate authorities
Keeps complainants informed of case progress

Future Development Plans

Expand language support to reach more communities
Enhance complaint verification mechanisms
Implement advanced data analytics to identify problematic areas
Integrate with additional government services
