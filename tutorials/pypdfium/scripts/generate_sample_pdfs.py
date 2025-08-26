#!/usr/bin/env python3
"""
Generate sample PDF documents for testing Energy Document AI system.

This script creates realistic energy sector PDFs with:
- Technical specifications and tables
- Regulatory compliance documents  
- Environmental impact reports
- Equipment manuals and procedures

Usage:
    python scripts/generate_sample_pdfs.py --all
    python scripts/generate_sample_pdfs.py --type technical
"""

import argparse
import os
from pathlib import Path
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import tempfile
import random


class SamplePDFGenerator:
    """Generate sample PDF documents for energy sector testing"""
    
    def __init__(self, output_dir="data/sample_pdfs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.styles = getSampleStyleSheet()
        
        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            spaceAfter=20,
            textColor=HexColor('#2E8B57')
        )
        
    def generate_all(self):
        """Generate all sample PDFs"""
        self.generate_solar_technical_spec()
        self.generate_wind_regulatory_doc()
        self.generate_grid_environmental_report()
        self.generate_transmission_equipment_manual()
        print(f"\n✅ All sample PDFs generated in {self.output_dir}")
        
    def generate_solar_technical_spec(self):
        """Generate a solar panel technical specification document"""
        filename = self.output_dir / "solar_panel_technical_specifications.pdf"
        doc = SimpleDocTemplate(str(filename), pagesize=letter)
        story = []
        
        # Title
        story.append(Paragraph("Solar Panel Technical Specifications", self.title_style))
        story.append(Spacer(1, 20))
        
        # Overview section
        story.append(Paragraph("Overview", self.styles['Heading2']))
        overview_text = """
        This document provides comprehensive technical specifications for the SolarMax Pro 400W 
        photovoltaic modules designed for commercial and residential applications. These high-efficiency 
        monocrystalline silicon solar panels are engineered to deliver optimal performance under 
        various environmental conditions.
        """
        story.append(Paragraph(overview_text, self.styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Technical specifications table
        story.append(Paragraph("Electrical Characteristics (STC)", self.styles['Heading2']))
        
        spec_data = [
            ['Parameter', 'Value', 'Unit', 'Tolerance'],
            ['Maximum Power (Pmax)', '400', 'W', '±3%'],
            ['Maximum Power Voltage (Vmp)', '31.2', 'V', '±3%'],
            ['Maximum Power Current (Imp)', '12.82', 'A', '±3%'],
            ['Open Circuit Voltage (Voc)', '37.8', 'V', '±3%'],
            ['Short Circuit Current (Isc)', '13.56', 'A', '±3%'],
            ['Module Efficiency', '20.4', '%', '±0.3%'],
            ['Power Temperature Coefficient', '-0.35', '%/°C', '±0.05%'],
            ['Voltage Temperature Coefficient', '-0.28', '%/°C', '±0.05%'],
            ['Current Temperature Coefficient', '+0.048', '%/°C', '±0.01%']
        ]
        
        spec_table = Table(spec_data, colWidths=[2.5*inch, 1*inch, 0.8*inch, 1*inch])
        spec_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        
        story.append(spec_table)
        story.append(Spacer(1, 20))
        
        # Mechanical specifications
        story.append(Paragraph("Mechanical Specifications", self.styles['Heading2']))
        
        mech_data = [
            ['Dimensions (L×W×H)', '2008×1002×35 mm'],
            ['Weight', '22.5 kg'],
            ['Cell Technology', 'Monocrystalline Silicon'],
            ['Number of Cells', '144 (6×24)'],
            ['Front Glass', '3.2mm tempered low-iron glass'],
            ['Frame Material', 'Anodized aluminum alloy'],
            ['Junction Box', 'IP68 rated with MC4 connectors'],
            ['Cable Length', '1200mm (+) / 1200mm (-)']
        ]
        
        mech_table = Table(mech_data, colWidths=[2.5*inch, 3*inch])
        mech_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
        ]))
        
        story.append(mech_table)
        story.append(Spacer(1, 20))
        
        # Performance curves section
        story.append(Paragraph("Performance Characteristics", self.styles['Heading2']))
        performance_text = """
        The SolarMax Pro 400W modules demonstrate excellent performance across varying irradiance 
        and temperature conditions. Peak efficiency occurs at 1000 W/m² irradiance and 25°C cell 
        temperature (Standard Test Conditions). Performance degradation is limited to less than 
        0.35% per year, ensuring reliable long-term energy production.
        """
        story.append(Paragraph(performance_text, self.styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Safety and certifications
        story.append(Paragraph("Safety and Certifications", self.styles['Heading2']))
        cert_text = """
        • IEC 61215: Design qualification and type approval for crystalline silicon PV modules<br/>
        • IEC 61730: Photovoltaic module safety qualification<br/>
        • UL 1703: Flat-plate photovoltaic modules and panels<br/>
        • IEEE 1547: Standard for interconnecting distributed resources<br/>
        • Fire Rating: Class C (UL 790)<br/>
        • Wind Load: 2400 Pa (50 psf)<br/>
        • Snow Load: 5400 Pa (113 psf)
        """
        story.append(Paragraph(cert_text, self.styles['Normal']))
        
        doc.build(story)
        print(f"Generated: {filename}")
        
    def generate_wind_regulatory_doc(self):
        """Generate wind farm regulatory compliance document"""
        filename = self.output_dir / "wind_farm_regulatory_compliance.pdf"
        doc = SimpleDocTemplate(str(filename), pagesize=letter)
        story = []
        
        # Title
        story.append(Paragraph("Wind Farm Regulatory Compliance Report", self.title_style))
        story.append(Paragraph("Prairie Wind Energy Project - Phase II", self.styles['Heading3']))
        story.append(Spacer(1, 20))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", self.styles['Heading2']))
        exec_summary = """
        This compliance report demonstrates adherence to Federal Energy Regulatory Commission (FERC) 
        requirements, North American Electric Reliability Corporation (NERC) standards, and local 
        environmental regulations for the Prairie Wind Energy Project Phase II. The 200 MW wind farm 
        consists of 67 GE Haliade-X 3.0 MW turbines and will provide clean energy to approximately 
        60,000 homes annually.
        """
        story.append(Paragraph(exec_summary, self.styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Regulatory framework table
        story.append(Paragraph("Applicable Regulations", self.styles['Heading2']))
        
        reg_data = [
            ['Regulation', 'Authority', 'Compliance Status', 'Date Verified'],
            ['NERC FAC-001-3', 'NERC', 'Compliant', '2024-01-15'],
            ['NERC FAC-002-3', 'NERC', 'Compliant', '2024-01-15'],
            ['FERC Order 2003', 'FERC', 'Compliant', '2024-01-20'],
            ['FAA Part 77', 'FAA', 'Compliant', '2024-01-10'],
            ['ESA Section 7', 'USFWS', 'Compliant', '2024-01-25'],
            ['NPDES Permit', 'EPA', 'Compliant', '2024-01-18'],
            ['State Siting Permit', 'State PSC', 'Approved', '2024-01-12']
        ]
        
        reg_table = Table(reg_data, colWidths=[1.8*inch, 1.2*inch, 1.2*inch, 1.2*inch])
        reg_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.lightblue),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        
        story.append(reg_table)
        story.append(Spacer(1, 20))
        
        # Environmental compliance
        story.append(Paragraph("Environmental Compliance", self.styles['Heading2']))
        env_text = """
        Comprehensive environmental impact assessments have been completed in accordance with the 
        National Environmental Policy Act (NEPA). Key findings include:
        
        • Avian and Bat Studies: 24-month pre-construction monitoring completed. Predicted annual 
          bird mortality rate of 2.3 birds per turbine per year, within acceptable limits.
        
        • Noise Assessment: Sound levels comply with local ordinances, with maximum levels of 
          45 dBA at nearest residence (500m from turbines).
        
        • Shadow Flicker Analysis: Maximum 30 hours per year at any residence, below the 
          30-hour threshold required by county regulations.
        
        • Wetland Delineation: All turbine locations maintain required 100-foot buffer from 
          identified wetlands. Temporary impacts during construction will be restored within 
          12 months.
        """
        story.append(Paragraph(env_text, self.styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Grid interconnection requirements
        story.append(Paragraph("Grid Interconnection Requirements", self.styles['Heading2']))
        grid_text = """
        The wind farm will interconnect to the regional transmission grid through a new 138 kV 
        transmission line and switching station. All equipment meets IEEE 1547 standards for 
        distributed resource interconnection:
        
        • Power Factor: 0.95 leading to 0.95 lagging
        • Voltage Regulation: ±5% of nominal voltage
        • Frequency Response: Primary frequency response within 10 seconds
        • Fault Ride-Through: Low/high voltage and frequency ride-through capabilities
        • Communication: DNP3 and IEC 61850 protocols for grid monitoring
        """
        story.append(Paragraph(grid_text, self.styles['Normal']))
        
        doc.build(story)
        print(f"Generated: {filename}")
        
    def generate_grid_environmental_report(self):
        """Generate power grid environmental impact report"""
        filename = self.output_dir / "transmission_environmental_impact_report.pdf"
        doc = SimpleDocTemplate(str(filename), pagesize=letter)
        story = []
        
        # Title
        story.append(Paragraph("Environmental Impact Assessment", self.title_style))
        story.append(Paragraph("High Voltage Transmission Line Project", self.styles['Heading3']))
        story.append(Spacer(1, 20))
        
        # Project overview
        story.append(Paragraph("Project Description", self.styles['Heading2']))
        project_text = """
        The proposed 345 kV transmission line will span 85 miles from the Johnson Substation to 
        the Anderson Switching Station, enhancing grid reliability and supporting renewable energy 
        integration. The project includes 187 transmission structures, two switching stations, 
        and associated access roads.
        """
        story.append(Paragraph(project_text, self.styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Environmental impacts summary
        story.append(Paragraph("Environmental Impact Summary", self.styles['Heading2']))
        
        impact_data = [
            ['Environmental Factor', 'Impact Level', 'Mitigation Measures'],
            ['Wildlife Habitat', 'Low-Moderate', 'Seasonal construction restrictions'],
            ['Wetlands', 'Minimal', 'Avoid/minimize disturbance'],
            ['Cultural Resources', 'Low', 'Archaeological surveys completed'],
            ['Air Quality', 'Temporary', 'Dust control during construction'],
            ['Noise', 'Low', 'Equipment noise limits enforced'],
            ['Visual Impact', 'Moderate', 'Structure design minimization'],
            ['Agricultural Land', 'Temporary', 'Restoration after construction'],
            ['Water Resources', 'Minimal', 'Erosion and sedimentation controls']
        ]
        
        impact_table = Table(impact_data, colWidths=[1.8*inch, 1.2*inch, 2.5*inch])
        impact_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.darkgreen),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.lightgreen),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'TOP')
        ]))
        
        story.append(impact_table)
        story.append(Spacer(1, 20))
        
        # Monitoring and compliance
        story.append(Paragraph("Environmental Monitoring Program", self.styles['Heading2']))
        monitoring_text = """
        A comprehensive environmental monitoring program will be implemented throughout construction 
        and operation phases:
        
        Pre-Construction Phase:
        • Biological surveys during spring and fall migration periods
        • Soil and groundwater quality baseline establishment  
        • Cultural resource field investigations
        • Public consultation and stakeholder engagement
        
        Construction Phase:
        • Daily environmental compliance inspections
        • Erosion and sediment control monitoring
        • Noise level measurements at sensitive receptors
        • Wildlife mortality reporting and adaptive management
        
        Operational Phase:
        • Annual vegetation monitoring for ROW maintenance
        • Bird and bat collision monitoring (first 3 years)
        • Structure inspection and maintenance scheduling
        • Long-term visual impact assessment
        """
        story.append(Paragraph(monitoring_text, self.styles['Normal']))
        
        doc.build(story)
        print(f"Generated: {filename}")
        
    def generate_transmission_equipment_manual(self):
        """Generate transmission equipment maintenance manual"""
        filename = self.output_dir / "substation_equipment_maintenance_manual.pdf"
        doc = SimpleDocTemplate(str(filename), pagesize=letter)
        story = []
        
        # Title
        story.append(Paragraph("Substation Equipment Maintenance Manual", self.title_style))
        story.append(Paragraph("345 kV Anderson Switching Station", self.styles['Heading3']))
        story.append(Spacer(1, 20))
        
        # Safety procedures
        story.append(Paragraph("Safety Procedures", self.styles['Heading2']))
        safety_text = """
        <b>WARNING:</b> All maintenance work on energized equipment must be performed by qualified 
        personnel following established safety procedures. Always verify equipment de-energization 
        and proper lockout/tagout procedures before beginning work.
        
        Personal Protective Equipment (PPE) Requirements:
        • Arc-rated clothing (minimum 40 cal/cm²)
        • Class 0 electrical gloves with leather protectors
        • Hard hat with face shield
        • Safety glasses with side shields
        • Steel-toed boots rated for electrical work
        """
        story.append(Paragraph(safety_text, self.styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Equipment maintenance schedule
        story.append(Paragraph("Preventive Maintenance Schedule", self.styles['Heading2']))
        
        maint_data = [
            ['Equipment', 'Maintenance Task', 'Frequency', 'Duration'],
            ['Circuit Breakers', 'SF6 gas pressure check', 'Monthly', '2 hours'],
            ['Circuit Breakers', 'Contact resistance test', 'Annual', '4 hours'],
            ['Power Transformers', 'Oil sampling and analysis', 'Semi-annual', '3 hours'],
            ['Power Transformers', 'Thermography inspection', 'Quarterly', '1 hour'],
            ['Disconnect Switches', 'Contact cleaning and lubrication', 'Annual', '6 hours'],
            ['Current Transformers', 'Insulation resistance test', 'Bi-annual', '2 hours'],
            ['Voltage Transformers', 'Ratio and polarity test', 'Bi-annual', '2 hours'],
            ['Lightning Arresters', 'Leakage current test', 'Annual', '1 hour'],
            ['Control Systems', 'Battery capacity test', 'Annual', '4 hours'],
            ['Protection Relays', 'Calibration and testing', 'Annual', '8 hours']
        ]
        
        maint_table = Table(maint_data, colWidths=[1.5*inch, 2*inch, 1*inch, 1*inch])
        maint_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.navy),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.lightsteelblue),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        
        story.append(maint_table)
        story.append(Spacer(1, 20))
        
        # Troubleshooting guide
        story.append(Paragraph("Troubleshooting Guide", self.styles['Heading2']))
        
        trouble_data = [
            ['Symptom', 'Possible Cause', 'Corrective Action'],
            ['Circuit breaker fails to close', 'Low SF6 pressure', 'Check gas pressure and refill'],
            ['High transformer temperature', 'Overloading or cooling system failure', 'Check loading and cooling pumps'],
            ['Protection relay false trip', 'CT saturation or settings error', 'Verify CT ratios and relay settings'],
            ['Control system malfunction', 'Battery failure or loose connections', 'Test battery and check connections'],
            ['Abnormal noise from transformer', 'Loose core or winding movement', 'Schedule detailed inspection'],
            ['High oil level in breaker', 'Temperature expansion or leak', 'Check for leaks and oil quality']
        ]
        
        trouble_table = Table(trouble_data, colWidths=[1.8*inch, 2*inch, 2*inch])
        trouble_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.red),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.mistyrose),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'TOP')
        ]))
        
        story.append(trouble_table)
        story.append(Spacer(1, 15))
        
        # Emergency procedures
        story.append(Paragraph("Emergency Response Procedures", self.styles['Heading2']))
        emergency_text = """
        In case of equipment failure or emergency conditions:
        
        1. Immediately notify system operator and control center
        2. Secure the area and prevent unauthorized access
        3. If fire is present, use CO2 or dry chemical extinguishers only
        4. For oil spills, contain spillage and notify environmental team
        5. Document all incidents and equipment conditions
        6. Do not attempt repairs on energized equipment without proper authorization
        
        Emergency Contact Numbers:
        • System Control Center: (555) 123-4567
        • Fire Department: 911
        • Environmental Response: (555) 123-4568
        • Maintenance Supervisor: (555) 123-4569
        """
        story.append(Paragraph(emergency_text, self.styles['Normal']))
        
        doc.build(story)
        print(f"Generated: {filename}")


def main():
    parser = argparse.ArgumentParser(description="Generate sample PDF documents for Energy Document AI")
    parser.add_argument('--all', action='store_true', help='Generate all sample PDFs')
    parser.add_argument('--type', choices=['technical', 'regulatory', 'environmental', 'equipment'], 
                       help='Generate specific type of PDF')
    parser.add_argument('--output', default='data/sample_pdfs', 
                       help='Output directory (default: data/sample_pdfs)')
    
    args = parser.parse_args()
    
    generator = SamplePDFGenerator(args.output)
    
    if args.all:
        generator.generate_all()
    elif args.type == 'technical':
        generator.generate_solar_technical_spec()
    elif args.type == 'regulatory':
        generator.generate_wind_regulatory_doc()
    elif args.type == 'environmental':
        generator.generate_grid_environmental_report()
    elif args.type == 'equipment':
        generator.generate_transmission_equipment_manual()
    else:
        print("Please specify --all or --type [technical|regulatory|environmental|equipment]")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())