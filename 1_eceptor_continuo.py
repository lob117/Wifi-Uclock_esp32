import socket
import pyaudio

# Configuración del servidor
ESP32_IP = '192.168.1.102'  # Cambia esto por la IP de tu ESP32
PORT = 8082
CHUNK_SIZE = 256  # Debe coincidir con el tamaño del buffer en la ESP32
SAMPLE_RATE = 22050  # Frecuencia de muestreo
FORMAT = pyaudio.paInt16  # Formato de audio (16 bits)
CHANNELS = 1  # Mono

# Inicializar PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=SAMPLE_RATE,
                output=True)

# Configurar el socket para conectarse al ESP32
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client_socket.connect((ESP32_IP, PORT))
    print(f"Conectado al servidor ESP32 ({ESP32_IP}:{PORT})")
except Exception as e:
    print(f"Error al conectar al servidor: {e}")
    exit()

print("Reproduciendo audio en tiempo real...")

def receive_and_play_audio(client_socket):
    """
    Recibe datos de audio desde el socket y los reproduce en tiempo real.
    """
    try:
        while True:
            # Recibir datos del socket
            raw_data = client_socket.recv(CHUNK_SIZE * 2)  # 2 bytes por muestra (16 bits)
            if not raw_data:
                print("Conexión cerrada por el servidor.")
                break

            # Reproducir audio en tiempo real
            stream.write(raw_data)

    except KeyboardInterrupt:
        print("Deteniendo la reproducción...")
    except Exception as e:
        print(f"Error durante la recepción de audio: {e}")

try:
    # Iniciar la recepción y reproducción de audio
    receive_and_play_audio(client_socket)
finally:
    # Cerrar recursos
    print("Cerrando conexiones...")
    stream.stop_stream()
    stream.close()
    p.terminate()
    client_socket.close()
    print("Conexión cerrada.")