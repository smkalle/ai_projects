#!/usr/bin/env python3
"""
NGO Medical AI Assistant - Gradio Demo
Quick prototype interface for hackathon demonstrations

This script provides a simple Gradio interface for testing the medical AI
capabilities without setting up the full FastAPI application.
"""

import gradio as gr
import os
import base64
from PIL import Image
import numpy as np
from typing import Dict, Tuple
import json

# Mock medical analysis for demo purposes
def analyze_medical_case(image, symptoms, patient_history=""):
    """
    Mock medical analysis function for demonstration
    In production, this would call the actual AI models
    """

    findings = []
    reasoning_chain = []
    recommendations = []

    # Process symptoms
    if symptoms:
        symptoms_lower = symptoms.lower()
        reasoning_chain.append(f"Initial Assessment: Patient presents with {symptoms}")

        # Symptom-based analysis
        if any(word in symptoms_lower for word in ["cough", "fever", "breathing"]):
            findings.extend([
                "Respiratory symptoms present",
                "Consider infectious etiology",
                "Monitor oxygen saturation"
            ])
            recommendations.append("Consider chest X-ray if not already obtained")

        if any(word in symptoms_lower for word in ["chest pain", "cardiac"]):
            findings.extend([
                "Chest pain requires evaluation", 
                "Consider cardiac causes"
            ])
            recommendations.append("Obtain ECG if chest pain present")

        if any(word in symptoms_lower for word in ["wound", "infection", "redness"]):
            findings.extend([
                "Possible wound infection",
                "Local inflammatory signs"
            ])
            recommendations.append("Consider antibiotic therapy")

    # Process image if provided
    if image is not None:
        reasoning_chain.append("Image Analysis: Medical image processed for assessment")
        findings.append("Image data received and analyzed")
        recommendations.append("Correlate imaging findings with clinical presentation")

    # Add standard reasoning steps
    reasoning_chain.extend([
        "Clinical Correlation: Integrating symptoms with available data",
        "Risk Assessment: Evaluating urgency and priority level",
        "Synthesis: Combining evidence for preliminary assessment"
    ])

    # Standard recommendations
    recommendations.extend([
        "Comprehensive medical evaluation recommended",
        "Document all findings and treatments provided",
        "Arrange follow-up with qualified medical professional"
    ])

    # Calculate priority and confidence
    priority_keywords = ["severe", "acute", "emergency", "difficulty breathing", "chest pain"]
    priority_level = "HIGH" if any(keyword in symptoms.lower() for keyword in priority_keywords) else "MODERATE"
    confidence_score = 0.85 if len(findings) > 2 else 0.70

    # Format response
    result = f"""
## Medical Analysis Results

### 🧠 Reasoning Chain:
{chr(10).join([f"• {step}" for step in reasoning_chain[:5]])}

### 🔍 Key Findings:
{chr(10).join([f"• {finding}" for finding in findings[:5]])}

### 💡 Recommendations:
{chr(10).join([f"• {rec}" for rec in recommendations[:5]])}

### 📊 Assessment:
- **Priority Level:** {priority_level}
- **Confidence Score:** {confidence_score:.1%}
- **Image Processed:** {"Yes" if image is not None else "No"}

### ⚠️ Medical Disclaimer:
**This analysis is for preliminary assessment only and should not replace professional medical diagnosis.
Always consult qualified medical professionals for diagnosis and treatment.
In case of emergency, contact local emergency services immediately.**
    """

    return result

def medical_chat(message, history):
    """Simple medical chat function for demonstration"""

    message_lower = message.lower()

    if "pneumonia" in message_lower:
        response = """
**Pneumonia Assessment:**

Key signs to look for:
• Fever, cough, difficulty breathing
• Chest pain when breathing
• Fatigue and weakness
• Abnormal lung sounds

Immediate actions:
• Check oxygen saturation
• Consider antibiotic therapy
• Monitor respiratory status closely
• Arrange advanced care if severe

⚠️ Seek immediate medical attention for severe symptoms.
        """
    elif "triage" in message_lower:
        response = """
**Emergency Triage Guidelines:**

Priority Levels:
• **EMERGENCY** (< 15 min): Life-threatening
• **HIGH** (< 1 hour): Urgent medical needs  
• **MODERATE** (< 4 hours): Important but stable
• **ROUTINE** (< 24 hours): Non-urgent

Assessment factors:
• Vital signs and consciousness
• ABC (Airway, Breathing, Circulation)
• Pain level and injury mechanism
• Age and medical history
        """
    elif "emergency" in message_lower:
        response = """
**Emergency Response Protocol:**

Primary Assessment (ABCDE):
• **A**irway: Clear and patent?
• **B**reathing: Rate, effort, oxygen
• **C**irculation: Pulse, BP, perfusion  
• **D**isability: Neurological status
• **E**xposure: Full examination

Immediate actions:
• Ensure scene safety
• Call for medical support
• Begin life-saving interventions
• Prepare for transport
        """
    else:
        response = f"""
Thank you for your question about: "{message}"

For specific medical guidance:
• Consult local medical protocols
• Contact medical supervision
• Prioritize patient safety
• Document all decisions

Common topics I can help with:
• Pneumonia signs and management
• Emergency triage protocols  
• Basic wound care
• When to seek advanced care

⚠️ **Always consult medical professionals for patient care decisions.**
        """

    return response

