// ==============================================================================
// 🌐 BILINGUAL I18N SYSTEM (ENGLISH DEFAULT / SPANISH TOGGLE)
// ==============================================================================
let currentLang = localStorage.getItem('parkvision_lang') || 'en';

const I18N = {
    en: {
        // App titles and navigation
        'doc.title': '🅿️ Smart Parking Vision | AI & Multi-GPU',
        'nav.monitor': '🖥️ Live Monitor',
        'nav.editor': '📐 Bay Editor',
        'nav.guide': '📖 How It Works',
        
        // Header Controls
        'pill.device_title': 'Hardware Acceleration: NVIDIA CUDA, AMD DirectML or CPU',
        'pill.device_label': '⚡ Engine:',
        'pill.device_auto': 'Auto Detection',
        'pill.source_title': 'Select video stream or camera',
        'pill.source_label': '📹 Source:',
        'pill.source_loading': 'Loading...',
        'btn.upload_title': 'Upload local parking video',
        'btn.upload': 'Upload',
        'btn.reports_title': 'Generate and download audit reports',
        'btn.reports': 'Reports',
        
        // HUD & Video
        'hud.live': 'LIVE',
        'stream.alt': 'Parking Lot Live Stream',
        
        // KPIs
        'kpi.total_spots': 'Total Bays',
        'kpi.occupied': 'Occupied',
        'kpi.available': 'Available',
        'kpi.occupancy_rate': 'Occupancy Rate',
        'kpi.avg_stay': 'Avg Dwell Time',
        'kpi.vehicles_today': 'Vehicles (Today)',
        
        // Live Monitor Sidebar
        'panel.parked_vehicles': 'Parked Vehicles',
        'panel.spot_status': 'Parking Bay Status',
        'btn.open_editor': 'Open Editor',
        'table.monitoring': 'Monitoring parking lot...',
        'table.no_vehicles': 'No parked vehicles at this time.',
        'th.bay': 'Bay',
        'th.id': 'ID',
        'th.type': 'Type',
        'th.entry': 'Entry',
        'th.time': 'Duration',
        
        // Editor Controls
        'editor.tools': '📐 Tools:',
        'btn.rect_title': 'Create rectangle and adjust angle with slider',
        'btn.rect': 'Rectangle',
        'btn.poly_title': 'Draw arbitrary polygon vertices point by point',
        'btn.poly': 'Polygon',
        'btn.corners_title': 'Mark 4 perspective corners',
        'btn.corners': '4 Corners',
        'btn.excl_title': 'Draw exclusion zone where model ignores all activity',
        'btn.excl': 'Exclusion Zone',
        'btn.toggle_excl_title': 'Toggle visibility of ignored zones on canvas',
        'btn.toggle_excl': 'Ignored Zones',
        'btn.template_title': 'Load 6-bay demo template',
        'btn.template': 'Template',
        'btn.clear_title': 'Delete all parking bays',
        'btn.clear': 'Clear',
        'editor.canvas_alt': 'Bay Editor Canvas',
        'editor.angle': '📐 Angle:',
        'btn.save': 'Save',
        'btn.cancel': 'Cancel',
        
        // Editor Sidebar
        'editor.tab_spots': '🅿️ Bays',
        'editor.tab_exclusions': '🚫 Ignored Zones',
        'th.name': 'Name',
        'th.status': 'Status',
        'th.actions': 'Actions',
        'th.desc': 'Name / Description',
        'th.vertices': 'Vertices',
        
        // Modals
        'modal.spot_title': '🅿️ Save Parking Bay',
        'modal.spot_id_label': 'Bay Identifier (ID):',
        'modal.spot_id_ph': 'e.g. P-01, A-10',
        'modal.spot_name_label': 'Visible Name / Label:',
        'modal.spot_name_ph': 'e.g. Bay 1, VIP Entrance',
        'modal.spot_type_label': 'Allowed Vehicle Type:',
        'btn.save_spot': 'Save Bay',
        
        'modal.excl_title': '🚫 Save Exclusion / Ignored Zone',
        'modal.excl_desc': 'The artificial intelligence model will completely ignore all vehicles inside this polygon.',
        'modal.excl_id_label': 'Identifier (ID):',
        'modal.excl_id_ph': 'e.g. EZ-01, STREET',
        'modal.excl_name_label': 'Descriptive Name / Label:',
        'modal.excl_name_ph': 'e.g. Outside street, Sidewalk',
        'btn.save_excl': 'Save Exclusion',
        
        'modal.edit_title': '✏️ Edit Parking Bay',
        'btn.save_changes': 'Save Changes',
        
        'rep.title': '📊 Occupancy & Traffic Reports',
        'rep.subtitle': 'Full historical logs of entries, exits, dwell times, and facility analytics',
        'rep.total_historical': 'Total Vehicles',
        'rep.completed_stays': 'Completed Stays',
        'rep.avg_duration': 'Avg Dwell Time',
        'rep.busiest_hour': 'Peak Hour',
        'rep.types_label': 'Types:',
        'rep.search_ph': '🔍 Filter by Bay or Vehicle ID...',
        'rep.download_btn': 'Download CSV / Excel',
        'th.vehicle_id': 'Vehicle ID',
        'th.entry_time': 'Entry Time',
        'th.exit_time': 'Exit Time',
        'th.stay_duration': 'Dwell Time',
        'btn.close': 'Close',
        
        'ip.title': '🌐 Connect IP / RTSP Camera',
        'ip.desc': 'Enter the full RTSP or HTTP video stream URL from your security camera:',
        'ip.url_label': 'Stream URL:',
        'ip.url_ph': 'rtsp://user:pass@192.168.1.50:554/stream1',
        'btn.connect': 'Connect Stream',
        
        // Options
        'opt.car': '🚗 Standard Car',
        'opt.motorcycle': '🏍️ Motorcycle',
        'opt.truck': '🚚 Truck / Bus',
        'opt.disabled': '♿ Accessible Parking',
        
        // Dynamic JavaScript Strings
        'str.spot_car': '🚗 Car',
        'str.spot_moto': '🏍️ Motorcycle',
        'str.spot_truck': '🚚 Truck/Bus',
        'str.spot_disabled': '♿ Accessible',
        'str.occupied': 'OCCUPIED',
        'str.vacant': 'VACANT',
        'str.parked_badge': 'Parked',
        'str.in_progress': 'In progress',
        'str.no_spots_msg': 'No bays created. Click <strong>"Rectangle"</strong>, <strong>"Polygon"</strong>, or <strong>"📐 Template"</strong>.',
        'str.no_spots_table': 'No parking bays currently created.',
        'str.no_exclusions_table': 'No exclusion zones created. Click "🚫 Exclusion Zone" to create one.',
        'str.no_history_table': 'No parking logs yet.',
        'str.vertices': 'vertices',
        'str.bays_configured': 'bays configured',
        'str.ignored_label': '⛔ IGNORED:',
        'str.toggle_vis': '👁️ Visible Zones',
        'str.toggle_hid': '🙈 Hidden Zones',
        'str.confirm_del_spot': (id) => `Delete parking bay ${id}?`,
        'str.confirm_clear_all': 'Are you sure you want to delete ALL parking bays?',
        'str.confirm_del_excl': (id) => `Delete exclusion zone ${id}?`,
        'str.alert_fill_fields': 'Please fill in all fields',
        'str.alert_save_error': 'Error saving parking bay',
        'str.alert_save_excl_error': 'Error saving exclusion zone',
        'str.alert_conn_error': 'Connection error',
        'str.alert_ip_url': 'Please enter a valid RTSP or HTTP URL',
        'str.alert_ip_failed': 'Could not connect to IP camera',
        'str.alert_upload_error': 'Error uploading video',
        'str.opt_parking_videos': 'Parking Lot Videos',
        'str.opt_webcams': 'Detected Webcams',
        'str.opt_security_network': 'Security / Network',
        'str.opt_ip_custom': '🌐 IP Camera (RTSP / HTTP)...',
        'str.default_spot_label': (idx) => `Bay ${idx}`,
        'str.default_excl_label': (idx) => `Ignored Zone ${idx}`,
        
        'instr.free_polygon': '📍 Click point by point. Double-click or click "Save" when finished.',
        'instr.exclusion_zone': '🚫 Mark exclusion zone points (model will ignore this area). Click "Save" or double-click.',
        'instr.rotate_rectangle': '🔲 Drag to create a rectangle and rotate angle if needed.',
        'instr.perspective': '📍 Click 4 times on the video at the corners of the parking bay.'
    },
    es: {
        // App titles and navigation
        'doc.title': '🅿️ Smart Parking Vision | IA & Multi-GPU',
        'nav.monitor': '🖥️ Monitor En Vivo',
        'nav.editor': '📐 Editor de Plazas',
        'nav.guide': '📖 ¿Cómo Funciona?',
        
        // Header Controls
        'pill.device_title': 'Aceleración de Hardware: NVIDIA CUDA, AMD DirectML o CPU',
        'pill.device_label': '⚡ Motor:',
        'pill.device_auto': 'Detección Automática',
        'pill.source_title': 'Seleccionar fuente de video o cámara',
        'pill.source_label': '📹 Fuente:',
        'pill.source_loading': 'Cargando...',
        'btn.upload_title': 'Subir video local de parqueadero',
        'btn.upload': 'Subir',
        'btn.reports_title': 'Generar y descargar reportes',
        'btn.reports': 'Reportes',
        
        // HUD & Video
        'hud.live': 'EN VIVO',
        'stream.alt': 'Transmisión en Vivo de Parqueadero',
        
        // KPIs
        'kpi.total_spots': 'Plazas Totales',
        'kpi.occupied': 'Ocupadas',
        'kpi.available': 'Disponibles',
        'kpi.occupancy_rate': 'Ocupación',
        'kpi.avg_stay': 'Permanencia Prom.',
        'kpi.vehicles_today': 'Vehículos (Hoy)',
        
        // Live Monitor Sidebar
        'panel.parked_vehicles': 'Vehículos Estacionados',
        'panel.spot_status': 'Estado de Plazas',
        'btn.open_editor': 'Ir al Editor',
        'table.monitoring': 'Monitoreando parqueadero...',
        'table.no_vehicles': 'No hay vehículos estacionados en este momento.',
        'th.bay': 'Plaza',
        'th.id': 'ID',
        'th.type': 'Tipo',
        'th.entry': 'Ingreso',
        'th.time': 'Tiempo',
        
        // Editor Controls
        'editor.tools': '📐 Herramientas:',
        'btn.rect_title': 'Crear rectángulo y ajustar ángulo con slider',
        'btn.rect': 'Rectángulo',
        'btn.poly_title': 'Trazar vértices libres uno a uno',
        'btn.poly': 'Polígono',
        'btn.corners_title': 'Marcar 4 esquinas de perspectiva',
        'btn.corners': '4 Esquinas',
        'btn.excl_title': 'Trazar zona donde el modelo no calculará nada',
        'btn.excl': 'Zona Exclusión',
        'btn.toggle_excl_title': 'Ver u ocultar zonas ignoradas en el lienzo del editor',
        'btn.toggle_excl': 'Zonas Ignoradas',
        'btn.template_title': 'Cargar plantilla de 6 plazas',
        'btn.template': 'Plantilla',
        'btn.clear_title': 'Eliminar todas las plazas',
        'btn.clear': 'Limpiar',
        'editor.canvas_alt': 'Editor de Plazas',
        'editor.angle': '📐 Ángulo:',
        'btn.save': 'Guardar',
        'btn.cancel': 'Cancelar',
        
        // Editor Sidebar
        'editor.tab_spots': '🅿️ Plazas',
        'editor.tab_exclusions': '🚫 Zonas Ignoradas',
        'th.name': 'Nombre',
        'th.status': 'Estado',
        'th.actions': 'Acciones',
        'th.desc': 'Nombre / Descripción',
        'th.vertices': 'Vértices',
        
        // Modals
        'modal.spot_title': '🅿️ Guardar Plaza de Parqueo',
        'modal.spot_id_label': 'Identificador de Plaza (ID):',
        'modal.spot_id_ph': 'Ej: P-01, A-10',
        'modal.spot_name_label': 'Nombre / Etiqueta Visible:',
        'modal.spot_name_ph': 'Ej: Plaza 1, VIP Entrada',
        'modal.spot_type_label': 'Tipo de Vehículo Permitido:',
        'btn.save_spot': 'Guardar Plaza',
        
        'modal.excl_title': '🚫 Guardar Zona de Exclusión / Ignorada',
        'modal.excl_desc': 'El modelo de inteligencia artificial ignorará por completo todos los vehículos dentro de este polígono.',
        'modal.excl_id_label': 'Identificador (ID):',
        'modal.excl_id_ph': 'Ej: EZ-01, CALLE',
        'modal.excl_name_label': 'Nombre / Etiqueta Descriptiva:',
        'modal.excl_name_ph': 'Ej: Vía exterior, Pasillo peatonal',
        'btn.save_excl': 'Guardar Exclusión',
        
        'modal.edit_title': '✏️ Editar Plaza de Parqueo',
        'btn.save_changes': 'Guardar Cambios',
        
        'rep.title': '📊 Reportes de Ocupación y Afluencia',
        'rep.subtitle': 'Historial completo de ingresos, salidas, permanencia y analítica',
        'rep.total_historical': 'Vehículos Totales',
        'rep.completed_stays': 'Estadías Completadas',
        'rep.avg_duration': 'Permanencia Prom.',
        'rep.busiest_hour': 'Hora Pico',
        'rep.types_label': 'Tipos:',
        'rep.search_ph': '🔍 Filtrar por Plaza o ID de vehículo...',
        'rep.download_btn': 'Descargar CSV / Excel',
        'th.vehicle_id': 'ID Vehículo',
        'th.entry_time': 'Hora Ingreso',
        'th.exit_time': 'Hora Salida',
        'th.stay_duration': 'Permanencia',
        'btn.close': 'Cerrar',
        
        'ip.title': '🌐 Conectar Cámara IP / RTSP',
        'ip.desc': 'Ingresa la URL completa del flujo RTSP o HTTP de tu cámara de seguridad:',
        'ip.url_label': 'URL del Flujo:',
        'ip.url_ph': 'rtsp://user:pass@192.168.1.50:554/stream1',
        'btn.connect': 'Conectar Flujo',
        
        // Options
        'opt.car': '🚗 Automóvil Estándar',
        'opt.motorcycle': '🏍️ Motocicleta',
        'opt.truck': '🚚 Camión / Autobús',
        'opt.disabled': '♿ Movilidad Reducida',
        
        // Dynamic JavaScript Strings
        'str.spot_car': '🚗 Auto',
        'str.spot_moto': '🏍️ Moto',
        'str.spot_truck': '🚚 Camión/Bus',
        'str.spot_disabled': '♿ Reducida',
        'str.occupied': 'OCUPADO',
        'str.vacant': 'LIBRE',
        'str.parked_badge': 'Estacionado',
        'str.in_progress': 'En curso',
        'str.no_spots_msg': 'No hay plazas creadas. Pulsa <strong>"Rectángulo"</strong>, <strong>"Polígono"</strong> o <strong>"📐 Plantilla"</strong>.',
        'str.no_spots_table': 'No hay plazas de parqueo creadas actualmente.',
        'str.no_exclusions_table': 'No hay zonas de exclusión creadas. Pulsa "🚫 Zona de Exclusión" para crear una.',
        'str.no_history_table': 'Aún no hay registros de parqueo.',
        'str.vertices': 'vértices',
        'str.bays_configured': 'plazas configuradas',
        'str.ignored_label': '⛔ IGNORADA:',
        'str.toggle_vis': '👁️ Zonas Visibles',
        'str.toggle_hid': '🙈 Zonas Ocultas',
        'str.confirm_del_spot': (id) => `¿Eliminar la plaza ${id}?`,
        'str.confirm_clear_all': '¿Estás seguro de eliminar TODAS las plazas de parqueo?',
        'str.confirm_del_excl': (id) => `¿Eliminar la zona de exclusión ${id}?`,
        'str.alert_fill_fields': 'Por favor completa todos los campos',
        'str.alert_save_error': 'Error al guardar la plaza',
        'str.alert_save_excl_error': 'Error al guardar la zona de exclusión',
        'str.alert_conn_error': 'Error de conexión',
        'str.alert_ip_url': 'Ingresa una URL RTSP o HTTP válida',
        'str.alert_ip_failed': 'No se pudo conectar a la cámara IP',
        'str.alert_upload_error': 'Error al subir video',
        'str.opt_parking_videos': 'Videos de Parqueadero',
        'str.opt_webcams': 'Cámaras Web Detectadas',
        'str.opt_security_network': 'Seguridad / Red',
        'str.opt_ip_custom': '🌐 Cámara IP (RTSP / HTTP)...',
        'str.default_spot_label': (idx) => `Plaza ${idx}`,
        'str.default_excl_label': (idx) => `Zona Ignorada ${idx}`,
        
        'instr.free_polygon': '📍 Haz clic punto por punto. Haz doble clic o pulsa "Guardar" al terminar.',
        'instr.exclusion_zone': '🚫 Marca los puntos de la Zona de Exclusión (el modelo no calculará nada aquí). Pulsa "Guardar" o doble clic.',
        'instr.rotate_rectangle': '🔲 Arrastra para crear un rectángulo y gira el ángulo si es necesario.',
        'instr.perspective': '📍 Haz 4 clics sobre el video en las esquinas de la plaza.'
    }
};

