import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración de la aplicación
st.title('Análisis de Datos con Streamlit')
st.write('Sube un archivo CSV para procesar y visualizar los datos.')

# Subir archivo CSV
uploaded_file = st.file_uploader("Elegir un archivo CSV", type=["csv"])

if uploaded_file is not None:
    # Leer el archivo CSV
    df = pd.read_csv(uploaded_file)

    # Mostrar el dataframe
    st.write("Datos del archivo CSV:")
    st.dataframe(df)

    # Mostrar estadísticas básicas
    st.write("Estadísticas básicas:")
    st.write(df.describe(include='all'))

    # Botones para generar gráficos
    st.sidebar.header('Generar Gráficos')
    chart_option = st.sidebar.selectbox(
        'Selecciona el tipo de gráfico',
        ['Ninguno', 'Gráfico de torta', 'Gráfico de barras', 'Distribución']
    )

    if chart_option == 'Gráfico de torta':
        st.subheader('Gráfico de Torta')
        column = st.selectbox('Selecciona la columna para el gráfico de torta', df.columns)
        if column:
            data = df[column].value_counts()
            fig, ax = plt.subplots()
            ax.pie(data, labels=data.index, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            st.pyplot(fig)

    elif chart_option == 'Gráfico de barras':
        st.subheader('Gráfico de Barras')
        column = st.selectbox('Selecciona la columna para el gráfico de barras', df.columns)
        if column:
            data = df[column].value_counts()
            fig, ax = plt.subplots()
            sns.barplot(x=data.index, y=data.values, ax=ax)
            ax.set_xlabel(column)
            ax.set_ylabel('Frecuencia')
            st.pyplot(fig)

    elif chart_option == 'Distribución':
        st.subheader('Distribución de Datos')
        column = st.selectbox('Selecciona la columna para la distribución', df.columns)
        if column and pd.api.types.is_numeric_dtype(df[column]):
            fig, ax = plt.subplots()
            sns.histplot(df[column], kde=True, ax=ax)
            ax.set_xlabel(column)
            ax.set_ylabel('Frecuencia')
            st.pyplot(fig)

    # Calcular y mostrar promedio de la columna edad
    st.sidebar.header('Promedio de Columnas Numéricas')
    numeric_column = st.sidebar.selectbox(
        'Selecciona una columna numérica para calcular el promedio',
        [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
    )

    if numeric_column:
        mean_value = df[numeric_column].mean()
        st.write(f'Promedio de la columna {numeric_column}: {mean_value:.2f}')

    # Agrupar y calcular estadísticas para columnas categóricas
    st.sidebar.header('Estadísticas por Agrupación')
    categorical_column = st.sidebar.selectbox(
        'Selecciona una columna categórica para agrupar',
        [col for col in df.columns if not pd.api.types.is_numeric_dtype(df[col])]
    )

    if categorical_column:
        st.write(f'Estadísticas agrupadas por {categorical_column}:')
        grouped = df.groupby(categorical_column).agg({
            'edad': ['mean', 'median', 'std']
        }).reset_index()
        st.write(grouped)

