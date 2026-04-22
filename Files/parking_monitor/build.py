import PyInstaller.__main__
import os

print("Iniciando compilación de la aplicación...")
print("Esto puede tardar varios minutos debido a la inclusión de modelos de Inteligencia Artificial (YOLO, PyTorch)...")

PyInstaller.__main__.run([
    'main_app.py',
    '--name=ParkVisionAI',
    '--windowed', # Evita que se abra la consola negra detrás de la app
    '--onedir', # Mejor para IA, un solo exe tarda mucho en descomprimir
    '--collect-all=ultralytics',
    '--collect-all=sqlalchemy',
    '--add-data=gui/styles.qss;gui',
    '--add-data=parking_video.mp4;.',
    '--add-data=yolov8n.pt;.',
    '--icon=NONE' # Puedes agregar un archivo .ico aquí
])

print("¡Compilación terminada! Revisa la carpeta 'dist/ParkVisionAI'")
