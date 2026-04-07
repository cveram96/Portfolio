# Experimentation Platform 🧪

Un proyecto educativo y profesional enfocado en **A/B Testing** y experimentación digital. Construido desde cero para aprender y aplicar conceptos de ciencia de datos en decisiones empresariales.

---

## 📋 ¿Qué es este proyecto?

**Experimentation Platform** es una plataforma didáctica que enseña cómo diseñar, ejecutar y analizar A/B tests. Es ideal para:

- 📚 **Estudiantes de Data Science**: Aprender fundamentales de experimentación
- 💼 **Product Managers**: Entender estadística detrás de decisiones
- 📊 **Data Analysts**: Implementar tests en producción
- 🎯 **Cualquiera interesado en decisiones basadas en datos**

---

## 🎯 ¿Qué es un A/B Test?

Un **A/B test** es un experimento controlado donde:

1. **Se divide** la audiencia en dos grupos aleatoriamente
2. **Se muestra** la versión actual (Control) a un grupo y una variante (Tratamiento) al otro
3. **Se mide** una métrica (ej: tasa de conversión, tiempo en sitio, etc.)
4. **Se comparan** resultados para tomar decisiones basadas en datos

### Ejemplo Real:
Una tienda online quiere saber si cambiar el color del botón "Comprar" de azul a naranja aumenta las ventas.

- **Control (A)**: Botón azul → 10% de conversión
- **Tratamiento (B)**: Botón naranja → 12% de conversión
- **Conclusión**: El botón naranja es mejor (+20% de uplift)

---

## 📁 Estructura del Proyecto

```
experimentation-platform/
├── data/                          # Almacenamiento de datasets
│   └── [datasets sintéticos y reales]
├── src/                           # Código reutilizable
│   └── [módulos y utilidades]
├── experiments/                   # Notebooks de experimentos
│   ├── 01_synthetic.ipynb         # ← FASE TEÓRICA: Datos Sintéticos (1-3) ✓
│   ├── 02_retail_ab_test.ipynb    # ← FASE APLICADA: Datos Reales (UCI) 🆕
│   └── ...
├── app/                           # Aplicación web (Streamlit)
│   └── [código de interfaz]
└── README.md                      # Este archivo
```

---

## ✅ FASE 1 + FASE 2 + FASE 3: Fundamentos, Validación y CUPED (COMPLETADAS)

### 📌 Archivo: `experiments/01_synthetic.ipynb`

En este notebook, construimos los **fundamentos del A/B testing** (FASE 1) y su **validación estadística** (FASE 2):

#### **Paso 1: Importar Librerías**
- pandas → Manipulación de datos
- numpy → Operaciones numéricas
- matplotlib → Visualizaciones

#### **Paso 2: Crear Dataset Sintético**
- Generamos 10,000 usuarios
- Asignación aleatoria: 50% control, 50% tratamiento
- Conversiones basadas en distribución binomial
- **Probabilidades usadas** (personalizables):
  - Control: 10% de conversión
  - Tratamiento: 12% de conversión

#### **Paso 3: Función `run_ab_test()`**
Implementamos una función que calcula:
- **Conversion Rate**: Porcentaje de usuarios que convirtieron
- **Uplift**: Cambio relativo en la métrica
- Estadísticas descriptivas por grupo

#### **Paso 4: Ejecutar Experimento**
Ejecutamos el análisis y mostramos:
- Conversiones por grupo
- Tasas de conversión
- Uplift porcentual

#### **Paso 5: Visualización**
Creamos un gráfico de barras que compara control vs tratamiento de forma clara.

#### **Paso 6: Explicar el Problema** (FASE 2)
¿Por qué el uplift no es suficiente? Introducir concepto de "ruido vs efecto real".

#### **Paso 7: Importar scipy.stats** (FASE 2)
Importar la librería de estadística avanzada para pruebas de hipótesis.

#### **Paso 8: Implementar T-Test** (FASE 2)
Crear función `perform_t_test()` que ejecute la prueba estadística.
- Explica qué hace t-test
- Define p-value
- Enseña cómo interpretar resultados

#### **Paso 9: Aplicar el Test** (FASE 2)
Ejecutar la función con los datos del control y tratamiento.
- Mostrar estadístico t
- Mostrar p-value
- Dar interpretación inicial

#### **Paso 10: Interpretación de Resultados** (FASE 2)
Explicar la regla de oro: p < 0.05 = significativo.
- Error Tipo I (falso positivo)
- Error Tipo II (falso negativo)
- Cómo comunicar resultados

