# Christian David Vera Mendivelso
### Data Scientist | Data Analytics | Business Intelligence
**M.Sc. in Data Science (Pontificia Universidad Javeriana) | Business Administration (Universidad Nacional de Colombia)**  
*Bogota, Colombia*

<p align="center">
  <img src="Files/images/portfolio_og_preview.png" alt="Christian David Vera | Data Science & Machine Learning Portfolio" width="100%" style="border-radius: 12px; box-shadow: 0 8px 30px rgba(0,0,0,0.5);">
</p>

[![Portfolio Website](https://img.shields.io/badge/Live_Portfolio-GitHub_Pages-4361EE?style=for-the-badge)](https://cveram96.github.io/Portfolio/)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/christianveram/)
[![Email](https://img.shields.io/badge/Email-verachristian4%40gmail.com-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:verachristian4@gmail.com)
[![WhatsApp](https://img.shields.io/badge/WhatsApp-%2B57_321_379_7876-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)](https://wa.me/573213797876)

---

### Tech Stack & Core Competencies

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-4479A1?style=flat-square&logo=postgresql&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Power BI](https://img.shields.io/badge/Power_BI-F2C811?style=flat-square&logo=powerbi&logoColor=black)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)
![YOLOv8](https://img.shields.io/badge/YOLOv8_Computer_Vision-00FFFF?style=flat-square&logo=yolo&logoColor=black)
![DirectML](https://img.shields.io/badge/DirectML_AMD_GPU-0078D4?style=flat-square&logo=windows&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=flat-square&logo=opencv&logoColor=white)
![Scikit--Learn](https://img.shields.io/badge/Scikit--Learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=flat-square&logo=git&logoColor=white)

---

## About Me

Data Scientist with a background in Business Administration and Data Science, focused on Python, SQL, Machine Learning, experimentation, and Business Intelligence. I build data-driven solutions that connect analytical methods with business problems.

Explore the live interactive portfolio at **[cveram96.github.io/Portfolio](https://cveram96.github.io/Portfolio/)**

<details>
<summary><strong>🇪🇸 Ver perfil en Español</strong></summary>
<br>

Data Scientist con formación en Administración de Empresas y Ciencia de Datos, enfocado en Python, SQL, Machine Learning, experimentación y Business Intelligence. Construyo soluciones analíticas orientadas a conectar métodos cuantitativos con problemas de negocio.
</details>

---

## Featured Projects (Data Science & Machine Learning)

### 1. [ParkVision AI — Smart Parking Monitoring System](https://cveram96.github.io/Portfolio/parkvision.html)
- **Problem:** Manual parking occupancy monitoring is inefficient, costly, and causes urban traffic congestion. Physical ground sensors require expensive installation and maintenance.
- **Data:** Real-time video streams (networked RTSP IP cameras, USB webcams, and video recordings).
- **Method:** End-to-end computer vision pipeline combining Ultralytics YOLOv8 for vehicle detection, ByteTrack for spatial tracking, vector polygon intersection algorithms (Point-in-Polygon & IoU) for bay occupancy, and a FastAPI + WebSockets server with DirectML/CUDA GPU acceleration.
- **Result:** Sub-second real-time occupancy detection, automated Available/Occupied state machine, and persistent historical logging in SQLite (`parking.db`).
- **Code:** [GitHub Code (Files/parking_monitor)](https://github.com/cveram96/Portfolio/tree/main/Files/parking_monitor) | [Interactive Project Page](https://cveram96.github.io/Portfolio/parkvision.html)

<details>
<summary><strong>🇪🇸 Ver resumen en Español</strong></summary>

- **Problema:** Monitoreo manual de ocupación de parqueaderos ineficiente y costoso; los sensores físicos en suelo tienen altos costos de instalación y mantenimiento.
- **Datos:** Video streams en tiempo real (cámaras IP / RTSP, webcams USB y grabaciones de video).
- **Método:** Pipeline end-to-end de visión por computador con Ultralytics YOLOv8 para detección vehicular, ByteTrack para seguimiento espacial, polígonos de intersección (Point-in-Polygon & IoU) y servidor FastAPI con WebSockets acelerado por DirectML / CUDA.
- **Resultado:** Detección de ocupación en tiempo real con latencia subsegundo, máquina de estados Disponible/Ocupado y analítica persistente en SQLite (`parking.db`).
- **Código:** [Repositorio GitHub](https://github.com/cveram96/Portfolio/tree/main/Files/parking_monitor) | [Página Interactiva](https://cveram96.github.io/Portfolio/parkvision.html)
</details>

---

### 2. [A/B Testing & Experimental Design (CUPED)](https://cveram96.github.io/Portfolio/ab_testing.html)
- **Problem:** Product teams risk deploying unvalidated UI changes that could harm conversion rates, often relying on noisy metrics or underpowered experiments.
- **Data:** E-commerce landing page experiment dataset from Udacity (290,584 unique users).
- **Method:** Experimental quality gates (I.I.D. deduplication), Chi-Square ($\chi^2$) Sample Ratio Mismatch (SRM) test, two-sample Z-test hypothesis testing, power sizing (MDE), and CUPED variance reduction using pre-experiment covariates.
- **Result:** Achieved **-42.8% metric variance reduction**, **-24.4% narrower 95% Confidence Interval** for Average Treatment Effect (ATE), and **-42.7% sample size reduction** to reach 80% power. Executive decision: validated NO-GO verdict ($Z = -1.31, p = 0.1899$), protecting the business against an estimated loss under an illustrative commercial scenario.
- **Code:** [Python Codebase](https://github.com/cveram96/Portfolio/tree/main/experimentation-platform/experiments) | [Case Study & Methodology](https://cveram96.github.io/Portfolio/ab_testing.html)

<details>
<summary><strong>🇪🇸 Ver resumen en Español</strong></summary>

- **Problema:** Riesgo financiero y de producto al desplegar cambios de interfaz no validados o basados en experimentos con métricas ruidosas y bajo poder estadístico.
- **Datos:** Dataset real de experimento de landing page de comercio electrónico de Udacity (290.584 usuarios únicos).
- **Método:** Filtros de calidad experimental (deduplicación I.I.D.), prueba de Sample Ratio Mismatch (SRM) con Chi-cuadrado ($\chi^2$), prueba Z de dos proporciones, dimensionamiento de potencia (MDE) y reducción de varianza mediante CUPED usando covariables previas.
- **Resultado:** Reducción de varianza métrica de **-42,8%**, intervalo de confianza al 95% un **-24,4% más estrecho** para el efecto de tratamiento (ATE) y reducción del tamaño de muestra requerido en **-42,7%** para 80% de potencia. Decisión ejecutiva: veredicto NO-GO ($Z = -1,31, p = 0,1899$), protegiendo al negocio en un escenario ilustrativo.
- **Código:** [Código en Python](https://github.com/cveram96/Portfolio/tree/main/experimentation-platform/experiments) | [Documentación del Experimento](https://cveram96.github.io/Portfolio/ab_testing.html)
</details>

---

### 3. [Customer Churn & Retention Economics](https://cveram96.github.io/Portfolio/churn.html)
- **Problem:** High customer attrition in telecommunications, where acquiring a new customer costs 5-7x more than retaining an existing one.
- **Data:** Telco Customer Churn dataset (7,043 customer accounts, 21 demographic, service, and contract attributes).
- **Method:** Supervised classification comparing Random Forest and Multi-Layer Perceptrons (MLP) with class rebalancing (SMOTE, SMOTEENN, ADASYN, RandomUnderSampler), RandomizedSearchCV hyperparameter tuning with stratified CV, and SHAP feature importance explainability.
- **Result:** Champion Random Forest + SMOTEENN model achieved **77.7% Recall** and **0.633 F1-score**, maximizing the capture of at-risk subscribers. Decision thresholds calibrated within an illustrative retention prioritization scenario.
- **Code:** [Jupyter Notebook](https://github.com/cveram96/Portfolio/blob/main/Files/Proyecto%20Churn.ipynb) | [Detailed Analysis & ROC Curves](https://cveram96.github.io/Portfolio/churn.html)

<details>
<summary><strong>🇪🇸 Ver resumen en Español</strong></summary>

- **Problema:** Deserción de clientes en telecomunicaciones, donde adquirir un nuevo cliente cuesta de 5 a 7 veces más que retener a uno existente.
- **Datos:** Dataset Telco Customer Churn (7.043 registros, 21 variables demográficas, contractuales y de servicio).
- **Método:** Clasificación supervisada comparando Random Forest y Perceptrón Multicapa (MLP) con técnicas de balanceo (SMOTE, SMOTEENN, ADASYN, RandomUnderSampler), optimización con RandomizedSearchCV y explicabilidad con SHAP.
- **Resultado:** Modelo campeón Random Forest con SMOTEENN alcanzando **77,7% Recall** y **0,633 F1-score**, maximizando la identificación de clientes en riesgo. Calibración de umbrales bajo un escenario ilustrativo de retención de clientes.
- **Código:** [Jupyter Notebook](https://github.com/cveram96/Portfolio/blob/main/Files/Proyecto%20Churn.ipynb) | [Análisis Detallado y Curvas ROC](https://cveram96.github.io/Portfolio/churn.html)
</details>

---

## Business Intelligence & Core Analytics

### 4. [Power BI Netflix Catalog Analytics](https://cveram96.github.io/Portfolio/netflix.html)
- **Problem:** Analyzing international content distribution, genre saturation, and viewer sentiment across a massive entertainment catalog.
- **Data:** Global Netflix catalog enriched with IMDb audience scores, votes, and production metadata (8,800+ titles).
- **Method:** Star schema relational model (5 tables), 14 custom DAX business measures, Power Query M ETL, dynamic field parameters, and interactive dashboards.
- **Result:** Identified catalog distribution patterns (~70% movies vs. higher average audience engagement per title on TV series), clarifying that measuring subscriber retention directly requires longitudinal user streaming data.
- **Dashboard / Code:** [Live Power BI Report](https://app.powerbi.com/view?r=eyJrIjoiZjQ3OTI1NTMtZGZkYi00Zjc3LWI1YmItYzBlZDQ3MDRkN2M5IiwidCI6IjE2YWY2YjQ1LTAwYzUtNGJhMy05ZDRjLThiZmExNmU0MzYwMyIsImMiOjR9) | [Project Walkthrough & DAX](https://cveram96.github.io/Portfolio/netflix.html) | [Download .pbix](https://github.com/cveram96/Portfolio/blob/main/Files/Netflix.pbix)

---

### 5. [SQL Northwind Commercial Analytics](https://cveram96.github.io/Portfolio/SQL_Northwind.html)
- **Problem:** Extracting commercial KPIs, logistics latency, and customer behavior directly from transactional ERP database tables.
- **Data:** Northwind relational database (13 normalized tables: orders, line-items, customers, products, and shippers).
- **Method:** Advanced analytical SQL: multi-table JOINs, Common Table Expressions (CTEs), Window Functions (`DENSE_RANK()`, `LAG()`, running totals via `SUM() OVER`), pure-SQL RFM segmentation (`NTILE(4)`), and cohort repeat-purchase matrices.
- **Result:** 10 production-grade analytical queries computing net revenue adjusted for item discounts, shipper delivery latency distributions, and an in-database customer segmentation engine.
- **Code:** [Jupyter Notebook & SQL Queries](https://github.com/cveram96/Portfolio/blob/main/Files/SQL_Northwind.ipynb) | [Query Walkthrough & ERD](https://cveram96.github.io/Portfolio/SQL_Northwind.html)

---

### 6. [Time Series Demand Forecasting (SARIMA)](https://cveram96.github.io/Portfolio/ARIMA.html)
- **Problem:** Forecasting passenger travel demand to optimize fleet capacity planning and scheduling.
- **Data:** Monthly international airline passenger time series (144 historical observations).
- **Method:** Box-Jenkins time series workflow: seasonal additive/multiplicative decomposition, Augmented Dickey-Fuller (ADF) stationarity test, ACF/PACF analysis, seasonal differencing, and SARIMA modeling.
- **Result:** Captured annual seasonality and upward trend with an out-of-sample Mean Absolute Percentage Error (MAPE) of **3.68%**.
- **Code:** [Forecasting Report & Notebook](https://cveram96.github.io/Portfolio/ARIMA.html)

---

### 7. [Customer Segmentation (K-Means & RFM)](https://cveram96.github.io/Portfolio/segmentacion.html)
- **Problem:** Inefficient blanket marketing campaigns caused by lack of customer behavioral differentiation.
- **Data:** E-commerce transaction logs (Recency, Frequency, Monetary value metrics).
- **Method:** Unsupervised clustering pipeline: `np.log1p` transformation for positive skewness, `MinMaxScaler` normalization, Elbow method and Silhouette score evaluation, and K-Means clustering.
- **Result:** Discovered 3 actionable customer archetypes (Champions, Loyal Regulars, and Dormant/At-Risk buyers) for lifecycle marketing strategies.
- **Code:** [Clustering Walkthrough & Notebook](https://cveram96.github.io/Portfolio/segmentacion.html)

---

### 8. [California Housing Price Regression (Gauss-Markov)](https://cveram96.github.io/Portfolio/RLM.html)
- **Problem:** Estimating median residential property values and quantifying the elasticity of socioeconomic and spatial variables.
- **Data:** California 1990 Census housing dataset (20,640 census block group observations).
- **Method:** Multivariate OLS linear regression, log-transformed target, elasticity analysis, and Gauss-Markov diagnostics (Jarque-Bera, Breusch-Pagan, Variance Inflation Factor).
- **Result:** Linear model explaining **63.6% of price variance** ($R^2 = 0.636$), establishing median income elasticity (+0.68) and ocean proximity as the primary valuation drivers.
- **Code:** [Econometric Analysis & Diagnostic Suite](https://cveram96.github.io/Portfolio/RLM.html)

---

## Technical Skills Summary

- **Programming & Query Languages:** Python (3.10+), SQL (PostgreSQL, SQLite), DAX.
- **Machine Learning & AI:** Supervised Learning (Classification, Regression), Unsupervised Learning (K-Means, PCA), Computer Vision (YOLOv8, OpenCV, ByteTrack), Time Series (ARIMA / SARIMA), Model Explainability (SHAP).
- **Statistics & Experimentation:** A/B Testing, CUPED (Variance Reduction), Hypothesis Testing (p-values, confidence intervals), Power & Sample Size Analysis (MDE), Causal Inference.
- **Business Intelligence & Data Engineering:** Power BI, Tableau, Power Query, ETL Pipelines, FastAPI, WebSockets, Relational Modeling.
- **Tools & Environments:** Git/GitHub, Jupyter, DirectML, CUDA, VS Code, Excel (Advanced).

---

## Contact & Links

- **Email:** [verachristian4@gmail.com](mailto:verachristian4@gmail.com)
- **LinkedIn:** [Christian David Vera Mendivelso](https://www.linkedin.com/in/christianveram/)
- **Phone / WhatsApp:** [+57 321 379 7876](https://wa.me/573213797876)
- **Location:** Bogota, Colombia *(Open to Remote, Hybrid, and Relocation)*
- **Live Portfolio:** [https://cveram96.github.io/Portfolio/](https://cveram96.github.io/Portfolio/)
