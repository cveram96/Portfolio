import cv2
import numpy as np
import math
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QComboBox, QListWidget,
                               QListWidgetItem, QFrame, QMessageBox, QSlider)
from PySide6.QtGui import QPixmap, QImage, QIcon, QCursor
from PySide6.QtCore import Qt, Signal, QSize, QPoint


# ── Interactive canvas that supports: click to add point, drag vertices ───────
class CanvasLabel(QLabel):
    point_added   = Signal(int, int)        # left click in draw mode
    undo_point    = Signal()                 # right click
    vertex_moved  = Signal(int, int, int, int)  # space_idx, vertex_idx, new_x, new_y

    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self._drag_space  = None
        self._drag_vertex = None
        self._spaces_ref  = []   # list[dict] reference kept up-to-date by ConfigView

    def _label_to_frame(self, lx, ly):
        """Map label coordinates → pixmap/frame coordinates."""
        pix = self.pixmap()
        if not pix:
            return lx, ly
        off_x = (self.width()  - pix.width())  / 2
        off_y = (self.height() - pix.height()) / 2
        return int(lx - off_x), int(ly - off_y)

    def _find_nearest_vertex(self, fx, fy, threshold=12):
        """Return (space_idx, vertex_idx) of the closest vertex within threshold."""
        best_dist, best = float('inf'), (None, None)
        for si, space in enumerate(self._spaces_ref):
            pts = space['points'] if isinstance(space, dict) else space
            for vi, pt in enumerate(pts):
                d = math.hypot(fx - pt[0], fy - pt[1])
                if d < best_dist:
                    best_dist, best = d, (si, vi)
        if best_dist <= threshold:
            return best
        return None, None

    def mousePressEvent(self, event):
        fx, fy = self._label_to_frame(event.pos().x(), event.pos().y())
        if event.button() == Qt.LeftButton:
            si, vi = self._find_nearest_vertex(fx, fy)
            if si is not None:
                self._drag_space, self._drag_vertex = si, vi
                self.setCursor(QCursor(Qt.ClosedHandCursor))
            else:
                self.point_added.emit(fx, fy)
        elif event.button() == Qt.RightButton:
            self.undo_point.emit()

    def mouseMoveEvent(self, event):
        fx, fy = self._label_to_frame(event.pos().x(), event.pos().y())
        if self._drag_space is not None:
            self.vertex_moved.emit(self._drag_space, self._drag_vertex, fx, fy)
        else:
            si, vi = self._find_nearest_vertex(fx, fy)
            self.setCursor(QCursor(Qt.CrossCursor if si is None else Qt.OpenHandCursor))

    def mouseReleaseEvent(self, event):
        self._drag_space = self._drag_vertex = None
        self.setCursor(QCursor(Qt.CrossCursor))


