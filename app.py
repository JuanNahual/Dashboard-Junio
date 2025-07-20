import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la app
st.set_page_config(
    page_title="Dashboard Estadísticas Junio",
    page_icon="📊",
    layout="wide"
)

# Carga de datos
df = pd.read_csv("reporte_junio.csv", delimiter=";")

# Limpieza de columnas numéricas
df["Importe Articulos"] = pd.to_numeric(df["Importe Articulos"], errors="coerce").fillna(0)
df["Cantidad"] = pd.to_numeric(df["Cantidad"], errors="coerce").fillna(0)
df["Importe"] = pd.to_numeric(df["Importe"], errors="coerce").fillna(0)
df["Fecha"] = pd.to_datetime(df["Fecha"], dayfirst=True)

# Título
st.markdown("<h1 style='text-align: center;'>📊 Dashboard Estadísticas Junio</h1>", unsafe_allow_html=True)

# Filtros
with st.sidebar:
    st.header("Filtros")

    fecha_min = df["Fecha"].min()
    fecha_max = df["Fecha"].max()
    fecha_sel = st.date_input("Filtrar por Fecha", [fecha_min, fecha_max])

    rubros_unicos = df["Rubro"].dropna().unique().tolist()
    rubro_sel = st.multiselect("Selecciona Rubro(s)", rubros_unicos, default=rubros_unicos)
    if not rubro_sel:
        rubro_sel = rubros_unicos  # Si está vacío, seleccionar todos

    usuarios_unicos = df["Usuario"].dropna().unique().tolist()
    usuario_sel = st.multiselect("Usuario", usuarios_unicos, default=usuarios_unicos)
    if not usuario_sel:
        usuario_sel = usuarios_unicos

    sucursales_unicas = df["Punto de venta"].dropna().unique().tolist()
    sucursal_sel = st.multiselect("Sucursal", sucursales_unicas, default=sucursales_unicas)
    if not sucursal_sel:
        sucursal_sel = sucursales_unicas

    df_filtrado = df[
        (df["Fecha"] >= pd.to_datetime(fecha_sel[0])) &
        (df["Fecha"] <= pd.to_datetime(fecha_sel[1])) &
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

