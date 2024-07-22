import tkinter as tk
from tkinter import simpledialog, messagebox
import subprocess
import os
import time
import unittest
from unittest.mock import patch
from twilio.rest import Client
import wave
from PIL import Image
import numpy as np

# Attempt to import pyaudio
try:
    import pyaudio
except ImportError:
    pyaudio = None

# Global variable to hold the scrcpy process
scrcpy_process = None

# Function to execute adb shell command
def adb_shell(command):
    """
    Execute adb shell command.
    """
    result = subprocess.run(['adb', 'shell', command], capture_output=True, text=True)
    return result.stdout.strip()

# Function to open Spotify
def open_spotify():
    spotify_package_name = "com.spotify.music"
    subprocess.run(["adb", "shell", "am", "start", "-n", f"{spotify_package_name}/com.spotify.music.MainActivity"], capture_output=True)
    log_action("Spotify opened on mobile device.")

# Function to search for music in Spotify
def search_music():
    music_name = simpledialog.askstring("Search Music", "Enter the name of the music to search:")
    if music_name:
        adb_shell('input tap 422 2340')  # Open search
        time.sleep(2)

        adb_shell('input tap 400 433')  # Tap on the search bar
        time.sleep(2)
        
        adb_shell(f'input text "{music_name}"')  # Type the music name
        time.sleep(3)
        
        adb_shell('input tap 550 1000')  # Tap on the first result
        time.sleep(2)
        
        adb_shell('input tap 570 2170')  # Play the song
        log_action(f"Searching and playing '{music_name}' on Spotify.")
    else:
        log_action("Music search cancelled.")

# Function to close Spotify app
def close_spotify():
    spotify_package_name = "com.spotify.music"
    adb_shell(f'am force-stop {spotify_package_name}')
    log_action("Spotify closed on mobile device.")

# Function to start scrcpy
def start_scrcpy():
    global scrcpy_process
    try:
        scrcpy_path = r"scrcpy_path"

        if os.path.exists(scrcpy_path):
            scrcpy_process = subprocess.Popen([scrcpy_path])
            log_action("Scrcpy started successfully.")
        else:
            log_action("Scrcpy not found at specified path.")
    except Exception as e:
        log_action(f"An error occurred while starting scrcpy: {e}")

# Function to close scrcpy
def close_scrcpy():
    global scrcpy_process
    if scrcpy_process:
        scrcpy_process.terminate()
        scrcpy_process = None
        log_action("Scrcpy closed successfully.")
    else:
        log_action("Scrcpy is not running.")

# Function to log actions
def log_action(action):
    log_list.insert(tk.END, action)
    log_list.yview(tk.END)

# Function to open Google Maps
def open_google_maps():
    """
    Open Google Maps on the device.
    """
    adb_shell('am start -n com.google.android.apps.maps/com.google.android.maps.MapsActivity')
    log_action("Google Maps opened on mobile device.")

# Function to force stop Google Maps
def close_google_maps():
    """
    Force stop Google Maps on the device.
    """
    google_maps_package_name = "com.google.android.apps.maps"
    adb_shell(f'am force-stop {google_maps_package_name}')
    log_action("Google Maps force-stopped on mobile device.")

# Function to initiate Google Maps search
def search_on_google_maps():
    """
    Open Google Maps on the device and perform search using adb commands.
    """
    destination = simpledialog.askstring("Search Google Maps", "Enter the destination to search:")
    if not destination:
        log_action("Google Maps search cancelled.")
        return

    open_google_maps()  # Start Google Maps (if not already started)
    time.sleep(5)       # Adjust the delay as needed

    try:
        # Tap on the search bar to open it
        adb_shell('input tap 400 150')  # Coordinates might need to be adjusted
        time.sleep(2)

        # Input destination message
        adb_shell(f'input text "{destination}"')
        log_action(f"Entered destination: {destination}.")
        time.sleep(2)

        # Tap on the search button (Enter key event)
        adb_shell('input keyevent 66')  # Key event for Enter
        log_action("Performed search.")
        time.sleep(5)

        # Tap on the directions button (assuming it's visible on the screen)
        adb_shell('input tap 180 1675')  # Coordinates might need to be adjusted
        log_action("Clicked on the Directions button.")
        time.sleep(5)

        # Start following route (assuming it's visible on the screen)
        adb_shell('input tap 160 2330')  # Coordinates might need to be adjusted
        log_action("Clicked on the Start button.")
        time.sleep(5)

        log_action(f"Searching and navigating to '{destination}' on Google Maps.")
    except Exception as e:
        log_action(f"An error occurred during the Google Maps search: {e}")

# Function to minimize the current app
def minimize():
    """
    Minimize the current app by simulating pressing the home button.
    """
    adb_shell('input keyevent KEYCODE_HOME')
    log_action("Minimized current app.")

# Function to control music playback in Spotify
def pause_music():
    adb_shell('input keyevent 85')  # Key event for pause/play toggle
    log_action("Music playback paused/resumed.")

