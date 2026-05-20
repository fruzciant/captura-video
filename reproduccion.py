"""
Reproduccion de video con transformaciones interactivas.

Uso:
    python reproduccion.py video.avi
    python reproduccion.py video.mp4 --transformacion escala_grises

Controles durante la reproduccion:
    ESPACIO  - pausar / reanudar
    g        - escala de grises
    c        - color original
    r        - rotar 90 grados en sentido horario
    l        - rotar 90 grados en sentido antihorario
    f        - voltear horizontalmente (espejo)
    +/-      - aumentar / disminuir velocidad de reproduccion
    q        - salir
"""

import cv2
import argparse
import numpy as np

TRANSFORMACIONES_VALIDAS = ["ninguna", "escala_grises", "rotar_90", "rotar_180",
                             "rotar_270", "voltear"]


def parsear_args():
    parser = argparse.ArgumentParser(description="Reproduce video con transformaciones")
    parser.add_argument("video", type=str,
                        help="Ruta al archivo de video")
    parser.add_argument("--transformacion", type=str, default="ninguna",
                        choices=TRANSFORMACIONES_VALIDAS,
                        help="Transformacion inicial a aplicar")
    return parser.parse_args()


def aplicar_transformacion(frame, modo_grises, angulo_rotacion, voltear):
    resultado = frame.copy()

    if modo_grises:
        gris = cv2.cvtColor(resultado, cv2.COLOR_BGR2GRAY)
        resultado = cv2.cvtColor(gris, cv2.COLOR_GRAY2BGR)

    if angulo_rotacion != 0:
        if angulo_rotacion == 90:
            resultado = cv2.rotate(resultado, cv2.ROTATE_90_CLOCKWISE)
        elif angulo_rotacion == 180:
            resultado = cv2.rotate(resultado, cv2.ROTATE_180)
        elif angulo_rotacion == 270:
            resultado = cv2.rotate(resultado, cv2.ROTATE_90_COUNTERCLOCKWISE)

    if voltear:
        resultado = cv2.flip(resultado, 1)

    return resultado


def dibujar_estado(frame, pausa, modo_grises, angulo_rotacion, voltear, fps_actual):
    transformaciones = []
    if modo_grises:
        transformaciones.append("Grises")
    if angulo_rotacion != 0:
        transformaciones.append(f"Rot {angulo_rotacion}deg")
    if voltear:
        transformaciones.append("Espejo")

    estado_reproduccion = "PAUSADO" if pausa else f"{fps_actual:.0f} FPS"
    texto_trans = " | ".join(transformaciones) if transformaciones else "Sin transformacion"

    cv2.putText(frame, estado_reproduccion, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 0), 2)
    cv2.putText(frame, texto_trans, (10, 58),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 0), 1)

    ayuda = "[ESPACIO] pausa  [g] grises  [c] color  [r/l] rotar  [f] espejo  [+/-] vel  [q] salir"
    cv2.putText(frame, ayuda, (10, frame.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 180, 180), 1)


def main():
    args = parsear_args()

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        print(f"Error: no se pudo abrir '{args.video}'")
        return

    fps_original = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    ancho = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    alto = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(f"Video: {args.video}")
    print(f"  Resolucion : {ancho}x{alto}")
    print(f"  FPS        : {fps_original:.2f}")
    print(f"  Frames     : {total_frames}")
    print(f"  Duracion   : {total_frames / fps_original:.2f}s")

    # Estado inicial segun argumento --transformacion
    modo_grises = args.transformacion == "escala_grises"
    angulo_rotacion = {"rotar_90": 90, "rotar_180": 180,
                       "rotar_270": 270}.get(args.transformacion, 0)
    voltear = args.transformacion == "voltear"

    pausa = False
    multiplicador_vel = 1.0
    retardo_ms = max(1, int(1000 / fps_original))

    while True:
        if not pausa:
            ret, frame = cap.read()
            if not ret:
                # Reiniciar al llegar al final
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

        frame_transformado = aplicar_transformacion(frame, modo_grises,
                                                    angulo_rotacion, voltear)
        fps_actual = fps_original * multiplicador_vel
        dibujar_estado(frame_transformado, pausa, modo_grises,
                       angulo_rotacion, voltear, fps_actual)

        cv2.imshow("Reproduccion de Video", frame_transformado)

        espera = max(1, int(retardo_ms / multiplicador_vel))
        tecla = cv2.waitKey(espera) & 0xFF

        if tecla == ord("q"):
            break
        elif tecla == ord(" "):
            pausa = not pausa
        elif tecla == ord("g"):
            modo_grises = True
        elif tecla == ord("c"):
            modo_grises = False
        elif tecla == ord("r"):
            angulo_rotacion = (angulo_rotacion + 90) % 360
        elif tecla == ord("l"):
            angulo_rotacion = (angulo_rotacion - 90) % 360
        elif tecla == ord("f"):
            voltear = not voltear
        elif tecla == ord("+") or tecla == ord("="):
            multiplicador_vel = min(multiplicador_vel * 1.5, 8.0)
            print(f"Velocidad: {multiplicador_vel:.1f}x")
        elif tecla == ord("-"):
            multiplicador_vel = max(multiplicador_vel / 1.5, 0.25)
            print(f"Velocidad: {multiplicador_vel:.1f}x")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
