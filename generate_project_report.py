# generate_project_report.py
# ─────────────────────────────────────────────────────────────────────────────
# Generates a formal Project Progress Report PDF for the Project Incharge.
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
    story.append(Paragraph("A Hardware-Free Webcam-Based Gaze-Control System", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2B6CB0"), spaceAfter=10))

    # Meta Table (Student & Guide Info)
    meta_data = [
        [Paragraph("<b>Project Title:</b> FocusLock (Gaze-Controlled Presentation System)", body), Paragraph("<b>Date:</b> Academic Term Progress", body)],
        [Paragraph("<b>Domain:</b> Computer Vision, HCI, Signal Processing", body), Paragraph("<b>Tech Stack:</b> Python, OpenCV, MediaPipe, NumPy", body)],
        [Paragraph("<b>Current Status:</b> Stages 1, 2, 3 Implemented & Verified (Working MVP)", body), Paragraph("<b>Target Delivery:</b> 6-Stage Working Demonstration", body)]
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
        "are the subsequent stages developed from scratch: <b>Spatial Normalization</b>, <b>Moving-Average Jitter Filtering</b>, <b>5-Point Linear Calibration</b>, and <b>Dwell-Based Intent Recognition</b>.",
        highlight_box
    ))

    # ── 2. Stages Planned vs Status ──────────────────────────────────────────
    story.append(Paragraph("2. Implementation Status Summary", sec_title))

    status_data = [
        ["Stage", "Module Name", "Status", "Deliverable Accomplished"],
        ["Stage 1", "Sensing & Iris Extraction", "COMPLETED", "MediaPipe 478-landmark tracking, iris centroid extraction (468/473)."],
        ["Stage 2", "Gaze Normalization & Filter", "COMPLETED", "Eye-box ratio calculation, dual-eye fusion, sliding-window jitter filter."],
        ["Stage 3", "5-Point Screen Calibration", "COMPLETED", "Interactive 5-target routine, 1D least-squares polynomial fit, JSON caching."],
        ["Stage 4", "Dwell Intent Detection", "IN PROGRESS", "Continuous 1.8s dwell timer logic to eliminate the 'Midas Touch' error."],
        ["Stage 5", "Presentation Controller", "NEXT PHASE", "PyAutoGUI slide-advance keyboard binding with safe DEMO_MODE toggle."],
        ["Stage 6", "Telemetry Logging & Plots", "NEXT PHASE", "CSV real-time coordinate logger for empirical latency & precision graphs."]
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

    # ── 3. Detailed Work Completed So Far ─────────────────────────────────────
    story.append(Paragraph("3. Detailed Work Completed (Stages 1 – 3)", sec_title))

    # Stage 1
    story.append(Paragraph("Stage 1: MediaPipe Iris & Landmark Extraction (tracking/iris_tracker.py)", sub_sec_title))
    story.append(Paragraph("• <b>Modern MediaPipe Tasks API:</b> Configured <code>FaceLandmarker</code> with the standalone 478-point <code>face_landmarker.task</code> model bundle, resolving Python 3.13 compatibility.", bullet))
    story.append(Paragraph("• <b>Iris Coordinates:</b> Extracted pixel centroids for right iris (Index 468) and left iris (Index 473).", bullet))
    story.append(Paragraph("• <b>Real-Time Visual Feedback:</b> Integrated dynamic HUD overlay rendering live FPS, face detection confidence, and pupil indicators.", bullet))

    # Stage 2
    story.append(Paragraph("Stage 2: Gaze Normalization & Moving-Average Filter (tracking/gaze_estimator.py, filtering/moving_average.py)", sub_sec_title))
    story.append(Paragraph("• <b>Mathematical Normalization:</b> Formulated scale-invariant ratios within the eye bounding box: <code>Gaze_X = (Iris_X - X_min) / (X_max - X_min)</code>. This ensures head movements do not distort eye-relative measurements.", bullet))
    story.append(Paragraph("• <b>Dual-Eye Fusion:</b> Averaged left and right eye vectors to mitigate unilateral eyelid occlusion.", bullet))
    story.append(Paragraph("• <b>Jitter Reduction Filter:</b> Implemented a FIFO sliding-window moving average filter (Window Size N=7). This successfully eliminates high-frequency sensor tremor and microsaccades with minimal perceptual latency (~230ms).", bullet))
    story.append(Paragraph("• <b>Visual Gaze Radar:</b> Created a real-time 2D radar HUD visually comparing RAW (Red) vs FILTERED (Green) gaze trajectories.", bullet))

    # Stage 3
    story.append(Paragraph("Stage 3: 5-Point Calibration & Screen Coordinate Mapping (calibration/calibrator.py, ui/overlay.py)", sub_sec_title))
    story.append(Paragraph("• <b>Why Calibration Was Essential:</b> Physiological eye rotation across a monitor only spans a narrow band (0.35 to 0.65) in normalized space. Calibration amplifies and shifts this range to cover the full screen [0.0, 1.0].", bullet))
    story.append(Paragraph("• <b>5-Target Routine:</b> Built an interactive state machine displaying Top-Left, Top-Right, Center, Bottom-Left, and Bottom-Right visual targets, collecting 30 sample frames per point.", bullet))
    story.append(Paragraph("• <b>Linear Regression Mapping:</b> Computed optimal gain (m) and offset (c) per axis using <code>numpy.polyfit</code>: <code>X_screen = m_x * Gaze_X + c_x</code>.", bullet))
    story.append(Paragraph("• <b>Persistence:</b> Calibration coefficients and target centroids are saved in <code>calibration.json</code> for instant re-use.", bullet))
    story.append(Paragraph("• <b>Interactive Overlay:</b> Rendered calibrated crosshairs and defined left (0-15%) and right (85-100%) trigger zones on the live camera viewport.", bullet))

    # ── 4. Key Engineering Problem Solved ─────────────────────────────────────
    story.append(Paragraph("4. Key Technical Challenge & Solution", sec_title))
    story.append(Paragraph(
        "<b>Challenge:</b> In Python 3.13 and MediaPipe 0.10.x, the legacy <code>mediapipe.solutions</code> API was completely deprecated, causing runtime import crashes.<br/>"
        "<b>Solution:</b> Re-engineered the tracking subsystem to interface with the modern <b>MediaPipe Tasks Python API</b> (<code>mediapipe.tasks.python.vision.FaceLandmarker</code>), including automated model asset caching and explicit landmark connection rendering.",
        highlight_box
    ))

    # ── 5. Next Immediate Steps ───────────────────────────────────────────────
    story.append(Paragraph("5. Next Immediate Steps (To Complete MVP)", sec_title))
    story.append(Paragraph("1. <b>Stage 4 (Dwell Intent Detection):</b> Implement continuous timer thresholding (1.8s) when gaze enters trigger zones to prevent accidental activations.", bullet))
    story.append(Paragraph("2. <b>Stage 5 (Presentation Actuation):</b> Integrate <code>pyautogui.press('right')</code> / <code>pyautogui.press('left')</code> with a safe <code>DEMO_MODE</code> toggle.", bullet))
    story.append(Paragraph("3. <b>Stage 6 (Telemetry Logging & Benchmark Report):</b> Log real-time frame telemetry to CSV and plot quantitative accuracy curves for the final viva presentation.", bullet))

    # Build PDF
    doc.build(story, canvasmaker=ReportCanvas)
    print(f"[FocusLock] Project Progress Report PDF created: {filename}")


if __name__ == "__main__":
    build_progress_report_pdf()
