import urllib.request
import os

urls = [
    ("parking_2.mp4", "https://raw.githubusercontent.com/computervisioneng/parking-space-counter/master/carPark.mp4"),
    ("parking_3.mp4", "https://raw.githubusercontent.com/DeGirum/PySDKExamples/main/images/Parking.mp4")
]

for name, url in urls:
    try:
        if not os.path.exists(name):
            print(f"Descargando {name}...")
            urllib.request.urlretrieve(url, name)
            print(f"Descargado {name} exitosamente.")
    except Exception as e:
        print(f"Fallo al descargar {name}: {e}")
