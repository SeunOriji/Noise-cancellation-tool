import tkinter as tk  # Imports the base Tkinter module used for creating graphical user interfaces (GUI)
from tkinter import ttk, messagebox  # Imports themed widgets (ttk) for a modern look and messagebox for showing alert popups
import threading  # Allows certain parts of the program (like audio processing) to run in parallel without freezing the interface
import sounddevice as sd  # Used to access and stream audio from microphones and to speakers
import noisereduce as nr  # A library that reduces background noise from audio in real-time
import numpy as np  # Numerical library used to perform math on audio signals efficiently

# This class handles the actual process of removing background noise from the microphone in real time
class NoiseCanceller:
    def __init__(self, input_device, output_device):
        self.input_device = input_device  # Stores the ID of the microphone the user selected
        self.output_device = output_device  # Stores the ID of the output device (usually a virtual microphone)
        self.stream = None  # Placeholder for the audio stream object that will be created later
        self.running = False  # Boolean flag to indicate whether the stream is active or not
        self.thread = None  # Reference to the background thread that runs audio processing

        # Gather info about the selected microphone and speaker
        input_info = sd.query_devices(input_device)  # Fetches capabilities of the input device
        output_info = sd.query_devices(output_device)  # Fetches capabilities of the output device

        # Get the number of channels (like mono = 1, stereo = 2), ensure at least 1
        self.input_channels = max(1, input_info['max_input_channels'])
        self.output_channels = max(1, output_info['max_output_channels'])

    # This function is automatically called to handle chunks of audio as they arrive. Processes each audio chunk to reduce noise in real-time.
    def _callback(self, indata, outdata, frames, time, status): #is typically used in audio processing with libraries such as sounddevice in Python
        if status:
            print(status)  # Print any issues or warnings about the stream

        audio = indata[:, 0]  # Take just the first channel of input audio to simplify (mono)

        # Clean up the noise using the noise reduction library
        reduced = nr.reduce_noise(y=audio, sr=44100, stationary=True)

       

        # Duplicate the mono audio to fill all output channels (like stereo)
        tiled = np.tile(reduced.reshape(-1, 1), (1, self.output_channels))
        outdata[:] = tiled  # Set the output audio to the cleaned version

    # Starts the noise cancelling process in a background thread
    def start(self):
        self.running = True  # Turn on the running flag
        self.thread = threading.Thread(target=self._run_stream)  # Prepare a new thread to handle audio
        self.thread.start()  # Begin the thread

    # This function manages the actual audio streaming process
    def _run_stream(self):
        try:
            with sd.Stream(
                device=(self.input_device, self.output_device),  # Sets both mic and speaker devices
                channels=(self.input_channels, self.output_channels),  # Assigns how many audio channels to use
                samplerate=44100,  # Number of samples of audio per second
                blocksize=1024,  # Size of each chunk of audio to process
                dtype='float32',  # Type of numbers representing the audio
                callback=self._callback  # This function processes each chunk
            ):
                print("Noise cancelling stream running...")
                while self.running:  # Keep looping while we want the stream active
                    sd.sleep(100)  # Sleep a short time to reduce CPU usage
        except Exception as e:
            print(f"Stream error: {e}")  # Show any errors that occur

    # This stops the noise cancelling and shuts down the stream
    def stop(self):
        self.running = False  # Turn off the flag
        if self.thread:
            self.thread.join()  # Wait for the thread to finish
            print("Stream stopped.")


# This class builds the visual window that allows users to use the noise cancelling tool
class NoiseCancellerGUI:
    def __init__(self):
        self.root = tk.Tk()  # Creates the main application window
        self.root.title("Noise Canceller")  # Gives the window a title
        self.root.geometry("500x400")  # Sets the fixed size of the window in pixels

        self.nc_engine = None  # Placeholder for the NoiseCanceller class instance

        self.devices = sd.query_devices()  # Get a list of all audio input and output devices
        self.device_names = [dev['name'] for dev in self.devices]  # Get just the device names

        self.input_devices = [dev['name'] for dev in self.devices if dev['max_input_channels'] > 0]
        self.output_devices = [dev['name'] for dev in self.devices if dev['max_output_channels'] > 0]

        # Auto-select a likely virtual microphone as output (e.g., contains 'VB' or 'Virtual')
        virtual_keywords = ["VB", "Virtual", "Cable", "VoiceMeeter", "BlackHole"]
        default_output_name = next((dev for dev in self.output_devices if any(k in dev for k in virtual_keywords)), self.output_devices[0] if self.output_devices else "")

        # Select system default microphone if possible
        try:
            default_input_index = sd.default.device[0] if sd.default.device[0] is not None else 0
            default_input_name = self.devices[default_input_index]['name']
        except:
            default_input_name = self.input_devices[0] if self.input_devices else "No Input Device"

        self.mic_var = tk.StringVar(value=default_input_name)
        self.output_var = tk.StringVar(value=default_output_name)

        self.build_gui()


