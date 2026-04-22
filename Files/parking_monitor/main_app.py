import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout,
                               QVBoxLayout, QListWidget, QStackedWidget,
                               QPushButton, QComboBox, QLabel, QFileDialog, QMessageBox)
from core.vision import VisionThread, STRATEGY_YOLO, STRATEGY_BGSUB, STRATEGY_HYBRID
from gui.monitor_view import MonitorView
from gui.config_view import ConfigView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ParkVision AI — Premium Monitor")
        self.resize(1280, 720)

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

        # Camera mode
        self.combo_cam = QComboBox()
        self.combo_cam.addItems(["🔄 Auto", "🛸 Vista Aérea", "📷 Vista Normal"])
        self.combo_cam.currentIndexChanged.connect(self.on_cam_mode)

        # Detection strategy
        self.combo_strategy = QComboBox()
        self.combo_strategy.addItems([
            "🤖 Solo YOLO",
            "🖼️ Background Sub",
            "⚡ Híbrido (recomendado)"
        ])
        self.combo_strategy.setCurrentIndex(0)
        self.combo_strategy.currentIndexChanged.connect(self.on_strategy)

        # YOLO model size
        self.combo_model = QComboBox()
        self.combo_model.addItems([
            "yolov8n  (rápido)",
            "yolov8m  (balanceado)",
            "yolov8l  (más preciso)",
        ])
        self.combo_model.currentIndexChanged.connect(self.on_model)

        # Buttons
        self.btn_video = QPushButton("📂 Cargar Video")
        self.btn_video.clicked.connect(self.load_video)

        self.btn_ref = QPushButton("📸 Capturar Referencia Vacía")
        self.btn_ref.clicked.connect(self.capture_reference)
        self.btn_ref.setObjectName("Secondary")

        self.lbl_strategy = QLabel("Estrategia: YOLO")
        self.lbl_strategy.setStyleSheet("color:#38bdf8; font-size:10px; padding:2px 10px;")

        sb_layout.addWidget(self.nav)
        sb_layout.addWidget(sep())
        sb_layout.addWidget(lbl("MODO DE CÁMARA"))
        sb_layout.addWidget(self.combo_cam)
        sb_layout.addWidget(sep())
        sb_layout.addWidget(lbl("ESTRATEGIA DE DETECCIÓN"))
        sb_layout.addWidget(self.combo_strategy)
        sb_layout.addWidget(self.lbl_strategy)
        sb_layout.addWidget(sep())
        sb_layout.addWidget(lbl("MODELO YOLO"))
        sb_layout.addWidget(self.combo_model)
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
        self.monitor_view.vision_thread = self.vision_thread

        self.vision_thread.start()

        root.addWidget(sidebar)
        root.addWidget(self.stack)
        self.nav.setCurrentRow(0)

    # ── Slots ─────────────────────────────────────────────────────────────────
    def on_cam_mode(self, idx):
        self.vision_thread.detection_mode = ['auto', 'aerial', 'normal'][idx]

    def on_strategy(self, idx):
        strategies = [STRATEGY_YOLO, STRATEGY_BGSUB, STRATEGY_HYBRID]
        self.vision_thread.detect_strategy = strategies[idx]

    def on_model(self, idx):
        names = ['yolov8n.pt', 'yolov8m.pt', 'yolov8l.pt']
        self.lbl_strategy.setText(f"Cargando {names[idx]}…")
        self.vision_thread.set_model(names[idx])

    def load_video(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Video", "",
                                              "Video Files (*.mp4 *.avi *.mkv)")
        if path:
            self.vision_thread.set_video(path)
            self.config_view.current_spaces = list(self.vision_thread.spaces)
            self.config_view.refresh_list()
            self.config_view.redraw_frame()

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

    def closeEvent(self, event):
        self.vision_thread.stop()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