function t(key, ...args) {
    const dict = I18N[currentLang] || I18N['en'];
    const val = dict[key] || I18N['en'][key] || key;
    if (typeof val === 'function') {
        return val(...args);
    }
    return val;
}

function setLanguage(lang) {
    currentLang = (lang === 'es') ? 'es' : 'en';
    localStorage.setItem('parkvision_lang', currentLang);
    document.documentElement.lang = currentLang;

    // Toggle button active states
    const btnEn = document.getElementById('langBtn-en');
    const btnEs = document.getElementById('langBtn-es');
    if (btnEn && btnEs) {
        if (currentLang === 'en') {
            btnEn.classList.add('active');
            btnEs.classList.remove('active');
        } else {
            btnEs.classList.add('active');
            btnEn.classList.remove('active');
        }
    }

    // Translate DOM elements
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        const translation = t(key);
        if (translation) el.textContent = translation;
    });

    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        const translation = t(key);
        if (translation) el.placeholder = translation;
    });

    document.querySelectorAll('[data-i18n-title]').forEach(el => {
        const key = el.getAttribute('data-i18n-title');
        const translation = t(key);
        if (translation) el.title = translation;
    });

    // Re-render dynamic components
    if (drawingMode) {
        updateDrawInstructions();
    }
    if (currentSpots) {
        renderSpotsList(currentSpots);
        renderSpotManagerTable(currentSpots);
    }
    if (window._currentExclusions) {
        renderExclusionsTable(window._currentExclusions);
    }
    loadSources();
}