# The `build_gui` function is responsible for creating the graphical user interface (GUI) elements 
# in the application window. It adds the following components:
# - A label and a combobox for selecting the input microphone.
# - A label and a combobox for selecting the output device (virtual microphone).
# - A "Start Noise Cancelling" button that triggers the start of the noise cancellation process.
# - A "Stop" button that stops the noise cancellation process, initially disabled.
# - A status label to display the current state of the noise cancellation (e.g., "Ready", "Active").
# The function uses Tkinter's `ttk` module for modern-styled widgets and packs them with padding for layout.

    def build_gui(self):
        ttk.Label(self.root, text="Select Microphone:").pack(pady=9)
        self.mic_combo = ttk.Combobox(self.root, textvariable=self.mic_var, values=self.input_devices)
        self.mic_combo.pack(pady=9)

        ttk.Label(self.root, text="Select Output (Virtual Mic):").pack(pady=9)
        self.output_combo = ttk.Combobox(self.root, textvariable=self.output_var, values=self.output_devices)
        self.output_combo.pack(pady=9)

        self.start_btn = ttk.Button(self.root, text="Start Noise Cancelling", command=self.start_cancelling)
        self.start_btn.pack(pady=10)

        self.stop_btn = ttk.Button(self.root, text="Stop", command=self.stop_cancelling, state="disabled")
        self.stop_btn.pack(pady=5)

        self.status_label = ttk.Label(self.root, text="Ready")
        self.status_label.pack(pady=5)
        
        
# The `start_cancelling` function is used to begin the noise cancellation process. 
# It retrieves the selected microphone and output device (virtual mic) from the GUI, 
# validates their availability and compatibility, and then starts the noise cancellation 
# process using the `NoiseCanceller` class. If any errors occur (e.g., device not found 
# or incompatible devices), appropriate error messages are displayed. Once the process 
# starts, it updates the GUI to reflect the active status and disables/enables the 
# respective buttons.

    def start_cancelling(self):
        mic_name = self.mic_var.get()
        out_name = self.output_var.get()

        try:
            mic_index = next(i for i, dev in enumerate(self.devices) if dev['name'] == mic_name)
            out_index = next(i for i, dev in enumerate(self.devices) if dev['name'] == out_name)
        except StopIteration:
            messagebox.showerror("Error", "Device not found.")
            return

        if self.devices[mic_index]['max_input_channels'] < 1:
            messagebox.showerror("Error", "Selected microphone device does not support input channels.")
            return

        if self.devices[out_index]['max_output_channels'] < 1:
            messagebox.showerror("Error", "Selected output device does not support output channels.")
            return

        try:
            self.nc_engine = NoiseCanceller(input_device=mic_index, output_device=out_index)
            self.status_label.config(text="Starting noise cancelling...")
            self.root.update()

            self.nc_engine.start()

            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.status_label.config(text="Noise cancelling active")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start noise cancelling: {str(e)}")
            self.status_label.config(text="Error occurred")

    # The stop_cancelling function is used to stop the noise cancellation process safely, 
    # reset the state of the program (such as enabling/disabling buttons), 
    # and update the status displayed in the GUI to reflect that the noise cancellation process has been stopped.
    def stop_cancelling(self):
        if self.nc_engine:
            self.nc_engine.stop()
            self.nc_engine = None
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            self.status_label.config(text="Stopped")

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    try:
        app = NoiseCancellerGUI()
        app.run()
    except Exception as e:
        print(f"Application error: {e}")
        messagebox.showerror("Critical Error", f"Failed to start application: {str(e)}")

