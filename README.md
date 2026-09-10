# 📚 Proyecto Integrador: Chat Cliente-Servidor Multi-usuario

**Materia:** Programación Distribuida
**Institución:** Facultad de Telemática, Universidad de Colima

## 🎯 Descripción del Proyecto
Este repositorio contiene la implementación de un chat de texto por terminal con arquitectura cliente-servidor, desarrollado en Python. Permite que múltiples usuarios se conecten simultáneamente y conversen en tiempo real mediante el uso de Sockets TCP e hilos (threading).

## ✅ Características Principales (Requisitos Base)
*   **Servidor TCP Multiusuario:** Acepta múltiples conexiones concurrentes. El servidor (`servidor-chat.py`) asigna un hilo independiente (`threading.Thread`) a cada cliente mediante la función `manejar_cliente`, permitiendo atender a múltiples usuarios sin bloquear la ejecución.
*   **Broadcast en Tiempo Real:** Cada mensaje enviado por un cliente es retransmitido automáticamente por el servidor a todos los demás clientes conectados a través de la función `retransmitir_mensaje`.
*   **Tolerancia a Fallos y Manejo de Errores:** El servidor está diseñado para soportar desconexiones abruptas (ej. si un cliente cierra la terminal a la fuerza). Utiliza bloques `try/except` para atrapar excepciones como `ConnectionResetError`, limpia la conexión removiendo al cliente de la lista global de sockets, y el chat sigue funcionando ininterrumpidamente para el resto.

## ⭐ Reto Especial Asignado: Historial para Nuevos Usuarios
Como parte de los requerimientos específicos de nuestro equipo, el servidor incluye la siguiente funcionalidad:
*   **Historial de los últimos 5 mensajes:** Al momento de que un nuevo cliente se conecta, el servidor le envía de forma automática los últimos mensajes intercambiados en el chat general (hasta un máximo de 5).
*   **Implementación técnica:** Esto se logró utilizando una lista global (`historial_mensajes`) en el servidor. Cada vez que se retransmite un mensaje, se agrega a esta lista. Si la lista supera los 5 elementos, se elimina el más antiguo (`historial_mensajes.pop(0)`). Al conectarse un nuevo usuario, se itera sobre esta lista y se le envían los mensajes guardados. El historial almacena el formato directo del mensaje, enfocándose exclusivamente en el contenido sin requerir que los clientes configuren un nombre de usuario ni gestionando marcas de tiempo complejas.

## 📁 Estructura del Repositorio
*   **`servidor-chat.py`:** Script principal del servidor. Escucha conexiones entrantes en `127.0.0.1:5000`. Gestiona la lista de `clientes_conectados`, almacena en memoria el `historial_mensajes` y realiza el broadcast. Maneja las desconexiones informando a los demás usuarios ("[SERVIDOR] El cliente X abandonó el chat").
*   **`cliente-chat.py`:** Script del cliente. Maneja la conexión TCP hacia el servidor. Utiliza un hilo (`hilo_recepcion`) que ejecuta la función `recibir_mensajes` para escuchar datos del servidor de forma constante y asíncrona, mientras que el hilo principal se queda a la espera de la entrada del usuario (`input()`) para enviar nuevos mensajes.

## 🚀 Instrucciones de Ejecución

1.  **Iniciar el Servidor:**
    Abre una terminal y ejecuta el script del servidor. Este debe estar en ejecución antes de que cualquier cliente intente conectarse.
    ```bash
    python servidor-chat.py
    ```
2.  **Iniciar los Clientes:**
    Abre múltiples terminales adicionales (una por cada usuario) y ejecuta el script del cliente en cada una de ellas.
    ```bash
    python cliente-chat.py
    ```
3.  **Pruebas de Funcionamiento:**
    *   Escribe mensajes en la terminal de un cliente; observarás cómo se replican (broadcast) hacia todos los demás (excepto al remitente original).
    *   Cierra un cliente abruptamente (Ctrl+C o cerrando la ventana) para comprobar que el servidor captura el error `ConnectionResetError` y no se detiene.
    *   Conecta un cliente nuevo después de haber enviado al menos 5 mensajes para validar la recepción de la cabecera "--- ÚLTIMOS MENSAJES (HISTORIAL) ---" seguida de los últimos 5 mensajes exactos.

## 👥 Equipo de Trabajo
*   **Said López Jr** 
*   **Ethan José Carbajal Guzmán** - 
*   **Jonathan Alejandro Flores Gómez** - 

---
*Este proyecto documenta nuestro proceso real, arquitectura y resolución de problemas de cara a la evaluación y presentación en vivo de la Sesión 09.*