// State
let drawingMode = null; // 'rotate_rectangle' | 'free_polygon' | 'perspective' | null
let currentPoints = [];
let dragStartPoint = null;
let currentRectangle = null; // { x1, y1, x2, y2, angle }
let rotationAngle = 0;
let currentSpots = [];
let videoNativeWidth = 1280;
let videoNativeHeight = 720;

// DOM Elements
const videoFeed = document.getElementById('videoFeed');
const videoFeedEditor = document.getElementById('videoFeedEditor');
const drawCanvas = document.getElementById('drawCanvas');
const ctx = drawCanvas.getContext('2d');
const drawToolbar = document.getElementById('drawToolbar');

function getSpotIcon(type) {
    const map = {
        car: t('str.spot_car'),
        motorcycle: t('str.spot_moto'),
        truck: t('str.spot_truck'),
        disabled: t('str.spot_disabled')
    };
    return map[type] || t('str.spot_car');
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initCanvas();
    setLanguage(currentLang);
    loadDeviceStatus();
    loadSources();
    loadSpots();
    loadExclusions();
    startPollingStats();

    window.addEventListener('resize', () => {
        syncCanvasSize();
        const activeTab = document.querySelector('.tab-btn.active');
        if (activeTab && activeTab.id === 'tabBtn-editor') {
            renderExclusionZonesOnCanvas();
        }
    });
});

