import cv2
import subprocess
import os

def get_camera_list():
    """
    Get list of available cameras with their names on Windows.
    Returns list of tuples: [(index, name), ...]
    """
    cameras = []
    
    # Test camera indices 0-9 and try to get names
    for i in range(10):
        try:
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                name = f"Cámara {i}"
                # Try to get the actual camera name
                try:
                    # Use PowerShell to find matching camera name
                    script_path = os.path.join(os.path.dirname(__file__), 'get_cameras.ps1')
                    if os.path.exists(script_path):
                        result = subprocess.run(
                            ['powershell', '-ExecutionPolicy', 'Bypass', '-File', script_path],
                            capture_output=True, text=True, timeout=5
                        )
                        if result.returncode == 0:
                            names = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
                            # Use the i-th name if available
                            if i < len(names):
                                name = names[i]
                except:
                    pass
                
                cameras.append((i, name))
                cap.release()
        except:
            pass
    
    if not cameras:
        cameras = [(0, "Cámara 0 (predeterminada)")]
    
    return cameras


if __name__ == "__main__":
    cams = get_camera_list()
    print("Cámaras disponibles:")
    for idx, name in cams:
        print(f"  [{idx}] {name}")