#### **Paso 11: Reporte Completo** (FASE 2)
Combinar todas las métricas en un reporte profesional:
- Conversion rates
- Uplift
- P-value
- Conclusión clara (¿Lanzar o no lanzar?)

#### **Paso 12: Visualización Mejorada** (FASE 2)
Gráfico con intervalos de confianza del 95%.
- Mostrar barras con error bars
- Indicador visual de significancia
- Comunicar incertidumbre

#### **Paso 13: Explicación Conceptual CUPED** (FASE 3)
Introducción a la reducción de varianza.
- ¿Qué problema resuelve CUPED?
- Ruido vs efecto real
- Intuición detrás del algoritmo

#### **Paso 14: Variable Pre-Experimento** (FASE 3)
Crear covariable para CUPED.
- Simular comportamiento histórico del usuario
- Crear correlación entre pre y post

#### **Paso 15: Implementar CUPED** (FASE 3)
Función para ajustar la métrica.
- Explicar θ (theta)
- Mostrar la matemática en 3 pasos
- Implementar `apply_cuped()`

#### **Paso 16: Aplicar CUPED** (FASE 3)
Ejecutar el ajuste.
- Calcular θ
- Crear métrica ajustada
- Mostrar reducción de varianza

#### **Paso 17: Repetir A/B Test** (FASE 3)
Análisis con métrica ajustada.
- Ejecutar t-test con datos CUPED
- Comparar p-values y t-statistics

#### **Paso 18: Comparación Antes vs Después** (FASE 3)
Tabla de comparativas.
- Mostrar cambios en todas las métricas
- Visualizar el impacto de CUPED

#### **Paso 19: Visualización del Impacto** (FASE 3)
Gráficos para mostrar mejoras.
- P-value reduction
- T-statistic improvement
- Varianza reducida
- Distribuciones antes/después

#### **Paso 20: Interpretación Profunda** (FASE 3)
Análisis completo de CUPED.
- ¿Cambió la decisión?
- ¿Es más confiable?
- Responder preguntas críticas
- Recomendaciones finales

### 📊 Resultados Esperados

| Métrica | Resultado |
|---------|-----------|
| Usuarios Control | ~5,000 |
| Usuarios Tratamiento | ~5,000 |
| Conversion Rate (Control) | ~10% |
| Conversion Rate (Tratamiento) | ~12% |
| Uplift | +20% |

---

## 🔬 FASE APLICADA: A/B Testing con Datos Reales 🆕

### 📌 Archivo: `experiments/02_retail_ab_test.ipynb`

Este notebook lleva todo lo aprendido en FASE 1-3 y lo **aplica a un dataset real de e-commerce**.

**Pregunta de Negocio:**
> "¿Debemos lanzar un cambio UX/UI que podría aumentar la tasa de compra repetida? ¿Para todos los clientes o solo para algunos?"

#### **Dataset: Online Retail (UCI Machine Learning Repository)**

Datos reales de una tienda online del Reino Unido:
- 📊 541,909 transacciones
- 👥 4,372 clientes únicos  
- 🛍️ 3,684 productos
- 📅 Período: Enero 2010 - Diciembre 2011

#### **Paso 1: Cargar Dataset**
- Usar librería `ucimlrepo` para descargar datos del UCI
- Entender estructura transaccional
- Visualizar primeras filas

#### **Paso 2: Limpieza de Datos**
- Eliminar clientes sin ID
- Remover cantidades ≤ 0
- Eliminar precios inválidos
- De ~542k filas → filas válidas

#### **Paso 3: Crear Dataset por Usuario**
- Transformar de vista transaccional a vista de usuario
- Agregar: número de órdenes, items totales, gasto total, país
- De ~542k filas → ~4.3k clientes únicos

#### **Paso 4: Crear Variables del Experimento**
- **Conversion**: ¿Cliente ha comprado más de una vez?
- **Treatment**: Asignación aleatoria 50/50 para A/B test

#### **Paso 5: Análisis Global**
- Función `run_ab_test()` reutilizable
- Comparar repeat purchase rate
- Control vs Tratamiento

#### **Paso 6: Validación Estadística**
- T-test independiente
- P-value
- ¿Es significativo?

#### **Paso 7: Crear Segmentos**
- **Value Segment**: High-value (gasto > mediana) vs Low-value
- **Country Segment**: Top 5 países vs Otros

#### **Paso 8: Análisis por Segmentos**
- CRITICAL: Buscar efectos heterogéneos
- ¿Funciona igual para todos?
- ¿Hay segmentos negativos?