function syncCanvasSize() {
    const container = drawCanvas.parentElement;
    const target = (container && container.clientWidth > 0) ? container : videoFeedEditor;
    if (!target) return;

    const w = target.clientWidth;
    const h = target.clientHeight;

    if (w > 0 && h > 0) {
        if (drawCanvas.width !== w || drawCanvas.height !== h) {
            drawCanvas.width = w;
            drawCanvas.height = h;
            if (!drawingMode) {
                const activeTab = document.querySelector('.tab-btn.active');
                if (activeTab && activeTab.id === 'tabBtn-editor') {
                    renderExclusionZonesOnCanvas();
                }
            }
        }
    }

    if (videoFeedEditor && videoFeedEditor.naturalWidth > 0) {
        videoNativeWidth = videoFeedEditor.naturalWidth;
        videoNativeHeight = videoFeedEditor.naturalHeight;
    } else if (videoFeed && videoFeed.naturalWidth > 0) {
        videoNativeWidth = videoFeed.naturalWidth;
        videoNativeHeight = videoFeed.naturalHeight;
    }
}

function initCanvas() {
    syncCanvasSize();

    drawCanvas.addEventListener('mousedown', handleCanvasMouseDown);
    drawCanvas.addEventListener('mousemove', handleCanvasMouseMove);
    drawCanvas.addEventListener('mouseup', handleCanvasMouseUp);
    drawCanvas.addEventListener('dblclick', handleCanvasDblClick);
}

// ----------------- TAB NAVIGATION -----------------
function switchTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-view').forEach(view => view.classList.remove('active'));

    const btn = document.getElementById(`tabBtn-${tabName}`);
    const view = document.getElementById(`tabView-${tabName}`);

    if (btn) btn.classList.add('active');
    if (view) view.classList.add('active');

    if (tabName === 'editor') {
        syncCanvasSize();
        loadExclusions().then(() => {
            syncCanvasSize();
            renderExclusionZonesOnCanvas();
        });
        setTimeout(() => {
            syncCanvasSize();
            renderExclusionZonesOnCanvas();
        }, 100);
        setTimeout(() => {
            syncCanvasSize();
            renderExclusionZonesOnCanvas();
        }, 300);
    } else {
        clearCanvas();
    }
}

// ----------------- DRAWING TOOLS -----------------
function updateDrawInstructions() {
    const instrEl = document.getElementById('drawInstructions');
    if (!instrEl) return;
    if (drawingMode === 'free_polygon') {
        instrEl.innerText = t('instr.free_polygon');
    } else if (drawingMode === 'exclusion_zone') {
        instrEl.innerText = t('instr.exclusion_zone');
    } else if (drawingMode === 'rotate_rectangle') {
        instrEl.innerText = t('instr.rotate_rectangle');
    } else if (drawingMode === 'perspective') {
        instrEl.innerText = t('instr.perspective');
    } else {
        instrEl.innerText = '';
    }
}

function setDrawMode(mode) {
    drawingMode = mode;
    currentPoints = [];
    dragStartPoint = null;
    currentRectangle = null;
    rotationAngle = 0;
    clearCanvas();

    const rotateBox = document.getElementById('rotateControlBox');
    const finishBtn = document.getElementById('finishPolygonBtn');

    if (rotateBox) rotateBox.style.display = (mode === 'rotate_rectangle') ? 'flex' : 'none';
    if (finishBtn) finishBtn.style.display = 'none';

    if (mode) {
        drawCanvas.classList.add('drawing-active');
        drawToolbar.classList.add('show');
        updateDrawInstructions();
    } else {
        drawCanvas.classList.remove('drawing-active');
        drawToolbar.classList.remove('show');
    }
}

function cancelDrawing() {
    setDrawMode(null);
    clearCanvas();
    const activeTab = document.querySelector('.tab-btn.active');
    if (activeTab && activeTab.id === 'tabBtn-editor') {
        renderExclusionZonesOnCanvas();
    }
}

function clearCanvas() {
    ctx.clearRect(0, 0, drawCanvas.width, drawCanvas.height);
}

function getCanvasCoords(e) {
    const rect = drawCanvas.getBoundingClientRect();
    const scaleX = videoNativeWidth / rect.width;
    const scaleY = videoNativeHeight / rect.height;

    const canvasX = e.clientX - rect.left;
    const canvasY = e.clientY - rect.top;

    const nativeX = Math.round(canvasX * scaleX);
    const nativeY = Math.round(canvasY * scaleY);

    return { canvasX, canvasY, nativeX, nativeY };
}

function handleCanvasMouseDown(e) {
    if (!drawingMode) return;
    const { canvasX, canvasY, nativeX, nativeY } = getCanvasCoords(e);

    if (drawingMode === 'perspective' || drawingMode === 'free_polygon' || drawingMode === 'exclusion_zone') {
        currentPoints.push({ canvasX, canvasY, nativeX, nativeY });
        renderDrawingPreview();

        const finishBtn = document.getElementById('finishPolygonBtn');
        if ((drawingMode === 'free_polygon' || drawingMode === 'exclusion_zone') && currentPoints.length >= 3) {
            if (finishBtn) finishBtn.style.display = 'inline-flex';
        }

        if (drawingMode === 'perspective' && currentPoints.length === 4) {
            finishDrawingSpot();
        }
    } else if (drawingMode === 'rotate_rectangle') {
        dragStartPoint = { canvasX, canvasY, nativeX, nativeY };
    }
}

function handleCanvasMouseMove(e) {
    if (!drawingMode) return;
    const { canvasX, canvasY } = getCanvasCoords(e);

    if (drawingMode === 'rotate_rectangle' && dragStartPoint) {
        currentRectangle = {
            x1: dragStartPoint.canvasX,
            y1: dragStartPoint.canvasY,
            x2: canvasX,
            y2: canvasY
        };
        renderRotatedRectanglePreview();
    } else if ((drawingMode === 'perspective' || drawingMode === 'free_polygon' || drawingMode === 'exclusion_zone') && currentPoints.length > 0) {
        renderDrawingPreview(canvasX, canvasY);
    }
}

function handleCanvasMouseUp(e) {
    if (drawingMode === 'rotate_rectangle' && dragStartPoint) {
        const { canvasX, canvasY } = getCanvasCoords(e);
        if (Math.abs(canvasX - dragStartPoint.canvasX) > 15 && Math.abs(canvasY - dragStartPoint.canvasY) > 15) {
            currentRectangle = {
                x1: dragStartPoint.canvasX,
                y1: dragStartPoint.canvasY,
                x2: canvasX,
                y2: canvasY
            };
            renderRotatedRectanglePreview();
            const finishBtn = document.getElementById('finishPolygonBtn');
            if (finishBtn) finishBtn.style.display = 'inline-flex';
        }
        dragStartPoint = null;
    }
}

