import socket
import numpy as np
import librosa
from tensorflow.keras.models import load_model
import sounddevice as sd
import threading
import queue
import time

# Cargar el modelo entrenado
model = load_model('GunshotIaModel_v9_old.h5')

# Configuración global
SAMPLE_RATE = 22050
CHUNK_SIZE = 256
DURATION = 4  # Duración de cada segmento de audio para procesar
BUFFER_SIZE = int(SAMPLE_RATE * DURATION)  # Tamaño del buffer para cada segmento

# Cola para almacenar los datos de audio capturados
audio_queue = queue.Queue()

def record_audio_from_wifi(esp32_ip, port):
    """
    Lee audio continuamente desde una ESP32 a través de WiFi y lo coloca en una cola.
    :param esp32_ip: Dirección IP de la ESP32.
    :param port: Puerto en el que escucha el servidor en la ESP32.
    """
    print(f"Conectando al servidor en {esp32_ip}:{port}...")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((esp32_ip, port))
        print("Conexión establecida.")
    except Exception as e:
        print(f"Error al conectar al servidor: {e}")
        return
    
    print("Iniciando captura de datos...")
    try:
        while True:
            # Recibir datos en bruto desde la ESP32
            raw_data = client_socket.recv(CHUNK_SIZE * 2)  # 2 bytes por muestra (16 bits)
            if raw_data:
                # Convertir los datos recibidos a enteros de 16 bits
                chunk = np.frombuffer(raw_data, dtype=np.int16)
                audio_queue.put(chunk)  # Agregar el chunk a la cola
            else:
                print("[CAPTURA] No se recibieron datos. Conexión cerrada por el servidor.")
                break
    finally:
        client_socket.close()
        print("[CAPTURA] Conexión cerrada.")

def process_audio():
    """
    Procesa continuamente los datos de audio de la cola, genera espectrogramas
    y realiza predicciones con el modelo de IA.
    """
    audio_buffer = []  # Buffer temporal para acumular audio
    print("[PROCESAMIENTO] Iniciando procesamiento de audio...")
    while True:
        try:
            # Obtener un chunk de audio de la cola
            chunk = audio_queue.get(timeout=1)  # Timeout para evitar bloqueos
            audio_buffer.extend(chunk)
            
            
            # Si el buffer tiene suficientes muestras para procesar un segmento
            if len(audio_buffer) >= BUFFER_SIZE:
                # Extraer un segmento de audio del buffer
                audio_segment = np.array(audio_buffer[:BUFFER_SIZE], dtype=np.float32)
                audio_buffer = audio_buffer[BUFFER_SIZE:]  # Eliminar el segmento procesado
                
                # Normalizar el audio a rango [-1, 1]
                audio_segment /= np.max(np.abs(audio_segment))
                
                # Generar espectrograma
                spectrogram = generate_spectrogram(audio_segment)
                
                # Realizar la predicción
                prob = predict_gunshot(spectrogram)
                print(f"[PROCESAMIENTO] Probabilidad de ser un disparo: {prob:.2f}")
                if prob > 0.5:
                    print("[PROCESAMIENTO] ¡Se detectó un disparo!")
                else:
                    print("[PROCESAMIENTO] No se detectó un disparo.")
        except queue.Empty:
            print("[PROCESAMIENTO] La cola está vacía. Esperando nuevos datos...")
            continue  # Continuar si la cola está vacía

def generate_spectrogram(audio, sample_rate=SAMPLE_RATE):
    """
    Genera un espectrograma a partir de un segmento de audio.
    :param audio: Segmento de audio como array de numpy.
    :param sample_rate: Frecuencia de muestreo del audio.
    :return: Espectrograma del audio procesado.
    """
    # Crear espectrograma
    spect = librosa.stft(audio)
    spect_db = librosa.amplitude_to_db(spect, ref=np.max)
    
    # Normalizar y agregar dimensiones para el modelo
    spect_db = np.expand_dims(spect_db, axis=-1)  # Agregar dimensión para el canal
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

# Configuración de dispositivos
ESP32_DEVICES = [
    {'ip': '192.168.1.102', 'port': 8082, 'name': 'ESP32_2'},
]

# Iniciar hilos para captura y procesamiento
threads = []
for device in ESP32_DEVICES:
    # Hilo para capturar audio
    capture_thread = threading.Thread(target=record_audio_from_wifi, args=(device['ip'], device['port']))
    capture_thread.daemon = True  # El hilo se detendrá cuando el programa principal termine
    threads.append(capture_thread)
    capture_thread.start()
    print(f"[HILO] Hilo de captura iniciado para {device['name']}")

# Hilo para procesar audio
processing_thread = threading.Thread(target=process_audio)
processing_thread.daemon = True
threads.append(processing_thread)
processing_thread.start()
print("[HILO] Hilo de procesamiento iniciado.")

# Mantener el programa principal en ejecución
try:
    while True:
        time.sleep(1)  # Reducir uso de CPU
except KeyboardInterrupt:
    print("\nDeteniendo el programa...")