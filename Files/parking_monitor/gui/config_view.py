import cv2
import numpy as np
import math
import json
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QComboBox, QListWidget,
                               QListWidgetItem, QFrame, QMessageBox, QSlider, QLineEdit,
                               QInputDialog)
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

        right_layout.addWidget(QLabel('Nombre del Espacio (opcional):'))
        self.edit_name = QLineEdit()
        self.edit_name.setPlaceholderText('Ej: A-01, VIP-1, P-101...')
        right_layout.addWidget(self.edit_name)

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

        self.btn_save_poly = QPushButton('💾 Finalizar y Guardar (Espacio Manual)')
        self.btn_save_poly.clicked.connect(self.finish_polygon)
        self.btn_save_poly.setStyleSheet("background-color: #0369a1; font-weight: bold;")
        right_layout.addWidget(self.btn_save_poly)

        self.btn_duplicate = QPushButton('👯 Duplicar Espacio Seleccionado')
        self.btn_duplicate.clicked.connect(self.duplicate_selected)
        right_layout.addWidget(self.btn_duplicate)

        right_layout.addWidget(QLabel('Espacios Guardados:'))
        self.list_spaces = QListWidget()
        self.list_spaces.setIconSize(QSize(100, 100))
        self.list_spaces.itemDoubleClicked.connect(self.rename_space)
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
        
        # Set focus policy to capture keys
        self.setFocusPolicy(Qt.StrongFocus)

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
            name = space.get('name', f'Espacio {i+1}') if isinstance(space, dict) else f'Espacio {i+1}'
            item  = QListWidgetItem(f'{name} ({stype})')
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
            prefix = self._get_type_prefix(stype)
            custom_name = self.edit_name.text().strip()
            if not custom_name:
                custom_name = self._get_next_space_number(prefix)
            found = False
            for box in results[0].boxes.xyxy.cpu().numpy():
                x1, y1, x2, y2 = map(int, box)
                if x1 <= px <= x2 and y1 <= py <= y2:
                    cw = (x2 - x1) * 1.15  # 15% extra width for parking space
                    ch = (y2 - y1) * 1.05  # 5% extra height
                    cx = int(x1 + (x2 - x1) / 2)
                    cy = int(y2)
                    poly = self._slanted_box(cx, cy, cw, ch, angle)
                    self.current_spaces.append({'points': poly, 'type': stype, 'name': custom_name})
                    found = True
                    break
            if not found:
                # Manual placement at click location using slider values
                poly = self._slanted_box(px, py + bh_default//2, bw_default, bh_default, angle)
                self.current_spaces.append({'points': poly, 'type': stype, 'name': custom_name})
            self.edit_name.clear()
            self.redraw_frame(); self.refresh_list()
        except Exception as e:
            print('Smart click error:', e)

    # ── Autodetect ────────────────────────────────────────────────────────────
    _precise_model_cache = None
    
    def _get_precise_model(self):
        """Cache the precise model to avoid reloading."""
        if self._precise_model_cache is None:
            from ultralytics import YOLO
            self._precise_model_cache = YOLO('yolo26m-seg.pt')
        return self._precise_model_cache
    
    def _sliced_detect(self, frame):
        """
        Tile-based inference con modelo preciso (yolov8m-seg).
        Usa segmentación para mejor precisión en detección de vehículos.
        """
        precise_model = self._get_precise_model()
        
        fh, fw = frame.shape[:2]
        tile_sz  = 640
        overlap  = 160
        step     = tile_sz - overlap
        conf_thr = 0.15
        nms_iou  = 0.45

        all_boxes = []
        all_masks = []
        all_confs = []
        
        for y in range(0, fh, step):
            for x in range(0, fw, step):
                x2 = min(x + tile_sz, fw)
                y2 = min(y + tile_sz, fh)
                tile = frame[y:y2, x:x2]
                r = precise_model.predict(tile, classes=[2, 3, 5, 7], conf=conf_thr, verbose=False, imgsz=640)
                
                for res in r:
                    if res.masks is not None:
                        masks_data = res.masks.xy
                        boxes = res.boxes.xyxy.cpu().numpy()
                        confs = res.boxes.conf.cpu().numpy()
                        
                        for mask_pts, box, conf in zip(masks_data, boxes, confs):
                            bx1, by1, bx2, by2 = box
                            adjusted_mask = np.array(mask_pts) + np.array([x, y])
                            all_boxes.append([x + bx1, y + by1, x + bx2, y + by2])
                            all_masks.append(adjusted_mask)
                            all_confs.append(float(conf))
                    else:
                        boxes = res.boxes.xyxy.cpu().numpy()
                        confs = res.boxes.conf.cpu().numpy()
                        for box, conf in zip(boxes, confs):
                            bx1, by1, bx2, by2 = box
                            all_boxes.append([x + bx1, y + by1, x + bx2, y + by2])
                            all_masks.append(None)
                            all_confs.append(float(conf))

        if not all_boxes:
            return []

        boxes_np = np.array(all_boxes, dtype=np.float32)
        widths  = boxes_np[:, 2] - boxes_np[:, 0]
        heights = boxes_np[:, 3] - boxes_np[:, 1]
        valid   = (widths > 30) & (widths < 350) & (heights > 25) & (heights < 300)
        boxes_np = boxes_np[valid]
        all_confs = [c for i, c in enumerate(all_confs) if valid[i]]
        all_masks = [m for i, m in enumerate(all_masks) if valid[i]]

        if len(boxes_np) == 0:
            return []

        xywh = boxes_np.copy()
        xywh[:, 2] -= xywh[:, 0]
        xywh[:, 3] -= xywh[:, 1]
        idx = cv2.dnn.NMSBoxes(xywh.astype(int).tolist(), all_confs, conf_thr, nms_iou)

        if len(idx) == 0:
            return []

        result = []
        for i in idx.flatten():
            box = boxes_np[i]
            mask = all_masks[i]
            conf = all_confs[i]
            
            if mask is not None and len(mask) >= 3:
                cx = int(np.mean(mask[:, 0]))
                cy = int(np.mean(mask[:, 1]))
            else:
                cx = int((box[0] + box[2]) / 2)
                cy = int((box[1] + box[3]) / 2)
            
            result.append({
                'box': box.tolist(),
                'centroid': (cx, cy),
                'confidence': conf,
                'mask': mask
            })
        
        return result

    def auto_detect_all(self):
        """Detect all cars via tiled inference con modelo preciso → create parking space from each detection."""
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
        prefix = self._get_type_prefix(stype)
        added = 0

        for det in detections:
            cx, cy = det['centroid']

            is_new = True
            for existing in self.current_spaces:
                ex_pts = existing['points'] if isinstance(existing, dict) else existing
                if cv2.pointPolygonTest(np.array(ex_pts, np.int32), (cx, cy), False) >= 0:
                    is_new = False
                    break

            if is_new:
                box = det['box']
                cw = (box[2] - box[0]) * 1.2
                ch = (box[3] - box[1]) * 1.1
                custom_name = self.edit_name.text().strip()
                if not custom_name:
                    custom_name = self._get_next_space_number(prefix)
                self.current_spaces.append({
                    'points': self._slanted_box(cx, int(box[3]), cw, ch, angle),
                    'type': stype,
                    'name': custom_name
                })
                added += 1

        self.edit_name.clear()
        self.redraw_frame()
        self.refresh_list()
        QMessageBox.information(self, 'Listo',
            f'Se detectaron {len(detections)} vehículos.\n'
            f'Se crearon {added} espacios.\n'
            f'Ajusta la inclinación con el slider.')

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
    def _get_next_space_number(self, prefix):
        """Get next sequential number for given prefix (e.g., 'A' -> 'A-01', 'A-02'...)."""
        max_num = 0
        for space in self.current_spaces:
            if isinstance(space, dict) and 'name' in space and space['name']:
                name = space['name']
                if name.startswith(prefix + '-'):
                    try:
                        num = int(name.split('-')[1])
                        max_num = max(max_num, num)
                    except:
                        pass
        return f"{prefix}-{max_num + 1:02d}"

    def _get_type_prefix(self, stype):
        """Map space type to prefix letter."""
        return {'Estándar': 'A', 'Motos': 'M', 'VIP': 'V', 'Discapacitados': 'D'}.get(stype, 'A')

    def finish_polygon(self):
        if self.mode == 'manual' and len(self.current_polygon) > 2:
            stype = self.combo_type.currentText()
            prefix = self._get_type_prefix(stype)
            custom_name = self.edit_name.text().strip()
            if not custom_name:
                custom_name = self._get_next_space_number(prefix)
            self.current_spaces.append({
                'points': list(self.current_polygon),
                'type': stype,
                'name': custom_name
            })
            self.current_polygon = []
            self.edit_name.clear()
            self.redraw_frame(); self.refresh_list()
        else:
            QMessageBox.warning(self, 'Error', 'El polígono necesita al menos 3 puntos.')

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.finish_polygon()
        elif event.key() == Qt.Key_Delete:
            self.delete_selected()
        elif event.key() == Qt.Key_D and event.modifiers() & Qt.ControlModifier:
            self.duplicate_selected()
        super().keyPressEvent(event)

    def delete_selected(self):
        row = self.list_spaces.currentRow()
        if row >= 0:
            self.current_spaces.pop(row)
            self.redraw_frame(); self.refresh_list()

    def rename_space(self, item=None):
        row = self.list_spaces.currentRow()
        if row < 0:
            return
        space = self.current_spaces[row]
        current_name = ''
        if isinstance(space, dict) and 'name' in space:
            current_name = space['name']
        new_name, ok = QInputDialog.getText(self, 'Renombrar Espacio',
                                               'Nuevo nombre:', text=current_name)
        if ok and new_name.strip():
            if isinstance(space, dict):
                space['name'] = new_name.strip()
            self.redraw_frame(); self.refresh_list()

    def duplicate_selected(self):
        row = self.list_spaces.currentRow()
        if row >= 0:
            space = self.current_spaces[row].copy()
            pts = space['points'] if isinstance(space, dict) else space
            new_pts = [(p[0]+20, p[1]+20) for p in pts]
            if isinstance(space, dict):
                space['points'] = new_pts
                # Add "(copia)" suffix to name
                if 'name' in space and space['name']:
                    space['name'] = f"{space['name']} (copia)"
                else:
                    space['name'] = f'Espacio {len(self.current_spaces)+1} (copia)'
            else:
                space = new_pts
            self.current_spaces.append(space)
            self.redraw_frame(); self.refresh_list()
            self.list_spaces.setCurrentRow(len(self.current_spaces)-1)

    def clear_all(self):
        self.current_spaces.clear()
        self.current_polygon = []
        self.redraw_frame(); self.refresh_list()

    def apply_changes(self):
        self.vision_thread.update_spaces(self.current_spaces)
        self.spaces_saved.emit(self.current_spaces)
        QMessageBox.information(self, 'Éxito', f'{len(self.current_spaces)} espacios guardados y aplicados.')
