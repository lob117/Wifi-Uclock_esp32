import serial
import pyaudio
import time
from scipy.io.wavfile import write
import numpy as np
import threading
import socket
import keyboard
import time
def select(sock,BUFFER_SIZE):
    audio = pyaudio.PyAudio()
    sample_rate = 24000  # Frecuencia de muestreo (debe coincidir)
    chunk = 256  # Tamaño del buffer de 
    duration = 11
    audioTotal = (sample_rate // chunk) * duration
    samples_chunk = 0
    stream = audio.open(format=pyaudio.paUInt8,  # Formato de 8 bits sin signo
                        channels=1,  # Audio mono
                        rate=sample_rate,
                        output=True)
    samples_chunk = 0
    buffer = bytearray()  # Buffer temporal para almacenar datos
    while True:
        # Leer datos disponibles del puerto serial
        data, address = sock.recvfrom(BUFFER_SIZE)  
        buffer.extend(data)  # Añadir datos al buffer
        # Enviar datos al stream si tenemos un chunk completo
        if len(buffer) >= chunk:
            samples_chunk += 1
            sample.extend(buffer[:chunk])
            #print(len(sample))
            stream.write(bytes(buffer[:chunk]))  # Reproducir el chunk
            buffer = buffer[chunk:]  # Eliminar los datos ya reproducidos
        if keyboard.is_pressed('esc'):  # Detiene al presionar Esc
            break
    stream.stop_stream()
    stream.close()
    audio.terminate()


# Configuración del socket UDP
IP = "0.0.0.0"  # Escuchar en todas las interfaces disponibles
PUERTO_ESP32_1 = 1234
PUERTO_ESP32_2 = 1235
BUFFER_SIZE = 256  # Tamaño del paquete a recibir

# Crear el socket UDP
sock_1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_1.bind((IP, PUERTO_ESP32_1))
sock_2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_2.bind((IP, PUERTO_ESP32_2))
# Configuración del puerto serial
puerto = 'COM3'  # Cambia según tu sistema ('/dev/ttyUSB0' en Linux)
baudrate = 4e6  # Velocidad en bps
sample = []
nameFile = "casalobato_5m_GLOBO"

# Configurar PyAudio

print("Reproduciendo audio... Presiona Ctrl+C para detener.")
i = 0
while True:
    num=int(input("cual esp32 escuchar? " ))
    if (num==1):
        select(sock_1,BUFFER_SIZE)
    if(num==2):
        select(sock_2,BUFFER_SIZE)
    time.sleep(6)
    if keyboard.is_pressed('esc'):  # Detiene al presionar Esc
        break