"""
Adquisicion de video desde camara y guardado en archivo.

Uso:
    python adquisicion.py
    python adquisicion.py --salida mi_video.avi --fps 30 --camara 0

Controles durante la grabacion:
    ESPACIO  - iniciar / pausar grabacion
    q        - salir y guardar
"""

import cv2
import argparse
import time


def parsear_args():
    parser = argparse.ArgumentParser(description="Captura video desde camara")
    parser.add_argument("--camara", type=int, default=0,
                        help="Indice de la camara (default: 0)")
    parser.add_argument("--salida", type=str, default="video_capturado.avi",
                        help="Nombre del archivo de salida (default: video_capturado.avi)")
    parser.add_argument("--fps", type=float, default=20.0,
                        help="Fotogramas por segundo (default: 20)")
    parser.add_argument("--ancho", type=int, default=640,
                        help="Ancho del frame en pixeles (default: 640)")
    parser.add_argument("--alto", type=int, default=480,
                        help="Alto del frame en pixeles (default: 480)")
    return parser.parse_args()


def abrir_camara(indice, ancho, alto):
    # DirectShow es más estable que MSMF en Windows
    for backend in (cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY):
        cap = cv2.VideoCapture(indice, backend)
        if not cap.isOpened():
            cap.release()
            continue
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, ancho)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, alto)
        # Warmup: descartar frames iniciales hasta que la camara estabilice
        for _ in range(10):
            cap.read()
        ret, frame = cap.read()
        if ret and frame is not None:
            nombre_backend = {cv2.CAP_DSHOW: "DirectShow",
                              cv2.CAP_MSMF: "MSMF",
                              cv2.CAP_ANY: "auto"}.get(backend, str(backend))
            print(f"Camara abierta con backend: {nombre_backend}")
            return cap
        cap.release()
    return None


def main():
    args = parsear_args()

    cap = abrir_camara(args.camara, args.ancho, args.alto)
    if cap is None:
        print(f"Error: no se pudo abrir la camara {args.camara}")
        print("Comprueba que la camara no este en uso por otra aplicacion.")
        return

    ancho_real = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    alto_real = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    escritor = cv2.VideoWriter(args.salida, fourcc, args.fps,
                               (ancho_real, alto_real))

    grabando = False
    frames_grabados = 0
    tiempo_inicio = None

    print("Camara lista.")
    print("  ESPACIO -> iniciar/pausar grabacion")
    print("  q       -> salir y guardar")

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Advertencia: frame no disponible, reintentando...")
            continue

        if grabando:
            escritor.write(frame)
            frames_grabados += 1

        # Indicador visual de estado
        estado = "GRABANDO" if grabando else "EN PAUSA"
        color = (0, 0, 220) if grabando else (200, 200, 200)
        cv2.putText(frame, estado, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        if grabando and tiempo_inicio is not None:
            segundos = time.time() - tiempo_inicio
            cv2.putText(frame, f"Tiempo: {segundos:.1f}s  Frames: {frames_grabados}",
                        (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)

        cv2.imshow("Adquisicion de Video", frame)

        tecla = cv2.waitKey(1) & 0xFF
        if tecla == ord("q"):
            break
        elif tecla == ord(" "):
            grabando = not grabando
            if grabando:
                tiempo_inicio = time.time()
                print("Grabacion iniciada")
            else:
                print(f"Grabacion pausada — {frames_grabados} frames capturados")

    cap.release()
    escritor.release()
    cv2.destroyAllWindows()

    if frames_grabados > 0:
        duracion = frames_grabados / args.fps
        print(f"\nVideo guardado en '{args.salida}'")
        print(f"  Frames: {frames_grabados}  |  FPS: {args.fps}  |  Duracion: {duracion:.2f}s")
    else:
        print("\nNo se grabaron frames.")


if __name__ == "__main__":
    main()
