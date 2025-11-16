# 🎙️ Whisper Audio Transcriber Pro

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/PyQt5-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![Whisper AI](https://img.shields.io/badge/OpenAI_Whisper-009A8F?style=for-the-badge&logo=openai&logoColor=white)

A desktop application built with Python and the powerful **OpenAI Whisper model** for fast, high-accuracy audio and video transcription. The application uses a multi-threaded architecture (PyQt5 `QThread`) to ensure the graphical user interface (GUI) remains responsive while the intensive transcription process runs in the background.

---

## ✨ Features

* **Fast & Accurate Transcription:** Leverages the state-of-the-art Whisper AI model.
* **Responsive GUI:** Built with PyQt5, the application uses a separate worker thread to prevent the UI from freezing during transcription (which can take minutes depending on file size).
* **Model Selection:** Allows users to select different model sizes (`base`, `small`, `medium`, `large-v2`) to balance speed and accuracy.
* **Output Management:** Automatically saves the full transcript to a dedicated `.txt` file named after the input audio.
* **Cross-Platform:** Developed using standard Python libraries, designed to run on Windows, macOS, and Linux.

---

## 💻 Installation

### Prerequisites

1.  **Python 3.x:** Ensure you have Python installed.
2.  **FFmpeg:** The Whisper model relies on FFmpeg for handling various audio formats.
    * **Windows/Linux/macOS:** You must install FFmpeg and ensure it is available in your system's PATH. ([Instructions for FFmpeg installation](https://ffmpeg.org/download.html)).

### Setup Steps

1.  **Clone the Repository:**

    ```bash
    git clone [https://github.com/MrRajiii/Whisper-Transcriber-App.git](https://github.com/MrRajiii/Whisper-Transcriber-App.git)
    cd Whisper-Transcriber-App
    ```

2.  **Create and Activate a Virtual Environment:** (Recommended best practice)

    ```bash
    # Create the environment
    python -m venv .venv

    # Activate the environment (Windows)
    .venv\Scripts\activate

    # Activate the environment (macOS/Linux)
    source .venv/bin/activate
    ```

3.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

---

## 🚀 Usage

1.  **Run the Application:**

    ```bash
    python transcriber_app.py
    ```

2.  **Select Audio:** Click the **"Browse"** button to select an audio or video file (`.mp3`, `.wav`, `.m4a`, `.mp4`, etc.).

3.  **Choose Model:** Select your preferred model size (e.g., `small` for speed, `medium` for better quality).

4.  **Start Transcription:** Click **"Start Transcription"**. The status label and progress bar will update while the AI model processes the file in the background.

5.  **View Output:** Once complete, the full transcript will appear in the output log and be saved as a `.txt` file in the same directory as the source audio.