def next_music():
    adb_shell('input keyevent 87')  # Key event for next
    log_action("Next music track.")

def previous_music():
    adb_shell('input keyevent 88')  # Key event for previous
    log_action("Previous music track.")

def play_music():
    adb_shell('input keyevent 126')  # Key event for play
    log_action("Music playback started.")

# Function to take a screenshot
def take_screenshot(device_path, filename):
    try:
        adb_path = r"adb_path"  # Replace this with the actual path to adb
        subprocess.run([adb_path, "shell", "screencap", "-p", f"{device_path}/{filename}"])
        subprocess.run([adb_path, "pull", f"{device_path}/{filename}", filename])
        log_action(f"Screenshot saved as {filename}")
    except Exception as e:
        log_action(f"Error while taking screenshot: {e}")

# Function to compare two screenshots using MSE
def compare_screenshots(image1, image2):
    try:
        img1_array = np.array(image1)
        img2_array = np.array(image2)
        err = np.sum((img1_array.astype("float") - img2_array.astype("float")) ** 2)
        err /= float(img1_array.shape[0] * img1_array.shape[1])
        return err
    except Exception as e:
        log_action(f"Error while comparing screenshots: {e}")
        return float('inf')  # Return a very high MSE score on error

# Function to take and compare screenshots
def take_and_compare_screenshots():
    try:
        # Take the first screenshot
        take_screenshot("/storage/emulated/0/screenshot", "screenshot1.png")
        time.sleep(5)  # Wait for 5 seconds

        # Take the second screenshot
        take_screenshot("/storage/emulated/0/screenshot", "screenshot2.png")

        # Load screenshots using PIL
        screenshot1 = Image.open("screenshot1.png")
        screenshot2 = Image.open("screenshot2.png")

        # Compare screenshots using MSE
        mse_score = compare_screenshots(screenshot1, screenshot2)

        # Define a threshold for MSE to determine similarity
        mse_threshold = 500

        if mse_score < mse_threshold:
            messagebox.showinfo("Screenshot Comparison", "Screenshots match!")
        else:
            messagebox.showwarning("Screenshot Comparison", "Screenshots do not match!")
        
    except Exception as e:
        log_action(f"Error during screenshot comparison: {e}")

# Function to test Spotify
def test_spotify():
    if pyaudio is None:
        log_action("pyaudio module not available. Please install pyaudio to run this test.")
        return

    # Define test cases for Spotify
    class TestMusicAndSpeaker(unittest.TestCase):
        def test_music_playing(self):
            # Open Spotify app
            subprocess.run(["adb", "shell", "am", "start", "-n", "com.spotify.music/com.spotify.music.MainActivity"], capture_output=True)
            time.sleep(10)  # Wait for the app to open and possibly play music
            
            # Check if the song is playing using adb command to get the media state
            media_state = adb_shell('dumpsys media_session')
            self.assertTrue('state=PlaybackState {state=3' in media_state, "The song is not playing.")
            log_action("Spotify music is playing successfully.")

        def test_speaker(self):
            try:
                # Play a test sound on the device
                subprocess.run(['adb', 'shell', 'am', 'start', '-a', 'android.intent.action.VIEW', '-d', 'file:///sdcard/Music/test_sound.wav'], capture_output=True)
                time.sleep(5)  # Wait for the sound to finish playing

                # Record audio from the device's microphone
                audio = pyaudio.PyAudio()
                stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
                frames = []
                for _ in range(0, int(44100 / 1024 * 5)):  # Record for 5 seconds
                    frames.append(stream.read(1024))
                stream.stop_stream()
                stream.close()
                audio.terminate()

                # Write recorded audio to a WAV file
                wave_file = wave.open("recorded_audio.wav", "wb")
                wave_file.setnchannels(1)
                wave_file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
                wave_file.setframerate(44100)
                wave_file.writeframes(b"".join(frames))
                wave_file.close()

                # Check if the recorded audio contains any sound (assuming sound is properly played by the speaker)
                with wave.open("recorded_audio.wav", "rb") as wave_file:
                    frames = wave_file.readframes(-1)
                    self.assertNotEqual(frames, b'', "No sound detected. Speaker may not be working properly.")
                log_action("Speaker test successful. Sound detected.")
            except Exception as e:
                log_action(f"An error occurred during the speaker test: {e}")

    # Run the test cases
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMusicAndSpeaker)
    unittest.TextTestRunner(verbosity=2).run(suite)

# Twilio call functionality
def make_twilio_call(account_sid, auth_token, to_number, from_number):
    client = Client(account_sid, auth_token)
    call = client.calls.create(
        twiml='<Response><Say>abhishek</Say></Response>',
        to=to_number,
        from_=from_number  # Note the underscore after from
    )
    return call.sid

# Function to initiate Twilio call
def initiate_twilio_call():         #register on twilio for get account_sid,account_sid,to_number,from_number
    account_sid = ' '
    auth_token = ' '
    to_number = ' '   
    from_number = ' ' 

    try:
        call_sid = make_twilio_call(account_sid, auth_token, to_number, from_number)
        log_action(f"Twilio call initiated successfully. Call SID: {call_sid}")
    except Exception as e:
        log_action(f"An error occurred while initiating Twilio call: {e}")

