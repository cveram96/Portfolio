import csv
import os
import json
from datetime import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                                 QLabel, QFrame, QListWidget, QListWidgetItem,
                                 QPushButton, QProgressBar, QFileDialog, QSlider,
                                 QMessageBox)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class MonitorView(QWidget):
    def __init__(self):
        super().__init__()
        self._stats = {'total': 0, 'occupied': 0, 'free': 0}
        self._current_fps = 0.0
        self._updating_slider = False

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

        # Timeline slider
        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setMinimum(0)
        self.timeline_slider.setMaximum(100)
        self.timeline_slider.setValue(0)
        self.timeline_slider.setTickPosition(QSlider.NoTicks)
        self.timeline_slider.setStyleSheet("""
            QSlider::groove:horizontal { height: 6px; background: #334155; border-radius: 3px; }
            QSlider::handle:horizontal { width: 14px; background: #38bdf8; border-radius: 7px; margin: -4px 0; }
            QSlider::sub-page:horizontal { background: #38bdf8; border-radius: 3px; }
        """)
        self.timeline_slider.sliderMoved.connect(self.on_sliderMoved)
        video_layout.addWidget(self.timeline_slider)

        # Time labels
        time_layout = QHBoxLayout()
        self.lbl_current_time = QLabel('00:00')
        self.lbl_current_time.setStyleSheet('color:#94a3b8; font-size:11px;')
        self.lbl_total_time = QLabel('00:00')
        self.lbl_total_time.setStyleSheet('color:#94a3b8; font-size:11px;')
        self.lbl_fps = QLabel('FPS: —')
        self.lbl_fps.setStyleSheet('color:#64748b; font-size:11px;')
        time_layout.addWidget(self.lbl_current_time)
        time_layout.addStretch()
        time_layout.addWidget(self.lbl_fps)
        time_layout.addStretch()
        time_layout.addWidget(self.lbl_total_time)
        video_layout.addLayout(time_layout)

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
        self.btn_export_csv = QPushButton('📊 Exportar CSV')
        self.btn_export_csv.clicked.connect(self.export_csv)
        self.btn_export_excel = QPushButton('📈 Exportar Excel')
        self.btn_export_excel.clicked.connect(self.export_excel)
        btn_row.addWidget(self.btn_snapshot)
        btn_row.addWidget(self.btn_export_csv)
        btn_row.addWidget(self.btn_export_excel)
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
        print(f"update_frame called: {qimage.width()}x{qimage.height()}")
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

    def update_position(self, current_frame: float, total_frames: float):
        if self._updating_slider or total_frames <= 0:
            return
        self._updating_slider = True
        self.timeline_slider.setMaximum(int(total_frames))
        self.timeline_slider.setValue(int(current_frame))
        self._updating_slider = False
        
        video_fps = 30.0
        if hasattr(self, 'vision_thread') and self.vision_thread and hasattr(self.vision_thread, '_video_fps'):
            video_fps = self.vision_thread._video_fps
            if video_fps <= 0:
                video_fps = 30.0
        
        curr_secs = int(current_frame / video_fps)
        total_secs = int(total_frames / video_fps)
        self.lbl_current_time.setText(self._format_time(curr_secs))
        self.lbl_total_time.setText(self._format_time(total_secs))

    def _format_time(self, seconds: int):
        mins = seconds // 60
        secs = seconds % 60
        return f'{mins:02d}:{secs:02d}'

    def on_sliderMoved(self, pos):
        if self.vision_thread and hasattr(self.vision_thread, 'seek_to'):
            self.vision_thread.seek_to(pos)

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
        path, _ = QFileDialog.getSaveFileName(self, 'Exportar Reporte CSV', '', 'CSV (*.csv)')
        if not path:
            return
        try:
            from db.crud import get_occupancy_report
            report = get_occupancy_report()
            
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'space_id', 'space_name', 'space_type', 
                               'is_occupied', 'timestamp'])
                for row in report:
                    writer.writerow([
                        row['id'], row['space_id'], row['space_name'],
                        row['space_type'], row['is_occupied'], row['timestamp']
                    ])
            
            QMessageBox.information(self, 'Éxito', f'Reporte CSV exportado a:\n{path}')
        except Exception as e:
            QMessageBox.warning(self, 'Error', str(e))

    def export_excel(self):
        """Export occupancy report to Excel with multiple sheets."""
        try:
            import pandas as pd
        except ImportError:
            QMessageBox.warning(self, 'Error', 
                'Pandas no está instalado.\nInstala con: pip install pandas openpyxl')
            return
        
        path, _ = QFileDialog.getSaveFileName(self, 'Exportar Reporte Excel', '', 'Excel (*.xlsx)')
        if not path:
            return
        
        try:
            import pandas as pd
            from db.crud import get_occupancy_report
            import json
            
            # Sheet 1: Historical Occupancy
            report = get_occupancy_report()
            data = []
            for row in report:
                data.append({
                    'ID': row['id'],
                    'Espacio ID': row['space_id'],
                    'Nombre': row['space_name'],
                    'Tipo': row['space_type'],
                    'Ocupado': 'Sí' if row['is_occupied'] else 'No',
                    'Timestamp': row['timestamp']
                })
            
            df = pd.DataFrame(data)
            
            # Sheet 2: Summary by space
            if not df.empty:
                summary = df.groupby(['Espacio ID', 'Nombre', 'Tipo']).agg({
                    'Ocupado': ['count', lambda x: (x == 'Sí').sum()]
                }).reset_index()
                summary.columns = ['Espacio ID', 'Nombre', 'Tipo', 'Total Eventos', 'Veces Ocupado']
            else:
                summary = pd.DataFrame(columns=['Espacio ID', 'Nombre', 'Tipo', 'Total Eventos', 'Veces Ocupado'])
            
            # Sheet 3: Current state from vision thread
            current_data = []
            if self.vision_thread and hasattr(self.vision_thread, 'spaces'):
                for i, space in enumerate(self.vision_thread.spaces):
                    name = f'Espacio {i+1}'
                    stype = 'Estándar'
                    if isinstance(space, dict):
                        if 'name' in space and space['name']:
                            name = space['name']
                        stype = space.get('type', 'Estándar')
                    
                    occupied = 'Sí' if self.vision_thread.space_states.get(i, False) else 'No'
                    
                    # Get vehicle type if occupied
                    vehicle = ''
                    if occupied == 'Sí' and hasattr(self.vision_thread, 'space_vehicle_types'):
                        if i in self.vision_thread.space_vehicle_types:
                            vclass = self.vision_thread.space_vehicle_types[i]
                            class_names = {2: 'AUTO', 3: 'MOTO', 5: 'BUS', 7: 'CAMION'}
                            vehicle = class_names.get(vclass, '')
                    
                    current_data.append({
                        'Espacio ID': i,
                        'Nombre': name,
                        'Tipo': stype,
                        'Ocupado': occupied,
                        'Vehiculo': vehicle
                    })
            
            df_current = pd.DataFrame(current_data)
            
            # Write to Excel with multiple sheets
            with pd.ExcelWriter(path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Historial Ocupación', index=False)
                summary.to_excel(writer, sheet_name='Resumen por Espacio', index=False)
                if not df_current.empty:
                    df_current.to_excel(writer, sheet_name='Estado Actual', index=False)
            
            QMessageBox.information(self, 'Éxito', f'Reporte Excel exportado a:\n{path}')
        except Exception as e:
            QMessageBox.warning(self, 'Error', str(e))

    def export_excel(self):
        """Export occupancy report to Excel with multiple sheets."""
        if 'pandas' not in sys.modules:
            try:
                import pandas as pd
            except ImportError:
                QMessageBox.warning(self, 'Error', 
                    'Pandas no está instalado.\nInstala con: pip install pandas openpyxl')
                return
        
        path, _ = QFileDialog.getSaveFileName(self, 'Exportar Reporte Excel', '', 'Excel (*.xlsx)')
        if not path:
            return
        
        try:
            import pandas as pd
            from db.models import Base, OccupancyLog, ParkingSpace
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            import json
            
            engine  = create_engine('sqlite:///parking.db')
            Session = sessionmaker(bind=engine)
            session = Session()
            
            # Get enriched occupancy data
            logs = session.query(
                OccupancyLog.id,
                OccupancyLog.space_id,
                OccupancyLog.is_occupied,
                OccupancyLog.timestamp,
                ParkingSpace.poly_data,
                ParkingSpace.space_type
            ).outerjoin(ParkingSpace, OccupancyLog.space_id == ParkingSpace.id
            ).order_by(OccupancyLog.id.desc()).limit(5000).all()
            
            session.close()
            
            # Process data
            data = []
            for log in logs:
                space_name = f'Espacio {log.space_id}'
                if log.poly_data:
                    try:
                        import json
                        d = json.loads(log.poly_data)
                        if isinstance(d, dict) and 'name' in d and d['name']:
                            space_name = d['name']
                    except:
                        pass
                
                data.append({
                    'ID': log.id,
                    'Espacio ID': log.space_id,
                    'Nombre': space_name,
                    'Tipo': log.space_type or 'Estándar',
                    'Ocupado': 'Sí' if log.is_occupied else 'No',
                    'Timestamp': log.timestamp
                })
            
            df = pd.DataFrame(data)
            
            # Sheet 2: Summary by space
            summary = df.groupby(['Espacio ID', 'Nombre', 'Tipo']).agg({
                'Ocupado': ['count', lambda x: (x == 'Sí').sum()]
            }).reset_index()
            summary.columns = ['Espacio ID', 'Nombre', 'Tipo', 'Total Eventos', 'Veces Ocupado']
            
            # Sheet 3: Current state from vision thread
            current_data = []
            if self.vision_thread and hasattr(self.vision_thread, 'spaces'):
                for i, space in enumerate(self.vision_thread.spaces):
                    name = f'Espacio {i+1}'
                    stype = 'Estándar'
                    if isinstance(space, dict):
                        if 'name' in space and space['name']:
                            name = space['name']
                        stype = space.get('type', 'Estándar')
                    occupied = 'Sí' if self.vision_thread.space_states.get(i, False) else 'No'
                    
                    # Get vehicle type if occupied
                    vehicle = ''
                    if occupied == 'Sí' and i in self.vision_thread.space_vehicle_types:
                        vclass = self.vision_thread.space_vehicle_types[i]
                        class_names = {2: 'AUTO', 3: 'MOTO', 5: 'BUS', 7: 'CAMION'}
                        vehicle = class_names.get(vclass, '')
                    
                    current_data.append({
                        'Espacio ID': i,
                        'Nombre': name,
                        'Tipo': stype,
                        'Ocupado': occupied,
                        'Vehiculo': vehicle
                    })
            
            df_current = pd.DataFrame(current_data)
            
            # Write to Excel with multiple sheets
            with pd.ExcelWriter(path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Historial Ocupación', index=False)
                summary.to_excel(writer, sheet_name='Resumen por Espacio', index=False)
                if not df_current.empty:
                    df_current.to_excel(writer, sheet_name='Estado Actual', index=False)
            
            QMessageBox.information(self, 'Éxito', f'Reporte Excel exportado a:\n{path}')
        except Exception as e:
            QMessageBox.warning(self, 'Error', str(e))
