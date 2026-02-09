Real-Time Noise Canceller GUI (Python)

This project is a **Python-based real-time noise cancellation tool** with a graphical user interface (GUI) built using Tkinter. It allows you to select your microphone and a virtual output device (like VB-Audio Cable or VoiceMeeter) to remove background noise from live audio input.

 Features

- Real-time background noise removal
- Simple and easy-to-use GUI
- Microphone and virtual output device selector
- Uses sounddevice, noisereduce, and numpy for audio processing
- Runs audio processing in a separate thread (so the UI stays responsive)

 Install dependencies
Make sure you’re using Python 3.7 or higher. Then install the required packages:
pip install sounddevice noisereduce numpy

3. Run the app
python noise_canceller.py

Requirements
Python 3.7+

VB-Audio Cable (Windows) or BlackHole (macOS) for virtual microphone

Working microphone and audio permissions

Tech Stack
Tkinter – GUI

sounddevice – Real-time audio stream

noisereduce – Noise reduction processing

numpy – Math for signal processing

threading – Keep UI responsive during live processing

Troubleshooting
No devices detected? Make sure your mic and speakers are plugged in and enabled.

App doesn't launch? Try running with admin privileges or ensure your Python environment is set up correctly.

Noise not reduced much? This tool works best for stationary background noise. Dynamic noise like talking may not be fully removed.

License
This project is open-source and free to use under the MIT License. Contributions are welcome!

Contact
If you have questions, suggestions, or want to contribute:

GitHub: SeunOriji

Email: seunoriji66@gmail.com

How It Works
1. Select your microphone as the input device.
2. Select a virtual microphone (like VB-Cable or BlackHole) as the output.
3. Click Start Noise Cancelling — the program listens through your mic, reduces noise in real time, and sends it to the virtual output.
4. Use the virtual mic as your audio input in apps like Zoom, Discord, or OBS.


Getting Started
1. Clone the repository

bash
git clone https://github.com/yourusername/noise-canceller-gui.git
cd noise-canceller-gui
Noise-cancellation-tool