#### **Paso 9: Visualización Profesional**
- 3 gráficos de barras comparativas
- Global, Value Segment, Country
- Formato presentación ejecutiva

#### **Paso 10: Interpretación Profunda**
- ¿Consistencia del efecto?
- ¿Segmentos en riesgo?
- ¿Oportunidades principales?

#### **Paso 11: Decisión de Negocio**
**3 recomendaciones posibles:**
1. ✅ **Lanzar para todos** - Si efecto positivo y significativo
2. ⚠️ **Lanzar selectivamente** - Si efecto mixto
3. ❌ **No lanzar** - Si efecto negativo y significativo

### 💡 Habilidades Desarrolladas

✅ **Data Pipeline Real**: De datos transaccionales a métricas de usuario
✅ **Segmentación Estratégica**: Encontrar heterogeneidad de tratamiento  
✅ **Comunicación Ejecutiva**: De números a recomendaciones
✅ **Decisiones Basadas en Datos**: Rigor + Contexto de negocio

---

## 🚀 Conceptos Aprendidos en FASE 1 + FASE 2 + FASE 3

**FASE 1:**
- ✅ **A/B Testing**: Concepto y estructura básica
- ✅ **Distribución Binomial**: Por qué los datos de conversión la siguen
- ✅ **Conversion Rate**: Cálculo e interpretación
- ✅ **Uplift**: Métrica de cambio relativo
- ✅ **Análisis Comparativo**: Cómo interpretar resultados
- ✅ **Visualización**: Comunicar datos gráficamente

**FASE 2:**
- ✅ **T-Test**: Prueba estadística para validar diferencias
- ✅ **P-Value**: Probabilidad de obtener resultados por azar
- ✅ **Significancia Estadística**: Criterio α = 0.05
- ✅ **Error Tipo I y II**: Falsos positivos y negativos
- ✅ **Intervalos de Confianza**: Rangos de confianza del 95%
- ✅ **Decisiones Profesionales**: Reporte completo y conclusiones

**FASE 3 (NUEVO):**
- ✅ **Varianza**: Ruido en los experimentos
- ✅ **Covariable**: Información pre-experimento
- ✅ **CUPED**: COVariate Usage Personal Experiment Design
- ✅ **θ (Theta)**: Parámetro de ajuste
- ✅ **Reducción de Varianza**: 30-50% menos ruido
- ✅ **Poder Estadístico**: Detectar efectos más débiles
- ✅ **Métrica Ajustada**: Análisis post-CUPED

**FASE APLICADA:**
- ✅ **Datos Reales**: Trabajar con datasets públicos (UCI)
- ✅ **Limpieza**: Manejar datos sucios del mundo real
- ✅ **Transformación**: De transaccional a agregado de usuario
- ✅ **Segmentación Estratégica**: Value y geografía
- ✅ **Heterogeneidad**: Encontrar quién se beneficia realmente
- ✅ **Comunicación Ejecutiva**: De análisis a decisión

---

## ✅ FASE 1 + FASE 2 + FASE 3: Fundamentos, Validación y CUPED (COMPLETADAS)

### 📌 Archivo: `experiments/01_synthetic.ipynb`

En este notebook, construimos los **fundamentos del A/B testing** (FASE 1) y su **validación estadística** (FASE 2):

#### **Paso 1: Importar Librerías**
- pandas → Manipulación de datos
- numpy → Operaciones numéricas
- matplotlib → Visualizaciones

#### **Paso 2: Crear Dataset Sintético**
- Generamos 10,000 usuarios
- Asignación aleatoria: 50% control, 50% tratamiento
- Conversiones basadas en distribución binomial
- **Probabilidades usadas** (personalizables):
  - Control: 10% de conversión
  - Tratamiento: 12% de conversión

#### **Paso 3: Función `run_ab_test()`**
Implementamos una función que calcula:
- **Conversion Rate**: Porcentaje de usuarios que convirtieron
- **Uplift**: Cambio relativo en la métrica
- Estadísticas descriptivas por grupo

#### **Paso 4: Ejecutar Experimento**
Ejecutamos el análisis y mostramos:
- Conversiones por grupo
- Tasas de conversión
- Uplift porcentual

#### **Paso 5: Visualización**
Creamos un gráfico de barras que compara control vs tratamiento de forma clara.

#### **Paso 6: Explicar el Problema** (FASE 2)
¿Por qué el uplift no es suficiente? Introducir concepto de "ruido vs efecto real".

#### **Paso 7: Importar scipy.stats** (FASE 2)
Importar la librería de estadística avanzada para pruebas de hipótesis.

