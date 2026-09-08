import socket
import threading

# --- CONFIGURACIÓN DEL SERVIDOR ---
HOST = '127.0.0.1'  # Dirección local (localhost)
PUERTO = 5000       # Puerto donde el servidor escuchará conexiones

# --- VARIABLES GLOBALES (COMPARTIDAS ENTRE HILOS) ---
# Lista para guardar los sockets de los clientes conectados actualmente
clientes_conectados = []

# Lista para guardar los últimos 5 mensajes (Historial)
historial_mensajes = []


def retransmitir_mensaje(mensaje, socket_remitente):
    """
    Toma un mensaje y lo envía a todos los clientes conectados,
    excepto a quien lo envió originalmente.
    También gestiona el guardado del historial.
    """
    # 1. Guardar el mensaje en el historial global
    historial_mensajes.append(mensaje)
    
    # 2. Si el historial tiene más de 5 mensajes, eliminamos el más viejo (posición 0)
    # Esto mantiene la lista siempre con un máximo de 5 elementos.
    if len(historial_mensajes) > 5:
        historial_mensajes.pop(0)

    # 3. Enviar el mensaje a todos los demás clientes
    for cliente in clientes_conectados:
        # Comparamos que no le estemos enviando el mensaje a quien lo escribió
        if cliente != socket_remitente:
            try:
                # El mensaje es texto, pero los sockets envían BYTES. Usamos .encode()
                cliente.send(mensaje.encode('utf-8'))
            except Exception as e:
                # Si falla el envío (ej: el cliente cerró su conexión de golpe)
                print(f"[ERROR] No se pudo enviar mensaje. {e}")
                # Nota: No eliminamos al cliente aquí de la lista para evitar errores 
                # al modificar la lista mientras la recorremos (for). 
                # El hilo del cliente se encargará de limpiarlo en su bloque 'finally'.


def manejar_cliente(socket_cliente, direccion_cliente):
    """
    Esta función atiende a UN solo cliente. 
    Se ejecuta en un "Hilo" (Thread) separado para cada persona que se conecta.
    """
    print(f"[NUEVA CONEXIÓN] Cliente conectado desde {direccion_cliente}")
    
    # Añadimos el nuevo cliente a nuestra lista global para poder enviarle mensajes luego
    clientes_conectados.append(socket_cliente)
    
    # --- RETO ESPECIAL: Enviar el historial de los últimos 5 mensajes ---
    # Revisamos si hay mensajes previos en la lista
    if len(historial_mensajes) > 0:
        socket_cliente.send("--- ÚLTIMOS MENSAJES (HISTORIAL) ---\n".encode('utf-8'))
        # Recorremos la lista del historial y enviamos mensaje por mensaje al nuevo usuario
        for msj in historial_mensajes:
            socket_cliente.send(msj.encode('utf-8'))
        socket_cliente.send("------------------------------------\n".encode('utf-8'))
    else:
        # Si la lista está vacía, es el primer cliente en llegar
        socket_cliente.send("--- EL CHAT ESTÁ VACÍO. ¡SÉ EL PRIMERO EN HABLAR! ---\n".encode('utf-8'))

    # Bucle principal: Escuchar lo que dice este cliente todo el tiempo
    try:
        while True:
            # recv(1024) frena la ejecución hasta recibir datos (máximo 1024 bytes)
            datos_recibidos = socket_cliente.recv(1024)
            
            # Si datos_recibidos está vacío, significa que el cliente cerró la conexión amablemente
            if not datos_recibidos:
                break
                
            # Decodificamos los bytes recibidos a texto (string)
            mensaje_texto = datos_recibidos.decode('utf-8')
            
            # Preparamos el mensaje final agregando quién lo envió (su IP y Puerto)
            # Ejemplo: "[127.0.0.1:54321] dice: Hola a todos"
            mensaje_final = f"[{direccion_cliente[0]}:{direccion_cliente[1]}] dice: {mensaje_texto}"
            
            # Imprimimos en la consola del servidor para tener un registro (log)
            print(mensaje_final.strip())
            
            # Llamamos a nuestra función para reenviar este mensaje a todos los demás
            retransmitir_mensaje(mensaje_final, socket_cliente)
            
    except ConnectionResetError:
        # Si el cliente cierra la terminal a la fuerza, atrapamos el error específico 
        # para que NO se caiga nuestro servidor.
        print(f"[DESCONEXIÓN ABRUPTA] El cliente {direccion_cliente} cerró la ventana inesperadamente.")
    except Exception as e:
        # Atrapamos cualquier otro error raro por si acaso
        print(f"[ERROR INESPERADO] Con el cliente {direccion_cliente}: {e}")
    finally:
        # IMPORTANTE: Este bloque 'finally' se ejecuta SIEMPRE, al salir del try/except.
        # Aquí hacemos la "limpieza" cuando un cliente se va, haya sido por error o salida normal.
        
        # 1. Lo quitamos de la lista global de conectados
        if socket_cliente in clientes_conectados:
            clientes_conectados.remove(socket_cliente)
        
        # 2. Cerramos su conexión de red de forma segura
        socket_cliente.close()
        
        # 3. Avisamos en la consola del servidor (log)
        print(f"[DESCONEXIÓN] Cliente {direccion_cliente} se ha ido.")
        
        # 4. Avisamos a los demás clientes que alguien se fue
        # Pasamos None como remitente porque este mensaje lo origina el propio servidor
        mensaje_despedida = f"[SERVIDOR] El cliente {direccion_cliente} abandonó el chat.\n"
        retransmitir_mensaje(mensaje_despedida, None) 


