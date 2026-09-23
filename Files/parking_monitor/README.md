# 🅿️ Smart Parking Monitor | Visión Artificial e Inteligencia Artificial

Sistema inteligente de visión por computador y analítica de estacionamientos en tiempo real. Permite crear y administrar plazas de parqueo interactivamente sobre el video (con corrección de perspectiva por 4 esquinas o rectángulos rápidos), trackear vehículos (autos, motos, camiones, buses), registrar tiempos exactos de ingreso y permanencia, conectar múltiples fuentes (videos locales, webcams con nombres reales, cámaras IP RTSP) y exportar reportes detallados en CSV/Excel.

Optimizado con aceleración multi-hardware para **GPU AMD (Radeon RX 6700 XT vía Microsoft DirectML)**, **GPU NVIDIA (CUDA)** y **CPU**.

---

## 🌟 Características Principales

1. **Gestión Interactiva de Plazas de Parqueo (Spots)**:
   - **Modo 4 Esquinas / Perspectiva**: Permite trazar cajones de estacionamiento en cámaras con ángulo inclinado marcando 4 puntos en el video.
   - **Modo Rectángulo Rápido**: Trazado instantáneo para cámaras cenitales o planos rectos.
   - **Plantilla Rápida de Ejemplo**: Crea 6 plazas instantáneamente para pruebas con un solo clic.
   - **Persistencia Total**: Plazas guardadas en SQLite y JSON; no se pierden al reiniciar.
   - **Indicadores en Vivo sobre el Video**:
     - 🟢 **Verde**: Plaza Libre / Disponible.
     - 🔴 **Rojo**: Plaza Ocupada, mostrando `#ID del Vehículo` y cronómetro de permanencia en tiempo real (`P-01 [#4] 14m 20s`).

2. **Detección y Tracking de Vehículos (YOLOv8 + ByteTrack)**:
   - Identificación de clases vehiculares: automóvil, motocicleta, camión y autobús.
   - Identificador único (`#1`, `#2`, etc.) persistente mediante filtro de Kalman y concordancia IoU.
   - Asignación inteligente a plazas mediante solapamiento geométrico poligonal (Shapely).
   - Filtro de histéresis anti-falsos positivos: evita que autos en movimiento por el pasillo marquen una plaza como ocupada por error.

3. **Métricas Temporales y Cronómetro en Tiempo Real**:
   - Registro exacto de fecha y hora de ingreso a la plaza.
   - Cronómetro activo segundo a segundo para cada vehículo estacionado.
   - Registro de hora de salida y duración total de la estancia.

4. **Multi-Fuente de Video**:
   - **Videos locales / muestras**: Clips incluidos en la carpeta `samples/` que se reproducen en bucle continuo.
   - **Subida de videos**: Sube tus propios archivos de video directamente desde la interfaz web.
   - **Cámaras Web Locales**: Detección y listado de los nombres oficiales de los dispositivos en Windows (DirectShow).
   - **Cámaras IP / RTSP / HTTP**: Conexión a cámaras de seguridad IP en red local o remota (Hikvision, Dahua, Tapo, Axis, etc.).

5. **Optimización Multi-Hardware**:
   - **GPU AMD Radeon** (ej. RX 6700 XT): Inferencia acelerada mediante ONNX Runtime con Microsoft DirectML (DirectX 12).
   - **GPU NVIDIA**: Inferencia mediante PyTorch con CUDA.
   - **CPU**: Inferencia multi-hilo con optimizaciones vectoriales.
   - Selector en caliente en el panel superior para alternar motores y ver FPS en tiempo real.

6. **Reportes y Analítica Exportable**:
   - **Exportación en CSV / Excel**: Descarga de reportes detallados con ID de sesión, plaza, ID de vehículo, tipo, fecha/hora de ingreso, fecha/hora de salida y tiempo de permanencia.
   - Métricas ejecutivas: tasa de ocupación actual (%), rotación de vehículos, tiempo promedio de estacionamiento y hora pico.
   - Buscador y filtro en vivo dentro de la plataforma.

---

## 🚀 Inicio Rápido

### Opción 1: Con un solo clic (Recomendado)
Haz doble clic sobre el archivo **`iniciar.bat`**.
Liberará automáticamente el puerto 8000, iniciará el servidor de visión y **abrirá tu navegador en `http://localhost:8000`**.

### Opción 2: Con PowerShell
```powershell
.\iniciar.ps1
```

### Opción 3: Manual desde la terminal
```bash
.venv\Scripts\python.exe run.py
```

---

## 📐 Cómo Dibujar y Configurar Plazas

1. En la barra superior, pulsa **"➕ Crear Plaza (4 Puntos)"**.
2. Haz 4 clics sobre el video en las esquinas de la plaza de parqueo siguiendo la perspectiva del cajón.
3. Se abrirá una ventana para ingresar el identificador (ej: `P-01`, `A-10`), el nombre visible y el tipo de vehículo permitido (Auto, Moto, etc.).
4. Pulsa **"Guardar Plaza"**. ¡Listo! El sistema comenzará a monitorear esa plaza inmediatamente.
5. También puedes pulsar **"📐 Plantilla Rápida"** para cargar 6 plazas preconfiguradas sobre el video de prueba.

---

## 📊 Descarga de Reportes

1. Pulsa el botón verde **"📊 Reportes"** en la barra superior.
2. Consulta el resumen de vehículos totales, horas pico y permanencia promedio.
3. Haz clic en **"📥 Descargar Reporte en CSV"** para abrirlo en Microsoft Excel, Power BI o Google Sheets.
