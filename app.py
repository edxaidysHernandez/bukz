import streamlit as st
import pandas as pd
from PIL import Image

# Cargar la imagen
logo_image = Image.open("LOGO_BUKZ.webp")  # Reemplaza con la ruta o nombre de archivo correcto

resized_image = logo_image.resize((200, 50))  # Especifica las dimensiones deseadas

# Mostrar la imagen redimensionada en la barra lateral
st.sidebar.image(resized_image)

st.title("Actualización de inventario Celesa")

st.write("Cargar archivos CSV:")
st.set_option('deprecation.showfileUploaderEncoding', False)  # Evita el aviso de codificación

st.markdown("<h3>Archivo Productos</h3>", unsafe_allow_html=True)
uploaded_file1 = st.file_uploader("El archivo de producto debe tener las columnas: ID,  Variant ID,  Vendor,  Variant SKU,  Variant Barcode,  Inventory Available Dropshipping [España]", type=["csv"], key="archivo_productos")

st.markdown("<h3>Archivo Azeta</h3>", unsafe_allow_html=True)
uploaded_file2 = st.file_uploader("", type=["csv"], key="archivo_azeta")


if uploaded_file1 is not None and uploaded_file2 is not None:
    st.write("Presiona el botón para continuar")
    if st.button("Continuar"):
        info_placeholder = st.empty()
        info_placeholder.info("Cargando...")

        df_products = pd.read_csv(uploaded_file1)
        df_azeta = pd.read_csv(uploaded_file2, sep=';', header=None)
        df_azeta.columns = ['Variant SKU', 'Stock_Azeta']

        try:
            df_products = df_products.loc[df_products['Vendor'] == 'Bukz España']
            df_products = df_products[['ID', 'Variant ID', 'Vendor', 'Variant SKU', 'Variant Barcode', 'Inventory Available: Dropshipping [España]']]
            df_products.insert(1, 'Command', 'UPDATE')
            df_merged = pd.merge(df_products, df_azeta, on="Variant SKU")
            comparar_filas = lambda x: 1 if x['Inventory Available: Dropshipping [España]'] == x['Stock_Azeta'] else 0
            df_merged['Resultado'] = df_merged.apply(comparar_filas, axis=1)
            df_final = df_merged.loc[df_merged['Resultado'] == 0]
            df_final['Inventory Available: Dropshipping [España]'] = df_final['Stock_Azeta']
            df_final.drop(['Stock_Azeta', 'Resultado'], axis=1, inplace=True)
            df_final = df_final.astype({'ID':str, 'Variant ID':str, 'Vendor':str, 'Variant SKU':str, 
                                       'Variant Barcode':str, 'Inventory Available: Dropshipping [España]':str})
            info_placeholder.empty()
            st.write(df_final)

            # Botón de descarga sin base64
            st.download_button(
                label="Descargar CSV",
                data=df_final.to_csv(index=False),
                file_name="resultado_cruzado.csv",
                mime="text/csv"
            )
        except Exception as e:
            info_placeholder.empty()
            st.error(f"Error: {str(e)}")
else:
    st.info("Por favor, carga ambos archivos para continuar.")

