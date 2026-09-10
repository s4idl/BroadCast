import socket
import threading
import sys

HOST = '127.0.0.1'
PUERTO = 5000

def recibir_mensajes(socket_cliente):
    """Escucha y muestra los mensajes provenientes del servidor en segundo plano."""
    while True:
        try:
            mensaje = socket_cliente.recv(1024).decode('utf-8')
            if mensaje:
                # Usamos end='' para no duplicar el salto de línea que ya manda el servidor
                print(mensaje, end='')
            else:
                print("\n[DESCONECTADO] El servidor ha cerrado la conexión.")
                socket_cliente.close()
                break
        except Exception:
            print("\n[FIN DE CONEXIÓN] Ya no estás conectado al chat.")
            break

def iniciar_cliente():
    """Conecta al servidor y lee los mensajes escritos por el usuario para enviarlos."""
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        cliente.connect((HOST, PUERTO))
        print(f"[CONECTADO] Unido al chat en {HOST}:{PUERTO}")
        print("Escribe tus mensajes y presiona Enter. Escribe 'salir' para abandonar.\n")
        
        # Hilo dedicado a escuchar al servidor sin bloquear el input del usuario
        hilo_recepcion = threading.Thread(target=recibir_mensajes, args=(cliente,))
        hilo_recepcion.daemon = True 
        hilo_recepcion.start()
        
        while True:
            mensaje = input()
            
            if mensaje.lower() == 'salir':
                break
                
            if mensaje.strip():
                cliente.send(mensaje.encode('utf-8'))
                
    except ConnectionRefusedError:
        print(f"[ERROR] No se pudo conectar. Asegúrate de que el servidor en {HOST}:{PUERTO} esté encendido.")
    except KeyboardInterrupt:
        print("\n[SALIENDO] Has forzado el cierre del chat.")
    finally:
        cliente.close()

if __name__ == "__main__":
    iniciar_cliente()
