# Audio Playback System Documentation

This document outlines the architecture of the audio playback system (`audio_player.py`) and its integration with the application's core logic (`AppState.py`). The system is designed to be robust, responsive, and controlled by the user interface.

## 1. `audio_player.py` - The Core Playback Engine

The audio playback engine is composed of two classes working together to ensure that audio playback does not block the main application thread, providing a smooth user experience.

### `PlaybackWorker(QObject)`

This is the low-level worker class that runs in a separate thread and directly interfaces with the `sounddevice` library.

- **Threading:** It is designed to be moved to a `QThread` to perform its tasks in the background.
- **Callback-Based Streaming:** Instead of using the simple but unreliable `sounddevice.play()`, it uses a `sounddevice.OutputStream` with a `_callback` function.
    - **Why?** This is the professional standard for real-time audio. The audio driver "pulls" data from our application in small, precise chunks exactly when it needs it. This prevents buffer underruns and eliminates the common issue of losing the beginning of a signal, which can happen when the main thread is busy.
- **`_callback` Method:** This is the core of the playback. It is responsible for:
    1.  Slicing the full audio signal (`self.data`) into small chunks.
    2.  Feeding the next chunk to the audio hardware via the `outdata` buffer.
    3.  Signaling the end of the stream by raising `sd.CallbackStop` when the data is exhausted.
- **State Management:** It has an `is_stopped` flag to gracefully handle stop requests.
- **Communication:** It uses Qt signals (`finished`, `error`) to communicate its status back to the main thread.

### `AudioPlaybackHandler(QObject)`

This is the high-level, public-facing class that the rest of the application interacts with. It acts as a manager for the `PlaybackWorker` and its thread.

- **Thread Management:** Its primary role is to create, manage, and clean up the `QThread` and `PlaybackWorker` for each playback session.
- **`play(data, fs)` Slot:**
    1.  Checks if a playback is already in progress. If so, it stops the old one.
    2.  Creates a new `QThread` and a `PlaybackWorker`.
    3.  Moves the worker to the thread.
    4.  Connects the worker's `finished` and `error` signals to its own cleanup slots (`on_playback_finished`, `on_playback_error`).
    5.  Starts the thread, which in turn calls the worker's `play` method.
- **`stop()` Slot:** Delegates the stop request to the currently active worker.
- **Cleanup:** The `on_playback_finished` method ensures that the `QThread` is properly quit and waited for, preventing resource leaks.

---

## 2. `AppState.py` - Integration with Application Logic

`AppState` acts as the central nervous system, connecting the UI's intent with the audio playback engine's functionality.

### Initialization and Instance Management

- In `AppState.__init__`, a single instance of `AudioPlaybackHandler` is created and stored as `self.audio_handler`.
- The handler's feedback signals (`playback_started`, `playback_finished`, `playback_error`) are immediately connected to corresponding slots within `AppState` (`_on_playback_started`, etc.). This creates a feedback loop for updating the UI.

### User-Controlled Playback

The system is explicitly designed to be controlled by the user, not to play audio automatically.

- **`on_play_btn_pressed()`:** This slot is intended to be connected to the "Play" button in the UI. When triggered, it calls `self.play_audio()`.
- **`play_audio()`:** This method retrieves the current bandpass signal, extracts its real component (as audio hardware plays real-valued signals), and passes it to `self.audio_handler.play()` to start the playback thread.
- **`on_stop_signal_pressed()`:** This slot is connected to the "Stop" button and directly calls `self.audio_handler.stop()`.

### UI Feedback Loop

`AppState` provides a clear status to the UI.

- The `playback_status_changed` signal is emitted from `AppState` whenever the playback state changes.
- The slots `_on_playback_started`, `_on_playback_finished`, and `_on_playback_error` receive feedback from the `AudioPlaybackHandler`.
- They then emit the `playback_status_changed` signal with a user-friendly string (e.g., "Status: Playing...", "Status: Idle", "Error: ..."). This signal can be connected to a `QLabel` in the `MediaPlayerWidget` to give the user real-time status updates.

This architecture ensures a clean separation of concerns: `audio_player.py` handles the complexities of real-time audio, while `AppState.py` handles the application logic and user intent, connecting the signal generation pipeline to the playback engine in a controlled, user-driven manner.
