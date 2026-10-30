# generate_guidebook.py
# ─────────────────────────────────────────────────────────────────────────────
# Generates a clean, professional PDF guidebook for the FocusLock project.
# Covers all 6 engineering stages in full detail.
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
        fontSize=14,
        leading=17,
        textColor=colors.HexColor("#0A2540"),
        spaceBefore=14,
        spaceAfter=5,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=9,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9.2,
        leading=13,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.0,
        leading=12.5,
        textColor=colors.HexColor("#2D3748"),
        leftIndent=14,
        firstLineIndent=-9,
        spaceAfter=3
    )

    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9.0,
        leading=12.5,
        textColor=colors.HexColor("#1A365D"),
        backColor=colors.HexColor("#EBF8FF"),
        borderColor=colors.HexColor("#BEE3F8"),
        borderWidth=1,
        borderPadding=6,
        spaceBefore=5,
        spaceAfter=7
    )

    story = []

    # ── Header / Title ────────────────────────────────────────────────────────
    story.append(Paragraph("FocusLock: Engineering Guidebook", title_style))
    story.append(Paragraph("Webcam-Based Gaze Control System — Complete 6-Stage Architecture & Viva Reference", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2B6CB0"), spaceAfter=10))

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
        "<b>5-Point Linear Calibration Mapping</b>, <b>Dwell-Based Intent Detection</b>, <b>OS Actuation Integration</b>, and <b>Empirical Telemetry Benchmarking</b>.",
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
        ["6. Actuation", "presentation_controller.py", "Simulate presentation keypresses", "PyAutoGUI Left/Right Arrow Dispatch"],
        ["7. Telemetry", "logger.py / plot_benchmarks.py", "Frame logging & scientific graphing", "Pandas CSV logging & Matplotlib plots"]
    ]
    
    t_pipe = Table(pipeline_data, colWidths=[1.0*inch, 1.4*inch, 2.6*inch, 2.5*inch])
    t_pipe.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
    ]))
    story.append(t_pipe)
    story.append(Spacer(1, 8))

    # ── Stage 1 Breakdown ─────────────────────────────────────────────────────
    story.append(Paragraph("3. Stage 1: Sensing & Iris Extraction", h1_style))
    story.append(Paragraph("• <b>Modern MediaPipe Tasks API:</b> Uses <code>FaceLandmarker</code> with standalone <code>face_landmarker.task</code> model bundle (~30MB), providing 478 3-D landmarks.", bullet_style))
    story.append(Paragraph("• <b>Iris Center Indices:</b> Landmark <b>468</b> represents the right iris center and landmark <b>473</b> represents the left iris center (in anatomical orientation).", bullet_style))
    story.append(Paragraph("• <b>BGR to RGB:</b> OpenCV decodes in BGR; MediaPipe requires RGB (<code>cv2.cvtColor</code> is mandatory).", bullet_style))

    # ── Stage 2 Breakdown ─────────────────────────────────────────────────────
    story.append(Paragraph("4. Stage 2: Gaze Normalization & Signal Smoothing", h1_style))
    story.append(Paragraph("• <b>Spatial Normalization:</b> <code>Gaze_X = (Iris_X - X_min) / (X_max - X_min)</code> maps iris inside [0.0, 1.0]. Because both the eyelid bbox and iris shift during head movement, the ratio remains partially head-pose invariant.", bullet_style))
    story.append(Paragraph("• <b>Dual-Eye Fusion:</b> Averages left and right eye vectors to mitigate unilateral eyelid occlusion.", bullet_style))
    story.append(Paragraph("• <b>Moving Average Filter:</b> FIFO sliding-window (N=7 frames) cancels high-frequency sensor noise and microsaccadic tremor with ~230ms perceptual latency.", bullet_style))

    # ── Stage 3 Breakdown ─────────────────────────────────────────────────────
    story.append(Paragraph("5. Stage 3: 5-Point Calibration & Screen Mapping", h1_style))
    story.append(Paragraph("• <b>Why Required:</b> Physiological iris rotation only spans a narrow band (0.35 to 0.65) in normalized space. Calibration calculates user-specific Gain ($m$) and Offset ($c$).", bullet_style))
    story.append(Paragraph("• <b>Linear Regression:</b> <code>X_screen = m_x * Gaze_X + c_x</code> via <code>numpy.polyfit</code> across 5 target targets, saved in <code>calibration.json</code>.", bullet_style))

    # ── Stage 4 Breakdown ─────────────────────────────────────────────────────
    story.append(Paragraph("6. Stage 4: Dwell-Based Intent Detection", h1_style))
    story.append(Paragraph("• <b>The Midas Touch Problem:</b> Human eyes are perceptual organs. Looking at the screen edge must not fire instant commands. We enforce a continuous 1.8s dwell threshold.", bullet_style))
    story.append(Paragraph("• <b>Single-Shot Trigger Protection:</b> Once 1.8s elapses, the action fires exactly once and locks further triggers until the user looks away from the zone.", bullet_style))

    # ── Stage 5 Breakdown ─────────────────────────────────────────────────────
    story.append(Paragraph("7. Stage 5: Presentation Control & DEMO_MODE Safety", h1_style))
    story.append(Paragraph("• <b>PyAutoGUI Actuation:</b> Maps <code>NEXT_SLIDE</code> $\to$ Right Arrow, and <code>PREV_SLIDE</code> $\to$ Left Arrow.", bullet_style))
    story.append(Paragraph("• <b>DEMO_MODE Safety Toggle ('d' key):</b> Allows testing without sending active keystrokes to other open computer windows.", bullet_style))

    # ── Stage 6 Breakdown ─────────────────────────────────────────────────────
    story.append(Paragraph("8. Stage 6: Telemetry Logging & Benchmark Graphing", h1_style))
    story.append(Paragraph("• <b>Frame Logging:</b> Writes timestamp, raw, filtered, calibrated coords, zone, and actions to <code>data/logs/gaze_log.csv</code>.", bullet_style))
    story.append(Paragraph("• <b>Matplotlib Benchmark:</b> <code>plot_benchmarks.py</code> generates 3-panel scientific figures (Raw vs. Filtered jitter reduction, Calibrated timeline with action markers, and 2D spatial trajectory).", bullet_style))

    # ── Viva Q&A Cheatsheet ───────────────────────────────────────────────────
    story.append(Paragraph("9. Viva & Demonstration Q&A Cheatsheet", h1_style))
    
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

    t_qa = Table(qa_data, colWidths=[2.3*inch, 4.8*inch])
    t_qa.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A365D")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_qa)

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[FocusLock] Complete Guidebook PDF successfully built: {filename}")


if __name__ == "__main__":
    build_pdf()
