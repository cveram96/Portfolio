# FASE APLICADA: A/B Testing con Datos Reales

**Archivo**: `experiments/02_retail_ab_test.ipynb`

**Objetivo**: Aplicar técnicas de FASE 1-3 a un dataset real de e-commerce para tomar decisiones de negocio.

---

## 📊 Dataset: Online Retail (UCI)

### Características
- **Tamaño**: 541,909 transacciones
- **Clientes**: 4,372 únicos
- **Productos**: 3,684
- **Período**: Enero 2010 - Diciembre 2011
- **Origen**: Tienda online del Reino Unido

### Estructura Original
```
InvoiceNo      | Quantity | UnitPrice | CustomerID | Country | Description | InvoiceDate
234001         | 6        | 2.55      | 17850      | United Kingdom | White Hanging Heart | 1/12/2010 08:26
234001         | 6        | 3.39      | 17850      | United Kingdom | White Metal Lantern  | 1/12/2010 08:26
...
```

**Importante**: Cada fila es una **compra de un producto**, no un cliente.
- Un cliente puede tener múltiples filas (múltiples compras)
- Un cliente puede tener múltiples filas en la misma factura (múltiples items)

---

## 🔧 Pipeline de Transformación

### PASO 1-2: Cargar y Limpiar
```
541,909 filas con posibles errores
    ↓
Eliminar clientes sin ID
    ↓
Eliminar Quantity ≤ 0 (cancelaciones)
    ↓
Eliminar UnitPrice ≤ 0 (errores)
    ↓
~500k filas válidas
```

### PASO 3: Agregar a Nivel de Usuario
```
~500k transacciones (línea en factura)
    ↓
Agrupar por CustomerID
    ↓
Calcular por usuario:
  - num_orders: Número de facturas únicas
  - total_items: Cantidad total de items comprados
  - total_spent: Gasto total en £
  - Country: País del cliente
    ↓
~4.3k clientes únicos
```

**Resultado**: Cada fila = 1 cliente con sus totales históricos

---

## 🎲 Experiment Design

### Variable 1: Conversion (Métrica)
```python
conversion = 1 si num_orders > 1 else 0
```
- **Significado**: ¿Es cliente repetidor (repeat customer)?
- **Por qué**: El objetivo del cambio UX/UI es motivar compras repetidas
- **Distribución**: ~%repetidores vs ~% one-time customers

### Variable 2: Treatment (Asignación)
```python
treatment = np.random.binomial(1, 0.5, n_clientes)
```
- **Significado**: ¿Ve el cliente el cambio UX/UI?
- **Treatment=0**: Control (versión original)
- **Treatment=1**: Tratamiento (nuevo cambio)
- **Ratio**: 50/50 split aleatorio
- **Seed**: 42 para reproducibilidad

---

## 📈 Análisis por Nivel

### PASO 5: Global
```
Control (n=~2,186 clientes)
├─ Repeat purchase rate: X%
└─ Promedio gasto: £Y

Treatment (n=~2,186 clientes)
├─ Repeat purchase rate: X+ε%  
└─ Promedio gasto: £Y+δ

Uplift: +ε% points (ε% relativo)
```

### PASO 6: Significancia (T-Test)
```
H0: No hay diferencia en repeat purchase rate
H1: Hay diferencia significativa

t-statistic: ...
p-value: ... 

Si p < 0.05 → Rechazo H0 (significativo ✓)
Si p ≥ 0.05 → Fallo en rechazar (no significativo ✗)
```

### PASO 7-8: Segmentación

#### Segmento 1: Value
```
High Value (gasto > mediana £X)
├─ Control repeat rate: A%
└─ Treatment repeat rate: B%
└─ Uplift: (B-A)%

Low Value (gasto ≤ mediana)
├─ Control repeat rate: C%
└─ Treatment repeat rate: D%
└─ Uplift: (D-C)%
```

#### Segmento 2: Geografía
```
United Kingdom    → Uplift = +X%
Netherlands       → Uplift = +Y%
Germany           → Uplift = +Z%
France            → Uplift = +W%
Sweden            → Uplift = +V%
Other             → Uplift = +U%
```

---

## 📊 Visualización (PASO 9)

### 3 Gráficos Principales

**Gráfico 1: Global**
- Barras: Control vs Treatment
- Métrica: Repeat purchase rate (%)
- Indicador: Uplift (+/-)

**Gráfico 2: Por Value Segment**  
- 2 grupos (Low / High)
- Cada grupo con Control vs Treatment
- Comparar uplift en cada segmento

**Gráfico 3: Por País**
- 6 barras por grupo (Top 5 + Other)
- Cada país con Control vs Treatment
- Identificar ganadores/perdedores geográficos

---

## 💡 Interpretación (PASO 10)

### 4 Preguntas Críticas