def iniciar_servidor():
    """
    Función principal que arranca el servidor, prepara el puerto y espera clientes.
    """
    # 1. Creamos el socket principal del servidor (TCP sobre IPv4)
    # AF_INET = usar protocolo IPv4
    # SOCK_STREAM = usar protocolo TCP (ideal para chats porque no pierde mensajes)
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 2. Configuración para evitar el error "Puerto en uso" si reiniciamos el servidor rápido
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        # 3. Enlazamos el servidor a la dirección (IP) y puerto (5000)
        servidor.bind((HOST, PUERTO))
        
        # 4. Ponemos el servidor a "escuchar" conexiones entrantes
        servidor.listen()
        print(f"[INICIANDO] Servidor de Chat escuchando en {HOST}:{PUERTO}...")
        print("[INFO] Esperando conexiones...\n")
        
        # 5. Bucle infinito para aceptar múltiples clientes
        while True:
            # accept() pausa el programa hasta que alguien se conecta.
            # Devuelve un NUEVO socket exclusivo para hablar con ese cliente, y su IP/Puerto.
            socket_cliente, direccion_cliente = servidor.accept()
            
            # Creamos un NUEVO HILO para atender a este cliente sin pausar el servidor.
            # Target = qué función va a ejecutar el hilo
            # Args = los datos que le pasamos a esa función (el socket y la dirección)
            hilo_cliente = threading.Thread(target=manejar_cliente, args=(socket_cliente, direccion_cliente))
            
            # daemon=True hace que los hilos se destruyan automáticamente si apagamos el programa principal
            hilo_cliente.daemon = True
            
            # ¡Arrancamos el hilo! Ahora manejar_cliente se está ejecutando en paralelo
            hilo_cliente.start()
            
    except KeyboardInterrupt:
        # Si presionamos Ctrl+C en la terminal, cerramos todo amablemente
        print("\n[APAGANDO] Servidor detenido por el administrador (Ctrl+C).")
    finally:
        # Nos aseguramos de cerrar el socket principal al terminar todo
        servidor.close()
        print("[APAGADO COMPLETADO] Socket del servidor cerrado.")

# Punto de entrada del programa. Si ejecutamos este archivo directamente, arranca el servidor.
if __name__ == "__main__":
    iniciar_servidor()
