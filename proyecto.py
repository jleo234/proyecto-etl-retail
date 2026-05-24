import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from pymongo import MongoClient
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go

# ==========================================
# FASE 1: EXTRACCIÓN (Fuentes Mixtas)
# ==========================================
print("Iniciando Extracción de Datos...")

# 1. SQL (Ventas Históricas)
# MOCK DATA para que el código corra sin base de datos local:
ventas_sql = pd.DataFrame({
    'id_transaccion': range(1, 5001), # 5,000 registros
    'Customer_ID': np.random.randint(1, 1000, 5000),
    'monto': np.random.uniform(50, 5000, 5000),
    'fecha': ['12/05/2023' if i % 2 == 0 else '2023-05-12' for i in range(5000)], # Fechas inconsistentes
    'id_tienda': np.random.randint(1, 50, 5000)
})

# 2. NoSQL (MongoDB - Perfiles)
# MOCK DATA CORREGIDA (1500 datos exactos en todas las columnas):
perfiles_mongo = pd.DataFrame({
    'Customer_ID': range(1, 1501), # <-- ¡AQUÍ ESTÁ LA CORRECCIÓN! (1500 IDs)
    'edad': np.random.randint(18, 70, 1500),
    'preferencias': ['Electrónica', 'Ropa', 'Hogar'] * 500,
    'ingresos': np.random.uniform(10000, 50000, 1500),
    'gastos_mensuales': np.random.uniform(1000, 10000, 1500),
    'puntos_lealtad': np.random.randint(0, 1000, 1500),
    'pais': ['México', 'mex', 'mx'] * 500 # Texto sucio
})

# 3. CSV (Inventario)
# MOCK DATA (con nulos y duplicados):
inventario = pd.DataFrame({
    'id_producto': list(range(1, 501)) + list(range(1, 26)), # 5% duplicados
    'stock': [np.nan if i % 10 == 0 else np.random.randint(0, 100) for i in range(525)] # 10% nulos
})

# ==========================================
# FASE 2: LIMPIEZA
# ==========================================
print("Iniciando Limpieza...")

# Detectar nulos en inventario y rellenar o eliminar
nulos_detectados = inventario.isnull().sum()
inventario_limpio = inventario.dropna() 

# Eliminar transacciones duplicadas en el SQL
ventas_sql_limpio = ventas_sql.drop_duplicates()

# ==========================================
# FASE 3: NORMALIZACIÓN
# ==========================================
print("Iniciando Normalización...")

# Convertir todas las fechas a datetime64
ventas_sql_limpio['fecha'] = pd.to_datetime(ventas_sql_limpio['fecha'], format='mixed')

# Limpieza de strings en categorías (ej: "México", "mex", "mx")
perfiles_mongo['pais'] = perfiles_mongo['pais'].str.lower().replace({'mx': 'méxico', 'mex': 'méxico'})

# Escalar las variables numéricas (Min-Max)
scaler = MinMaxScaler()
cols_a_escalar = ['ingresos', 'gastos_mensuales', 'puntos_lealtad']
perfiles_mongo[cols_a_escalar] = scaler.fit_transform(perfiles_mongo[cols_a_escalar])

# ==========================================
# FASE 4: ENRIQUECIMIENTO (Merge)
# ==========================================
print("Enriqueciendo datos...")
# Un left join entre las ventas (SQL) y los perfiles (MongoDB) usando Pandas
df_master = pd.merge(ventas_sql_limpio, perfiles_mongo, on='Customer_ID', how='left')

# ==========================================
# FASE 5: REGLAS DE NEGOCIO
# ==========================================
print("Aplicando Reglas de Negocio...")
# Crear una columna segmento_cliente usando np.where
df_master['segmento_cliente'] = np.where(
    (df_master['monto'] > 1000) & (df_master['edad'] < 30), 
    'Premium Joven', 
    'Estándar'
)

# ==========================================
# FASE 6: REDUCCIÓN DE DIMENSIÓN (PCA)
# ==========================================
print("Aplicando PCA...")
# Simular 20 variables de comportamiento para el ejercicio
for i in range(1, 21):
    df_master[f'var_comportamiento_{i}'] = np.random.rand(len(df_master))

vars_pca = [f'var_comportamiento_{i}' for i in range(1, 21)]

# Rellenar cualquier valor nulo extra que pudiera haber quedado tras el Left Join para que PCA no falle
df_master[vars_pca] = df_master[vars_pca].fillna(0) 

# Aplicar PCA para identificar los 3 componentes principales
pca = PCA(n_components=3)
componentes = pca.fit_transform(df_master[vars_pca])

df_master['PCA_1'] = componentes[:, 0]
df_master['PCA_2'] = componentes[:, 1]
df_master['PCA_3'] = componentes[:, 2]

varianza_explicada = pca.explained_variance_ratio_.sum()
print(f"Varianza explicada por los 3 componentes: {varianza_explicada:.2%}")

# ==========================================
# FASE 7: VISUALIZACIÓN Y SALIDA
# ==========================================
print("Generando Dashboard Estático y Archivo Final...")

# 1. Boxplots: Para detectar outliers en los montos de venta
plt.figure(figsize=(8, 5))
sns.boxplot(x=df_master['monto'])
plt.title('Detección de Outliers en Montos de Venta')
plt.savefig('boxplot_montos.png')
plt.close()

# 2. Scatter Plot: Visualización de los clusters tras aplicar el PCA
plt.figure(figsize=(8, 5))
sns.scatterplot(x='PCA_1', y='PCA_2', hue='segmento_cliente', data=df_master)
plt.title('Clusters de Clientes (PCA)')
plt.savefig('scatter_pca.png')
plt.close()

# 3. Sankey Diagram (Mockup básico del flujo)
fig = go.Figure(data=[go.Sankey(
    node = dict(
      pad = 15, thickness = 20,
      line = dict(color = "black", width = 0.5),
      label = ["Visita Web", "Añade a Carrito", "Compra Final"]
    ),
    link = dict(
      source = [0, 1], # indices of labels
      target = [1, 2],
      value = [800, 400]
    ))])
fig.write_image("sankey_diagram.png")

# 4. Archivo Final optimizado para consumo de BI
df_master.to_parquet('data_master_clean.parquet', index=False)
print("¡Pipeline ejecutado con éxito! Archivo .parquet generado y gráficas guardadas.")