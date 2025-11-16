import sys
import os
import time
import whisper
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QProgressBar, QTextEdit,
    QFileDialog, QMessageBox, QComboBox
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont

# --- 1. Worker Thread for Transcription ---


class WhisperWorker(QThread):
    """
    Worker thread to run the time-consuming Whisper transcription process 
    without freezing the main PyQt5 GUI.
    """
    # Signals for communication with the main thread
    started_transcription = pyqtSignal(str)
    progress_update = pyqtSignal(str)
    transcription_complete = pyqtSignal(str)
    transcription_error = pyqtSignal(str)

    def __init__(self, audio_path, model_name):
        super().__init__()
        self.audio_path = audio_path
        self.model_name = model_name

    def run(self):
        """
        Main execution method for the thread. Runs the Whisper model.
        """
        if not os.path.exists(self.audio_path):
            self.transcription_error.emit(
                f"Audio file not found at '{self.audio_path}'.")
            return

        self.started_transcription.emit(
            f"Loading Whisper model: {self.model_name}...")

        try:
            # Load the model. fp16=False for stable CPU usage.
            # This can take significant time on the first run as it downloads the model weights.
            model = whisper.load_model(self.model_name)
            device = model.device
            self.progress_update.emit(
                f"Model loaded successfully. Running on device: {device}. Starting transcription...")

            start_time = time.time()

            # --- Transcription Core ---
            # NOTE: Whisper's verbose=True prints directly to the console/thread stdout,
            # but we cannot capture intermediate segment progress easily.
            # We rely on the initial and final messages.
            result = model.transcribe(self.audio_path, fp16=False)

            end_time = time.time()
            elapsed_time = end_time - start_time

            full_transcript = result["text"]

            # Save the full transcript to a file
            base_name = os.path.splitext(os.path.basename(self.audio_path))[0]
            output_filename = f"{base_name}_{self.model_name}_transcript.txt"

            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(full_transcript)

            summary = (f"Transcription complete in {elapsed_time:.2f} seconds.\n"
                       f"Result saved to: {output_filename}\n\n"
                       f"Full Transcript:\n{full_transcript}")

            self.transcription_complete.emit(summary)

        except Exception as e:
            # Handle model loading issues, file access errors, etc.
            self.transcription_error.emit(
                f"An unexpected error occurred: {e}. Check FFmpeg installation and file permissions.")

# --- 2. Main Application Window ---


class TranscriberApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Whisper Audio Transcriber Pro")
        self.setGeometry(100, 100, 800, 600)
        self.worker = None
        self.init_ui()

    def init_ui(self):
        # Apply Tailwind-like styling via QSS for a modern look
        self.setStyleSheet("""
            QMainWindow { background-color: #f7f9fb; }
            QWidget { background-color: #ffffff; border-radius: 8px; }
            QLabel { font-size: 14px; color: #333; }
            QPushButton {
                background-color: #4f46e5;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #4338ca; }
            QPushButton:disabled { background-color: #a5b4fc; }
            QLineEdit, QComboBox, QTextEdit {
                border: 1px solid #d1d5db;
                padding: 8px;
                border-radius: 6px;
                font-size: 14px;
            }
            QProgressBar {
                text-align: center;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                background-color: #e5e7eb;
            }
            QProgressBar::chunk {
                background-color: #10b981;
                border-radius: 8px;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)

        # Title
        title_label = QLabel("Whisper AI Transcriber")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # --- Input Section ---
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        input_layout.setContentsMargins(20, 20, 20, 20)

        # Audio Path Input
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText(
            "Select the audio file (.mp3, .wav, .m4a, etc.)")
        self.path_input.setReadOnly(True)
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.select_audio_file)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_btn)

        # Model Selection
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Select Model Size:"))
        self.model_combo = QComboBox()
        # 'small' and 'base' are fast; 'medium' is the best accuracy/speed trade-off on CPU
        self.model_combo.addItems(["base", "small", "medium", "large-v2"])
        self.model_combo.setCurrentText("medium")
        model_layout.addWidget(self.model_combo)
        model_layout.addStretch(1)

        input_layout.addLayout(path_layout)
        input_layout.addLayout(model_layout)

        main_layout.addWidget(input_widget)

        # --- Control and Status Section ---
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)
        control_layout.setContentsMargins(20, 20, 20, 20)

        # Action Button
        self.transcribe_btn = QPushButton("Start Transcription")
        self.transcribe_btn.clicked.connect(self.start_transcription)
        control_layout.addWidget(self.transcribe_btn)

        # Progress Bar and Status Label
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)

        self.status_label = QLabel("Ready to transcribe.")
        self.status_label.setWordWrap(True)

        control_layout.addWidget(self.progress_bar)
        control_layout.addWidget(self.status_label)

        main_layout.addWidget(control_widget)

        # --- Output Log ---
        output_widget = QWidget()
        output_layout = QVBoxLayout(output_widget)
        output_layout.setContentsMargins(20, 20, 20, 20)
        output_layout.addWidget(QLabel("Transcription Output:"))

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText(
            "Transcription results and process logs will appear here.")

        output_layout.addWidget(self.output_text)
        main_layout.addWidget(output_widget)

        # Initial status setup
        self.update_ui_state(True)
        self.output_text.setText(
            "⚠️ **Prerequisite:** Ensure FFmpeg is installed and accessible on your system for Whisper to process audio files correctly.")

    def select_audio_file(self):
        """Opens file dialog to select an audio file."""
        # Use QFileDialog to get the file path
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio File",
            "",
            "Audio Files (*.mp3 *.wav *.m4a *.mp4);;All Files (*)"
        )
        if filepath:
            self.path_input.setText(filepath)

    def update_ui_state(self, is_ready):
        """Controls which UI elements are enabled/disabled based on app state."""
        self.browse_btn.setEnabled(is_ready)
        self.path_input.setEnabled(is_ready)
        self.model_combo.setEnabled(is_ready)
        self.transcribe_btn.setEnabled(is_ready)

        if is_ready:
            self.transcribe_btn.setText("Start Transcription")
            self.progress_bar.setVisible(False)

        else:
            self.transcribe_btn.setText("Processing...")
            self.progress_bar.setRange(0, 0)  # Indeterminate progress bar
            self.progress_bar.setVisible(True)

    def start_transcription(self):
        """Initializes and starts the worker thread."""
        audio_path = self.path_input.text()
        model_name = self.model_combo.currentText()

        if not audio_path or not os.path.exists(audio_path):
            QMessageBox.warning(
                self, "Input Error", "Please select a valid audio file before starting transcription.")
            return

        self.update_ui_state(False)
        self.output_text.clear()
        self.status_label.setText("Starting process...")

        # Instantiate the worker thread with input parameters
        self.worker = WhisperWorker(audio_path, model_name)

        # Connect signals to slots (methods in the main thread)
        self.worker.started_transcription.connect(self.handle_started)
        self.worker.progress_update.connect(self.handle_progress)
        self.worker.transcription_complete.connect(self.handle_complete)
        self.worker.transcription_error.connect(self.handle_error)

        # Start the thread
        self.worker.start()

    # --- Signal Handlers (Slots) ---

    def handle_started(self, message):
        """Updates UI when the thread officially starts."""
        self.status_label.setText(message)

    def handle_progress(self, message):
        """Updates status label with ongoing progress."""
        self.status_label.setText(message)

    def handle_complete(self, summary):
        """Handles successful transcription completion."""
        self.output_text.setText(summary)
        self.status_label.setText(
            "✅ Transcription Finished! Output saved to disk.")
        self.update_ui_state(True)
        # Clean up the worker thread
        self.worker = None

    def handle_error(self, message):
        """Handles any errors from the worker thread."""
        self.status_label.setText(f"ERROR: {message}")
        QMessageBox.critical(self, "Transcription Error", message)
        self.update_ui_state(True)
        # Clean up the worker thread
        self.worker = None


if __name__ == "__main__":
    # --- FIX: DPI scaling must be set BEFORE the QApplication is created ---
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)

    window = TranscriberApp()
    window.show()
    sys.exit(app.exec_())