# Create Gradio interface
def create_medical_ai_interface():
    """Create the main Gradio interface"""

    with gr.Blocks(title="NGO Medical AI Assistant", theme=gr.themes.Soft()) as demo:

        gr.Markdown("""
        # 🏥 NGO Medical AI Assistant

        **Multimodal medical reasoning for NGO healthcare initiatives**

        This tool provides preliminary medical insights by analyzing symptoms and medical images.

        ⚠️ **Important**: This is for educational and triage support only. Always consult medical professionals.
        """)

        with gr.Tabs():

            # Medical Analysis Tab
            with gr.TabItem("🔬 Medical Analysis"):
                gr.Markdown("### Upload medical image and describe symptoms for AI analysis")

                with gr.Row():
                    with gr.Column(scale=1):
                        image_input = gr.Image(label="Medical Image (X-ray, wound photo, etc.)", type="pil")
                        symptoms_input = gr.Textbox(
                            label="Patient Symptoms", 
                            placeholder="Describe the patient's symptoms in detail...",
                            lines=3
                        )
                        history_input = gr.Textbox(
                            label="Patient History (optional)", 
                            placeholder="Previous medical history, medications, etc.",
                            lines=2
                        )
                        analyze_btn = gr.Button("🔬 Analyze Case", variant="primary")

                    with gr.Column(scale=2):
                        analysis_output = gr.Markdown(label="Analysis Results")

                analyze_btn.click(
                    analyze_medical_case,
                    inputs=[image_input, symptoms_input, history_input],
                    outputs=[analysis_output]
                )

            # Medical Chat Tab  
            with gr.TabItem("💬 Medical Chat"):
                gr.Markdown("### Ask medical questions and get guidance for NGO healthcare work")

                chatbot = gr.Chatbot(height=400)
                msg_input = gr.Textbox(
                    label="Ask a medical question",
                    placeholder="e.g., 'How do I assess for pneumonia?' or 'Emergency triage protocols'"
                )

                def respond(message, chat_history):
                    bot_message = medical_chat(message, chat_history)
                    chat_history.append((message, bot_message))
                    return "", chat_history

                msg_input.submit(respond, [msg_input, chatbot], [msg_input, chatbot])

            # Sample Cases Tab
            with gr.TabItem("📋 Sample Cases"):
                gr.Markdown("""
                ### Example Medical Cases for Testing

                Try these sample scenarios to test the AI analysis:
                """)

                sample_cases = [
                    {
                        "title": "Chest X-ray Analysis", 
                        "symptoms": "Patient presents with persistent cough, fever, and difficulty breathing for 3 days"
                    },
                    {
                        "title": "Emergency Triage",
                        "symptoms": "45-year-old patient with severe chest pain radiating to left arm, sweating profusely"  
                    },
                    {
                        "title": "Wound Assessment",
                        "symptoms": "Local injury with redness, swelling, and warmth around the wound site"
                    }
                ]

                for case in sample_cases:
                    with gr.Row():
                        gr.Markdown(f"**{case['title']}**")
                        gr.Textbox(value=case['symptoms'], interactive=False)

            # Documentation Tab
            with gr.TabItem("📚 Documentation"):
                gr.Markdown("""
                ### Setup and Usage Guide

                #### Quick Start:
                1. **Medical Analysis**: Upload image + describe symptoms
                2. **Review Results**: Check reasoning, findings, recommendations  
                3. **Chat Assistant**: Ask medical questions for guidance
                4. **Always**: Consult medical professionals for final decisions

                #### API Keys Setup:
                - Copy `config/.env.example` to `config/.env`
                - Add your OpenAI API key for full functionality
                - For local deployment, see README.md

                #### Medical Use Cases:
                - **Pneumonia Detection**: Chest X-ray + respiratory symptoms
                - **Emergency Triage**: Rapid patient prioritization  
                - **Wound Assessment**: Infection risk evaluation
                - **General Consultation**: Medical guidance for NGO workers

                #### Ethical Guidelines:
                - ✅ Use for preliminary assessment and education
                - ✅ Always provide medical disclaimers
                - ✅ Ensure patient privacy and consent
                - ❌ Never replace professional medical judgment
                - ❌ Avoid use in life-threatening emergencies without backup

                #### Technical Support:
                - GitHub: [medai-hackathon-project](https://github.com/your-username/medai-hackathon-project)
                - Email: support@medai-hackathon.org
                - Documentation: See README.md for full setup
                """)

        gr.Markdown("""
        ---
        **⚠️ Medical Disclaimer**: This software is for educational and research purposes only. 
        It is not intended to provide medical advice, diagnosis, or treatment. 
        Always consult qualified healthcare professionals for medical decisions.
        In case of medical emergency, contact local emergency services immediately.
        """)

    return demo

if __name__ == "__main__":
    # Create and launch the interface
    demo = create_medical_ai_interface()

    # Launch with sharing enabled for demos
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,  # Creates public link for demos
        debug=True
    )
