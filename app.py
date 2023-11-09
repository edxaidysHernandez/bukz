import streamlit as st
from streamlit_option_menu import option_menu
import streamlit.components.v1 as html
import pandas as pd
from PIL import Image
from unidecode import unidecode
import math
import json
import numpy as np
import io
import traceback
import os
import shutil
from io import BytesIO
import zipfile

# Cargar la imagen
logo_image = Image.open("LOGO_BUKZ.webp")  # Reemplaza con la ruta o nombre de archivo correcto

resized_image = logo_image.resize((200, 50))  # Especifica las dimensiones deseadas

# Mostrar la imagen redimensionada en la barra lateral
st.sidebar.image(resized_image)


with st.sidebar:
    choose = option_menu("Menú de opciones", ['Actualización de inventario celesa', 'Creación de productos', 'Corte Proveedores'],
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
                
                df_merged = pd.merge(df_products, df_azeta, on="Variant SKU", how='left')
                df_merged['Inventory Available: Dropshipping [España]'].fillna(0, inplace=True)
                df_merged['Stock_Azeta'].fillna(0, inplace=True)
                df_merged['Stock_Azeta'] = df_merged['Stock_Azeta'].astype(int)
                df_merged['Inventory Available: Dropshipping [España]'] = pd.to_numeric(df_merged['Inventory Available: Dropshipping [España]'], errors='coerce').fillna(0).astype(int)

                df_merged['Inventory Available: Dropshipping [España]'] = df_merged['Inventory Available: Dropshipping [España]'].astype(int)

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
                st.error(f"Traceback: {traceback.format_exc()}")
    else:
        st.info("Por favor, carga ambos archivos para continuar.")


elif choose == 'Creación de productos':
    st.title("Creación de productos")
    st.markdown("<h3>Plantilla creación de productos</h3>", unsafe_allow_html=True)
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
    
    st.write("Cargar archivo XLSX (Formato Excel):")
    st.markdown("<h3>Archivo con datos</h3>", unsafe_allow_html=True)
    uploaded_file3 = st.file_uploader("Los nombres de las columnas del archivo debe conservar el mismo nombre de la plantilla de creación de productos", type=["xlsx"], key="archivo_productos")
    if uploaded_file3 is not None:
        st.write("Presiona el botón para continuar")
        if st.button("Continuar"):
            info_placeholder = st.empty()
            info_placeholder.info("Cargando...")

            df2 = pd.read_excel(uploaded_file3, sheet_name='Products', engine='openpyxl')

            try:  
                df = pd.DataFrame()
                df['Title'] = df2['Titulo'].str.title()
                
                df['Command'] = 'NEW'
                
                df['Body HTML'] = df2['Sipnosis']
                
                df2['Variant SKU'] = df2['SKU'].apply(lambda x: str(x).replace('.0', ''))
                
                df['Handle'] = df['Title'].str.lower().apply(unidecode).str.replace(r'[^\w\s]+', '', regex=True).str.replace(' ', '-') + '-' + df2['Variant SKU']
                
                #Vendor
                df['Vendor'] = df2['Vendor']
                
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
                df['Variant SKU'] = df2['SKU'].apply(lambda x: str(x).replace('.0', ''))
                #Variant Barcode
                df['Variant Barcode'] = df['Variant SKU']
                
                #Variant Image
                df['Image Src'] = df2['Portada (URL)']
                
                df['Variant Price'] = df2["Precio"]
                
                df['Variant Compare At Price'] = df2["Precio de comparacion"]
                
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
                df['Variant Weight'] = df2['peso (kg)']
                
                #Variant Weight Unit
                df['Variant Weight Unit'] = df['Variant Weight'].apply(lambda x: 'kg' if pd.notnull(x) else np.nan)
                
                #Metafield: custom.autor [single_line_text_field]
                df['Metafield: custom.autor [single_line_text_field]'] = df2["Autor"].fillna("").str.title()
                
                replacements2 = {'Español' : '["Español"]', 'Ingles' : '["Ingles"]', 'Frances' : '["Frances"]', 'Italiano' : '["Italiano"]', 'Portugues' : '["Portugues"]', 
                    'Aleman' : '["Aleman"]', 'Bilingue (Español-Ingles)' : '["Bilingue (Español-Ingles)"]', 'Bilingue (Español-Portugues)' : '["Bilingue (Español-Portugues)"]', 
                    'Vasco' : '["Vasco"]', 'Gallego' : '["Gallego"]', 'Latin' : '["Latin"]', 'Ruso' : '["Ruso"]', 'Arabe' : '["Arabe"]', 'Chino' : '["Chino"]', 
                    'Japones' : '["Japones"]', 'Catalan' : '["Catalan"]', 'Rumano' : '["Rumano"]', 'Holandes' : '["Holandes"]', 'Bulgaro' : '["Bulgaro"]', 'Griego' : '["Griego"]', 
                    'Polaco' : '["Polaco"]', 'Checo' : '["Checo"]', 'Sueco' : '["Sueco"]'}
                
                df['Metafield: custom.idioma [list.single_line_text_field]'] = df2['Idioma'].apply(lambda x: replacements2.get(x, x))
                
                replacements = {
                    'Tapa Dura' : '["Tapa Dura"]', 'Tapa Blanda' : '["Tapa Blanda"]', 'Bolsillo' : '["Bolsillo"]', 'Libro de lujo' : '["Libro de lujo"]', 
                    'Espiral' : '["Espiral"]', 'Tela' : '["Tela"]', 'Grapado' : '["Grapado"]', 'Fasciculo Encuadernable' : '["Fasciculo Encuadernable"]', 
                    'Troquelado' : '["Troquelado"]', 'Anillas' : '["Anillas"]', 'Otros' : '["Otros"]'}
                
                df['Metafield: custom.formato [list.single_line_text_field]'] = df2['Formato'].apply(lambda x: replacements.get(x, x))
                
                df['Metafield: custom.alto [dimension]'] = df2['Alto'].apply(lambda x: np.nan if np.isnan(x) else json.dumps({"value": x, "unit": "cm"}))
                
                df['Metafield: custom.ancho [dimension]'] = df2['Ancho'].apply(lambda x: np.nan if np.isnan(x) else json.dumps({"value": x, "unit": "cm"}))
                
                df['Metafield: custom.editorial [single_line_text_field]'] = df2['Editorial'].str.title()
                
                df['Metafield: custom.numero_de_paginas [number_integer]'] = df2['Numero de paginas']
                
                df['Metafield: custom.ilustrador [single_line_text_field]'] = df2['Ilustrador']
                
                df['Image Alt Text'] = 'Libro ' + df['Title']+' '+ df['Variant SKU']
                df_crear = df
                
                info_placeholder.empty()
                st.write(df_crear)

                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_crear.to_excel(writer, index=False)
        
                # Mostrar el botón de descarga
                st.download_button(
                    label="Descargar archivo xlsx",
                    data=output.getvalue(),
                    file_name="resultado_crear_productos.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                
            except Exception as e:
                info_placeholder.empty()
                st.error(f"Error: {str(e)}")
    else:
        st.info("Por favor, carga el archivo para continuar.")
    

elif choose == 'Corte Proveedores':
    st.title("Corte Proveedores")
    # Resto de tu código para la actualización de productos...
     
    st.write("Cargar archivo XLSX (Formato Excel):")
    st.markdown("<h3>Archivo de ventas</h3>", unsafe_allow_html=True)
    uploaded_file_provedores = st.file_uploader("El archivo debe tener las columnas: product_title, product_vendor, variant_sku, net_quantity", type=["xlsx"], key="archivo_productos")
    if uploaded_file_provedores is not None:
        st.write("Presiona el botón para continuar")
        if st.button("Continuar"):
            # Crear el marcador de posición de carga
            info_placeholder = st.empty()
            info_placeholder.info("Cargando...")
            
            def save_df_to_excel(df, filename):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                processed_data = output.getvalue()
                return processed_data
            
            def create_zip(files, directory):
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zip_file:
                    for file, data in files.items():
                        zip_file.writestr(f'{directory}/{file}', data)
                return zip_buffer.getvalue()
            
            # Carga y procesamiento del archivo
            df_provedores = pd.read_excel(uploaded_file_provedores, engine='openpyxl')
            files_to_download = {}
            output_directory = 'cortes'
            
            for vendor, group in df_provedores.groupby('product_vendor'):
                # Define el nombre del archivo
                file_name = f'{vendor}.xlsx'
                # Guarda el DataFrame del grupo en un BytesIO
                files_to_download[file_name] = save_df_to_excel(group, file_name)
            
            # Si hay archivos para descargar, crea un ZIP
            if files_to_download:
                zip_to_download = create_zip(files_to_download, output_directory)
                st.download_button(
                    label="Descargar corte de proveedores",
                    data=zip_to_download,
                    file_name="cortes_proveedores.zip",
                    mime="application/zip"
                )
                # Elimina el marcador de posición de carga una vez que el botón de descarga está listo
                info_placeholder.empty()

