from pydub import AudioSegment
import numpy as np
import librosa
from pydub.audio_segment import array

class BPM_Detector:
    def __init__(self, audio_path: str):
        y, sr = self.load_audio(audio_path)
        # Преобразуем в float и нормализуем
        y = y.astype(np.float32) / np.iinfo(y.dtype).max
        self.tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        
    def load_audio(self, path):
        audio = AudioSegment.from_file(path)
        samples = np.array(audio.get_array_of_samples())
        sr = audio.frame_rate
        return samples, sr


# Использование
# detector = BPM_Detector('/home/awed/Music/пад луной ДЕМО.mp3')
# print(round(float(detector.tempo.tolist()[0])))
