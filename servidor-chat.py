import socket
import threading

HOST = '127.0.0.1'
PUERTO = 5000

# Variables globales para el chat
clientes_conectados = []
historial_mensajes = []  # Reto especial: Guarda los últimos 5 mensajes

def retransmitir_mensaje(mensaje, socket_remitente):
    """Retransmite el mensaje a todos los clientes excepto al remitente y gestiona el historial."""
    historial_mensajes.append(mensaje)
    
    # Mantiene solo los últimos 5 mensajes
    if len(historial_mensajes) > 5:
        historial_mensajes.pop(0)

    for cliente in clientes_conectados:
        if cliente != socket_remitente:
            try:
                cliente.send(mensaje.encode('utf-8'))
            except Exception as e:
                print(f"[ERROR] {e}")

def manejar_cliente(socket_cliente, direccion_cliente):
    """Hilo dedicado a escuchar y atender a un cliente específico."""
    print(f"[NUEVA CONEXIÓN] Cliente conectado desde {direccion_cliente}")
    clientes_conectados.append(socket_cliente)
    
    # Enviar historial de los últimos mensajes al conectarse
    if historial_mensajes:
        socket_cliente.send("--- ÚLTIMOS MENSAJES ---\n".encode('utf-8'))
        for msj in historial_mensajes:
            socket_cliente.send(msj.encode('utf-8'))
        socket_cliente.send("------------------------\n".encode('utf-8'))
    else:
        socket_cliente.send("--- EL CHAT ESTÁ VACÍO ---\n".encode('utf-8'))

    try:
        while True:
            datos = socket_cliente.recv(1024)
            if not datos:
                break
                
            mensaje_texto = datos.decode('utf-8')
            # Corrección: Se agregó \n para que no se amontonen los mensajes en el historial
            mensaje_final = f"[{direccion_cliente[0]}:{direccion_cliente[1]}] dice: {mensaje_texto}\n"
            
            print(mensaje_final.strip())
            retransmitir_mensaje(mensaje_final, socket_cliente)
            
    except ConnectionResetError:
        print(f"[DESCONEXIÓN ABRUPTA] {direccion_cliente}")
    except Exception as e:
        print(f"[ERROR INESPERADO] {e}")
    finally:
        # Limpieza cuando un cliente se desconecta
        if socket_cliente in clientes_conectados:
            clientes_conectados.remove(socket_cliente)
        socket_cliente.close()
        
        print(f"[DESCONEXIÓN] Cliente {direccion_cliente} se ha ido.")
        retransmitir_mensaje(f"[SERVIDOR] El cliente {direccion_cliente} abandonó el chat.\n", None) 

def iniciar_servidor():
    """Configura e inicia el servidor TCP."""
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        servidor.bind((HOST, PUERTO))
        servidor.listen()
        print(f"[INICIANDO] Servidor escuchando en {HOST}:{PUERTO}...\n")
        
        while True:
            socket_cliente, direccion_cliente = servidor.accept()
            # Cada cliente es manejado en un hilo independiente para no bloquear el servidor
            hilo_cliente = threading.Thread(target=manejar_cliente, args=(socket_cliente, direccion_cliente))
            hilo_cliente.daemon = True
            hilo_cliente.start()
            
    except KeyboardInterrupt:
        print("\n[APAGANDO] Servidor detenido (Ctrl+C).")
    finally:
        servidor.close()
        print("[APAGADO COMPLETADO] Socket del servidor cerrado.")

if __name__ == "__main__":
    iniciar_servidor()
