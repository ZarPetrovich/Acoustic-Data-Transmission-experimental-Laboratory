import numpy as np
import sounddevice as sd
from PySide6.QtCore import QObject, Signal, Slot, QThread

# --- Worker for non-blocking, callback-based audio playback ---
class PlaybackWorker(QObject):
    """
    Handles audio playback in a separate thread using a real-time stream callback
    to ensure low-latency and prevent buffer underruns.
    """
    finished = Signal()
    error = Signal(str)

    def __init__(self, data, fs):
        super().__init__()
        self.data = data
        self.fs = fs
        self.stream = None
        self.current_frame = 0
        self.is_stopped = False

    def _callback(self, outdata: np.ndarray, frames: int, time, status: sd.CallbackFlags):
        """
        The heart of the stream. Called by the audio driver to request more data.
        """
        if status:
            self.error.emit(f"Stream callback status: {status}")

        chunk_end = self.current_frame + frames
        remaining_frames = len(self.data) - self.current_frame

        if remaining_frames < frames:
            # Last chunk
            outdata[:remaining_frames] = self.data[self.current_frame:].reshape(-1, 1)
            outdata[remaining_frames:] = 0 # Pad with silence
            raise sd.CallbackStop # Signal that this is the last chunk
        else:
            # Standard chunk
            outdata[:] = self.data[self.current_frame:chunk_end].reshape(-1, 1)

        self.current_frame = chunk_end

    @Slot()
    def play(self):
        """
        Initializes and starts the audio output stream.
        """
        try:
            # Normalize audio data safely
            max_val = np.max(np.abs(self.data))
            if max_val > 0:
                self.data = self.data / max_val

            self.stream = sd.OutputStream(
                samplerate=self.fs,
                channels=1, # Assuming mono audio
                callback=self._callback,
                finished_callback=self._on_stream_finished
            )

            with self.stream:
                # The stream runs in the background. We wait here until it's stopped.
                # The 'finished_callback' will trigger the 'finished' signal.
                while not self.is_stopped and self.stream.active:
                    sd.sleep(100) # Sleep to avoid busy-waiting

        except Exception as e:
            self.error.emit(f"Audio stream error: {e}")
            self.finished.emit() # Ensure we always finish

    @Slot()
    def stop(self):
        """
        Stops the audio stream.
        """
        self.is_stopped = True
        if self.stream:
            self.stream.stop()
            self.stream.close()
        # The finished_callback will be called upon stopping.

    def _on_stream_finished(self):
        """A safe, simple proxy method to emit the finished signal."""
        self.finished.emit()


# --- Main Handler Class (Thread Manager) ---
class AudioPlaybackHandler(QObject):
    """
    Manages the QThread for the PlaybackWorker to ensure the GUI remains responsive.
    """
    playback_started = Signal()
    playback_finished = Signal()
    playback_error = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.playback_thread = None
        self.playback_worker = None
        self.is_playing = False

    @Slot(np.ndarray, int)
    def play(self, data, fs):
        if self.is_playing:
            self.stop() # Stop previous playback before starting a new one

        self.is_playing = True
        self.playback_thread = QThread()
        self.playback_worker = PlaybackWorker(data, fs)

        self.playback_worker.moveToThread(self.playback_thread)

        # Connect signals
        self.playback_thread.started.connect(self.playback_worker.play)
        self.playback_worker.finished.connect(self.on_playback_finished)
        self.playback_worker.error.connect(self.on_playback_error)

        self.playback_thread.start()
        self.playback_started.emit()

    @Slot()
    def stop(self):
        if self.playback_worker:
            self.playback_worker.stop()

    def on_playback_finished(self):
        if self.playback_thread is not None:
            self.playback_thread.quit()
            self.playback_thread.wait()

        self.playback_thread = None
        self.playback_worker = None
        self.is_playing = False
        self.playback_finished.emit()

    def on_playback_error(self, error_message):
        print(f"Playback Error: {error_message}") # It's good to log this
        self.playback_error.emit(error_message)
        self.on_playback_finished()