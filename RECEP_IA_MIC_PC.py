import sounddevice as sd
import numpy as np
import librosa
import librosa.display
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt
import soundfile as sf

# Cargar el modelo entrenado
model = load_model('gunshot_detection_model_110125.h5')

def record_audio(duration, sample_rate=22050):
    """
    Graba un audio desde el micrófono por una duración específica.

    :param duration: Duración de la grabación en segundos.
    :param sample_rate: Frecuencia de muestreo del audio.
    :return: Audio grabado como un array de numpy.
    """
    print("Grabando...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()  # Esperar a que termine la grabación
    print("Grabación finalizada.")
    return audio.flatten()

def play_audio(audio, sample_rate=22050):
    """
    Reproduce un audio grabado.

    :param audio: Audio como array de numpy.
    :param sample_rate: Frecuencia de muestreo del audio.
    """
    print("Reproduciendo el audio grabado...")
    sd.play(audio, samplerate=sample_rate)
    sd.wait()
    print("Reproducción finalizada.")

def process_audio(audio, sample_rate=22050, duration=4):
    """
    Ajusta la duración del audio y genera un espectrograma.

    :param audio: Audio como array de numpy.
    :param sample_rate: Frecuencia de muestreo del audio.
    :param duration: Duración deseada del audio en segundos.
    :return: Espectrograma del audio procesado.
    """
    num_samples = duration * sample_rate
    if len(audio) > num_samples:
        audio = audio[:num_samples]
    else:
        silence = np.zeros(num_samples - len(audio))
        audio = np.concatenate([audio, silence])
    
    # Crear espectrograma
    spect = librosa.stft(audio)
    spect_db = librosa.amplitude_to_db(spect, ref=np.max)
    
    # Normalizar
    spect_db = np.expand_dims(spect_db, axis=-1)  # Agregar una dimensión para el canal
    return spect_db

def predict_gunshot(spectrogram):
    """
    Realiza la predicción con el modelo entrenado.

    :param spectrogram: Espectrograma del audio.
    :return: Predicción de probabilidad.
    """
    # Ajustar el tamaño para el modelo
    spectrogram = np.expand_dims(spectrogram, axis=0)  # Batch dimension
    prob = model.predict(spectrogram)[0][0]
    return prob

# Grabar audio desde el micrófono
duration = 4  # Duración en segundos
sample_rate = 22050
audio = record_audio(duration, sample_rate)

# Guardar el audio grabado para inspección si es necesario
sf.write("audio_grabado.wav", audio, sample_rate)

# Reproducir el audio grabado
play_audio(audio, sample_rate)

# Procesar el audio
spectrogram = process_audio(audio, sample_rate, duration)

# Mostrar el espectrograma para verificar visualmente
plt.figure(figsize=(10, 4))
librosa.display.specshow(spectrogram[:, :, 0], sr=sample_rate, x_axis='time', y_axis='hz', cmap='coolwarm')
plt.colorbar(format='%+2.0f dB')
plt.title("Espectrograma del Audio Grabado")
plt.show()

# Realizar la predicción
prob = predict_gunshot(spectrogram)
print(f"Probabilidad de ser un disparo modelo 1: {prob:.3f}")


# Interpretar la predicción
if prob > 0.5:
    print("¡Se detectó un disparo!")
else:
    print("No se detectó un disparo.")
