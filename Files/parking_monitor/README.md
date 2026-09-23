# Smart Parking Monitor | Computer Vision & Artificial Intelligence

Intelligent real-time computer vision and parking analytics system. Allows operators to interactively create and manage parking bays directly over video streams (with 4-corner perspective correction or quick rectangles), track vehicles (cars, motorcycles, trucks, buses), record exact entry and dwell times, connect multiple video sources (local sample videos, USB webcams with native device names, RTSP IP cameras), and export detailed analytics reports to CSV and Excel.

Optimized with multi-hardware acceleration for **AMD GPUs (Radeon RX 6700 XT via Microsoft DirectML)**, **NVIDIA GPUs (CUDA)**, and **multi-threaded CPU**.

---

## Key Features

1. **Interactive Parking Bay Management (Spots)**:
   - **4-Corner / Perspective Mode**: Allows tracing parking bays in angled surveillance camera feeds by placing 4 anchor points directly on the video canvas.
   - **Quick Rectangle Mode**: Instant rectangular bounding boxes for top-down or orthogonal camera angles.
   - **Quick Preset Template**: Instantly loads 6 calibrated bays for rapid testing with a single click.
   - **Full Persistence**: Bay coordinates are persisted in both SQLite (`parking.db`) and JSON (`data/spots.json`); configurations are preserved across application restarts.
   - **Live Video Indicators**:
     - **Green**: Vacant / Available Bay.
     - **Red**: Occupied Bay, displaying the detected Vehicle ID and real-time dwell timer (e.g., `P-01 [#4] 14m 20s`).

2. **Vehicle Detection & Tracking (YOLOv8 + ByteTrack)**:
   - Multi-class vehicle classification: car, motorcycle, truck, and bus.
   - Persistent unique vehicle IDs (`#1`, `#2`, etc.) maintained via Kalman filtering and IoU association.
   - Spatial spot assignment using geometric polygon intersection (Shapely).
   - Hysteresis anti-false-positive filter: prevents moving transit vehicles in lanes from momentarily triggering false occupancy states.

3. **Temporal Metrics & Real-Time Dwell Timer**:
   - Exact entry date and timestamp logging upon bay occupancy.
   - Active second-by-second dwell timer for each parked vehicle.
   - Exit timestamp logging and total session duration calculation upon vacancy.

4. **Multi-Source Video Feeds**:
   - **Local Video Files / Samples**: Pre-loaded clips in the `samples/` directory with seamless continuous looping.
   - **Video Upload**: Operators can upload custom MP4/AVI video files directly through the web interface.
   - **Local USB Webcams**: Automatic enumeration and display of native device names on Windows (DirectShow).
   - **IP / RTSP / HTTP Cameras**: Direct connection to commercial network IP surveillance cameras (Hikvision, Dahua, Tapo, Axis, etc.).

5. **Multi-Hardware Acceleration**:
   - **AMD Radeon GPUs** (e.g., RX 6700 XT): Hardware-accelerated inference via ONNX Runtime with Microsoft DirectML (DirectX 12).
   - **NVIDIA GPUs**: PyTorch inference accelerated via CUDA.
   - **CPU**: Multi-threaded execution with vectorized math optimizations.
   - Hot-swappable execution engine selector in the top navbar with live FPS telemetry.

6. **Exportable Reports & Analytics**:
   - **CSV / Excel Export**: Download detailed historical session records including Session ID, Bay ID, Vehicle ID, Vehicle Type, Entry Timestamp, Exit Timestamp, and Total Dwell Duration.
   - Executive KPIs: Current occupancy rate (%), vehicle turnover, average parking duration, and peak hours.
   - Real-time search and filter tools within the web dashboard.

---

## Quick Start

### Option 1: One-Click Launcher (Recommended)
Double-click the **`iniciar.bat`** file.
It automatically terminates any conflicting processes on port 8000, launches the FastAPI vision server, and **opens your default browser at `http://localhost:8000`**.

### Option 2: Using PowerShell
```powershell
.\iniciar.ps1
```

### Option 3: Manual Terminal Execution
```bash
.venv\Scripts\python.exe run.py
```

---

## How to Draw and Configure Parking Bays

1. On the top navigation bar, click **"Create Bay (4 Points)"**.
2. Click 4 times on the video feed at the corners of the parking bay, following the perspective of the road markings.
3. A configuration modal will appear to set the identifier (e.g., `P-01`, `A-10`), the display label, and permitted vehicle types (Car, Motorcycle, etc.).
4. Click **"Save Bay"**. The system begins monitoring the new bay immediately.
5. Alternatively, click **"Quick Template"** to load 6 pre-configured bays mapped to the sample video.

---

## Exporting Analytics Reports

1. Click the **"Reports"** button on the top navigation bar.
2. Review aggregated metrics: total vehicles served, peak occupancy hours, and average dwell duration.
3. Click **"Download CSV Report"** to export the dataset for analysis in Microsoft Excel, Power BI, or Python.