function handleCanvasDblClick(e) {
    if ((drawingMode === 'free_polygon' || drawingMode === 'exclusion_zone') && currentPoints.length >= 3) {
        finishDrawingSpot();
    }
}

function updateRotationAngle(val) {
    rotationAngle = parseInt(val, 10);
    const label = document.getElementById('rotationAngleValue');
    if (label) label.innerText = `${rotationAngle}°`;

    if (drawingMode === 'rotate_rectangle' && currentRectangle) {
        renderRotatedRectanglePreview();
    }
}

function renderRotatedRectanglePreview() {
    clearCanvas();
    if (!currentRectangle) return;

    const { x1, y1, x2, y2 } = currentRectangle;
    const cx = (x1 + x2) / 2;
    const cy = (y1 + y2) / 2;
    const width = Math.abs(x2 - x1);
    const height = Math.abs(y2 - y1);
    const rad = (rotationAngle * Math.PI) / 180;

    const unrotatedCorners = [
        { x: -width / 2, y: -height / 2 },
        { x: width / 2, y: -height / 2 },
        { x: width / 2, height / 2 },
        { x: -width / 2, height / 2 }
    ];

    const rotatedCanvasCorners = unrotatedCorners.map(pt => ({
        x: cx + pt.x * Math.cos(rad) - pt.y * Math.sin(rad),
        y: cy + pt.x * Math.sin(rad) + pt.y * Math.cos(rad)
    }));

    ctx.strokeStyle = '#00f2fe';
    ctx.lineWidth = 2;
    ctx.fillStyle = 'rgba(0, 242, 254, 0.2)';

    ctx.beginPath();
    ctx.moveTo(rotatedCanvasCorners[0].x, rotatedCanvasCorners[0].y);
    for (let i = 1; i < rotatedCanvasCorners.length; i++) {
        ctx.lineTo(rotatedCanvasCorners[i].x, rotatedCanvasCorners[i].y);
    }
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    const scaleX = videoNativeWidth / drawCanvas.width;
    const scaleY = videoNativeHeight / drawCanvas.height;

    currentPoints = rotatedCanvasCorners.map(pt => ({
        nativeX: Math.round(pt.x * scaleX),
        nativeY: Math.round(pt.y * scaleY)
    }));
}

function renderDrawingPreview(cursorX = null, cursorY = null) {
    clearCanvas();
    if (currentPoints.length === 0) return;

    const isExclusion = (drawingMode === 'exclusion_zone');
    const strokeCol = isExclusion ? '#ffaa00' : '#00f2fe';
    const fillCol = isExclusion ? 'rgba(255, 170, 0, 0.25)' : 'rgba(0, 242, 254, 0.2)';

    ctx.strokeStyle = strokeCol;
    ctx.lineWidth = 2;
    ctx.fillStyle = fillCol;

    ctx.beginPath();
    ctx.moveTo(currentPoints[0].canvasX, currentPoints[0].canvasY);
    for (let i = 1; i < currentPoints.length; i++) {
        ctx.lineTo(currentPoints[i].canvasX, currentPoints[i].canvasY);
    }
    if (cursorX !== null && cursorY !== null) {
        ctx.lineTo(cursorX, cursorY);
    }
    if (currentPoints.length >= 3 && (drawingMode === 'free_polygon' || drawingMode === 'exclusion_zone')) {
        ctx.closePath();
        ctx.fill();
    }
    ctx.stroke();

    for (let pt of currentPoints) {
        ctx.fillStyle = strokeCol;
        ctx.beginPath();
        ctx.arc(pt.canvasX, pt.canvasY, 5, 0, Math.PI * 2);
        ctx.fill();
    }
}

function finishDrawingSpot() {
    clearCanvas();
    const points = currentPoints.map(p => [p.nativeX, p.nativeY]);

    if (drawingMode === 'exclusion_zone') {
        const nextIdx = (window._currentExclusions ? window._currentExclusions.length : 0) + 1;
        document.getElementById('exclusionIdInput').value = `EZ-${nextIdx < 10 ? '0' + nextIdx : nextIdx}`;
        document.getElementById('exclusionLabelInput').value = t('str.default_excl_label', nextIdx);
        window._tempExclusionPoints = points;
        openModal('exclusionModal');
        setDrawMode(null);
        return;
    }

    const nextIdx = currentSpots.length + 1;
    document.getElementById('spotIdInput').value = `P-${nextIdx < 10 ? '0' + nextIdx : nextIdx}`;
    document.getElementById('spotLabelInput').value = t('str.default_spot_label', nextIdx);

    window._tempSpotPoints = points;
    openModal('spotModal');
    setDrawMode(null);
}

async function saveSpotFromModal() {
    const id = document.getElementById('spotIdInput').value.trim();
    const label = document.getElementById('spotLabelInput').value.trim();
    const spotType = document.getElementById('spotTypeInput').value;
    const points = window._tempSpotPoints;

    if (!id || !label || !points) {
        alert(t('str.alert_fill_fields'));
        return;
    }

    try {
        const res = await fetch('/api/spots', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, label, spot_type: spotType, points })
        });
        if (res.ok) {
            closeModal('spotModal');
            loadSpots();
        } else {
            alert(t('str.alert_save_error'));
        }
    } catch (e) {
        console.error(e);
        alert(t('str.alert_conn_error'));
    }
}

// ----------------- EXCLUSION / MASK ZONES -----------------
async function saveExclusionFromModal() {
    const id = document.getElementById('exclusionIdInput').value.trim();
    const label = document.getElementById('exclusionLabelInput').value.trim();
    const points = window._tempExclusionPoints;

    if (!id || !label || !points) {
        alert(t('str.alert_fill_fields'));
        return;
    }

    try {
        const res = await fetch('/api/exclusions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, label, points })
        });
        if (res.ok) {
            closeModal('exclusionModal');
            loadExclusions();
        } else {
            alert(t('str.alert_save_excl_error'));
        }
    } catch (e) {
        console.error(e);
        alert(t('str.alert_conn_error'));
    }
}

let showExclusionsInEditor = true;

