import numpy as np
import librosa
from pydub import AudioSegment
from scipy.signal import find_peaks

class HighPrecisionBPM:
    def __init__(self, audio_path: str):
        self.y, self.sr = self._load_audio(audio_path)
        self.tempo = self._calculate_precise_bpm()
    
    def _load_audio(self, path):
        """Загрузка с двойной проверкой качества"""
        audio = AudioSegment.from_file(path)
        y = np.array(audio.get_array_of_samples()).astype(np.float32)
        y /= np.iinfo(audio.sample_width * 8).max
        
        # Проверка частоты дискретизации
        if audio.frame_rate < 44100:
            print(f"Внимание: низкая частота {audio.frame_rate}Hz может снизить точность")
        return y, audio.frame_rate

    def _calculate_precise_bpm(self):
        """Многоступенчатый расчёт с интерполяцией"""
        # 1. Первичная оценка
        onset_env = librosa.onset.onset_strength(
            y=self.y, sr=self.sr,
            hop_length=1024,
            aggregate=np.median,
            n_fft=4096
        )
        initial_bpm = float(librosa.feature.tempo(
            onset_envelope=onset_env,
            sr=self.sr,
            start_bpm=120,
            ac_size=16
        )[0])
        
        # 2. Анализ автокорреляции
        autocorr = librosa.autocorrelate(onset_env)
        peaks = find_peaks(autocorr, distance=10)[0]
        if len(peaks) > 1:
            lag = peaks[1] - peaks[0]
            refined_bpm = 60 * self.sr / (1024 * lag)
            initial_bpm = refined_bpm
        
        # 3. Спектральная интерполяция
        n_fft = 32768  # Увеличенное FFT для точности
        S = np.abs(librosa.stft(self.y, n_fft=n_fft))
        freqs = librosa.fft_frequencies(sr=self.sr, n_fft=n_fft)
        
        # Поиск в узком диапазоне ±5% от initial_bpm
        target_min = initial_bpm * 0.95 / 60
        target_max = initial_bpm * 1.05 / 60
        mask = (freqs >= target_min) & (freqs <= target_max)
        
        if np.any(mask):
            peak_freq = freqs[mask][np.argmax(S[mask].mean(axis=1))]
            final_bpm = 60 * peak_freq
            return round(final_bpm, 3)
        
        return round(initial_bpm, 3)

# Использование
# bpm_analyzer = HighPrecisionBPM("music.mp3")
# print(f"BPM: {bpm_analyzer.tempo:.0f}")
