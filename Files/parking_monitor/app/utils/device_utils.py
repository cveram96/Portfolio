import os
import sys
import platform
import subprocess
from typing import Dict, Any, Optional, Tuple, List

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

try:
    import onnxruntime as ort
    HAS_ORT = True
except ImportError:
    HAS_ORT = False

_CACHED_GPUS: Optional[List[str]] = None
_CACHED_CPU: Optional[str] = None

def is_directml_available() -> bool:
    if not HAS_ORT:
        return False
    try:
        return "DmlExecutionProvider" in ort.get_available_providers()
    except Exception:
        return False

def is_cuda_available() -> bool:
    if not HAS_TORCH:
        return False
    try:
        return torch.cuda.is_available()
    except Exception:
        return False

def get_all_system_gpus() -> List[str]:
    global _CACHED_GPUS
    if _CACHED_GPUS is not None:
        return _CACHED_GPUS
    try:
        cmd = "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name"
        out = subprocess.check_output(["powershell", "-NoProfile", "-Command", cmd], text=True, stderr=subprocess.DEVNULL)
        lines = [line.strip() for line in out.splitlines() if line.strip()]
        physical = [l for l in lines if not any(x in l.lower() for x in ["virtual", "rdp", "remote", "vnc", "basic render"])]
        _CACHED_GPUS = physical if physical else lines
    except Exception:
        _CACHED_GPUS = []
    return _CACHED_GPUS

def get_system_gpu_info() -> str:
    gpus = get_all_system_gpus()
    return ", ".join(gpus) if gpus else "No GPU detected"

def get_system_cpu_info() -> str:
    global _CACHED_CPU
    if _CACHED_CPU is not None:
        return _CACHED_CPU
    try:
        cmd = "Get-CimInstance Win32_Processor | Select-Object -ExpandProperty Name"
        out = subprocess.check_output(["powershell", "-NoProfile", "-Command", cmd], text=True, stderr=subprocess.DEVNULL)
        lines = [line.strip() for line in out.splitlines() if line.strip()]
        _CACHED_CPU = lines[0] if lines else platform.processor() or "Standard Processor"
    except Exception:
        _CACHED_CPU = platform.processor() or "Standard Processor"
    return _CACHED_CPU

def resolve_device_config(preference: str = "auto") -> Tuple[str, str, str]:
    """
    Returns (effective_mode, model_path, status_message).
    effective_mode: 'gpu_dml', 'gpu_cuda', or 'cpu'.
    """
    pref = preference.strip().lower()
    dml_ok = is_directml_available()
    cuda_ok = is_cuda_available()
    gpus = get_all_system_gpus()
    gpu_desc = ", ".join(gpus) if gpus else "No GPU detected"
    cpu_name = get_system_cpu_info()

    has_nvidia_hardware = any("nvidia" in g.lower() or "geforce" in g.lower() or "rtx" in g.lower() or "gtx" in g.lower() for g in gpus)
    has_amd_hardware = any("amd" in g.lower() or "radeon" in g.lower() for g in gpus)

    from app.config.settings import DEFAULT_PT_MODEL, DEFAULT_ONNX_MODEL
    onnx_path = DEFAULT_ONNX_MODEL
    pt_path = DEFAULT_PT_MODEL
    model_to_use_for_dml = onnx_path if os.path.exists(onnx_path) else pt_path

    if pref in ["gpu_nvidia", "cuda"]:
        if cuda_ok:
            device_name = torch.cuda.get_device_name(0) if cuda_ok else "NVIDIA"
            return "gpu_cuda", pt_path, f"NVIDIA GPU active with CUDA ({device_name})"
        elif has_nvidia_hardware:
            return "cpu", pt_path, f"NVIDIA GPU physically detected, but PyTorch CUDA is not compiled. Using CPU ({cpu_name})"
        else:
            return "cpu", pt_path, f"NVIDIA CUDA not detected on this system. Using CPU ({cpu_name})"

    elif pref in ["gpu_amd", "dml", "directml"]:
        if dml_ok and os.path.exists(onnx_path):
            return "gpu_dml", model_to_use_for_dml, f"AMD Radeon GPU active with DirectML ({gpu_desc})"
        elif os.path.exists(onnx_path):
            return "gpu_dml", model_to_use_for_dml, f"DirectML GPU active ({gpu_desc})"
        else:
            return "cpu", pt_path, f"DirectML not available or ONNX model missing. Using CPU ({cpu_name})"

    elif pref in ["cpu"]:
        return "cpu", pt_path, f"CPU mode active ({cpu_name})"

    else:  # "auto"
        # Auto prioritization: NVIDIA CUDA -> AMD DirectML -> CPU
        if cuda_ok:
            device_name = torch.cuda.get_device_name(0)
            return "gpu_cuda", pt_path, f"Auto: NVIDIA GPU with CUDA active ({device_name})"
        elif has_amd_hardware and (dml_ok or os.path.exists(onnx_path)):
            return "gpu_dml", model_to_use_for_dml, f"Auto: AMD Radeon GPU detected ({gpu_desc}) with DirectML"
        elif dml_ok and os.path.exists(onnx_path):
            return "gpu_dml", model_to_use_for_dml, f"Auto: DirectML GPU ({gpu_desc})"
        else:
            return "cpu", pt_path, f"Auto: Running on CPU ({cpu_name})"

def get_hardware_status(active_mode: str = "auto") -> Dict[str, Any]:
    gpus = get_all_system_gpus()
    gpu_desc = ", ".join(gpus) if gpus else "No dedicated GPU"
    cpu_name = get_system_cpu_info()
    dml_ok = is_directml_available()
    cuda_ok = is_cuda_available()

    options = [
        {"id": "auto", "label": "Automatic Detection (Optimal)", "active": active_mode == "auto"},
        {"id": "gpu_amd", "label": f"AMD Radeon GPU [DirectML] ({'Active' if dml_ok else 'Available'})", "active": active_mode in ["gpu_amd", "dml", "gpu_dml"]},
        {"id": "gpu_nvidia", "label": f"NVIDIA GPU [CUDA / TensorRT] ({'CUDA Ready' if cuda_ok else 'PyTorch/CUDA'})", "active": active_mode in ["gpu_nvidia", "cuda", "gpu_cuda"]},
        {"id": "cpu", "label": f"CPU ({cpu_name})", "active": active_mode == "cpu"}
    ]

    return {
        "gpu_name": gpu_desc,
        "gpus": gpus,
        "cpu_name": cpu_name,
        "directml_supported": dml_ok,
        "cuda_supported": cuda_ok,
        "options": options,
        "active_mode": active_mode
    }
