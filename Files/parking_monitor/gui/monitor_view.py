import csv
import os
from datetime import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QFrame, QListWidget, QListWidgetItem,
                               QPushButton, QProgressBar, QFileDialog)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class MonitorView(QWidget):
    def __init__(self):
        super().__init__()
        self._stats = {'total': 0, 'occupied': 0, 'free': 0}
        self._current_fps = 0.0

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # ── Left: video ──────────────────────────────────────────────────────
        video_frame = QFrame()
        video_frame.setProperty('class', 'glass-panel')
        video_layout = QVBoxLayout(video_frame)
        video_layout.setContentsMargins(4, 4, 4, 4)

        self.video_label = QLabel('Iniciando motor de visión...')
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet('color:#64748b; font-size:18px;')
        video_layout.addWidget(self.video_label)

        # FPS bar at bottom of video
        self.lbl_fps = QLabel('FPS: —')
        self.lbl_fps.setStyleSheet('color:#64748b; font-size:11px; padding: 2px;')
        video_layout.addWidget(self.lbl_fps, 0, Qt.AlignRight)

        # ── Right: stats panel ───────────────────────────────────────────────
        right_panel = QWidget()
        right_panel.setFixedWidth(280)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(10)

        # --- Occupancy card ---
        stats_frame = QFrame()
        stats_frame.setProperty('class', 'glass-panel')
        stats_layout = QVBoxLayout(stats_frame)

        title = QLabel('Estado del Parqueadero')
        title.setObjectName('Title')
        stats_layout.addWidget(title)

        grid = QHBoxLayout()

        free_col = QVBoxLayout()
        free_lbl = QLabel('LIBRES')
        free_lbl.setStyleSheet('color:#94a3b8; font-size:11px; font-weight:bold;')
        self.lbl_free = QLabel('0')
        self.lbl_free.setObjectName('StatValueGreen')
        free_col.addWidget(free_lbl, 0, Qt.AlignHCenter)
        free_col.addWidget(self.lbl_free, 0, Qt.AlignHCenter)

        occ_col = QVBoxLayout()
        occ_lbl = QLabel('OCUPADOS')
        occ_lbl.setStyleSheet('color:#94a3b8; font-size:11px; font-weight:bold;')
        self.lbl_occupied = QLabel('0')
        self.lbl_occupied.setObjectName('StatValueRed')
        occ_col.addWidget(occ_lbl, 0, Qt.AlignHCenter)
        occ_col.addWidget(self.lbl_occupied, 0, Qt.AlignHCenter)

        tot_col = QVBoxLayout()
        tot_lbl = QLabel('TOTAL')
        tot_lbl.setStyleSheet('color:#94a3b8; font-size:11px; font-weight:bold;')
        self.lbl_total = QLabel('0')
        self.lbl_total.setStyleSheet('font-size:36px; font-weight:bold; color:#e2e8f0;')
        tot_col.addWidget(tot_lbl, 0, Qt.AlignHCenter)
        tot_col.addWidget(self.lbl_total, 0, Qt.AlignHCenter)

        grid.addLayout(free_col)
        grid.addLayout(occ_col)
        grid.addLayout(tot_col)
        stats_layout.addLayout(grid)

        # Occupancy progress bar
        self.pct_label = QLabel('Ocupación: 0%')
        self.pct_label.setStyleSheet('color:#94a3b8; font-size:12px;')
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(12)
        self.progress.setStyleSheet('''
            QProgressBar { background-color: #1e293b; border-radius: 6px; border: 1px solid #334155; }
            QProgressBar::chunk { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #22c55e,stop:0.6 #f59e0b,stop:1 #ef4444); border-radius: 6px; }
        ''')
        stats_layout.addWidget(self.pct_label)
        stats_layout.addWidget(self.progress)

        # Action buttons
        btn_row = QHBoxLayout()
        self.btn_snapshot = QPushButton('📸 Captura')
        self.btn_snapshot.clicked.connect(self.take_snapshot)
        self.btn_export = QPushButton('📊 Exportar CSV')
        self.btn_export.clicked.connect(self.export_csv)
        btn_row.addWidget(self.btn_snapshot)
        btn_row.addWidget(self.btn_export)
        stats_layout.addLayout(btn_row)

        # --- Alerts card ---
        alerts_frame = QFrame()
        alerts_frame.setProperty('class', 'glass-panel')
        alerts_layout = QVBoxLayout(alerts_frame)
        alerts_title = QLabel('Alertas Recientes')
        alerts_title.setObjectName('Title')
        self.list_alerts = QListWidget()
        self.list_alerts.setStyleSheet('font-size:12px;')
        alerts_layout.addWidget(alerts_title)
        alerts_layout.addWidget(self.list_alerts)

        right_layout.addWidget(stats_frame)
        right_layout.addWidget(alerts_frame)

        main_layout.addWidget(video_frame, stretch=7)
        main_layout.addWidget(right_panel, stretch=3)

        # Reference to vision thread set externally
        self.vision_thread = None

    # ── slots ────────────────────────────────────────────────────────────────
    def update_frame(self, qimage):
        pixmap = QPixmap.fromImage(qimage)
        scaled = pixmap.scaled(self.video_label.size(),
                               Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.video_label.setPixmap(scaled)

    def update_stats(self, stats: dict):
        self._stats = stats
        self.lbl_total.setText(str(stats['total']))
        self.lbl_occupied.setText(str(stats['occupied']))
        self.lbl_free.setText(str(stats['free']))
        pct = int(stats['occupied'] / stats['total'] * 100) if stats['total'] else 0
        self.progress.setValue(pct)
        self.pct_label.setText(f'Ocupación: {pct}%')

    def update_fps(self, fps: float):
        self._current_fps = fps
        self.lbl_fps.setText(f'FPS: {fps:.1f}')

    def add_alert(self, message: str):
        ts = datetime.now().strftime('%H:%M:%S')
        self.list_alerts.insertItem(0, QListWidgetItem(f'[{ts}] {message}'))
        if self.list_alerts.count() > 100:
            self.list_alerts.takeItem(self.list_alerts.count() - 1)

    def take_snapshot(self):
        if self.vision_thread is None:
            return
        path, _ = QFileDialog.getSaveFileName(self, 'Guardar Captura', '', 'Imagen (*.jpg *.png)')
        if path:
            self.vision_thread.request_snapshot(path)

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Exportar Reporte', '', 'CSV (*.csv)')
        if not path:
            return
        try:
            from db.models import Base, OccupancyLog
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            engine  = create_engine('sqlite:///parking.db')
            Session = sessionmaker(bind=engine)
            session = Session()
            logs = session.query(OccupancyLog).order_by(OccupancyLog.id.desc()).limit(5000).all()
            session.close()

            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'space_id', 'is_occupied', 'timestamp'])
                for log in logs:
                    writer.writerow([log.id, log.space_id, log.is_occupied, log.timestamp])

            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, 'Éxito', f'Reporte exportado a:\n{path}')
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, 'Error', str(e))