function renderExclusionZonesOnCanvas() {
    const activeTab = document.querySelector('.tab-btn.active');
    if (!activeTab || activeTab.id !== 'tabBtn-editor') {
        clearCanvas();
        return;
    }
    if (!showExclusionsInEditor || drawingMode) return;
    if (!window._currentExclusions || window._currentExclusions.length === 0) {
        clearCanvas();
        return;
    }

    clearCanvas();
    if (drawCanvas.width <= 0 || drawCanvas.height <= 0) {
        syncCanvasSize();
    }
    const nativeW = (videoNativeWidth && videoNativeWidth > 0) ? videoNativeWidth : 1280;
    const nativeH = (videoNativeHeight && videoNativeHeight > 0) ? videoNativeHeight : 720;
    const scaleX = drawCanvas.width / nativeW;
    const scaleY = drawCanvas.height / nativeH;

    for (let zone of window._currentExclusions) {
        if (!zone.points || zone.points.length < 3) continue;

        ctx.save();
        ctx.setLineDash([8, 6]);
        ctx.strokeStyle = '#ffaa00';
        ctx.lineWidth = 2.5;
        ctx.fillStyle = 'rgba(255, 170, 0, 0.22)';

        ctx.beginPath();
        const startX = zone.points[0][0] * scaleX;
        const startY = zone.points[0][1] * scaleY;
        ctx.moveTo(startX, startY);

        let minX = startX, minY = startY, maxX = startX, maxY = startY;

        for (let i = 1; i < zone.points.length; i++) {
            const px = zone.points[i][0] * scaleX;
            const py = zone.points[i][1] * scaleY;
            ctx.lineTo(px, py);
            minX = Math.min(minX, px);
            minY = Math.min(minY, py);
            maxX = Math.max(maxX, px);
            maxY = Math.max(maxY, py);
        }
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        // Badge label
        const cx = (minX + maxX) / 2;
        const cy = (minY + maxY) / 2;
        const label = `${t('str.ignored_label')} ${zone.label}`;

        ctx.setLineDash([]);
        ctx.font = 'bold 12px Inter, sans-serif';
        const textWidth = ctx.measureText(label).width;

        ctx.fillStyle = 'rgba(20, 20, 25, 0.92)';
        ctx.strokeStyle = '#ffaa00';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.rect(cx - textWidth/2 - 8, cy - 12, textWidth + 16, 24);
        ctx.fill();
        ctx.stroke();

        ctx.fillStyle = '#ffb347';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(label, cx, cy);

        ctx.restore();
    }
}

function toggleExclusionsVisibility() {
    showExclusionsInEditor = !showExclusionsInEditor;
    const btn = document.getElementById('toggleExclusionsCanvasBtn');
    if (btn) {
        if (showExclusionsInEditor) {
            btn.classList.add('btn-cyan');
            btn.classList.remove('btn-glass');
            btn.innerText = t('str.toggle_vis');
            renderExclusionZonesOnCanvas();
        } else {
            btn.classList.remove('btn-cyan');
            btn.classList.add('btn-glass');
            btn.innerText = t('str.toggle_hid');
            clearCanvas();
        }
    }
}

function highlightExclusion(zoneId) {
    if (!window._currentExclusions) return;
    const zone = window._currentExclusions.find(z => z.id === zoneId);
    if (!zone || !zone.points || zone.points.length < 3) return;

    showExclusionsInEditor = true;
    renderExclusionZonesOnCanvas();

    const scaleX = drawCanvas.width / videoNativeWidth;
    const scaleY = drawCanvas.height / videoNativeHeight;

    ctx.save();
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 4;
    ctx.fillStyle = 'rgba(255, 255, 255, 0.35)';
    ctx.beginPath();
    ctx.moveTo(zone.points[0][0] * scaleX, zone.points[0][1] * scaleY);
    for (let i = 1; i < zone.points.length; i++) {
        ctx.lineTo(zone.points[i][0] * scaleX, zone.points[i][1] * scaleY);
    }
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    ctx.restore();

    setTimeout(renderExclusionZonesOnCanvas, 900);
}

async function loadExclusions() {
    try {
        const res = await fetch('/api/exclusions');
        window._currentExclusions = await res.json();
        renderExclusionsTable(window._currentExclusions);
        const activeTab = document.querySelector('.tab-btn.active');
        if (activeTab && activeTab.id === 'tabBtn-editor') {
            renderExclusionZonesOnCanvas();
        }
    } catch (e) {
        console.error(e);
    }
}

function renderExclusionsTable(zones) {
    const tbody = document.getElementById('managerExclusionsTableBody');
    if (!tbody) return;

    if (!zones || zones.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;color:var(--text-muted);padding:2rem;">${t('str.no_exclusions_table')}</td></tr>`;
        return;
    }

    tbody.innerHTML = zones.map(z => `
        <tr onclick="highlightExclusion('${z.id}')" style="cursor:pointer;" title="Click to highlight in video">
            <td><strong style="color:var(--neon-amber);">${z.id}</strong></td>
            <td><strong>${z.label}</strong></td>
            <td><span class="tag-badge" style="background:rgba(255,170,0,0.15);color:#ffaa00;">${z.points ? z.points.length : 0} ${t('str.vertices')}</span></td>
            <td style="text-align:right;">
                <button class="btn btn-scarlet-outline btn-icon" onclick="event.stopPropagation(); deleteExclusion('${z.id}')" title="Delete ignored zone" style="font-size:0.75rem;padding:0.25rem 0.6rem;">
                    🗑️
                </button>
            </td>
        </tr>
    `).join('');
}

async function deleteExclusion(id) {
    if (!confirm(t('str.confirm_del_excl', id))) return;
    try {
        await fetch(`/api/exclusions/${encodeURIComponent(id)}`, { method: 'DELETE' });
        loadExclusions();
    } catch (e) {
        console.error(e);
    }
}

function switchEditorSubView(subview) {
    const spotsBtn = document.getElementById('editorSubView-spots');
    const exclusionsBtn = document.getElementById('editorSubView-exclusions');
    const spotsTable = document.getElementById('managerSpotsTable');
    const exclusionsTable = document.getElementById('managerExclusionsTable');

    if (subview === 'spots') {
        if (spotsBtn) spotsBtn.classList.add('active');
        if (exclusionsBtn) exclusionsBtn.classList.remove('active');
        if (spotsTable) spotsTable.style.display = '';
        if (exclusionsTable) exclusionsTable.style.display = 'none';
    } else {
        if (spotsBtn) spotsBtn.classList.remove('active');
        if (exclusionsBtn) exclusionsBtn.classList.add('active');
        if (spotsTable) spotsTable.style.display = 'none';
        if (exclusionsTable) exclusionsTable.style.display = '';
        showExclusionsInEditor = true;
        loadExclusions();
    }
}

// ----------------- SPOTS MANAGEMENT & EDITING -----------------
async function loadSpots() {
    try {
        const res = await fetch('/api/spots');
        currentSpots = await res.json();
        renderSpotsList(currentSpots);
        renderSpotManagerTable(currentSpots);
    } catch (e) {
        console.error(e);
    }
}

