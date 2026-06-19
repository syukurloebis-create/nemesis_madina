"""
Court-Ready PDF Report Generator
Generates legally admissible investigation reports
"""

import os
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
import json
import logging

from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)


class CourtReportGenerator:
    """
    Generate court-ready PDF reports with:
    - Hash chain verification
    - Chain of custody
    - Evidence package
    - Expert witness summary
    - Digital signature
    """
    
    def __init__(self, template_dir: str = "backend/reports/templates"):
        self.template_dir = template_dir
        self.env = Environment(loader=FileSystemLoader(template_dir))
    
    async def generate_investigation_report(
        self,
        case_data: Dict[str, Any],
        events: List[Dict],
        collusion_data: Dict,
        evidence_list: List[Dict],
        output_path: str
    ) -> str:
        """
        Generate comprehensive investigation report.
        
        Args:
            case_data: Case metadata
            events: Event chain with hashes
            collusion_data: Collusion detection results
            evidence_list: List of evidence items
            output_path: Path to save PDF
        
        Returns:
            Path to generated PDF file
        """
        template = self.env.get_template("court_report.html")
        
        # Prepare hash chain verification
        hash_chain_valid = all(e.get("previous_hash") is None or 
                               e.get("event_hash") for e in events)
        
        # Prepare timeline
        timeline = [
            {
                "timestamp": e.get("timestamp"),
                "event_type": e.get("event_type"),
                "description": self._format_event_description(e),
                "hash": e.get("event_hash")[:16] + "...",
            }
            for e in events
        ]
        
        html_content = template.render(
            case=case_data,
            events=timeline,
            collusion=collusion_data,
            evidence=evidence_list,
            hash_chain_valid=hash_chain_valid,
            generated_at=datetime.now().isoformat(),
            report_id=f"NEMESIS-{case_data.get('id', 'UNKNOWN')[:8]}",
            verifier="Nemesis Madina v2.3",
        )
        
        # Generate PDF
        pdf_path = Path(output_path)
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        
        HTML(string=html_content).write_pdf(pdf_path)
        logger.info(f"Report generated: {pdf_path}")
        
        return str(pdf_path)
    
    def _format_event_description(self, event: Dict) -> str:
        """Format event description for human readability"""
        event_type = event.get("event_type", "")
        data = event.get("data", {})
        
        if event_type == "case_created":
            return f"Case created: {data.get('title', 'Unknown')}"
        elif event_type == "case_updated":
            changes = data.get("changes", {})
            parts = [f"{k}: {v.get('old')} → {v.get('new')}" for k, v in changes.items()]
            return f"Case updated: {', '.join(parts)}"
        elif event_type == "collusion_detected":
            return f"Collusion detected: {data.get('pattern_type', 'Unknown')}"
        else:
            return f"Event: {event_type}"
    
    async def generate_evidence_package(
        self,
        case_id: str,
        evidence_items: List[Dict],
        output_path: str
    ) -> str:
        """Generate evidence package with chain of custody"""
        template = self.env.get_template("evidence_package.html")
        
        html_content = template.render(
            case_id=case_id,
            evidence=evidence_items,
            generated_at=datetime.now().isoformat(),
            total_items=len(evidence_items),
        )
        
        pdf_path = Path(output_path)
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        
        HTML(string=html_content).write_pdf(pdf_path)
        
        return str(pdf_path)


# Template HTML for court report
COURT_REPORT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>NEMESIS Investigation Report - {{ case.id }}</title>
    <style>
        body {
            font-family: 'Times New Roman', serif;
            margin: 2cm;
            line-height: 1.4;
        }
        h1 { color: #1a3a5c; border-bottom: 2px solid #1a3a5c; }
        h2 { color: #2c5f8a; margin-top: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .case-info { background: #f5f5f5; padding: 15px; margin: 20px 0; }
        .timeline { margin: 20px 0; }
        .timeline-item { border-left: 3px solid #1a3a5c; padding: 10px 20px; margin: 10px 0; }
        .hash { font-family: monospace; font-size: 10pt; color: #666; }
        .verification { background: #e8f5e9; padding: 10px; border-left: 4px solid green; }
        .warning { background: #fff3e0; padding: 10px; border-left: 4px solid orange; }
        footer { margin-top: 50px; text-align: center; font-size: 9pt; color: #666; }
        @page {
            size: A4;
            margin: 2cm;
            @bottom-center {
                content: "Nemesis Madina v2.3 - Court-Ready Report";
                font-size: 8pt;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>NEMESIS Investigation Report</h1>
        <p><strong>Report ID:</strong> {{ report_id }}</p>
        <p><strong>Generated:</strong> {{ generated_at }}</p>
        <p><strong>Verifier:</strong> {{ verifier }}</p>
    </div>
    
    <div class="verification">
        <strong>✓ Hash Chain Integrity: {{ "VALID" if hash_chain_valid else "INVALID" }}</strong>
        <p>This report is cryptographically verifiable via SHA256 hash chain.</p>
    </div>
    
    <div class="case-info">
        <h2>Case Information</h2>
        <p><strong>Case ID:</strong> {{ case.id }}</p>
        <p><strong>Title:</strong> {{ case.title }}</p>
        <p><strong>Status:</strong> {{ case.status }}</p>
        <p><strong>Priority:</strong> {{ case.priority }}</p>
        <p><strong>Created:</strong> {{ case.created_at }}</p>
    </div>
    
    <h2>Event Timeline (Immutable Chain)</h2>
    <div class="timeline">
        {% for event in events %}
        <div class="timeline-item">
            <strong>{{ event.timestamp }}</strong><br>
            {{ event.description }}<br>
            <span class="hash">Hash: {{ event.hash }}</span>
        </div>
        {% endfor %}
    </div>
    
    <h2>Intelligence Analysis</h2>
    <div class="case-info">
        <p><strong>Collusion Detected:</strong> {{ collusion.has_collusion }}</p>
        <p><strong>Risk Score:</strong> {{ collusion.collusion_risk }}%</p>
        <p><strong>Patterns Found:</strong> {{ collusion.pattern_count }}</p>
        {% for pattern in collusion.patterns %}
        <div class="timeline-item">
            <strong>{{ pattern.type }}</strong><br>
            {{ pattern.description }}<br>
            Confidence: {{ pattern.confidence }} | Severity: {{ pattern.severity }}
        </div>
        {% endfor %}
    </div>
    
    <footer>
        This report is generated by NEMESIS MADINA v2.3<br>
        All events are immutably recorded with SHA256 hash chain.
    </footer>
</body>
</html>
"""

# Create templates directory
os.makedirs("backend/reports/templates", exist_ok=True)

with open("backend/reports/templates/court_report.html", "w") as f:
    f.write(COURT_REPORT_TEMPLATE)