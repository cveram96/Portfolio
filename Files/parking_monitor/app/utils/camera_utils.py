import os
import subprocess
import cv2
from typing import List, Dict, Any

def get_real_windows_cameras() -> List[Dict[str, Any]]:
    """
    Scans physical and virtual video input devices in Windows using DirectShow / PowerShell,
    returning a list of cameras with real friendly names and device IDs.
    """
    cameras = []
    
    # 1. Try querying DirectShow devices via PowerShell / PnP
    try:
        cmd = """
        Get-CimInstance Win32_PnPEntity | Where-Object { 
            $_.PNPClass -eq 'Camera' -or $_.PNPClass -eq 'Image' 
        } | Select-Object -ExpandProperty Caption
        """
        out = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command", cmd],
            text=True, stderr=subprocess.DEVNULL
        )
        names = [line.strip() for line in out.splitlines() if line.strip()]
        for idx, name in enumerate(names):
            # Test if OpenCV can open it
            cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
            is_valid = cap.isOpened()
            if is_valid:
                cap.release()
                cameras.append({
                    "id": idx,
                    "name": f"{name} (ID {idx})",
                    "type": "webcam"
                })
    except Exception:
        pass

    # 2. Fallback: standard probe up to 4 devices if no cameras returned or exception
    if not cameras:
        for idx in range(4):
            cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
            if cap.isOpened():
                cap.release()
                cameras.append({
                    "id": idx,
                    "name": f"Webcam {idx}",
                    "type": "webcam"
                })

    return cameras