function renderSpotsList(spots) {
    const container = document.getElementById('spotsList');
    if (!container) return;

    if (spots.length === 0) {
        container.innerHTML = `<p style="grid-column: 1/-1; color:var(--text-muted);font-size:0.75rem;text-align:center;padding:1rem;">${t('str.no_spots_msg')}</p>`;
        return;
    }

    container.innerHTML = spots.map(s => `
        <div class="spot-tile ${s.is_occupied ? 'occupied' : 'vacant'}" onclick="openEditSpotModal('${s.id}')" title="Click to edit ${s.label}">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.15rem;">
                <span class="spot-tile-id">${s.id}</span>
                <div>
                    <button class="spot-action-btn" onclick="event.stopPropagation(); openEditSpotModal('${s.id}')" title="Edit">✏️</button>
                    <button class="spot-action-btn" onclick="event.stopPropagation(); deleteSpot('${s.id}')" title="Delete" style="color:#ff6b8b;">✕</button>
                </div>
            </div>
            <div style="font-size:0.7rem;color:#cbd5e1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${s.label}</div>
            <div class="spot-tile-status">${s.is_occupied ? t('str.occupied') : t('str.vacant')}</div>
            ${s.is_occupied ? `<div class="spot-tile-time">#${s.vehicle_id || '?'} • ${formatSeconds(s.duration_seconds)}</div>` : ''}
        </div>
    `).join('');
}

function renderSpotManagerTable(spots) {
    const tbody = document.getElementById('managerTableBody');
    const countEl = document.getElementById('managerSpotCount');
    if (countEl) countEl.innerText = `${spots.length} ${t('str.bays_configured')}`;
    if (!tbody) return;

    if (spots.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:var(--text-muted);padding:2rem;">${t('str.no_spots_table')}</td></tr>`;
        return;
    }

    tbody.innerHTML = spots.map(s => `
        <tr>
            <td><strong style="color:var(--neon-cyan);">${s.id}</strong></td>
            <td><strong>${s.label}</strong></td>
            <td>${getSpotIcon(s.spot_type)}</td>
            <td>
                ${s.is_occupied 
                    ? `<span class="tag-badge tag-occupied">🔴 ${t('str.occupied')} (#${s.vehicle_id || '?'})</span>` 
                    : `<span class="tag-badge tag-completed">🟢 ${t('str.vacant')}</span>`}
            </td>
            <td style="text-align:right;">
                <button class="btn btn-glass btn-icon" onclick="openEditSpotModal('${s.id}')" title="Edit bay" style="font-size:0.75rem;padding:0.25rem 0.6rem;">
                    ✏️
                </button>
                <button class="btn btn-scarlet-outline btn-icon" onclick="deleteSpot('${s.id}')" title="Delete bay" style="font-size:0.75rem;padding:0.25rem 0.6rem;">
                    🗑️
                </button>
            </td>
        </tr>
    `).join('');
}

function openEditSpotModal(spotId) {
    const spot = currentSpots.find(s => s.id === spotId);
    if (!spot) return;

    document.getElementById('editSpotOldId').value = spot.id;
    document.getElementById('editSpotIdInput').value = spot.id;
    document.getElementById('editSpotLabelInput').value = spot.label;
    document.getElementById('editSpotTypeInput').value = spot.spot_type || 'car';

    openModal('editSpotModal');
}

async function saveEditedSpot() {
    const oldId = document.getElementById('editSpotOldId').value;
    const newId = document.getElementById('editSpotIdInput').value.trim();
    const label = document.getElementById('editSpotLabelInput').value.trim();
    const spotType = document.getElementById('editSpotTypeInput').value;

    if (!newId || !label) {
        alert(t('str.alert_fill_fields'));
        return;
    }

    try {
        const res = await fetch(`/api/spots/${encodeURIComponent(oldId)}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ new_id: newId, label, spot_type: spotType })
        });
        if (res.ok) {
            closeModal('editSpotModal');
            loadSpots();
        } else {
            alert(t('str.alert_save_error'));
        }
    } catch (e) {
        console.error(e);
        alert(t('str.alert_conn_error'));
    }
}

async function deleteSpot(id) {
    if (!confirm(t('str.confirm_del_spot', id))) return;
    try {
        await fetch(`/api/spots/${encodeURIComponent(id)}`, { method: 'DELETE' });
        loadSpots();
    } catch (e) {
        console.error(e);
    }
}

async function clearAllSpots() {
    if (!confirm(t('str.confirm_clear_all'))) return;
    try {
        await fetch('/api/spots/clear', { method: 'POST' });
        loadSpots();
    } catch (e) {
        console.error(e);
    }
}

async function loadPresetTemplate() {
    try {
        await fetch('/api/spots/presets', { method: 'POST' });
        loadSpots();
    } catch (e) {
        console.error(e);
    }
}

// ----------------- HARDWARE ACCELERATION -----------------
async function loadDeviceStatus() {
    try {
        const res = await fetch('/api/device');
        const data = await res.json();

        const select = document.getElementById('deviceSelect');
        select.innerHTML = data.options.map(opt => `
            <option value="${opt.id}" ${opt.active ? 'selected' : ''}>${opt.label}</option>
        `).join('');

        const badge = document.getElementById('deviceActiveBadge');
        if (badge) {
            badge.innerText = data.device_message || data.effective_mode;
            badge.title = data.device_message || '';
        }
    } catch (e) {
        console.error(e);
    }
}

async function changeDevice(mode) {
    try {
        await fetch('/api/device/select', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode })
        });
        loadDeviceStatus();
    } catch (e) {
        console.error(e);
    }
}

// ----------------- VIDEO SOURCES -----------------
async function loadSources() {
    try {
        const res = await fetch('/api/sources');
        const data = await res.json();

        const select = document.getElementById('sourceSelect');
        let optionsHtml = '';

        if (data.samples && data.samples.length > 0) {
            optionsHtml += `<optgroup label="${t('str.opt_parking_videos')}">`;
            data.samples.forEach(s => {
                const isPreferred = s.name.includes('camara_fija');
                optionsHtml += `<option value="sample:${s.name}" ${isPreferred ? 'selected' : ''}>📹 ${s.name}</option>`;
            });
            optionsHtml += '</optgroup>';
        }

        if (data.webcams && data.webcams.length > 0) {
            optionsHtml += `<optgroup label="${t('str.opt_webcams')}">`;
            data.webcams.forEach(c => {
                optionsHtml += `<option value="webcam:${c.id}">📷 ${c.name}</option>`;
            });
            optionsHtml += '</optgroup>';
        }

        optionsHtml += `<optgroup label="${t('str.opt_security_network')}"><option value="ip:custom">${t('str.opt_ip_custom')}</option></optgroup>`;
        select.innerHTML = optionsHtml;

        if (data.active) {
            videoNativeWidth = data.active.width || 1280;
            videoNativeHeight = data.active.height || 720;
        }
    } catch (e) {
        console.error(e);
    }
}