#### **Paso 8: Implementar T-Test** (FASE 2)
Crear función `perform_t_test()` que ejecute la prueba estadística.
- Explica qué hace t-test
- Define p-value
- Enseña cómo interpretar resultados

#### **Paso 9: Aplicar el Test** (FASE 2)
Ejecutar la función con los datos del control y tratamiento.
- Mostrar estadístico t
- Mostrar p-value
- Dar interpretación inicial

#### **Paso 10: Interpretación de Resultados** (FASE 2)
Explicar la regla de oro: p < 0.05 = significativo.
- Error Tipo I (falso positivo)
- Error Tipo II (falso negativo)
- Cómo comunicar resultados

#### **Paso 11: Reporte Completo** (FASE 2)
Combinar todas las métricas en un reporte profesional:
- Conversion rates
- Uplift
- P-value
- Conclusión clara (¿Lanzar o no lanzar?)

#### **Paso 12: Visualización Mejorada** (FASE 2)
Gráfico con intervalos de confianza del 95%.
- Mostrar barras con error bars
- Indicador visual de significancia
- Comunicar incertidumbre

#### **Paso 13: Explicación Conceptual CUPED** (FASE 3)
Introducción a la reducción de varianza.
- ¿Qué problema resuelve CUPED?
- Ruido vs efecto real
- Intuición detrás del algoritmo

#### **Paso 14: Variable Pre-Experimento** (FASE 3)
Crear covariable para CUPED.
- Simular comportamiento histórico del usuario
- Crear correlación entre pre y post

#### **Paso 15: Implementar CUPED** (FASE 3)
Función para ajustar la métrica.
- Explicar θ (theta)
- Mostrar la matemática en 3 pasos
- Implementar `apply_cuped()`

#### **Paso 16: Aplicar CUPED** (FASE 3)
Ejecutar el ajuste.
- Calcular θ
- Crear métrica ajustada
- Mostrar reducción de varianza

#### **Paso 17: Repetir A/B Test** (FASE 3)
Análisis con métrica ajustada.
- Ejecutar t-test con datos CUPED
- Comparar p-values y t-statistics

#### **Paso 18: Comparación Antes vs Después** (FASE 3)
Tabla de comparativas.
- Mostrar cambios en todas las métricas
- Visualizar el impacto de CUPED

#### **Paso 19: Visualización del Impacto** (FASE 3)
Gráficos para mostrar mejoras.
- P-value reduction
- T-statistic improvement
- Varianza reducida
- Distribuciones antes/después

#### **Paso 20: Interpretación Profunda** (FASE 3)
Análisis completo de CUPED.
- ¿Cambió la decisión?
- ¿Es más confiable?
- Responder preguntas críticas
- Recomendaciones finales

### 📊 Resultados Esperados

| Métrica | Resultado |
|---------|-----------|
| Usuarios Control | ~5,000 |
| Usuarios Tratamiento | ~5,000 |
| Conversion Rate (Control) | ~10% |
| Conversion Rate (Tratamiento) | ~12% |
| Uplift | +20% |

---

## 🚀 Conceptos Aprendidos en FASE 1 + FASE 2 + FASE 3

**FASE 1:**
- ✅ **A/B Testing**: Concepto y estructura básica
- ✅ **Distribución Binomial**: Por qué los datos de conversión la siguen
- ✅ **Conversion Rate**: Cálculo e interpretación
- ✅ **Uplift**: Métrica de cambio relativo
- ✅ **Análisis Comparativo**: Cómo interpretar resultados
- ✅ **Visualización**: Comunicar datos gráficamente

**FASE 2:**
- ✅ **T-Test**: Prueba estadística para validar diferencias
- ✅ **P-Value**: Probabilidad de obtener resultados por azar
- ✅ **Significancia Estadística**: Criterio α = 0.05
- ✅ **Error Tipo I y II**: Falsos positivos y negativos
- ✅ **Intervalos de Confianza**: Rangos de confianza del 95%
- ✅ **Decisiones Profesionales**: Reporte completo y conclusiones

**FASE 3 (NUEVO):**
- ✅ **Varianza**: Ruido en los experimentos
- ✅ **Covariable**: Información pre-experimento
- ✅ **CUPED**: COVariate Usage Personal Experiment Design
- ✅ **θ (Theta)**: Parámetro de ajuste
- ✅ **Reducción de Varianza**: 30-50% menos ruido
- ✅ **Poder Estadístico**: Detectar efectos más débiles
- ✅ **Métrica Ajustada**: Análisis post-CUPED