# ── Main Configuration View ───────────────────────────────────────────────────
class ConfigView(QWidget):
    spaces_saved = Signal(list)

    def __init__(self, vision_thread):
        super().__init__()
        self.vision_thread    = vision_thread
        self.raw_frame        = None
        self.current_spaces   = list(vision_thread.spaces)
        self.current_polygon  = []
        self.mode             = 'manual'

        main_layout = QHBoxLayout(self)

        # ── Left: video canvas ───────────────────────────────────────────────
        left_panel = QVBoxLayout()

        toolbar = QHBoxLayout()
        self.btn_manual = QPushButton('✏️ Dibujo Manual')
        self.btn_manual.setCheckable(True); self.btn_manual.setChecked(True)
        self.btn_manual.clicked.connect(lambda: self.set_mode('manual'))

        self.btn_smart = QPushButton('🤖 Clic Inteligente')
        self.btn_smart.setCheckable(True)
        self.btn_smart.clicked.connect(lambda: self.set_mode('smart'))

        self.btn_edit = QPushButton('🖱️ Editar Vértices')
        self.btn_edit.setCheckable(True)
        self.btn_edit.clicked.connect(lambda: self.set_mode('edit'))

        self.btn_auto  = QPushButton('⚡ Autodetectar Todo')
        self.btn_auto.clicked.connect(self.auto_detect_all)

        self.btn_lines = QPushButton('📐 Detectar Líneas')
        self.btn_lines.clicked.connect(self.detect_parking_lines)

        for b in [self.btn_manual, self.btn_smart, self.btn_edit, self.btn_auto, self.btn_lines]:
            toolbar.addWidget(b)

        self.canvas = CanvasLabel()
        self.canvas.setAlignment(Qt.AlignCenter)
        self.canvas.point_added.connect(self.handle_click)
        self.canvas.undo_point.connect(self.handle_right_click)
        self.canvas.vertex_moved.connect(self.handle_vertex_drag)

        instructions = QLabel(
            'Manual: clic izq añade punto | clic der deshace | "Guardar Polígono" cierra\n'
            'Editar: arrastra cualquier vértice para ajustar con precisión'
        )
        instructions.setStyleSheet('color:#64748b; font-size:11px;')

        left_panel.addLayout(toolbar)
        left_panel.addWidget(self.canvas, stretch=1)
        left_panel.addWidget(instructions)

        # ── Right: settings panel ────────────────────────────────────────────
        right_panel = QFrame()
        right_panel.setProperty('class', 'glass-panel')
        right_panel.setFixedWidth(320)
        right_layout = QVBoxLayout(right_panel)

        right_layout.addWidget(QLabel('Tipo de Espacio:'))
        self.combo_type = QComboBox()
        self.combo_type.addItems(['Estándar', 'Motos', 'VIP', 'Discapacitados'])
        right_layout.addWidget(self.combo_type)

        right_layout.addWidget(QLabel('Inclinación (Autodetect):'))
        self.slider_angle = QSlider(Qt.Horizontal)
        self.slider_angle.setRange(-60, 60); self.slider_angle.setValue(0)
        right_layout.addWidget(self.slider_angle)

        right_layout.addWidget(QLabel('Ancho del Espacio:'))
        self.slider_w = QSlider(Qt.Horizontal)
        self.slider_w.setRange(40, 200); self.slider_w.setValue(80)
        right_layout.addWidget(self.slider_w)

        right_layout.addWidget(QLabel('Largo del Espacio:'))
        self.slider_h = QSlider(Qt.Horizontal)
        self.slider_h.setRange(80, 300); self.slider_h.setValue(120)
        right_layout.addWidget(self.slider_h)

        self.btn_save_poly = QPushButton('💾 Cerrar y Guardar Polígono Actual')
        self.btn_save_poly.clicked.connect(self.finish_polygon)
        right_layout.addWidget(self.btn_save_poly)

        right_layout.addWidget(QLabel('Espacios Guardados:'))
        self.list_spaces = QListWidget()
        self.list_spaces.setIconSize(QSize(100, 100))
        right_layout.addWidget(self.list_spaces)

        btn_row = QHBoxLayout()
        btn_del = QPushButton('🗑️ Eliminar')
        btn_del.setObjectName('Secondary'); btn_del.clicked.connect(self.delete_selected)
        btn_clr = QPushButton('🧹 Limpiar Todo')
        btn_clr.setObjectName('Secondary'); btn_clr.clicked.connect(self.clear_all)
        btn_row.addWidget(btn_del); btn_row.addWidget(btn_clr)
        right_layout.addLayout(btn_row)

        btn_apply = QPushButton('✅ Aplicar Todos los Cambios')
        btn_apply.clicked.connect(self.apply_changes)
        right_layout.addWidget(btn_apply)

        main_layout.addLayout(left_panel, stretch=7)
        main_layout.addWidget(right_panel, stretch=3)

    # ── Mode switching ────────────────────────────────────────────────────────
    def set_mode(self, mode):
        self.mode = mode
        self.btn_manual.setChecked(mode == 'manual')
        self.btn_smart.setChecked(mode == 'smart')
        self.btn_edit.setChecked(mode == 'edit')
        self.current_polygon = []
        # Give canvas a ref to spaces only in edit mode
        self.canvas._spaces_ref = self.current_spaces if mode == 'edit' else []
        self.redraw_frame()

    # ── Frame management ──────────────────────────────────────────────────────
    def update_frame(self):
        if hasattr(self.vision_thread, 'last_raw_frame') and self.vision_thread.last_raw_frame is not None:
            self.raw_frame = self.vision_thread.last_raw_frame.copy()
            self.redraw_frame()
            self.refresh_list()

    def _frame_to_qpixmap(self, img):
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        return QPixmap.fromImage(QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888))

    def get_thumbnail(self, pts):
        if self.raw_frame is None:
            return QIcon()
        x, y, w, h = cv2.boundingRect(np.array(pts, np.int32))
        crop = self.raw_frame[max(0, y):max(0, y)+max(1, h), max(0, x):max(0, x)+max(1, w)]
        if crop.size == 0:
            return QIcon()
        pix = self._frame_to_qpixmap(crop).scaled(100, 100, Qt.KeepAspectRatio)
        return QIcon(pix)

    def refresh_list(self):
        self.list_spaces.clear()
        for i, space in enumerate(self.current_spaces):
            pts   = space['points'] if isinstance(space, dict) else space
            stype = space.get('type', 'Estándar') if isinstance(space, dict) else 'Estándar'
            item  = QListWidgetItem(f'Espacio {i+1} ({stype})')
            item.setIcon(self.get_thumbnail(pts))
            self.list_spaces.addItem(item)

    def redraw_frame(self):
        if self.raw_frame is None:
            return
        display = self.raw_frame.copy()

        # Draw confirmed spaces
        for i, space in enumerate(self.current_spaces):
            pts   = space['points'] if isinstance(space, dict) else space
            stype = space.get('type', 'Estándar') if isinstance(space, dict) else 'Estándar'
            poly  = np.array(pts, np.int32)
            type_colors = {'Discapacitados': (255,144,30), 'VIP': (180,0,200), 'Motos': (255,165,0)}
            color = type_colors.get(stype, (30, 200, 30))
            cv2.polylines(display, [poly], True, color, 2)

            # Draw draggable vertices as circles in edit mode
            if self.mode == 'edit':
                for pt in pts:
                    cv2.circle(display, tuple(pt), 7, (0, 220, 255), -1)
                    cv2.circle(display, tuple(pt), 7, (255, 255, 255), 1)

            # Label
            M = cv2.moments(poly)
            if M['m00'] != 0:
                cv2.putText(display, str(i+1),
                            (int(M['m10']/M['m00'])-6, int(M['m01']/M['m00'])+5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)

        # Draw in-progress polygon
        if self.current_polygon:
            pts = np.array(self.current_polygon, np.int32)
            cv2.polylines(display, [pts], False, (0, 0, 255), 2)
            for pt in self.current_polygon:
                cv2.circle(display, tuple(pt), 5, (0, 0, 255), -1)

        self.canvas.setPixmap(self._frame_to_qpixmap(display))

    # ── Interaction handlers ──────────────────────────────────────────────────
    def handle_click(self, px, py):
        if self.mode == 'manual':
            self.current_polygon.append((px, py))
            self.redraw_frame()
        elif self.mode == 'smart':
            self._smart_click(px, py)

    def handle_right_click(self):
        if self.mode == 'manual' and self.current_polygon:
            self.current_polygon.pop()
            self.redraw_frame()

    def handle_vertex_drag(self, space_idx, vertex_idx, nx, ny):
        """Update a specific polygon vertex in real-time."""
        if 0 <= space_idx < len(self.current_spaces):
            space = self.current_spaces[space_idx]
            pts = space['points'] if isinstance(space, dict) else space
            pts[vertex_idx] = (nx, ny)
            if isinstance(space, dict):
                space['points'] = pts
            self.canvas._spaces_ref = self.current_spaces
            self.redraw_frame()

    # ── Smart click ───────────────────────────────────────────────────────────
    def _smart_click(self, px, py):
        if self.raw_frame is None:
            return
        try:
            imgsz = self.vision_thread.get_imgsz()
            results = self.vision_thread.model.predict(
                self.raw_frame, classes=[2, 3, 5, 7], conf=0.15, imgsz=imgsz, verbose=False)
            angle = self.slider_angle.value()
            bw_default = self.slider_w.value()
            bh_default = self.slider_h.value()
            stype = self.combo_type.currentText()
            found = False
            for box in results[0].boxes.xyxy.cpu().numpy():
                x1, y1, x2, y2 = map(int, box)
                if x1 <= px <= x2 and y1 <= py <= y2:
                    cw = (x2 - x1) * 1.15  # 15% extra width for parking space
                    ch = (y2 - y1) * 1.05  # 5% extra height
                    cx = int(x1 + (x2 - x1) / 2)
                    cy = int(y2)
                    poly = self._slanted_box(cx, cy, cw, ch, angle)
                    self.current_spaces.append({'points': poly, 'type': stype})
                    found = True
                    break
            if not found:
                # Manual placement at click location using slider values
                poly = self._slanted_box(px, py + bh_default//2, bw_default, bh_default, angle)
                self.current_spaces.append({'points': poly, 'type': stype})
            self.redraw_frame(); self.refresh_list()
        except Exception as e:
            print('Smart click error:', e)

    # ── Autodetect ────────────────────────────────────────────────────────────
    def _sliced_detect(self, frame):
        """
        Tile-based inference: splits frame into overlapping tiles, runs YOLO on each,
        maps boxes back to frame coords, then applies global NMS.
        Returns list of [x1, y1, x2, y2] in frame coords (filtered by size).
        """
        import cv2, numpy as np
        fh, fw = frame.shape[:2]
        tile_sz  = 480
        overlap  = 120
        step     = tile_sz - overlap
        conf_thr = 0.05    # low threshold to catch aerial cars
        nms_iou  = 0.35

        all_boxes = []
        for y in range(0, fh, step):
            for x in range(0, fw, step):
                x2 = min(x + tile_sz, fw)
                y2 = min(y + tile_sz, fh)
                tile = frame[y:y2, x:x2]
                r = self.vision_thread.model.predict(
                    tile, classes=[2, 3, 5, 7], conf=conf_thr, verbose=False)
                for box in r[0].boxes.xyxy.cpu().numpy():
                    bx1, by1, bx2, by2 = box
                    all_boxes.append([x + bx1, y + by1, x + bx2, y + by2])

        if not all_boxes:
            return []

        boxes_np = np.array(all_boxes, dtype=np.float32)

        # Filter boxes that are too big (false positives = large tiles, rooftops)
        # or too small (noise). Cars should be between 30x25 and 250x200 pixels.
        widths  = boxes_np[:, 2] - boxes_np[:, 0]
        heights = boxes_np[:, 3] - boxes_np[:, 1]
        valid   = (widths > 28) & (widths < 260) & (heights > 20) & (heights < 220)
        boxes_np = boxes_np[valid]

        if len(boxes_np) == 0:
            return []

        # NMS to remove duplicates from overlapping tiles
        xywh = boxes_np.copy()
        xywh[:, 2] -= xywh[:, 0]
        xywh[:, 3] -= xywh[:, 1]
        idx = cv2.dnn.NMSBoxes(
            xywh.astype(int).tolist(),
            [0.5] * len(boxes_np), conf_thr, nms_iou)

        if len(idx) == 0:
            return []

        return [boxes_np[i].tolist() for i in idx.flatten()]

    def auto_detect_all(self):
        """Detect all cars via tiled inference → create a parking space from each car's bounding box."""
        if self.raw_frame is None:
            return

        from PySide6.QtWidgets import QApplication
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            detections = self._sliced_detect(self.raw_frame)
        finally:
            QApplication.restoreOverrideCursor()

        if not detections:
            QMessageBox.information(self, 'Sin Detecciones',
                'No se detectaron vehículos.\n'
                'Intenta cambiar a "Vista Aérea" en el selector de Modo de Cámara.')
            return

        angle = self.slider_angle.value()
        stype = self.combo_type.currentText()

        for box in detections:
            x1, y1, x2, y2 = map(int, box)
            cw = (x2 - x1) * 1.15  # 15% extra width for parking space
            ch = (y2 - y1) * 1.05  # 5% extra height
            cx = int(x1 + (x2 - x1) / 2)
            cy = int(y2)

            # Avoid duplicating spaces if the car is already covered by an existing space
            is_new = True
            for existing in self.current_spaces:
                ex_pts = existing['points'] if isinstance(existing, dict) else existing
                if cv2.pointPolygonTest(np.array(ex_pts, np.int32), (cx, cy), False) >= 0:
                    is_new = False
                    break

            if is_new:
                self.current_spaces.append({
                    'points': self._slanted_box(cx, cy, cw, ch, angle),
                    'type':   stype
                })

        self.redraw_frame()
        self.refresh_list()
        QMessageBox.information(self, 'Listo',
            f'Se crearon {len(detections)} espacios basados en vehículos detectados.\n'
            f'Ajusta la inclinación con el slider y usa "✏️ Dibujo Manual" para los espacios vacíos.')


    # ── Line-based detection ──────────────────────────────────────────────────
    def detect_parking_lines(self):
        """Detect white parking space markings via Hough lines and group into spaces."""
        if self.raw_frame is None:
            return

        gray   = cv2.cvtColor(self.raw_frame, cv2.COLOR_BGR2GRAY)
        # Enhance white lines on gray asphalt
        _, white_mask = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
        edges  = cv2.Canny(white_mask, 50, 150)
        lines  = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=40,
                                  minLineLength=40, maxLineGap=10)
        if lines is None:
            QMessageBox.information(self, 'Líneas', 'No se detectaron líneas de parqueadero.\nIntenta con otro frame o ajusta el modo de cámara.')
            return

        bw = self.slider_w.value()
        bh = self.slider_h.value()

        # Cluster lines by angle to find dominant parking angle
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            ang = math.degrees(math.atan2(y2 - y1, x2 - x1)) % 180
            angles.append(ang)

        # Use median angle as the parking direction
        if angles:
            median_ang = float(np.median(angles))
            # Convert to shear angle for our slanted box (-90..90 relative to vertical)
            shear_angle = int(median_ang - 90) if median_ang > 45 else int(median_ang)
        else:
            shear_angle = 0

        # Find endpoints of detected lines and create spaces along them
        added = 0
        for line in lines[::3]:  # sample every 3rd line to avoid duplicates
            x1, y1, x2, y2 = line[0]
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)
            poly = self._slanted_box(cx, cy, bw, bh, shear_angle)
            self.current_spaces.append({'points': poly, 'type': self.combo_type.currentText()})
            added += 1

        self.redraw_frame(); self.refresh_list()
        QMessageBox.information(self, 'Líneas Detectadas',
                                f'Se detectaron {added} espacios potenciales a {shear_angle}° de inclinación.\n'
                                f'Usa "Editar Vértices" para ajustar los que no queden perfectos.')

    # ── Geometry ──────────────────────────────────────────────────────────────
    def _slanted_box(self, cx, cy_ground, w, h, angle_deg):
        x1, x2 = cx - w/2, cx + w/2
        y1, y2 = cy_ground - h, cy_ground
        shear  = math.tan(math.radians(angle_deg))
        dx     = (h / 2) * shear
        return [(int(x1+dx), int(y1)), (int(x2+dx), int(y1)),
                (int(x2-dx), int(y2)), (int(x1-dx), int(y2))]

    # ── Polygon controls ──────────────────────────────────────────────────────
    def finish_polygon(self):
        if self.mode == 'manual' and len(self.current_polygon) > 2:
            self.current_spaces.append({
                'points': list(self.current_polygon),
                'type':   self.combo_type.currentText()
            })
            self.current_polygon = []
            self.redraw_frame(); self.refresh_list()
        else:
            QMessageBox.warning(self, 'Error', 'El polígono necesita al menos 3 puntos.')

    def delete_selected(self):
        row = self.list_spaces.currentRow()
        if row >= 0:
            self.current_spaces.pop(row)
            self.redraw_frame(); self.refresh_list()

    def clear_all(self):
        self.current_spaces.clear()
        self.current_polygon = []
        self.redraw_frame(); self.refresh_list()

    def apply_changes(self):
        self.vision_thread.update_spaces(self.current_spaces)
        self.spaces_saved.emit(self.current_spaces)
        QMessageBox.information(self, 'Éxito', f'{len(self.current_spaces)} espacios guardados y aplicados.')
