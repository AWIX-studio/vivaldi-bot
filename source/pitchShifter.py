from pydub import AudioSegment
import numpy as np

def change_pitch_with_speed(input_file, output_file, cents):
    """
    Изменяет pitch и длительность аудио.
    :param cents: +100 (выше и быстрее), -100 (ниже и медленнее)
    """
    audio = AudioSegment.from_file(input_file)
    samples = np.array(audio.get_array_of_samples())
    
    # Рассчитываем коэффициент изменения частоты
    ratio = 2 ** (cents / 1200)
    
    # Новая частота дискретизации
    new_frame_rate = int(audio.frame_rate * ratio)
    
    # Создаём аудио с изменённой частотой дискретизации
    shifted_audio = audio._spawn(
        samples,
        overrides={'frame_rate': new_frame_rate}
    )
    
    # Экспортируем с исходной частотой (длительность изменится)
    shifted_audio.export(output_file, format="mp3")

# Примеры:
change_pitch_with_speed("./RadioheadCreep.mp3", "higher_faster.mp3", 100)  # +100 центов (выше и быстрее)