1. **¿Consistencia?**
   - ¿Todos los segmentos tienen mismo signo de uplift?
   - ¿O hay mix de + y -?

2. **¿Segmentos negativos?**
   - ¿Alguien empeora con el cambio?
   - ¿Cuánto es el daño?

3. **¿Oportunidades?**
   - ¿Quién se beneficia más?
   - ¿Hay low-hanging fruit?

4. **¿Riesgos?**
   - ¿Lanzar global causaría daño a algún segmento?
   - ¿Cuál es el costo?

---

## 🎯 Decisión de Negocio (PASO 11)

### 3 Opciones (Según Datos)

#### Opción A: LANZAR PARA TODOS ✅
**Condiciones**:
- Global uplift > 0 AND significativo
- Todos los segmentos positivos
- Ningún riesgo identificado

**Acción**:
```
→ Rollout 100% del cambio
→ Esperar mejora en repeat purchase rate
→ Monitorear en post-lanzamiento
```

#### Opción B: LANZAR SELECTIVAMENTE ⚠️
**Condiciones**:
- Global uplift > 0 pero inconsistente
- Algunos segmentos positivos, otros negativos

**Acción**:
```
→ Rollout solo para segmentos ganadores
→ Mantener versión original para otros
→ A/B test dentro de segmentos problemáticos
```

#### Opción C: NO LANZAR ❌
**Condiciones**:
- Global uplift < 0 Y significativo
- Mayoría de segmentos negativos

**Acción**:
```
→ Rechazar cambio
→ Design review (¿qué falló?)
→ Iterar y hacer nuevo test
```

---

## 📋 Estructura del Notebook

| Paso | Tipo | Contenido |
|------|------|----------|
| 1 | MD+Código | Cargar UCI dataset |
| 2 | MD+Código | Limpieza de datos |
| 3 | MD+Código | Agregación a usuario |
| 4 | MD+Código | Variables del experimento |
| 5 | MD+Código | Análisis global |
| 6 | MD+Código | T-test |
| 7 | MD+Código | Crear segmentos |
| 8 | MD+Código | Análisis por segmentos |
| 9 | MD+Código | 3 gráficos comparativos |
| 10 | MD+Código | Interpretación profunda |
| 11 | MD+Código | Decisión ejecutiva |

**Total células**: ~19 (Markdown + Code combinadas)

---

## 🔑 Habilidades Desarrolladas

### Data Engineering
- ✅ Descargar datasets públicos (UCI)
- ✅ Limpiar datos transaccionales reales
- ✅ Agregar a nivel de usuario
- ✅ Feature engineering (value_segment, country_segment)

### Statistical Analysis
- ✅ Aplicar t-test a datos reales
- ✅ Interpretar p-values en contexto
- ✅ Identificar significancia práctica vs estadística

### Business Analytics
- ✅ Segmentación estratégica
- ✅ Análisis de heterogeneidad de tratamiento
- ✅ Comunicación ejecutiva
- ✅ Toma de decisiones bajo incertidumbre

### Data Communication
- ✅ Visualización para no-técnicos
- ✅ Narrative en los datos
- ✅ Balancear rigor + claridad

---

## 📌 Insights Esperados

### Posibles Descubrimientos

**Escenario 1: El color del botón funciona** 
```
✓ Repeat rate +3% (global)
✓ Significativo (p=0.02)
✓ Consistente en todos los segmentos
→ Acción: Lanzar para todos
```

**Escenario 2: Funciona solo para clientes ricos**
```
⚠️ High-value +5% (significativo)
⚠️ Low-value -1% (no significativo)
⚠️ Global +2% (marginal)
→ Acción: Lanzar selectivamente para high-value
```

**Escenario 3: No funciona**
```
❌ Global -0.5% (no significativo)
❌ Estocasticidad alta
❌ No hay patrón claro
→ Acción: Recopilar más datos O iterar diseño
```

---

## 🚀 Próximos Pasos

Después de FASE APLICADA:

1. **FASE 4**: Power Analysis
   - ¿Cuántos clientes necesito para detectar efecto de 2%?
   - ¿Cuántos días debo ejecutar?

2. **FASE 5**: Multi-armed Bandits
   - ¿Y si tengo 5 variantes diferentes?
   - ¿Cómo asigno tráfico dinámicamente?

3. **FASE 6**: Heterogeneous Treatment Effects
   - ¿Puedo predecir quién va a responder mejor?
   - Machine learning + causal inference

4. **FASE 7**: Plataforma Interactiva
   - Dashboard en Streamlit
   - Upload tu dataset → Análisis automático

---

## 📚 Referencias

- **Dataset**: [UCI ML Repository - Online Retail](https://archive.ics.uci.edu/ml/datasets/Online+Retail)
- **Patrón de análisis**: Real A/B testing en industria
- **Técnicas**: T-test independiente, segmentación, comunicación ejecutiva
