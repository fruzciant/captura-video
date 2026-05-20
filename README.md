# Adquisición y Análisis de Video con Python y OpenCV

## 1. ¿Qué es un video?

Un video es una **secuencia de imágenes** (llamadas *frames* o fotogramas) reproducidas en orden a una velocidad suficientemente alta para que el ojo humano perciba movimiento continuo. Cada frame es, en términos digitales, una matriz de píxeles con valores de color o intensidad.

```
Frame 1  →  Frame 2  →  Frame 3  →  ...  →  Frame N
  🖼️           🖼️           🖼️                  🖼️
  t=0 s       t=0.04 s    t=0.08 s          t=fin
```

### Representación en memoria

Cuando OpenCV lee un frame, lo almacena como un array de NumPy con forma `(alto, ancho, canales)`:

- **Canal** = componente de color. En BGR (formato por defecto de OpenCV): azul, verde, rojo.
- Cada valor de canal es un entero de 8 bits (0–255).

```python
import cv2
cap = cv2.VideoCapture("video.avi")
ret, frame = cap.read()
print(frame.shape)  # e.g. (480, 640, 3)
```

---

## 2. Conceptos clave

### 2.1 FPS — Fotogramas por segundo (*Frames Per Second*)

El **FPS** indica cuántas imágenes se capturan o reproducen cada segundo.

| FPS | Uso típico |
|-----|-----------|
| 24 | Cine |
| 30 | Televisión, webcams estándar |
| 60 | Videojuegos, cámaras de acción |
| 120–240 | Cámara lenta (*slow motion*) |

Un video a 30 FPS dura 10 segundos → contiene **300 frames**.

> **Relación tiempo–frame:**
> `tiempo (s) = número_de_frame / FPS`

### 2.2 Resolución

Dimensiones en píxeles del frame: `ancho × alto`.  
Ejemplos comunes: 640×480, 1280×720 (HD), 1920×1080 (Full HD).

### 2.3 Códec y contenedor

- **Contenedor** (extensión del archivo): `.avi`, `.mp4`, `.mkv` — define cómo se empaqueta la información.
- **Códec** (algoritmo de compresión): XVID, H.264, HEVC — define cómo se comprimen los frames.

OpenCV usa **FOURCC** para especificar el códec al escribir:

```python
fourcc = cv2.VideoWriter_fourcc(*"XVID")   # para .avi
fourcc = cv2.VideoWriter_fourcc(*"mp4v")   # para .mp4
```

### 2.4 VideoCapture y VideoWriter

`cv2.VideoCapture` abre una fuente de video (archivo o cámara):

```python
cap = cv2.VideoCapture(0)          # cámara índice 0
cap = cv2.VideoCapture("video.avi")  # archivo
```

`cv2.VideoWriter` escribe frames a un archivo:

```python
escritor = cv2.VideoWriter("salida.avi", fourcc, fps, (ancho, alto))
escritor.write(frame)
escritor.release()
```

---

## 3. Transformaciones de imagen básicas

Cada frame es una imagen, por lo que todas las operaciones de procesamiento de imágenes aplican directamente.

### 3.1 Escala de grises

Reduce los 3 canales de color a 1 canal de luminancia. Útil para reducir complejidad computacional.

```python
gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
```

Para mostrar la imagen en gris manteniendo 3 canales (compatibilidad con VideoWriter):

```python
gris_bgr = cv2.cvtColor(gris, cv2.COLOR_GRAY2BGR)
```

### 3.2 Rotación

OpenCV ofrece rotaciones de 90° de forma eficiente:

```python
rotado = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
rotado = cv2.rotate(frame, cv2.ROTATE_180)
rotado = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
```

Para ángulos arbitrarios se usa una matriz de transformación afín:

```python
alto, ancho = frame.shape[:2]
centro = (ancho // 2, alto // 2)
M = cv2.getRotationMatrix2D(centro, angulo, escala=1.0)
rotado = cv2.warpAffine(frame, M, (ancho, alto))
```

### 3.3 Volteo (espejo)

```python
espejo = cv2.flip(frame, 1)   # horizontal
espejo = cv2.flip(frame, 0)   # vertical
```

---

## 4. Scripts del repositorio

### `adquisicion.py` — Captura desde cámara

Abre la cámara, permite iniciar/pausar la grabación con `ESPACIO` y guarda el video al salir con `q`.

```bash
python adquisicion.py
python adquisicion.py --salida clase_01.avi --fps 30 --camara 0
```

**Argumentos:**

| Argumento | Descripción | Default |
|-----------|-------------|---------|
| `--camara` | Índice de la cámara | `0` |
| `--salida` | Archivo de salida | `video_capturado.avi` |
| `--fps` | Fotogramas por segundo | `20` |
| `--ancho` | Ancho en píxeles | `640` |
| `--alto` | Alto en píxeles | `480` |

### `reproduccion.py` — Reproducción con transformaciones

Carga un video y permite aplicar transformaciones en tiempo real mediante teclas.

```bash
python reproduccion.py video_capturado.avi
python reproduccion.py video.mp4 --transformacion escala_grises
```

**Controles interactivos:**

| Tecla | Acción |
|-------|--------|
| `ESPACIO` | Pausar / reanudar |
| `g` | Activar escala de grises |
| `c` | Restaurar color original |
| `r` | Rotar 90° horario |
| `l` | Rotar 90° antihorario |
| `f` | Voltear horizontalmente |
| `+` / `-` | Aumentar / disminuir velocidad |
| `q` | Salir |

---

## 5. Instalación de dependencias

```bash
pip install opencv-python numpy
```

Para verificar la instalación:

```python
import cv2
print(cv2.__version__)
```

---

## 6. Flujo de trabajo sugerido

```
1. Capturar video    →   python adquisicion.py --salida experimento.avi
2. Revisar y analizar →  python reproduccion.py experimento.avi
3. Aplicar transformaciones interactivas con las teclas del reproductor
```

---

## 7. Ejercicios propuestos

1. Modifica `adquisicion.py` para que muestre en pantalla el tiempo transcurrido y los FPS reales de la cámara (`CAP_PROP_FPS`).
2. Agrega en `reproduccion.py` una transformación de **detección de bordes** con `cv2.Canny`.
3. Modifica `reproduccion.py` para guardar el video transformado en un nuevo archivo al presionar `s`.
4. Investiga la diferencia visual entre rotar con `cv2.rotate` y rotar con `cv2.warpAffine` a 45°.
