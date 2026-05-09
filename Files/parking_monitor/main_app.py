import sys
import cv2
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout,
                               QVBoxLayout, QListWidget, QStackedWidget,
                               QPushButton, QComboBox, QLabel, QFileDialog, 
                               QMessageBox, QInputDialog)
from core.vision import VisionThread, STRATEGY_YOLO, STRATEGY_BGSUB, STRATEGY_HYBRID
from db.crud import init_db
from gui.monitor_view import MonitorView
from gui.config_view import ConfigView
from camera_utils import get_camera_list

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ParkVision AI — Premium Monitor")
        self.resize(1280, 720)
        
        # Initialize Database
        init_db()

        try:
            with open("gui/styles.qss", "r") as f:
                self.setStyleSheet(f.read())
        except:
            pass

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Sidebar ───────────────────────────────────────────────────────────
        sidebar = QWidget()
        sidebar.setFixedWidth(210)
        sidebar.setStyleSheet("background:#1e293b;")
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(0, 0, 0, 8)
        sb_layout.setSpacing(4)

        self.nav = QListWidget()
        self.nav.setObjectName("Sidebar")
        self.nav.addItem("  📹  Monitoreo en Vivo")
        self.nav.addItem("  ⚙️   Gestor de Espacios")
        self.nav.currentRowChanged.connect(self.change_view)

        def sep():
            l = QLabel()
            l.setFixedHeight(1)
            l.setStyleSheet("background:#334155; margin:4px 10px;")
            return l

        def lbl(text):
            l = QLabel(text)
            l.setStyleSheet("color:#64748b; font-size:10px; font-weight:bold; padding:4px 10px 0 10px;")
            return l

        # Camera source selection
        self.combo_source = QComboBox()
        self.combo_source.addItems(["📹 Video", "📷 Webcam", "🔴 RTSP"])
        self.combo_source.setCurrentIndex(0)
        self.combo_source.currentIndexChanged.connect(self.on_source_changed)

        self.input_rtsp = QPushButton("🌐 Configurar RTSP")
        self.input_rtsp.clicked.connect(self.configure_rtsp)
        self.input_rtsp.setObjectName("Secondary")
        self.input_rtsp.setVisible(False)

        # Camera mode
        self.combo_cam = QComboBox()
        self.combo_cam.addItems(["🛸 Vista Aérea", "📷 Vista Normal"])
        self.combo_cam.currentIndexChanged.connect(self.on_cam_mode)

        # Playback speed
        self.combo_speed = QComboBox()
        self.combo_speed.addItems(["⏩ x1", "⏩ x2", "⏩ x4", "⏩ x0.5", "⏩ x0.25"])
        self.combo_speed.setCurrentIndex(0)
        self.combo_speed.currentIndexChanged.connect(self.on_speed_changed)

        # Detection strategy
        self.combo_strategy = QComboBox()
        self.combo_strategy.addItems([
            "🤖 Solo YOLO",
            "🖼️ Background Sub",
            "⚡ Híbrido (recomendado)"
        ])
        self.combo_strategy.setCurrentIndex(0)
        self.combo_strategy.currentIndexChanged.connect(self.on_strategy)

        # Buttons
        self.btn_video = QPushButton("📂 Cargar Video")
        self.btn_video.clicked.connect(self.load_video)
        self.btn_video.setObjectName("Secondary")

        self.btn_ref = QPushButton("📸 Capturar Referencia Vacía")
        self.btn_ref.clicked.connect(self.capture_reference)
        self.btn_ref.setObjectName("Secondary")

        self.lbl_strategy = QLabel("yolo26m-seg (preciso - Vista Aérea)")
        self.lbl_strategy.setStyleSheet("color:#38bdf8; font-size:10px; padding:2px 10px;")

        sb_layout.addWidget(self.nav)
        sb_layout.addWidget(sep())
        sb_layout.addWidget(lbl("FUENTE DE VIDEO"))
        sb_layout.addWidget(self.combo_source)
        sb_layout.addWidget(self.input_rtsp)
        sb_layout.addWidget(sep())
        sb_layout.addWidget(lbl("MODO DE CÁMARA"))
        sb_layout.addWidget(self.combo_cam)
        sb_layout.addWidget(sep())
        sb_layout.addWidget(lbl("VELOCIDAD"))
        sb_layout.addWidget(self.combo_speed)
        sb_layout.addWidget(sep())
        sb_layout.addWidget(lbl("ESTRATEGIA DE DETECCIÓN"))
        sb_layout.addWidget(self.combo_strategy)
        sb_layout.addWidget(self.lbl_strategy)
        sb_layout.addWidget(sep())
        sb_layout.addWidget(self.btn_ref)
        sb_layout.addWidget(self.btn_video)

        # ── Views ─────────────────────────────────────────────────────────────
        self.stack = QStackedWidget()

        self.vision_thread = VisionThread()

        self.monitor_view = MonitorView()
        self.config_view  = ConfigView(self.vision_thread)

        self.stack.addWidget(self.monitor_view)
        self.stack.addWidget(self.config_view)

        # signals
        self.vision_thread.frame_ready.connect(self.monitor_view.update_frame)
        self.vision_thread.stats_updated.connect(self.monitor_view.update_stats)
        self.vision_thread.alert_triggered.connect(self.monitor_view.add_alert)
        self.vision_thread.fps_updated.connect(self.monitor_view.update_fps)
        self.vision_thread.strategy_status.connect(self.lbl_strategy.setText)
        self.vision_thread.position_updated.connect(self.monitor_view.update_position)
        self.vision_thread.error_occurred.connect(self.on_vision_error)
        self.monitor_view.vision_thread = self.vision_thread

        self.vision_thread.start()

        root.addWidget(sidebar)
        root.addWidget(self.stack)
        self.nav.setCurrentRow(0)

    # ── Slots ─────────────────────────────────────────────────────────────────
    def on_source_changed(self, idx):
        self.input_rtsp.setVisible(idx == 2)
        if idx == 0:
            pass
        elif idx == 1:
            self.select_webcam()
        elif idx == 2:
            pass

    def select_webcam(self):
        """Let user select webcam from list with real names."""
        cameras = get_camera_list()
        
        if not cameras:
            QMessageBox.warning(self, "Sin Cámaras", 
                "No se encontraron cámaras web disponibles.\n"
                "Verifica que una cámara esté conectada.")
            return
        
        # Create list of camera names for display
        cam_names = [f"{name}" for idx, name in cameras]
        
        cam_name, ok = QInputDialog.getItem(self, "Seleccionar Cámara Web",
                                          "Cámaras disponibles:",
                                          cam_names,0, False)
        if ok and cam_name:
            # Find the index of the selected camera
            idx = None
            for camera_idx, name in cameras:
                if name == cam_name:
                    idx = camera_idx
                    break
            
            if idx is None:
                idx =0  # fallback
            
            # Test if camera works with DirectShow (Windows)
            test_cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
            if not test_cap.isOpened():
                test_cap.release()
                test_cap = cv2.VideoCapture(idx)
            
            if test_cap.isOpened():
                # Test if we can read a frame
                ret, frame = test_cap.read()
                if ret:
                    print(f"Webcam {idx} test: OK (frame size: {frame.shape})")
                    test_cap.release()
                    # Now set the camera in the vision thread
                    self.vision_thread.set_camera(idx)
                    # Switch to monitor view to see the feed
                    self.nav.setCurrentRow(0)
                    QMessageBox.information(self, "Cámara Conectada",
                        f"Cámara conectada:\n{name}\n\n"
                        "Cambiando a Monitoreo en Vivo...")
                else:
                    test_cap.release()
                    QMessageBox.warning(self, "Error de Cámara",
                        f"La cámara se abrió pero no puede leer frames.\n"
                        f"Nombre: {name}\n"
                        f"Índice: {idx}\n\n"
                        "Intenta con otro índice.")
            else:
                test_cap.release()
                QMessageBox.warning(self, "Error de Cámara",
                    f"No se pudo conectar a la cámara.\n"
                    f"Nombre: {name}\n"
                    f"Índice: {idx}\n\n"
                    "Intenta seleccionar otra cámara.")

    def configure_rtsp(self):
        url, ok = QInputDialog.getText(self, "Configurar RTSP",
                                     "Ingresa la URL RTSP de la cámara IP:",
                                     text=self.vision_thread.rtsp_url if self.vision_thread.rtsp_url else "rtsp://")
        if ok and url:
            self.vision_thread.set_rtsp(url)
            QMessageBox.information(self, "RTSP Configurada",
                f"Cámara RTSP conectada a:\n{url}")

    def on_cam_mode(self, idx):
        mode = ['aerial', 'normal'][idx]
        self.vision_thread.detection_mode = mode
        
        if self.vision_thread.source_type == 'video':
            reply = QMessageBox.question(self, "Cambiar Modo",
                f"¿Seleccionar un nuevo video para {'Vista Aérea' if mode == 'aerial' else 'Vista Normal'}?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self.load_video()

    def on_speed_changed(self, idx):
        speeds = [1.0, 2.0, 4.0, 0.5, 0.25]
        self.vision_thread.playback_speed = speeds[idx]

    def on_strategy(self, idx):
        strategies = [STRATEGY_YOLO, STRATEGY_BGSUB, STRATEGY_HYBRID]
        self.vision_thread.detect_strategy = strategies[idx]

    def load_video(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Video", "",
                                              "Video Files (*.mp4 *.avi *.mkv)")
        if path:
            self.vision_thread.set_video(path)
            self.config_view.current_spaces = list(self.vision_thread.spaces)
            self.config_view.refresh_list()
            self.config_view.redraw_frame()
            self.combo_source.setCurrentIndex(0)

    def capture_reference(self):
        """Capture current frame as background reference for BgSub strategy."""
        ok = self.vision_thread.capture_reference()
        if ok:
            QMessageBox.information(self, "Referencia Capturada",
                "Frame de referencia (parqueadero vacío) guardado.\n"
                "Ahora activa la estrategia 'Background Sub' o 'Híbrido' para usarla.")
        else:
            QMessageBox.warning(self, "Sin Frame", "Espera a que el video cargue antes de capturar.")

    def change_view(self, index):
        self.stack.setCurrentIndex(index)
        if index == 1:
            self.vision_thread.paused = True
            self.config_view.update_frame()
        else:
            self.vision_thread.paused = False

    def on_vision_error(self, message):
        """Handle error messages from VisionThread."""
        QMessageBox.warning(self, "Error de Vision", message)

    def closeEvent(self, event):
        self.vision_thread.stop()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
