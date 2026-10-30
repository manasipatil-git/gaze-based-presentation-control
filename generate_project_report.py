# generate_project_report.py
# ─────────────────────────────────────────────────────────────────────────────
# Generates a formal Project Completion & Progress Report PDF for the Project Incharge.
# ─────────────────────────────────────────────────────────────────────────────

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.pdfgen import canvas


class ReportCanvas(canvas.Canvas):
    """Canvas with header and page numbering footer."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_footer(num_pages)
            super().showPage()
        super().save()

    def draw_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8.5)
        self.setFillColor(colors.HexColor("#555555"))
        
        # Top running header
        self.setStrokeColor(colors.HexColor("#D0D7DE"))
        self.setLineWidth(0.5)
        self.line(40, 750, 572, 750)
        self.drawString(40, 755, "FocusLock — Project Progress & Implementation Report")

        # Bottom footer
        self.line(40, 42, 572, 42)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(572, 30, page_text)
        self.drawString(40, 30, "Submitted to Project Incharge / Faculty Advisor — Computer Vision Project")
        self.restoreState()


def build_progress_report_pdf(filename="FocusLock_Progress_Report.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=55,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    # Typography styles
    title_style = ParagraphStyle(
        'RepTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'RepSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#4A5568"),
        spaceAfter=10
    )

    sec_title = ParagraphStyle(
        'SecTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=16,
        textColor=colors.HexColor("#0D3880"),
        spaceBefore=12,
        spaceAfter=5,
        keepWithNext=True
    )

    sub_sec_title = ParagraphStyle(
        'SubSecTitle',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=13.5,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )

    body = ParagraphStyle(
        'RepBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=5
    )

    bullet = ParagraphStyle(
        'RepBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.2,
        leading=13,
        textColor=colors.HexColor("#2D3748"),
        leftIndent=14,
        firstLineIndent=-9,
        spaceAfter=3
    )

    highlight_box = ParagraphStyle(
        'HighlightBox',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1A365D"),
        backColor=colors.HexColor("#EDF8FD"),
        borderColor=colors.HexColor("#BEE3F8"),
        borderWidth=1,
        borderPadding=6,
        spaceBefore=5,
        spaceAfter=7
    )

    story = []

    # ── Report Header ─────────────────────────────────────────────────────────
    story.append(Paragraph("PROJECT PROGRESS REPORT: FOCUSLOCK", title_style))
    story.append(Paragraph("A Hardware-Free Webcam-Based Gaze-Control System (Full MVP Delivered)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2B6CB0"), spaceAfter=10))

    # Meta Table (Student & Guide Info)
    meta_data = [
        [Paragraph("<b>Project Title:</b> FocusLock (Gaze-Controlled Presentation System)", body), Paragraph("<b>Delivery Phase:</b> Working MVP (All 6 Stages Completed)", body)],
        [Paragraph("<b>Domain:</b> Computer Vision, HCI, Signal Processing", body), Paragraph("<b>Tech Stack:</b> Python, OpenCV, MediaPipe, NumPy, PyAutoGUI, Pandas", body)],
        [Paragraph("<b>Current Status:</b> End-to-End Pipeline Verified in Live Testing", body), Paragraph("<b>Evaluation Milestone:</b> Ready for Live Demonstration & Defense", body)]
    ]
    t_meta = Table(meta_data, colWidths=[3.7*inch, 3.6*inch])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 8))

    # ── 1. Project Objective & Methodology ────────────────────────────────────
    story.append(Paragraph("1. Project Objective & Methodology", sec_title))
    story.append(Paragraph(
        "The objective of <b>FocusLock</b> is to develop a contact-free, low-cost presentation navigation system using only a standard laptop webcam. "
        "Commercial eye-trackers depend on expensive dedicated infrared cameras. FocusLock achieves real-time gaze tracking through a structured 6-stage software pipeline.",
        body
    ))
    story.append(Paragraph(
        "<b>Core Design Methodology:</b> MediaPipe is utilized exclusively as the low-level geometric sensor. The core intellectual and algorithmic contributions of this project "
        "are the subsequent stages developed from scratch: <b>Spatial Normalization</b>, <b>Moving-Average Jitter Filtering</b>, <b>5-Point Linear Calibration</b>, <b>Dwell-Based Intent Recognition</b>, "
        "<b>OS Actuation Integration</b>, and <b>Empirical Telemetry Benchmarking</b>.",
        highlight_box
    ))

    # ── 2. Stages Completed Summary ──────────────────────────────────────────
    story.append(Paragraph("2. Implementation Status Summary (All 6 Stages Completed)", sec_title))

    status_data = [
        ["Stage", "Module Name", "Status", "Deliverable Accomplished"],
        ["Stage 1", "Sensing & Iris Extraction", "COMPLETED", "MediaPipe 478-landmark tracking, iris centroid extraction (468/473)."],
        ["Stage 2", "Gaze Normalization & Filter", "COMPLETED", "Eye-box ratio calculation, dual-eye fusion, sliding-window jitter filter."],
        ["Stage 3", "5-Point Screen Calibration", "COMPLETED", "Interactive 5-target routine, 1D least-squares polynomial fit, JSON caching."],
        ["Stage 4", "Dwell Intent Detection", "COMPLETED", "Continuous 1.8s dwell timer state machine eliminating the 'Midas Touch' error."],
        ["Stage 5", "Presentation Controller", "COMPLETED", "PyAutoGUI slide-advance keyboard binding with safe DEMO_MODE toggle ('d')."],
        ["Stage 6", "Telemetry Logging & Plots", "COMPLETED", "Real-time CSV logging & 3-panel matplotlib benchmark analysis script."]
    ]
    t_status = Table(status_data, colWidths=[0.8*inch, 1.8*inch, 1.1*inch, 3.6*inch])
    t_status.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    story.append(t_status)
    story.append(Spacer(1, 8))

    # ── 3. Detailed Work Completed ────────────────────────────────────────────
    story.append(Paragraph("3. Detailed Pipeline Architecture & Results", sec_title))

    story.append(Paragraph("Stage 1: MediaPipe Iris & Landmark Extraction (tracking/iris_tracker.py)", sub_sec_title))
    story.append(Paragraph("• Configured MediaPipe Tasks <code>FaceLandmarker</code> with standalone 478-point model bundle (indices 468 & 473 for pupil centers), achieving 30+ FPS on CPU.", bullet))

    story.append(Paragraph("Stage 2: Gaze Normalization & Moving-Average Filter (tracking/gaze_estimator.py, filtering/moving_average.py)", sub_sec_title))
    story.append(Paragraph("• Implemented scale-invariant eye-socket boundary ratios: <code>Gaze = (Iris - Eye_min) / Eye_span</code>. Dual-eye fusion averages left and right eye vectors.", bullet))
    story.append(Paragraph("• FIFO sliding-window filter (N=7) successfully eliminates high-frequency optical sensor tremor and microsaccades.", bullet))

    story.append(Paragraph("Stage 3: 5-Point Calibration & Screen Coordinate Mapping (calibration/calibrator.py)", sub_sec_title))
    story.append(Paragraph("• 5-point target sequence (Top-L, Top-R, Center, Bottom-L, Bottom-R) maps narrow physiological iris range (0.35-0.65) to screen space [0.0, 1.0] via <code>numpy.polyfit</code> linear regression.", bullet))

    story.append(Paragraph("Stage 4: Dwell-Based Intent Detection (intent/dwell_detector.py)", sub_sec_title))
    story.append(Paragraph("• Formulated continuous 1.8s dwell state machine with single-shot lock, solving the classic 'Midas Touch' false-positive trigger problem.", bullet))

    story.append(Paragraph("Stage 5: Presentation Actuation & Safety Toggle (control/presentation_controller.py)", sub_sec_title))
    story.append(Paragraph("• Dispatches OS keyboard arrow events via PyAutoGUI. Dynamic runtime <code>DEMO_MODE</code> switch ('d' key) allows safe simulation during testing.", bullet))

    story.append(Paragraph("Stage 6: Telemetry Logging & Benchmark Graphing (data/logger.py, plot_benchmarks.py)", sub_sec_title))
    story.append(Paragraph("• Records frame telemetry (timestamp, raw X/Y, filtered X/Y, calibrated X/Y, zone, action) to <code>data/logs/gaze_log.csv</code>. Matplotlib script generates 3-panel scientific benchmark charts.", bullet))

    # ── 4. Academic Evaluation & Limitations ──────────────────────────────────
    story.append(Paragraph("4. Real-World Limitations & Evaluation Defense", sec_title))
    story.append(Paragraph(
        "<b>Honest Academic Assessment:</b><br/>"
        "1. <b>Hardware Boundaries:</b> Ordinary webcams lack IR illumination; strong ambient lighting shifts can distort eyelid contour detection.<br/>"
        "2. <b>Head Motion:</b> Pronounced head rotations introduce coordinate drift, solvable in future work via 3D head-pose homography.<br/>"
        "3. <b>Model Simplicity:</b> Linear least-squares mapping is computationally lightweight and interpretable, though a polynomial model could better capture spherical eyeball geometry.",
        highlight_box
    ))

    # Build PDF
    doc.build(story, canvasmaker=ReportCanvas)
    print(f"[FocusLock] Updated Project Progress Report PDF: {filename}")


if __name__ == "__main__":
    build_progress_report_pdf()
