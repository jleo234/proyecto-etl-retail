# Proyecto ETL End-to-End: Pipeline de Analítica para Retail

Este proyecto implementa un pipeline de Ingeniería de Datos completo (ETL) utilizando **Python** para extraer, transformar y cargar datos provenientes de fuentes mixtas (Bases de datos Relacionales, NoSQL y Archivos Planos/Estructurados). El objetivo final es consolidar un *Data Master* optimizado y generar análisis avanzados 

## 👥 Autores
* **Jesús Leonardo Torres Soberanes**
* **Francisco Fernando Cartajena Loaiza**

---

## 📊 Arquitectura del Ecosistema

El pipeline procesa información de los siguientes componentes:
1. **SQL (MySQL):** Extracción de ventas históricas corporativas.
2. **NoSQL (MongoDB):** Extracción de perfiles y preferencias de usuarios en formato JSON.
3. **Archivos Planos y Estructurados:**
   - `inventario.csv`: Control de existencias con manejo explícito de valores nulos y duplicados.
   - `logs_servidor.txt`: Logs semiestructurados parseados mediante Expresiones Regulares (RegEx).
   - `catalogos.xml`: Jerarquías y categorías de productos.
   - `metas_anuales.xlsx`: KPIs corporativos y metas por región con formatos comerciales.

---

## 🛠️ Estructura del Proyecto

```text
├── proyecto.py              # Script principal con el pipeline ETL completo
├── proyectoventas.py        # Script auxiliar para la generación de datos sintéticos
├── requirements.txt         # Librerías y dependencias del entorno
├── README.md                # Documentación del proyecto (Este archivo)
│
├── data_master_clean.parquet # Entregable final consolidado en formato columnar de Big Data
│
├── catalogos.xml            # Fuente: Categorías de productos
├── inventario.csv           # Fuente: Stock físico
├── logs_servidor.txt        # Fuente: Tráfico web parsed con RegEx
├── metas_anuales.xlsx       # Fuente: Objetivos comerciales
│
└── de_salida_graficas/      # Reportes visuales automatizados
    ├── boxplot_montos.png   # Distribución y detección de outliers en ventas
    ├── scatter_pca.png      # Visualización de clusters tras reducción dimensional
    └── sankey_diagram.png   # Flujo del comportamiento del cliente