# Function to test Twilio call
def test_twilio_call():
    class TestMakeTwilioCall(unittest.TestCase):
        @patch('twilio.rest.api.v2010.account.call.CallList.create')
        def test_make_twilio_call(self, mock_create):
            # Setup mock
            expected_call_sid = 'dummy_call_sid'
            mock_create.return_value.sid = expected_call_sid

            # Call the function with mock parameters
            call_sid = make_twilio_call('dummy_sid', 'dummy_token', '+1234567890', '+0987654321')

            # Assertions to verify expected outcomes
            self.assertEqual(call_sid, expected_call_sid)
            mock_create.assert_called_once_with(
                twiml='<Response><Say>abhishek</Say></Response>',
                to='+1234567890',
                from_='+0987654321'  # Note the underscore after from
            )

    # Run the test cases
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMakeTwilioCall)
    unittest.TextTestRunner(verbosity=2).run(suite)

# GUI setup
root = tk.Tk()
root.title("Mobile Testing GUI")
root.geometry("700x600")

# ADB Features
frame_adb = tk.LabelFrame(root, text="Screen Mirroring", padx=10, pady=10)
frame_adb.pack(pady=10, fill="x")

btn_start_scrcpy = tk.Button(frame_adb, text="Start Scrcpy", command=start_scrcpy)
btn_start_scrcpy.pack(side=tk.LEFT, padx=5)

btn_close_scrcpy = tk.Button(frame_adb, text="Close Scrcpy", command=close_scrcpy)
btn_close_scrcpy.pack(side=tk.LEFT, padx=5)

btn_screenshot_compare = tk.Button(frame_adb, text="Take and Compare Screenshots", command=take_and_compare_screenshots)
btn_screenshot_compare.pack(side=tk.LEFT, padx=5)

# Spotify Controls
frame_spotify = tk.LabelFrame(root, text="Spotify Controls", padx=10, pady=10)
frame_spotify.pack(pady=10, fill="x")

btn_open_spotify = tk.Button(frame_spotify, text="Open Spotify", command=open_spotify)
btn_open_spotify.pack(side=tk.LEFT, padx=5)

btn_search_music = tk.Button(frame_spotify, text="Search Music", command=search_music)
btn_search_music.pack(side=tk.LEFT, padx=5)

btn_close_spotify = tk.Button(frame_spotify, text="Close Spotify", command=close_spotify)
btn_close_spotify.pack(side=tk.LEFT, padx=5)

btn_test_spotify = tk.Button(frame_spotify, text="Test Spotify", command=test_spotify)
btn_test_spotify.pack(side=tk.LEFT, padx=5)

btn_pause_music = tk.Button(frame_spotify, text="Play/Pause Music", command=pause_music)
btn_pause_music.pack(side=tk.LEFT, padx=5)

btn_next_music = tk.Button(frame_spotify, text="Next Music", command=next_music)
btn_next_music.pack(side=tk.LEFT, padx=5)

btn_previous_music = tk.Button(frame_spotify, text="Previous Music", command=previous_music)
btn_previous_music.pack(side=tk.LEFT, padx=5)

# Twilio Call Features
frame_twilio = tk.LabelFrame(root, text="Twilio Call", padx=10, pady=10)
frame_twilio.pack(pady=10, fill="x")

btn_initiate_call = tk.Button(frame_twilio, text="Initiate Call", command=initiate_twilio_call)
btn_initiate_call.pack(side=tk.LEFT, padx=5)

btn_test_call = tk.Button(frame_twilio, text="Test Call", command=test_twilio_call)
btn_test_call.pack(side=tk.LEFT, padx=5)

# Google Maps Features
frame_maps = tk.LabelFrame(root, text="Google Maps", padx=10, pady=10)
frame_maps.pack(pady=10, fill="x")

btn_search_maps = tk.Button(frame_maps, text="Search on Google Maps", command=search_on_google_maps)
btn_search_maps.pack(side=tk.LEFT, padx=5)

btn_minimize = tk.Button(frame_maps, text="Minimize App", command=minimize)
btn_minimize.pack(side=tk.LEFT, padx=5)

# Button to force stop Google Maps
btn_close_maps = tk.Button(frame_maps, text="Force Stop Google Maps", command=close_google_maps)
btn_close_maps.pack(side=tk.LEFT, padx=5)

# Logs
frame_logs = tk.LabelFrame(root, text="Logs", padx=10, pady=10)
frame_logs.pack(pady=10, fill="both", expand=True)

log_list = tk.Listbox(frame_logs, height=10, width=70)
log_list.pack(side=tk.LEFT, fill="both", expand=True)

scrollbar = tk.Scrollbar(frame_logs, command=log_list.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
log_list.config(yscrollcommand=scrollbar.set)

# Start the GUI
root.mainloop()