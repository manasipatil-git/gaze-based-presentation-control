# generate_guidebook.py
# ─────────────────────────────────────────────────────────────────────────────
# Generates a clean, professional PDF guidebook for the FocusLock project.
# ─────────────────────────────────────────────────────────────────────────────

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Adds page numbers and running footer to every page."""
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
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#666666"))
        
        # Header rule
        self.setStrokeColor(colors.HexColor("#E0E0E0"))
        self.setLineWidth(0.5)
        self.line(40, 750, 572, 750)
        self.drawString(40, 755, "FocusLock — Technical Reference & Architecture Guidebook")

        # Footer rule
        self.line(40, 45, 572, 45)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(572, 32, page_text)
        self.drawString(40, 32, "Confidential — Educational Computer Vision Project (MVP)")
        self.restoreState()


def build_pdf(filename="FocusLock_Guidebook.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=55,
        bottomMargin=55
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#0A2540"),
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#4A5568"),
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#0A2540"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#2D3748"),
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#1A202C"),
        backColor=colors.HexColor("#EDF2F7"),
        borderColor=colors.HexColor("#CBD5E0"),
        borderWidth=0.5,
        borderPadding=5,
        spaceBefore=4,
        spaceAfter=6
    )

    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#1A365D"),
        backColor=colors.HexColor("#EBF8FF"),
        borderColor=colors.HexColor("#BEE3F8"),
        borderWidth=1,
        borderPadding=6,
        spaceBefore=6,
        spaceAfter=8
    )

    story = []

    # ── Header / Title ────────────────────────────────────────────────────────
    story.append(Paragraph("FocusLock: Engineering Guidebook", title_style))
    story.append(Paragraph("Webcam-Based Gaze Control System — Step-by-Step Architecture & Theory", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2B6CB0"), spaceAfter=12))

    # ── Executive Summary ─────────────────────────────────────────────────────
    story.append(Paragraph("1. Executive Overview & Core Philosophy", h1_style))
    story.append(Paragraph(
        "<b>FocusLock</b> is an educational computer-vision project designed to achieve hands-free computer interaction "
        "using standard webcam hardware. Unlike commercial eye-trackers (which rely on infrared illumination and specialized cameras), "
        "FocusLock uses standard RGB imagery processed through a structured 6-layer engineering pipeline.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Crucial College Demo Concept:</b> MediaPipe is <i>only the sensor</i>. The true novelty and engineering value of this project "
        "lies in the downstream stages: <b>Coordinate Normalization</b>, <b>Temporal Filtering (Jitter Reduction)</b>, "
        "<b>5-Point Linear Calibration Mapping</b>, and <b>Dwell-Based Intent Detection</b>.",
        callout_style
    ))

    # ── Full Architecture Pipeline ───────────────────────────────────────────
    story.append(Paragraph("2. Full Architectural Pipeline", h1_style))
    
    pipeline_data = [
        ["Layer", "Module", "Primary Function", "Key Math / Technique"],
        ["1. Sensing", "iris_tracker.py", "Extract 478 face & iris landmarks", "MediaPipe Tasks FaceLandmarker (RGB)"],
        ["2. Normalization", "gaze_estimator.py", "Make iris position relative to eye socket", "Ratio: (iris - min) / (max - min)"],
        ["3. Filtering", "moving_average.py", "Eliminate sensor noise & micro-saccades", "Sliding Window FIFO Mean (N=7)"],
        ["4. Calibration", "calibrator.py", "Map normalized gaze to screen coordinates", "1D Linear Least Squares (numpy.polyfit)"],
        ["5. Intent", "dwell_detector.py", "Prevent unintended clicks (Midas Touch)", "Continuous Zone Dwell Timer (1.8s)"],
        ["6. Actuation", "presentation_controller.py", "Simulate presentation keypresses", "PyAutoGUI Left/Right Arrow Dispatch"]
    ]
    
    t_pipe = Table(pipeline_data, colWidths=[1.1*inch, 1.4*inch, 2.7*inch, 2.3*inch])
    t_pipe.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
    ]))
    story.append(t_pipe)
    story.append(Spacer(1, 10))

    # ── Stage 1 Breakdown ─────────────────────────────────────────────────────
    story.append(Paragraph("3. Stage 1: Sensing & Iris Extraction", h1_style))
    story.append(Paragraph(
        "<b>Objective:</b> Capture live webcam video and locate anatomical facial features without training custom neural networks.",
        body_style
    ))
    story.append(Paragraph("<b>Detailed Technical Decisions:</b>", h2_style))
    story.append(Paragraph("• <b>Modern MediaPipe Tasks API:</b> Uses <code>FaceLandmarker</code> with <code>face_landmarker.task</code> model (~30MB), providing 478 3-D landmarks.", bullet_style))
    story.append(Paragraph("• <b>Iris Center Indices:</b> Landmark <b>468</b> represents the right iris center and landmark <b>473</b> represents the left iris center (in anatomical orientation).", bullet_style))
    story.append(Paragraph("• <b>BGR to RGB Conversion:</b> OpenCV decodes camera streams into BGR format, whereas MediaPipe models are trained on RGB tensors. <code>cv2.cvtColor()</code> is strictly mandatory.", bullet_style))
    story.append(Paragraph("• <b>Mirror Flipping:</b> We apply <code>cv2.flip(frame, 1)</code> so that moving your head to the right mirrors user intuition in the GUI.", bullet_style))

    # ── Stage 2 Breakdown ─────────────────────────────────────────────────────
    story.append(Paragraph("4. Stage 2: Gaze Normalization & Signal Smoothing", h1_style))
    story.append(Paragraph(
        "<b>Objective:</b> Transform raw pixel coordinates into a scale-invariant ratio within the eye region, and eliminate high-frequency tremor.",
        body_style
    ))
    story.append(Paragraph("<b>The Mathematical Formulation:</b>", h2_style))
    story.append(Paragraph(
        "1. <b>Eye Bounding Box Extraction:</b> We determine the minimum and maximum pixel boundaries of the eyelids:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<code>W_eye = X_max - X_min</code>,&nbsp;&nbsp;<code>H_eye = Y_max - Y_min</code>",
        body_style
    ))
    story.append(Paragraph(
        "2. <b>Normalization Formula:</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<code>Gaze_X = (Iris_X - X_min) / W_eye</code><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<code>Gaze_Y = (Iris_Y - Y_min) / H_eye</code><br/>"
        "This maps the iris to a dimensionless coordinate in <code>[0.0, 1.0]</code>. When your head shifts relative to the camera, both the eye bounding box and the iris shift concurrently, making the ratio partially head-pose invariant.",
        body_style
    ))
    story.append(Paragraph(
        "3. <b>Dual-Eye Fusion:</b> Gaze coordinates are estimated for both the left and right eyes independently and averaged: <code>Gaze = (Gaze_Left + Gaze_Right) / 2.0</code>. This halves single-eye landmark variance.",
        body_style
    ))
    story.append(Paragraph("<b>Noise & The Moving-Average Filter:</b>", h2_style))
    story.append(Paragraph(
        "Webcam gaze data suffers from <i>high-frequency jitter</i> due to optical sensor noise, lighting variations, and involuntary biological eye movements (microsaccades).<br/>"
        "We implement a sliding window filter using <code>collections.deque(maxlen=7)</code>:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<code>Filtered_Gaze(t) = (1 / N) * SUM(Raw_Gaze(t - i)) for i in [0..N-1]</code>",
        body_style
    ))
    story.append(Paragraph(
        "<b>Engineering Trade-off:</b> A larger window (e.g. N=15) yields zero jitter but introduces significant perceptual latency (sluggish response). N=7 provides an optimal compromise for 30 FPS webcam streams (~230ms lag).",
        callout_style
    ))

    # ── Stage 3 Breakdown ─────────────────────────────────────────────────────
    story.append(Paragraph("5. Stage 3: 5-Point Calibration & Screen Mapping", h1_style))
    story.append(Paragraph(
        "<b>Objective:</b> Convert physiological eye socket coordinates [0.0, 1.0] into actual user screen coordinates.",
        body_style
    ))
    story.append(Paragraph("<b>Why Calibration is Mathematically Obligatory:</b>", h2_style))
    story.append(Paragraph(
        "When looking at the far corners of a laptop screen, the physical human iris only traverses a small subset of the eye socket (typically between 0.35 and 0.65). Without calibration, the user could never reach the screen boundaries. "
        "Calibration computes the exact <b>Gain (Amplification)</b> and <b>Offset (Center Bias)</b> for that user's posture and camera angle.",
        body_style
    ))
    story.append(Paragraph("<b>The 5 Calibration Target Coordinates:</b>", h2_style))
    
    calib_table_data = [
        ["Target Name", "Target Screen Pos (X, Y)", "User Action"],
        ["1. Top-Left", "(0.15, 0.15)", "User fixes gaze on top-left bullseye for 30 frames"],
        ["2. Top-Right", "(0.85, 0.15)", "User fixes gaze on top-right bullseye for 30 frames"],
        ["3. Center", "(0.50, 0.50)", "User fixes gaze on center bullseye for 30 frames"],
        ["4. Bottom-Left", "(0.15, 0.85)", "User fixes gaze on bottom-left bullseye for 30 frames"],
        ["5. Bottom-Right", "(0.85, 0.85)", "User fixes gaze on bottom-right bullseye for 30 frames"]
    ]
    t_calib = Table(calib_table_data, colWidths=[1.5*inch, 2.0*inch, 3.8*inch])
    t_calib.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
    ]))
    story.append(t_calib)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Linear Least-Squares Regression (numpy.polyfit):</b>", h2_style))
    story.append(Paragraph(
        "We fit 1st-degree polynomial equations relating raw eye coordinates to target screen coordinates:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<code>Screen_X = m_x * Gaze_X + c_x</code><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<code>Screen_Y = m_y * Gaze_Y + c_y</code><br/>"
        "Parameters are saved persistently to <code>calibration.json</code> so calibration persists across application restarts.",
        body_style
    ))

    # ── Stage 4-6 Roadmap ─────────────────────────────────────────────────────
    story.append(Paragraph("6. Remaining Pipeline Roadmap (Stages 4, 5, 6)", h1_style))
    story.append(Paragraph("• <b>Stage 4 (Dwell Intent Detection):</b> Implements a continuous timer (1.8s) when calibrated gaze resides inside the left (0–15%) or right (85–100%) trigger zones to solve the <i>Midas Touch</i> problem.", bullet_style))
    story.append(Paragraph("• <b>Stage 5 (Presentation Control):</b> Connects PyAutoGUI to emit actual <code>LEFT</code> / <code>RIGHT</code> keyboard events, guarded by a safe <code>DEMO_MODE</code> flag.", bullet_style))
    story.append(Paragraph("• <b>Stage 6 (Logging & Evaluation):</b> Exports real frame-by-frame gaze coordinates to CSV (<code>data/logs/gaze_log.csv</code>) for quantitative error and latency plots.", bullet_style))

    # ── Viva Q&A Cheatsheet ───────────────────────────────────────────────────
    story.append(Paragraph("7. Viva & Demonstration Q&A Cheatsheet", h1_style))
    
    qa_data = [
        [
            Paragraph("<b>Question from Evaluator</b>", body_style),
            Paragraph("<b>Strong Engineering Response</b>", body_style)
        ],
        [
            Paragraph("Why did you not use a Deep Learning classifier for gaze?", body_style),
            Paragraph("Custom neural networks require thousands of labeled user gaze images and high GPU compute. Our geometric pipeline (MediaPipe landmarks + relative normalization + linear calibration) is lightweight, runs in real-time on CPU at 30+ FPS, and provides explicit mathematical interpretability.", body_style)
        ],
        [
            Paragraph("What is the 'Midas Touch' problem in gaze interaction?", body_style),
            Paragraph("The human eye is primarily a sensory organ, not an actuator. Everywhere the user looks cannot trigger a click. Dwell-time intent detection ensures only deliberate, sustained focus triggers a system command.", body_style)
        ],
        [
            Paragraph("What are the real-world limitations of this system?", body_style),
            Paragraph("1. Variable room illumination alters eyelid contours.<br/>2. Severe head rotations cause calibration drift.<br/>3. Eyeglasses reflections can briefly occlude iris landmarks.<br/>4. First-order linear mapping assumes flat planar projection rather than spherical eye geometry.", body_style)
        ]
    ]

    t_qa = Table(qa_data, colWidths=[2.5*inch, 4.8*inch])
    t_qa.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A365D")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_qa)

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[FocusLock] Guidebook PDF successfully built: {filename}")


if __name__ == "__main__":
    build_pdf()
