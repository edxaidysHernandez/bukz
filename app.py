import streamlit as st
from streamlit_option_menu import option_menu
import streamlit.components.v1 as html
import pandas as pd
from PIL import Image
from unidecode import unidecode
import math
import json
import numpy as np

# Cargar la imagen
logo_image = Image.open("LOGO_BUKZ.webp")  # Reemplaza con la ruta o nombre de archivo correcto

resized_image = logo_image.resize((200, 50))  # Especifica las dimensiones deseadas

# Mostrar la imagen redimensionada en la barra lateral
st.sidebar.image(resized_image)


with st.sidebar:
    choose = option_menu("Menú de opciones", ['Actualización de inventario celesa', 'Creación de productos', 'Actualización de productos'],
    icons=["list check", "database up", "check2 square"], menu_icon="cast", default_index=0,
    styles={ "container": {"padding": "5!important", "background-color": "#fafafa"},
        "icon": { "font-size": "25px"}, 
        "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee", "color": "black"},
        "nav-link-selected": {"background-color": "#F9CB00"}})
        
if choose == 'Actualización de inventario celesa':
    st.title("Actualización de inventario celesa")
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


elif choose == 'Creación de productos':
    st.title("Creación de productos")
    plantilla de creación de productos
    st.write("Plantilla creación de productos")
    st.set_option('deprecation.showfileUploaderEncoding', False)  # Evita el aviso de codificación

