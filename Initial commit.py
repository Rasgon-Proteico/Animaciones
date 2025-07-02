"""""""""""""""""""""""""""""""""

How to draw a circle   :)   

"""""""""""""""""""""""""""""""""


import time 
from machine import Pin, I2C  
import sh1106  



SCL_PIN = 22 
SDA_PIN = 21 
ANCHO_PANTALLA = 128 
ALTO_PANTALLA = 64   


print("Inicializando bus I2C...")
# Un bloque `try...except` se usa para manejar errores. Si algo falla durante la
# inicialización, el programa no se detendrá bruscamente, sino que mostrará un error controlado.
try:
    # Se crea el objeto I2C.
    # Parámetro 0: indica que se usará el bus I2C número 0 del ESP32.
    i2c = I2C(0, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=400000)

    
    devices = i2c.scan()

    if not devices:
        raise Exception("No se encontraron dispositivos I2C.") # Lanza un error personalizado.

    # Si se encuentran dispositivos, se imprime su dirección en formato hexadecimal.
    print("Dispositivos I2C encontrados:", [hex(device) for device in devices])

except Exception as e:
    print(f"Error fatal al inicializar I2C: {e}")
    import sys
    sys.exit()  

print("\nInicializando pantalla OLED...")
try:
    # Se crea el objeto `display` que representa nuestra pantalla física.
    # sh1106.SH1106_I2C: es la clase del driver para una pantalla SH1106 conectada por I2C.
    # Se le pasan las dimensiones, el objeto `i2c` que creamos antes, y la dirección
    # del dispositivo en el bus I2C (0x3c es la dirección más común para estas pantallas).
    display = sh1106.SH1106_I2C(ANCHO_PANTALLA, ALTO_PANTALLA, i2c, addr=0x3c)

    # Rota la orientación de la pantalla 180 grados. Es útil si el montaje físico está al revés.
    # Pon `False` o elimina la línea si no necesitas rotarla.
    display.rotate(True)

    # `display.fill(0)` limpia el búfer de la pantalla. El búfer es una memoria interna
    # donde se "dibuja" la imagen antes de mostrarla. 0 significa píxel apagado (negro).
    display.fill(0)

    # Se escribe un texto de bienvenida en el búfer.
    display.text('Animation...', 15, 28) # texto, coord-x, coord-y

    # `display.show()` envía el contenido del búfer a la pantalla física para que se muestre.
    # Cualquier cosa dibujada con `pixel`, `text`, `fill`, etc., no será visible hasta que se llame a `show()`.
    display.show()
    print("  Pantalla OLED inicializada.")
    time.sleep(2)  # Pausa de 2 segundos para que el mensaje sea legible.

except Exception as e:
    # Captura errores específicos de la inicialización de la pantalla.
    print(f"ERROR AL INICIALIZAR LA PANTALLA: {e}")
    import sys
    sys.exit() # Detiene el script si la pantalla no funciona.

print("-" * 20)


# Esta función utiliza el Algoritmo de Círculo de Bresenham, solo usa números enteros
 