---

## 🔜 Próximas Fases (Roadmap)

### **FASE 2: Análisis Estadístico** ✅ **COMPLETADA**
- ✅ Prueba t-test
- ✅ P-values
- ✅ Intervalos de confianza
- ✅ Concepto de significancia estadística
- ✅ Error Tipo I y Error Tipo II
- ✅ Determinar si los resultados son reales o por azar

### **FASE 3: Reducción de Varianza (CUPED)** ✅ **COMPLETADA**
- ✅ Concepto de varianza y ruido
- ✅ Variable pre-experimento (covariable)
- ✅ Función CUPED (reducción matemática)
- ✅ Comparación antes/después
- ✅ Visualización del impacto
- ✅ Interpretación de θ y mejora de precisión

### **FASE 3: Diseño de Experimentos** 🎲
- ✓ Cálculo de poder estadístico
- ✓ Tamaño de muestra requerido
- ✓ Duración del experimento
- ✓ Múltiples comparaciones (problema de FWER)

### **FASE 4: A/B Testing Avanzado** 🔬
- ✓ Multi-armed Bandits
- ✓ A/B/n testing (3+ variantes)
- ✓ Análisis de heterogeneidad de tratamiento
- ✓ Causal Inference aplicado

### **FASE 5: Plataforma Interactiva** 🌐
- ✓ Dashboard en Streamlit
- ✓ Carga de datos propios
- ✓ Análisis en tiempo real
- ✓ Generador de reportes
- ✓ API para integración con herramientas

---

## 🛠️ Cómo Ejecutar FASE 1

### Requisitos Previos
```bash
pip install pandas numpy matplotlib jupyter
```

### Pasos
1. Navega a la carpeta del proyecto:
   ```bash
   cd experimentation-platform
   ```

2. Abre Jupyter Notebook:
   ```bash
   jupyter notebook
   ```

3. Abre `experiments/01_synthetic.ipynb`

4. Ejecuta las celdas en orden (de arriba a abajo)

5. Lee las explicaciones en celdas Markdown

6. Observa los gráficos y resultados

---

## 💡 Puntos Clave de Aprendizaje

### ¿Por qué importa este proyecto?

1. **Decisiones basadas en datos**: No adivines, prueba y mide
2. **ROI**: Los A/B tests evitan desperdiciar dinero en cambios inútiles
3. **Escalabilidad**: Las técnicas aprendidas aplican desde startups hasta Fortune 500
4. **Carrera profesional**: Experimentation es una habilidad muy demandada

### Errores Comunes que Evitamos

❌ **No hacer A/B tests**: Cambios sin datos = pérdida de dinero
❌ **Tamaño de muestra muy pequeño**: Resultados no confiables
❌ **Duración incorrecta**: Detener experimento demasiado pronto
❌ **Múltiples comparaciones**: Aumenta falsos positivos
❌ **No documentar**: Perder conocimiento valioso

---

## 📚 Referencias y Recursos

### Libros Recomendados
- "Trustworthy Online Controlled Experiments" - Van der Lans & Kohavi
- "A/B Testing: The Most Powerful Way to Turn Clicks Into Customers" - Hansen & Thomke

### Cursos Relacionados
- Coursera: "A/B Testing"
- Udacity: "Product Analytics"

### Herramientas Profesionales
- Google Optimize
- Optimizely
- VWO (Visual Website Optimizer)

---

## 🤝 Contribuciones

Este es un proyecto educativo. Si encuentras errores o tienes sugerencias para mejorar las explicaciones, ¡siéntete libre de sugerir cambios!

---

## 📝 Licencia

Este proyecto es de **código abierto** y está disponible para uso educativo.

---

## 📞 Contacto

**Proyecto creado como parte de: Experimentation Platform**
- Objetivo: Enseñanza de A/B Testing desde cero
- Nivel: Principiante a Intermedio
- Duración esperada: 1-2 horas por fase

---

## 🎓 Hoja de Ruta Sugerida

**Semana 1**: Completar FASE 1 (este notebook)
**Semana 2**: Completar FASE 2 (análisis estadístico)
**Semana 3**: Completar FASE 3 (diseño de experimentos)
**Semana 4**: Completar FASE 4 (técnicas avanzadas)
**Semana 5**: Completar FASE 5 (plataforma interactiva)

---

**Última actualización**: Abril 2026
**Estado**: FASE 1 ✓ Completada | FASE 2 ✓ Completada | FASE 3 ✓ Completada

¡Buena suerte en tu viaje por el mundo del A/B Testing! 🚀
