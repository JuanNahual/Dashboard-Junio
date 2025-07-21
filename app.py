import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Configuración de la app
st.set_page_config(
    page_title="Dashboard Estadísticas",
    page_icon="📊",
    layout="wide"
)

# Carpeta con archivos CSV
csv_folder = "data"

# Carga de archivos CSV
dfs = []

st.sidebar.header("📂 Cargando datos...")

for archivo in os.listdir(csv_folder):
    if archivo.endswith(".csv"):
        path = os.path.join(csv_folder, archivo)
        df_temp = pd.read_csv(path, delimiter=";")
        df_temp["Mes"] = archivo.replace("reporte_", "").replace(".csv", "").capitalize()
        df_temp["Fecha"] = pd.to_datetime(df_temp["Fecha"], format="%d/%m/%y", errors="coerce")
        df_temp = df_temp.dropna(subset=["Fecha"])  # Solo filas con fechas válidas
        
        dfs.append(df_temp)

# Verificamos que haya datos cargados
if not dfs:
    st.warning("⚠️ No se cargaron datos válidos desde la carpeta `/data`.")
    st.stop()

# Concatenar todos los DataFrames en uno solo
df = pd.concat(dfs, ignore_index=True)

# Validar que existan fechas válidas
if df["Fecha"].isna().all():
    st.warning("⚠️ No se encontraron fechas válidas en los datos cargados.")
    st.stop()
df["Rubro"] = df["Rubro"].fillna("Sin rubro").replace("", "Sin rubro")

# Convertir columnas numéricas
df["Cantidad"] = pd.to_numeric(df["Cantidad"], errors="coerce").fillna(0)
df["Importe Articulos"] = pd.to_numeric(df["Importe Articulos"], errors="coerce").fillna(0)
df["Importe Envio"] = pd.to_numeric(df["Importe Envio"], errors="coerce").fillna(0)
df["Importe"] = pd.to_numeric(df["Importe"], errors="coerce").fillna(0)
# Título
st.markdown("<h1 style='text-align: center;'>📊 Dashboard Estadísticas</h1>", unsafe_allow_html=True)
# -------------------------
# FILTROS
# -------------------------
st.sidebar.header("🔎 Filtros")

fecha_min = df["Fecha"].min()
fecha_max = df["Fecha"].max()
fecha_sel = st.sidebar.date_input("Rango de fechas", [fecha_min, fecha_max])

# Lista de valores únicos para filtros
meses_disponibles = df["Mes"].dropna().unique().tolist()
mes_sel = st.sidebar.multiselect("Mes", meses_disponibles, default=meses_disponibles)
if not mes_sel:
    mes_sel = meses_disponibles

rubros = df["Rubro"].dropna().unique().tolist()
rubro_sel = st.sidebar.multiselect("Rubro", rubros, default=rubros)
if not rubro_sel:
    rubro_sel = rubros

usuarios = df["Usuario"].dropna().unique().tolist()
usuario_sel = st.sidebar.multiselect("Usuario", usuarios, default=usuarios)
if not usuario_sel:
    usuario_sel = usuarios

sucursales = df["Punto de venta"].dropna().unique().tolist()
sucursal_sel = st.sidebar.multiselect("Sucursal", sucursales, default=sucursales)
if not sucursal_sel:
    sucursal_sel = sucursales
print(df['Importe Articulos'].sum())
# Aplicar filtros
df_filtrado = df[
    (df["Fecha"] >= pd.to_datetime(fecha_sel[0])) &
    (df["Fecha"] <= pd.to_datetime(fecha_sel[1])) &
    (df["Mes"].isin(mes_sel)) &
    (df["Rubro"].isin(rubro_sel)) &
    (df["Usuario"].isin(usuario_sel)) &
    (df["Punto de venta"].isin(sucursal_sel))
]

# KPIs
st.subheader("📈 KPIs Ejecutivos")
col1, col2, col3= st.columns(3)

with col1:
    st.metric("💰 Ingresos Totales", f"${df_filtrado['Importe Articulos'].sum():,.0f}")

with col2:
    st.metric("🛒 Productos Vendidos", int(df_filtrado["Cantidad"].sum()))



with col3:
    tickets = df_filtrado.groupby("Numero Comprobante")["Importe Articulos"].sum()
    ticket_promedio = tickets.mean() if not tickets.empty else 0
    st.metric("💳 Ticket Promedio", f"${ticket_promedio:,.0f}")

# Visualizaciones seguras
if df_filtrado.empty:
    st.warning("⚠️ No hay datos disponibles para los filtros seleccionados. Por favor ajusta los filtros.")
else:
    st.subheader("📊 Productos más vendidos")
    top_productos = df_filtrado.groupby("Descripcion")["Cantidad"].sum().sort_values(ascending=False).head(10)
    fig1 = px.bar(top_productos, x=top_productos.values, y=top_productos.index, orientation="h", labels={'x': 'Cantidad'}, title="Top 10 productos")
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("📦 Ingresos por Rubro")
    ingresos_rubro = df_filtrado.groupby("Rubro")["Importe Articulos"].sum().sort_values(ascending=False)
    fig2 = px.pie(names=ingresos_rubro.index, values=ingresos_rubro.values, title="Distribución de ingresos por rubro")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("⏱️ Ventas por Hora")
    df_filtrado["Hora"] = pd.to_datetime(df_filtrado["Hora"], format="%H:%M:%S", errors="coerce").dt.hour
    ventas_hora = df_filtrado.groupby("Hora")["Importe Articulos"].sum()
    fig3 = px.line(x=ventas_hora.index, y=ventas_hora.values, labels={'x': 'Hora', 'y': 'Ingresos'}, title="Ingresos por hora del día")
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("🏪 Ventas por Punto de Venta")
    ventas_sucursal = df_filtrado.groupby("Punto de venta")["Importe Articulos"].sum().sort_values(ascending=False)
    fig4 = px.bar(
        ventas_sucursal,
        x=ventas_sucursal.index,
        y=ventas_sucursal.values,
        labels={"x": "Sucursal", "y": "Ingresos"},
        title="Ingresos por Punto de Venta",
        text_auto=".2s"
    )
    st.plotly_chart(fig4, use_container_width=True)
    st.subheader("📅 Evolución diaria de ventas")
    ventas_dia = df_filtrado.groupby("Fecha")["Importe Articulos"].sum()
    fig6 = px.line(
        x=ventas_dia.index,
        y=ventas_dia.values,
        labels={"x": "Fecha", "y": "Ingresos"},
        title="Evolución de ingresos por día"
    )
    st.plotly_chart(fig6, use_container_width=True)