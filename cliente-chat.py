import socket
import threading
import sys

# --- CONFIGURACIÓN DEL CLIENTE ---
# Debe coincidir con la configuración del servidor
HOST = '127.0.0.1'
PUERTO = 5000

def recibir_mensajes(socket_cliente):
    """
    Esta función se ejecuta de fondo en su propio "Hilo" (Thread).
    Se encarga únicamente de escuchar lo que envía el servidor y mostrarlo en pantalla.
    Esto permite que podamos leer los mensajes de otros mientras nosotros estamos escribiendo.
    """
    while True:
        try:
            # Esperamos recibir datos del servidor (hasta 1024 bytes a la vez)
            mensaje = socket_cliente.recv(1024).decode('utf-8')
            
            if mensaje:
                # Imprimimos el mensaje recibido.
                # Nota: El historial de los últimos 5 mensajes llegará por aquí 
                # automáticamente apenas nos conectemos.
                print(f"{mensaje}")
            else:
                # Si recibimos un mensaje vacío, significa que el servidor se cayó o cerró
                print("\n[DESCONECTADO] El servidor ha cerrado la conexión.")
                socket_cliente.close()
                break
        except Exception as e:
            # Si el cliente cierra el programa, se corta el socket y da error aquí, es normal al salir.
            print(f"\n[FIN DE CONEXIÓN] Ya no estás conectado al chat.")
            break

def iniciar_cliente():
    """
    Función principal que conecta con el servidor y se encarga de leer
    lo que el usuario escribe en su teclado para enviarlo.
    """
    # 1. Creamos el socket del cliente (TCP sobre IPv4, igual que el servidor)
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # 2. Intentamos conectarnos a la dirección y puerto del servidor
        cliente.connect((HOST, PUERTO))
        print(f"[CONECTADO] Unido al chat en {HOST}:{PUERTO}")
        print("Escribe tus mensajes y presiona Enter. Escribe 'salir' para abandonar.\n")
        
        # 3. Arrancamos el Hilo que se encarga de RECIBIR mensajes simultáneamente.
        # Le pasamos el socket 'cliente' para que sepa por dónde escuchar.
        hilo_recepcion = threading.Thread(target=recibir_mensajes, args=(cliente,))
        # daemon=True hace que este hilo se cierre solo cuando cerremos el programa principal
        hilo_recepcion.daemon = True 
        hilo_recepcion.start()
        
        # 4. Bucle principal: ENVIAR mensajes
        while True:
            # Esperamos a que el usuario escriba algo en la terminal
            mensaje = input()
            
            # Si el usuario escribe 'salir', rompemos el bucle para desconectarnos
            if mensaje.lower() == 'salir':
                break
                
            # Si el mensaje no son solo espacios en blanco, lo enviamos al servidor
            if mensaje.strip():
                # Convertimos el texto a bytes usando .encode() antes de enviar
                cliente.send(mensaje.encode('utf-8'))
                
    except ConnectionRefusedError:
        print(f"[ERROR] No se pudo conectar. Asegúrate de que el servidor en {HOST}:{PUERTO} esté encendido.")
    except KeyboardInterrupt:
        # Captura si el usuario presiona Ctrl+C
        print("\n[SALIENDO] Has forzado el cierre del chat.")
    finally:
        # 5. Siempre, al salir, cerramos nuestra conexión de red de forma limpia
        cliente.close()

# Punto de entrada: Inicia el cliente si ejecutamos este archivo directamente
if __name__ == "__main__":
    iniciar_cliente()
