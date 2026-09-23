import os

# Project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_DIR = os.path.join(BASE_DIR, "models")
SAMPLES_DIR = os.path.join(BASE_DIR, "samples")
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Database & File Storage
DB_PATH = os.path.join(DATA_DIR, "parking.db")
SPOTS_FILE = os.path.join(DATA_DIR, "spots.json")
EXCLUSION_ZONES_FILE = os.path.join(DATA_DIR, "exclusion_zones.json")

# Model paths
DEFAULT_PT_MODEL = os.path.join(MODELS_DIR, "yolov8n.pt")
DEFAULT_ONNX_MODEL = os.path.join(MODELS_DIR, "yolov8n.onnx")
if not os.path.exists(DEFAULT_PT_MODEL):
    DEFAULT_PT_MODEL = os.path.join(BASE_DIR, "yolov8n.pt")
if not os.path.exists(DEFAULT_ONNX_MODEL):
    DEFAULT_ONNX_MODEL = os.path.join(BASE_DIR, "yolov8n.onnx")

# Target vehicle classes (COCO dataset): 2: car, 3: motorcycle, 5: bus, 7: truck
VEHICLE_CLASSES = [2, 3, 5, 7]
CLASS_NAMES = {
    2: "Car",
    3: "Motorcycle",
    5: "Bus",
    7: "Truck"
}

# Detection and Tracking thresholds
DEFAULT_CONF_THRESHOLD = 0.22         # Lower threshold to detect parked, distant and angled vehicles accurately
SPOT_OCCUPANCY_IOU_THRESHOLD = 0.20   # Overlap ratio to trigger occupancy
SPOT_DEBOUNCE_FRAMES = 4             # Consecutive frames required to change spot status (filters flicker)

# Server settings
HOST = "0.0.0.0"
PORT = 8000