# Ruta del archivo local
    file_path = "plantilla_creacion_productos.xlsx"
    
    # Botón de descarga
    def download_file():
        with open(file_path, "rb") as file:
            btn = st.download_button(label="Descargar archivo", data=file, file_name="plantilla_creacion_productos.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        return btn
    # Llamar a la función para mostrar el botón de descarga
    download_file()
    
    st.write("Cargar archivo XLSX (Fotmato Excel):")
    st.markdown("<h3>Archivo con datos</h3>", unsafe_allow_html=True)
    uploaded_file3 = st.file_uploader("Los nombres de las columnas del archivo debe conservar el mismo nombre de la plantilla de creación de productos", type=["xlsx"], key="archivo_productos")
     if uploaded_file3 is not None:
        st.write("Presiona el botón para continuar")
        if st.button("Continuar"):
            info_placeholder = st.empty()
            info_placeholder.info("Cargando...")

            df2 = pd.read_excel(uploaded_file3, sheet_name='Products')

            try:
                
                df = pd.DataFrame()
                df['Title'] = df2['titulo'].str.title()
                df['Command'] = 'NEW'

                df['Body HTML'] = df2['book_description']

                df2['Variant SKU'] = df2['ISBN13'].apply(lambda x: str(x).replace('.0', ''))

                df['Handle'] = df['Title'].str.lower().apply(unidecode).str.replace(r'[^\w\s]+', '', regex=True).str.replace(' ', '-') + '-' + df2['Variant SKU']

                #Vendor
                df['Vendor'] = 'Bukz USA'

                #Vendor
                df['Type'] = 'Libro'

                #tags
                df['Tags'] = pd.Series(dtype=str)

                #Status
                df['Status'] = 'Active'

                #Published
                df['Published'] = 'TRUE'

                #Published Scope
                df['Published Scope'] = 'global'

                #Gift Card
                df['Gift Card'] = 'FALSE'

                #Row #
                df['Row #'] = 1

                #Top Row
                df['Top Row'] = 'TRUE'

                # Option1 Name
                df['Option1 Name'] = 'Title'

                #Option1 Value
                df['Option1 Value'] = 'Default Title'

                # Option2 Name
                df['Option2 Name'] = pd.Series(dtype=str)

                # Option2 Value
                df['Option2 Value'] = pd.Series(dtype=str)

                # Option3 Name
                df['Option3 Name'] = pd.Series(dtype=str)

                # Option3 Value
                df['Option3 Value'] = pd.Series(dtype=str)

                #Variant Position
                df['Variant Position'] = pd.Series(dtype=str)

                #Variant SKU
                df['Variant SKU'] = df2['ISBN13']

                #Variant Barcode
                df['Variant Barcode'] = df['Variant SKU']

                #Variant Image
                df['Image Src'] = df2['portada']

                df['Variant Price'] = df2["precio_final"] * 9000
                df['Variant Price']= df['Variant Price'].apply(lambda x:((math.ceil(x / 1000) * 1000))-10 )

                df['Variant Compare At Price'] = df2["precio_final"] / 0.75
                df['Variant Compare At Price']= df['Variant Compare At Price'].apply(lambda x:((math.ceil(x / 1000) * 1000)))


                #Variant Taxable
                df['Variant Taxable'] = 'FALSE'

                #Variant Tax Code
                df['Variant Tax Code'] = pd.Series(dtype=str)

                #Variant Inventory Tracker
                df['Variant Inventory Tracker'] = 'shopify'

                #Variant Inventory Policy
                df['Variant Inventory Policy'] = 'deny'

                #Variant Inventory Tracker
                df['Variant Fulfillment Service'] = 'manual'

                #Variant Requires Shipping
                df['Variant Requires Shipping'] = 'TRUE'
                #Variant Weight
                df['Variant Weight'] = df2['Peso en kg']

                #Variant Weight Unit
                df['Variant Weight Unit'] = df['Variant Weight'].apply(lambda x: 'kg' if pd.notnull(x) else np.nan)

                #Metafield: custom.autor [single_line_text_field]
                df['Metafield: custom.autor [single_line_text_field]'] =  df2["Author"].str.title()

                replacements2 = {'Alemán': '["Aleman"]','Chino': '["Chino"]','Español': '["Español"]','Francés': '["Frances"]','Inglés': '["Ingles"]','Italiano': '["Italiano"]','Japonés': '["Japones"]','Portugués': '["Portugues"]','Ruso': '["Ruso"]'}
                df['Metafield: custom.idioma [list.single_line_text_field]'] = df2['Idioma'].apply(lambda x: replacements2.get(x, x))

                replacements = {'Encuadernación en espiral' : '["Espiral"]', 'Libro de bolsillo': '["Bolsillo"]', 'Libro de cartón':'["Libro de Carton"]', 'Tapa blanda':'["Tapa Blanda"]','Tapa dura':'["Tapa Dura"]'}
                df['Metafield: custom.formato [list.single_line_text_field]'] = df2['encuadernacion'].apply(lambda x: replacements.get(x, x))


                df['Metafield: custom.alto [dimension]'] = df2['largo'].apply(lambda x: np.nan if np.isnan(x) else json.dumps({"value": x, "unit": "cm"}))

                df['Metafield: custom.ancho [dimension]'] = df2['ancho'].apply(lambda x: np.nan if np.isnan(x) else json.dumps({"value": x, "unit": "cm"}))

                df['Metafield: custom.editorial [single_line_text_field]'] = df2['Editorial']

                def convertir_fecha(fecha_str):
                    partes_fecha = fecha_str.split()
                    dia = int(partes_fecha[0])
                    mes = datetime.strptime(partes_fecha[1], '%B').month
                    anio = int(partes_fecha[2])
                    return f"{anio}-{mes:02d}-{dia:02d}"

                df['Metafield: custom.editorial [single_line_text_field]'] = df['Fecha'].apply(convertir_fecha)


                df['Image Alt Text'] = 'Libro ' + df['Title']+' '+ df['Variant SKU']

                df_crear = df
                info_placeholder.empty()
                st.write(df_final)

                # Botón de descarga sin base64
                st.download_button(
                    label="Descargar XLSX",
                    data=df_crear.to_exce(index=False),
                    file_name="resultado_crear_productos.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
"
                )
            except Exception as e:
                info_placeholder.empty()
                st.error(f"Error: {str(e)}")
    else:
        st.info("Por favor, carga el archivo para continuar.")
    

elif choose == 'Actualización de productos':
    st.title("Actualización de productos")
    # Resto de tu código para la actualización de productos...