async function changeSource(val) {
    if (val === 'ip:custom') {
        openModal('ipModal');
        return;
    }

    const [type, value] = val.split(':');
    try {
        await fetch('/api/sources/select', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ source_type: type, source_value: value })
        });
        reloadVideoFeed();
    } catch (e) {
        console.error(e);
    }
}

async function connectIpCamera() {
    const url = document.getElementById('ipCameraUrl').value.trim();
    if (!url) {
        alert(t('str.alert_ip_url'));
        return;
    }

    try {
        const res = await fetch('/api/sources/select', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ source_type: 'ip', source_value: url })
        });
        if (res.ok) {
            closeModal('ipModal');
            reloadVideoFeed();
        } else {
            alert(t('str.alert_ip_failed'));
        }
    } catch (e) {
        console.error(e);
        alert(t('str.alert_conn_error'));
    }
}

async function uploadVideoFile(input) {
    if (!input.files || input.files.length === 0) return;
    const file = input.files[0];
    const formData = new FormData();
    formData.append('file', file);

    try {
        const res = await fetch('/api/sources/upload', {
            method: 'POST',
            body: formData
        });
        if (res.ok) {
            await loadSources();
            reloadVideoFeed();
        } else {
            alert(t('str.alert_upload_error'));
        }
    } catch (e) {
        console.error(e);
    }
}

function reloadVideoFeed() {
    const url = `/video_feed?t=${Date.now()}`;
    if (videoFeed) videoFeed.src = url;
    if (videoFeedEditor) videoFeedEditor.src = url;
}

// ----------------- LIVE METRICS POLLING -----------------
function startPollingStats() {
    setInterval(async () => {
        try {
            const res = await fetch('/api/stats/live');
            if (!res.ok) return;
            const data = await res.json();

            document.getElementById('kpiTotalSpots').innerText = data.total_spots ?? 0;
            document.getElementById('kpiOccupiedSpots').innerText = data.occupied_spots ?? 0;
            document.getElementById('kpiAvailableSpots').innerText = data.available_spots ?? 0;
            document.getElementById('kpiOccupancyRate').innerText = `${data.occupancy_rate ?? 0}%`;
            document.getElementById('kpiTotalVehicles').innerText = data.total_vehicles_seen ?? 0;
            document.getElementById('kpiAvgStay').innerText = data.avg_stay_formatted ?? '0m 00s';
            document.getElementById('liveFps').innerText = `${data.fps ?? 0} FPS`;

            const bar = document.getElementById('occupancyProgressBar');
            if (bar) bar.style.width = `${Math.min(data.occupancy_rate ?? 0, 100)}%`;

            renderParkedVehiclesTable(data.parked_vehicles || []);
            loadSpots();
        } catch (e) {
            // Ignore temporary network tick
        }
    }, 1000);
}

function renderParkedVehiclesTable(vehicles) {
    const tbody = document.getElementById('parkedVehiclesTableBody');
    if (!tbody) return;

    if (vehicles.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:var(--text-muted);padding:1.5rem;">${t('table.no_vehicles')}</td></tr>`;
        return;
    }

    tbody.innerHTML = vehicles.map(v => `
        <tr>
            <td><strong style="color:var(--neon-cyan);">${v.spot_label}</strong></td>
            <td><span class="tag-badge tag-occupied">#${v.vehicle_id}</span></td>
            <td>${v.vehicle_type}</td>
            <td style="color:#cbd5e1;">${v.entry_time}</td>
            <td style="font-family:monospace;font-weight:800;color:var(--neon-amber);">⏱️ ${v.duration_formatted}</td>
        </tr>
    `).join('');
}

// ----------------- REPORTS & HISTORICAL DATA -----------------
async function openReportsModal() {
    openModal('reportsModal');
    loadReportsData();
}

async function loadReportsData() {
    try {
        const sumRes = await fetch('/api/reports/summary');
        const summary = await sumRes.json();

        document.getElementById('repTotalHistorical').innerText = summary.total_historical_vehicles ?? 0;
        document.getElementById('repCompletedStays').innerText = summary.completed_stays ?? 0;
        document.getElementById('repAvgDuration').innerText = summary.avg_duration_formatted ?? '0s';
        document.getElementById('repBusiestHour').innerText = summary.busiest_hour ?? '--';

        const typeContainer = document.getElementById('repVehicleTypes');
        if (typeContainer && summary.vehicle_type_breakdown) {
            typeContainer.innerHTML = Object.entries(summary.vehicle_type_breakdown)
                .map(([type, count]) => `<span class="tag-badge tag-completed">${type}: <strong>${count}</strong></span>`)
                .join(' ');
        }

        const histRes = await fetch('/api/reports/history?limit=50');
        const sessions = await histRes.json();
        renderHistoryTable(sessions);
    } catch (e) {
        console.error(e);
    }
}

function renderHistoryTable(sessions) {
    const tbody = document.getElementById('historyTableBody');
    if (!tbody) return;

    if (sessions.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:var(--text-muted);padding:1.5rem;">${t('str.no_history_table')}</td></tr>`;
        return;
    }

    tbody.innerHTML = sessions.map(s => {
        const isAct = s.status === 'active';
        return `
            <tr>
                <td><strong style="color:var(--neon-cyan);">${s.spot_id}</strong></td>
                <td>#${s.vehicle_track_id}</td>
                <td>${s.vehicle_type}</td>
                <td>${s.entry_time.replace('T', ' ').slice(0, 19)}</td>
                <td>${s.exit_time ? s.exit_time.replace('T', ' ').slice(0, 19) : `<span style="color:var(--neon-amber);">${t('str.in_progress')}</span>`}</td>
                <td>${isAct ? `<span class="tag-badge tag-occupied">${t('str.parked_badge')}</span>` : `<span class="tag-badge tag-completed">${formatSeconds(s.duration_seconds)}</span>`}</td>
            </tr>
        `;
    }).join('');
}

function filterHistoryTable() {
    const query = document.getElementById('historySearchInput').value.toLowerCase();
    const rows = document.querySelectorAll('#historyTableBody tr');
    rows.forEach(row => {
        const text = row.innerText.toLowerCase();
        row.style.display = text.includes(query) ? '' : 'none';
    });
}

function downloadCsv() {
    window.location.href = '/api/reports/download-csv';
}

// ----------------- MODAL CONTROLS -----------------
function openModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.add('active');
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.remove('active');
}

function formatSeconds(sec) {
    if (!sec || sec < 0) return '00:00';
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    const h = Math.floor(m / 60);
    const remM = m % 60;
    if (h > 0) return `${h}h ${remM.toString().padStart(2, '0')}m`;
    return `${remM.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}