def draw_clipped_circle(x0, y0, radius, color):
    """
    Dibuja un círculo centrado en (x0, y0) con un radio `radius`.
    La parte "clipped" (recortada) significa que no intentará dibujar
    píxeles que estén fuera de los límites de la pantalla, evitando errores.
    """
    """
    comentario largo oooo
    """
    # Se define una "función auxiliar" o "helper" dentro de esta función.
    # Su único propósito es dibujar un píxel de forma segura.
    def safe_pixel(x, y, c):
        # Antes de intentar dibujar, comprueba si las coordenadas (x, y) están
        # dentro de los límites visibles de la pantalla.
        if 0 <= x < ANCHO_PANTALLA and 0 <= y < ALTO_PANTALLA:
            # Solo si las coordenadas son válidas, se llama a la función de la librería
            # para encender el píxel en el búfer.
            display.pixel(x, y, c)

    # --- Inicio del Algoritmo de Bresenham ---
    # Variables de decisión y contadores del algoritmo.
    f = 1 - radius
    ddf_x = 1
    ddf_y = -2 * radius
    x = 0
    y = radius

    # El algoritmo es simétrico. Primero dibuja los 4 puntos cardinales del círculo.
    safe_pixel(x0, y0 + radius, color)        # Punto superior
    safe_pixel(x0, y0 - radius, color)        # Punto inferior
    safe_pixel(x0 + radius, y0, color)        # Punto derecho
    safe_pixel(x0 - radius, y0, color)        # Punto izquierdo

    # El bucle `while x < y` calcula los píxeles solo para un octante (1/8) del círculo.
    # Esto es una optimización enorme, ya que los otros 7 octantes se pueden
    # deducir por simetría.
    while x < y:
        # La variable `f` es un término de error que decide si el siguiente
        # píxel debe estar más cerca en la horizontal o en la diagonal.
        if f >= 0:
            y -= 1
            ddf_y += 2
            f += ddf_y
        x += 1
        ddf_x += 2
        f += ddf_x

        # Por cada píxel (x, y) calculado en el primer octante, dibujamos
        # sus 8 equivalentes simétricos en todo el círculo.
        safe_pixel(x0 + x, y0 + y, color)
        safe_pixel(x0 - x, y0 + y, color)
        safe_pixel(x0 + x, y0 - y, color)
        safe_pixel(x0 - x, y0 - y, color)
        safe_pixel(x0 + y, y0 + x, color)
        safe_pixel(x0 - y, y0 + x, color)
        safe_pixel(x0 + y, y0 - x, color)
        safe_pixel(x0 - y, y0 - x, color)

# === 6. BUCLE PRINCIPAL DE LA ANIMACIÓN ===
print("Iniciando animación... (Presiona Ctrl+C para detener)")

# Se calcula la coordenada central de la pantalla para el círculo.
# El operador `//` realiza una división entera (ej. 64 // 2 = 32).
centro_x =  ANCHO_PANTALLA // 2
centro_y =  ALTO_PANTALLA // 2

# Definimos hasta dónde crecerá el radio. Lo hacemos un poco más grande que la
# pantalla para que el círculo desaparezca por completo por los bordes.
# Gracias a `safe_pixel`, esto no causará errores.
radio_maximo = (ANCHO_PANTALLA // 2) + 20

# `while True` crea un bucle infinito que mantendrá la animación corriendo.
while True:
    try:
        # Este bucle `for` es el que genera cada "fotograma" de la animación.
        #? `range(start, stop, step)` genera una secuencia de números.
        # Aquí, `radio_actual` tomará los valores: 0, 3, 6, 9, ... hasta `radio_maximo`.
        # El `step` de 3 hace que el círculo crezca más rápido. Un `step` de 1 sería más suave pero más lento.
        for radio_actual in range(0, radio_maximo, 2):
            # PASO 1: Limpiar el fotograma anterior.
            # Se borra todo el contenido del búfer para empezar a dibujar el nuevo fotograma.
            display.fill(0)

            # PASO 2: Dibujar el nuevo contenido.
            # Se llama a nuestra función para dibujar un círculo en el centro, con el radio
            # que corresponda a esta iteración del bucle. El color 1 es "encendido" (blanco/azul).
            draw_clipped_circle(centro_x, centro_y, radio_actual, 1)

            # PASO 3: Mostrar el nuevo fotograma.
            # Se envía el búfer actualizado (con el nuevo círculo) a la pantalla.
            display.show()
            # Este ciclo de fill->draw->show se repite rápidamente, creando la ilusión de movimiento.

    # Si el usuario presiona Ctrl+C en la consola, se genera una excepción `KeyboardInterrupt`.
    except KeyboardInterrupt:
        print("\nPrograma detenido por el usuario.")
        break
    # Captura cualquier otro error inesperado que pueda ocurrir durante la animación.
    except Exception as e:
        print(f"\nOcurrió un error en el bucle: {e}")
        break

# === 7. APAGADO Y LIMPIEZA ===
# Este código se ejecuta una vez que el bucle `while` ha terminado (por Ctrl+C o un error).
# Es una buena práctica dejar la pantalla limpia.
display.fill(0)
display.show()
print("Animación terminada. ¡Adiós!")
