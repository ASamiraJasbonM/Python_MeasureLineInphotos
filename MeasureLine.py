import cv2
import numpy as np

class LineaRecta:
    def __init__(self, image):
        self.original_image = image
        self.image = image.copy()
        self.puntos = []
        self.moviendo_punto = -1
        self.factor_escala = 1.0
        self.texto = ""
        self.puntos_dependientes = []
        self.magnitud_cm = 0
        self.distancia_pixeles_referencia = 0

    def click_event(self, event, x, y, flags, param):
        x_original = int(x / self.factor_escala)
        y_original = int(y / self.factor_escala)
        
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(self.puntos) < 2:
                self.puntos.append((x_original, y_original))
            else:
                for i, punto in enumerate(self.puntos):
                    if abs(punto[0] - x_original) < 10 and abs(punto[1] - y_original) < 10:
                        self.moviendo_punto = i
                        break
            self.dibujar_linea()

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.moviendo_punto != -1:
                self.puntos[self.moviendo_punto] = (x_original, y_original)
                self.limitar_puntos()
                self.dibujar_linea()

        elif event == cv2.EVENT_LBUTTONUP:
            self.moviendo_punto = -1

    def escalar_imagen(self, aumentar=True):
        if aumentar:
            self.factor_escala *= 1.1  # Incrementar el tamaño en un 10%
        else:
            self.factor_escala /= 1.1  # Reducir el tamaño en un 10%
        nuevo_ancho = int(self.original_image.shape[1] * self.factor_escala)
        nuevo_alto = int(self.original_image.shape[0] * self.factor_escala)
        self.image = cv2.resize(self.original_image, (nuevo_ancho, nuevo_alto))
        self.dibujar_linea()

    def dibujar_linea(self):
        imagen_temp = self.image.copy()
        if len(self.puntos) == 2:
            punto1 = (int(self.puntos[0][0] * self.factor_escala), int(self.puntos[0][1] * self.factor_escala))
            punto2 = (int(self.puntos[1][0] * self.factor_escala), int(self.puntos[1][1] * self.factor_escala))
            cv2.line(imagen_temp, punto1, punto2, (0, 255, 0), 2)
            # Añadir texto sobre la línea
            midpoint = ((punto1[0] + punto2[0]) // 2, (punto1[1] + punto2[1]) // 2)
            cv2.putText(imagen_temp, self.texto, midpoint, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            # Dibujar la línea dependiente
            if len(self.puntos_dependientes) == 2:
                punto_dep1 = (int(self.puntos_dependientes[0][0] * self.factor_escala), int(self.puntos_dependientes[0][1] * self.factor_escala))
                punto_dep2 = (int(self.puntos_dependientes[1][0] * self.factor_escala), int(self.puntos_dependientes[1][1] * self.factor_escala))
                cv2.line(imagen_temp, punto_dep1, punto_dep2, (255, 0, 0), 2)
                # Añadir texto sobre la línea dependiente
                midpoint_dep = ((punto_dep1[0] + punto_dep2[0]) // 2, (punto_dep1[1] + punto_dep2[1]) // 2)
                distancia_pixeles = np.sqrt((self.puntos_dependientes[1][0] - self.puntos_dependientes[0][0])**2 + (self.puntos_dependientes[1][1] - self.puntos_dependientes[0][1])**2)
                if self.distancia_pixeles_referencia != 0:
                    magnitud_cm = (distancia_pixeles / self.distancia_pixeles_referencia) * self.magnitud_cm
                    cv2.putText(imagen_temp, f"{magnitud_cm:.2f} cm", midpoint_dep, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)
        for punto in self.puntos:
            punto_escalado = (int(punto[0] * self.factor_escala), int(punto[1] * self.factor_escala))
            cv2.circle(imagen_temp, punto_escalado, 5, (0, 0, 255), -1)
        cv2.imshow('Imagen', imagen_temp)

    def asignar_texto(self, texto):
        self.texto = texto
        self.magnitud_cm = float(texto)
        if len(self.puntos) == 2:
            self.distancia_pixeles_referencia = np.sqrt((self.puntos[1][0] - self.puntos[0][0])**2 + (self.puntos[1][1] - self.puntos[0][1])**2)
        self.dibujar_linea()

    def limitar_puntos(self):
        for i, (x, y) in enumerate(self.puntos):
            x = max(0, min(x, self.original_image.shape[1] - 1))
            y = max(0, min(y, self.original_image.shape[0] - 1))
            self.puntos[i] = (x, y)

    def agregar_linea_dependiente(self):
        self.puntos_dependientes = []
        self.moviendo_punto = -1
        cv2.setMouseCallback('Imagen', self.click_event_dependiente)

    def click_event_dependiente(self, event, x, y, flags, param):
        x_original = int(x / self.factor_escala)
        y_original = int(y / self.factor_escala)
        
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(self.puntos_dependientes) < 2:
                self.puntos_dependientes.append((x_original, y_original))
            else:
                for i, punto in enumerate(self.puntos_dependientes):
                    if abs(punto[0] - x_original) < 10 and abs(punto[1] - y_original) < 10:
                        self.moviendo_punto = i
                        break
            self.dibujar_linea()

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.moviendo_punto != -1:
                self.puntos_dependientes[self.moviendo_punto] = (x_original, y_original)
                self.limitar_puntos_dependientes()
                self.dibujar_linea()

        elif event == cv2.EVENT_LBUTTONUP:
            self.moviendo_punto = -1

    def limitar_puntos_dependientes(self):
        for i, (x, y) in enumerate(self.puntos_dependientes):
            x = max(0, min(x, self.original_image.shape[1] - 1))
            y = max(0, min(y, self.original_image.shape[0] - 1))
            self.puntos_dependientes[i] = (x, y)

# Cargar la imagen
image = cv2.imread('plano.PNG')

# Crear una instancia de la clase LineaRecta
linea_recta = LineaRecta(image)

# Función para manejar las teclas
def manejar_teclas():
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('g'):
            linea_recta.escalar_imagen(aumentar=True)
        elif key == ord('f'):
            linea_recta.escalar_imagen(aumentar=False)
        elif key == ord('t'):
            texto = input("Write rhe reference size: ")
            linea_recta.asignar_texto(texto)
        elif key == ord('n'):
            linea_recta.agregar_linea_dependiente()
        elif key == 27:  # Tecla 'Esc' para salir
            break

# Mostrar la imagen y configurar el evento de clic
cv2.imshow('Imagen', image)
cv2.setMouseCallback('Imagen', linea_recta.click_event)

# Manejar las teclas
manejar_teclas()

cv2.destroyAllWindows()
