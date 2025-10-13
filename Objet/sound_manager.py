import ffmpeg
import pyaudio

class SoundManager:
    def __init__(self, video_file):
        self.video_file = video_file
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16, channels=2, rate=44100, output=True)
        self.process = None

    def play_audio(self):
        """Joue l'audio de la vidéo en temps réel."""
        # Lance ffmpeg pour extraire l'audio en direct
        self.process = (
            ffmpeg.input(self.video_file)
            .output('pipe:', format='wav', acodec='pcm_s16le', ac=2, ar=44100)
            .run_async(pipe_stdout=True, pipe_stderr=None, quiet=True)
        )

        # Lire et jouer l'audio en continu
        while True:
            data = self.process.stdout.read(4096)  # Lire un chunk de 4096 octets
            if not data:
                break
            self.stream.write(data)  # Jouer le son

    def close(self):
        """Ferme les flux audio."""
        if self.process:
            self.process.stdout.close()
            self.process.wait()
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
