import socket
import pyaudio
import keyboard
import wave

# Configuración del servidor
ESP32_IP_1 = '192.168.1.101'  # Cambiar por la IP de tu ESP32
PORT_1 = 8082
ESP32_IP_2 = '192.168.1.100'  # Cambiar por la IP de tu ESP32
PORT_2 = 80
CHUNK_SIZE = 256  # Debe coincidir con el tamaño del buffer en la ESP32
SAMPLE_RATE = 44100

# Inicializar PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=SAMPLE_RATE,
                output=True)

# Configurar los sockets


client_socket_2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket_2.connect((ESP32_IP_2, PORT_2))

# Configurar archivos .wav
output_file_1 = "output_esp32_1.wav"
output_file_2 = "output_esp32_2.wav"

wave_file_1 = wave.open(output_file_1, 'wb')
wave_file_1.setnchannels(1)
wave_file_1.setsampwidth(p.get_sample_size(pyaudio.paInt16))
wave_file_1.setframerate(SAMPLE_RATE)

wave_file_2 = wave.open(output_file_2, 'wb')
wave_file_2.setnchannels(1)
wave_file_2.setsampwidth(p.get_sample_size(pyaudio.paInt16))
wave_file_2.setframerate(SAMPLE_RATE)

print("Conectado al servidor, reproduciendo audio...")

def sonido(client_socket,wave_file):
    while True:
        raw_data = client_socket.recv(CHUNK_SIZE * 2)  # 2 bytes por muestra (16 bits)
        if raw_data:
            # Reproducir y guardar audio
            stream.write(raw_data)
            wave_file.writeframes(raw_data)
            if keyboard.is_pressed('e'):  # Detecta si se presionó la tecla "e"
                print("Cambio de ESP32")
                break   
        else:
            break
try:
    while True:
        num = int(input("¿Cuál ESP32 escuchar? (1 o 2): "))
        
        if num == 1:
            sonido(client_socket_1,wave_file_1)


        elif num == 2:
            sonido(client_socket_2,wave_file_2)
        
        else :
            print("Opción no válida. Intente de nuevo.")
            continue

except KeyboardInterrupt:
    print("\nDetenido por el usuario.")
except Exception as e:
    print("Error:", e)
finally:
    # Cerrar recursos
    print("Cerrando conexiones y guardando archivos...")
    stream.stop_stream()
    stream.close()
    p.terminate()

    wave_file_1.close()
    wave_file_2.close()

    client_socket_1.close()
    client_socket_2.close()
    print(f"Archivos de audio guardados: {output_file_1}, {output_file_2}")
