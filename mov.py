import cv2
from tkinter import Tk, filedialog, Button, Label, Toplevel, StringVar, OptionMenu
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import Calendar
from pyzbar.pyzbar import decode, ZBarSymbol
import numpy as np
import os
import shutil
from datetime import date, datetime
import threading
import psycopg2
from psycopg2 import sql    
import re

# Diccionario de farmacias y sus códigos IMED
farmacias = {
    "Sanchez Antoniolli 99": "9999",
    "Sanchez Antoniolli 1": "99029498005",
    "Sanchez Antoniolli II": "99029499003",
    "Sanchez Antoniolli III": "99029404003",
    "Sanchez Antoniolli IV": "99033358005",
    "Sanchez Antoniolli V": "99033295009",
    "Sanchez Antoniolli VI": "99029500008",
    "Sanchez Antoniolli VII": "99033296007",
    "Sanchez Antoniolli VIII": "99033294002",
    "Sanchez Antoniolli IX": "99033663008",
    "Sanchez Antoniolli X": "99033293004",
    "Sanchez Anoniolli XI": "99035665001",
    "Sanchez Antoniolli XII": "99033291008",
    "Sanchez Antoniolli XIV": "99037419001",
    "Sanchez Antoniolli XV": "99033297005",
    "Sanchez Antoniolli XVI": "99036568006",
    "Sanchez Antoniolli XVII": "99036629006",
    "SANCHEZ ANTONIOLLI XVIII": "99036998005",
    "Sanchez Antoniolli XIX": "99037744002",
    "Sanchez Antoniolli XX": "99033579006",
    "Sanchez Antoniolli XXI": "99037766005",
    "Sanchez Antoniolli 23": "99038657005",
    "SANCHEZ ANTONIOLLI 24": "99038046001",
    "Sanchez Antoniolli 25": "99038698009",
    "Sanchez Antoniolli 26": "99038968006",
    "Sanchez Carestia": "99036479006"
}

# Función para extraer el último número o número romano de una cadena
def extract_last_number_or_roman(text):
    match = re.search(r'(\d+|[IVXLCDM]+)$', text, re.IGNORECASE)
    if match:
        numeral = match.group(0)
        if numeral.isdigit():
            return int(numeral)
        roman_numeral_map = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
        result = 0
        prev_value = 0
        for char in reversed(numeral.upper()):
            value = roman_numeral_map.get(char, 0)
            if value < prev_value:
                result -= value
            else:
                result += value
            prev_value = value
        return result
    return None

def get_sucursal_number(sucursal_name):
    if "Carestia" in sucursal_name:
        return 22
    return extract_last_number_or_roman(sucursal_name)

# def select_images_from_sucursal():
#     global file_paths, start_date_entry, end_date_entry
#     selected_code = farmacias[selected_farmacia.get()]
#     # ruta_inicial = r"\\10.0.0.123\recetas"
#     ruta_inicial = r"C:\Users\Administrador\Desktop\origenes"
#     sucursal_path = os.path.join(ruta_inicial, selected_code)

#     # Obtener el rango de fechas seleccionadas por el usuario
#     start_date_str = start_date_entry.get_date()
#     end_date_str = end_date_entry.get_date()
#     try:
#         start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
#         end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
#     except ValueError:
#         messagebox.showerror("Error", "Formato de fecha incorrecto.")
#         return

#     file_paths = []
#     for f in os.listdir(sucursal_path):
#         if f.endswith('.tif') and 'pami' in f.lower():
#             file_path = os.path.join(sucursal_path, f)
#             file_creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
#             if start_date <= file_creation_time <= end_date:
#                 file_paths.append(file_path)

#     if file_paths:
#         file_count.set(f"{len(file_paths)} archivos seleccionados de la sucursal {selected_farmacia.get()}.")
#     else:
#         file_count.set("No se encontraron archivos que cumplan con los criterios en la sucursal seleccionada.")

def select_images_from_sucursal():
    global file_paths, start_date_entry, end_date_entry
    selected_code = farmacias[selected_farmacia.get()]
    ruta_inicial = r"C:\Users\Administrador\Desktop\origenes"
    sucursal_path = os.path.join(ruta_inicial, selected_code)
    
    if not os.path.exists(sucursal_path):
        messagebox.showerror("Error", f"No se encontró la carpeta: {sucursal_path}")
        return

    # Obtener el rango de fechas seleccionadas por el usuario
    start_date_str = start_date_entry.get_date()
    end_date_str = end_date_entry.get_date()
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    except ValueError:
        messagebox.showerror("Error", "Formato de fecha incorrecto.")
        return

    file_paths = []
    print(f"Buscando archivos .tif en {sucursal_path} entre {start_date_str} y {end_date_str}")
    for f in os.listdir(sucursal_path):
        if f.endswith('.tif'):
            file_path = os.path.join(sucursal_path, f)
            file_creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
            print(f"Revisando archivo: {f}, fecha de creación: {file_creation_time}")
            if start_date <= file_creation_time <= end_date:
                file_paths.append(file_path)

    if file_paths:
        file_count.set(f"{len(file_paths)} archivos seleccionados de la sucursal {selected_farmacia.get()}.")
    else:
        file_count.set("No se encontraron archivos que cumplan con los criterios en la sucursal seleccionada.")
        print("No se encontraron archivos en el rango de fechas especificado.")


def select_save_directory():
    global manual_save_directory
    manual_save_directory = filedialog.askdirectory()
    if manual_save_directory:
        save_directory_label.set(f"Directorio de guardado manual seleccionado: {manual_save_directory}")
    else:
        save_directory_label.set("No se seleccionó un directorio de guardado.")

# def process_images():
#     if not file_paths:
#         messagebox.showwarning("Advertencia", "No se seleccionaron archivos.")
#         return

#     # Usar el directorio manual si está seleccionado, de lo contrario usar el automático
#     directory_to_use = manual_save_directory if manual_save_directory else save_directory
#     if not directory_to_use:
#         messagebox.showwarning("Advertencia", "No se seleccionó un directorio de guardado.")
#         return

#     total_count = 0
#     total_autorizacion_count = 0
#     valid_barcodes = []
#     valid_autorizaciones = []
#     failed_images = []
#     progress_bar["maximum"] = len(file_paths)

#     for i, file_path in enumerate(file_paths):
#         count, autorizacion_count, barcode, autorizacion = read_barcodes_from_image(file_path)
#         if barcode or autorizacion:
#             if barcode:
#                 valid_barcodes.append((file_path, barcode))
#                 total_count += count
#             if autorizacion:
#                 valid_autorizaciones.append((file_path, autorizacion))
#                 total_autorizacion_count += autorizacion_count
#         else:
#             print(f'Aplicando técnicas adicionales a la imagen {file_path}')
#             count, autorizacion_count, barcode, autorizacion = process_failed_image(file_path)
#             if barcode or autorizacion:
#                 if barcode:
#                     valid_barcodes.append((file_path, barcode))
#                     total_count += count
#                 if autorizacion:
#                     valid_autorizaciones.append((file_path, autorizacion))
#                     total_autorizacion_count += autorizacion_count
#             else:
#                 failed_images.append(file_path)

#         progress_bar["value"] = i + 1
#         root.update_idletasks()

#     messagebox.showinfo("Resultados", f'Total de códigos de barras que comienzan con 8: {total_count}\n'
#                                       f'Total de códigos de autorización que comienzan con 0: {total_autorizacion_count}')
#     result_file_path = save_results(valid_barcodes, valid_autorizaciones, directory_to_use)
#     if failed_images:
#         save_failed_images(failed_images, directory_to_use)

#     # Enviar resultados a la base de datos
#     upload_progress_bar["maximum"] = len(valid_barcodes) + len(valid_autorizaciones)
#     send_to_database(valid_barcodes, valid_autorizaciones, selected_farmacia.get(), failed_images)


def process_images():
    if not file_paths:
        messagebox.showwarning("Advertencia", "No se seleccionaron archivos.")
        return

    directory_to_use = manual_save_directory if manual_save_directory else save_directory
    if not directory_to_use:
        messagebox.showwarning("Advertencia", "No se seleccionó un directorio de guardado.")
        return

    total_count = 0
    total_autorizacion_count = 0
    valid_barcodes = []
    valid_autorizaciones = []
    failed_images = []
    progress_bar["maximum"] = len(file_paths)

    for i, file_path in enumerate(file_paths):
        count, autorizacion_count, barcode, autorizacion = read_barcodes_from_image(file_path)
        if barcode or autorizacion:
            if barcode:
                valid_barcodes.append((file_path, barcode))
                total_count += count
            if autorizacion:
                valid_autorizaciones.append((file_path, autorizacion))
                total_autorizacion_count += autorizacion_count
        else:
            print(f'Aplicando técnicas adicionales a la imagen {file_path}')
            count, autorizacion_count, barcode, autorizacion = process_failed_image(file_path)
            if barcode or autorizacion:
                if barcode:
                    valid_barcodes.append((file_path, barcode))
                    total_count += count
                if autorizacion:
                    valid_autorizaciones.append((file_path, autorizacion))
                    total_autorizacion_count += autorizacion_count
            else:
                print(f"No se pudo leer la imagen {file_path}. La imagen será ignorada.")
                failed_images.append(file_path)

        progress_bar["value"] = i + 1
        root.update_idletasks()

    messagebox.showinfo("Resultados", f'Total de códigos de barras que comienzan con 8: {total_count}\n'
                                      f'Total de códigos de autorización que comienzan con 0: {total_autorizacion_count}')
    result_file_path = save_results(valid_barcodes, valid_autorizaciones, directory_to_use)
    if failed_images:
        save_failed_images(failed_images, directory_to_use)

    # Enviar resultados a la base de datos
    upload_progress_bar["maximum"] = len(valid_barcodes) + len(valid_autorizaciones)
    send_to_database(valid_barcodes, valid_autorizaciones, selected_farmacia.get(), failed_images)

# def enhance_image(image, attempt):
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     if attempt == 1:
#         gray = cv2.equalizeHist(gray)
#     elif attempt == 2:
#         gray = cv2.medianBlur(gray, 3)
#     elif attempt == 3:
#         kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
#         gray = cv2.filter2D(gray, -1, kernel)
#     elif attempt == 4:
#         gray = cv2.GaussianBlur(gray, (5, 5), 0)
#     _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#     return thresh

def enhance_image(image, attempt):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if attempt == 1:
        gray = cv2.equalizeHist(gray)
    elif attempt == 2:
        gray = cv2.medianBlur(gray, 3)
    elif attempt == 3:
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        gray = cv2.filter2D(gray, -1, kernel)
    elif attempt == 4:
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        _, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return gray



# def process_failed_image(image_path):
#     image = cv2.imread(image_path)
#     height, width = image.shape[:2]
#     cropped_image = image[0:int(height * 0.2), 0:width]
#     count = 0
#     autorizacion_count = 0
#     barcode = None
#     autorizacion = None
#     try:
#         for sigma in [1, 2, 3]:
#             blurred = cv2.GaussianBlur(cropped_image, (0, 0), sigma)
#             unsharp_image = cv2.addWeighted(cropped_image, 1.5, blurred, -0.5, 0)
#             for attempt in range(1, 5):
#                 enhanced_image = enhance_image(unsharp_image, attempt)
#                 for angle in [0, 90, 180, 270]:
#                     rotated_image = rotate_image(unsharp_image, angle)
#                     rotated_enhanced_image = rotate_image(enhanced_image, angle)
#                     barcodes = decode(rotated_image, symbols=[ZBarSymbol.CODE128, ZBarSymbol.CODE39, ZBarSymbol.EAN13, ZBarSymbol.EAN8, ZBarSymbol.PDF417])
#                     barcodes += decode(rotated_enhanced_image, symbols=[ZBarSymbol.CODE128, ZBarSymbol.CODE39, ZBarSymbol.EAN13, ZBarSymbol.EAN8, ZBarSymbol.PDF417])
#                     for barcode_obj in barcodes:
#                         barcode_data = barcode_obj.data.decode('utf-8')
#                         if barcode_data.startswith('8'):
#                             print(f'Código de barras: {barcode_data}')
#                             count += 1
#                             barcode = barcode_data
#                         elif barcode_data.startswith('0'):
#                             print(f'Código de autorización: {barcode_data}')
#                             autorizacion_count += 1
#                             autorizacion = barcode_data
#                         if barcode or autorizacion:
#                             break
#                     if barcode or autorizacion:
#                         break
#                 if barcode or autorizacion:
#                     break
#             if barcode or autorizacion:
#                 break
#         if not barcode and not autorizacion:
#             kernel = np.ones((5,5),np.uint8)
#             morph_image = cv2.morphologyEx(cropped_image, cv2.MORPH_CLOSE, kernel)
#             for attempt in range(1, 5):
#                 enhanced_image = enhance_image(morph_image, attempt)
#                 for angle in [0, 90, 180, 270]:
#                     rotated_image = rotate_image(morph_image, angle)
#                     rotated_enhanced_image = rotate_image(enhanced_image, angle)
#                     barcodes = decode(rotated_image, symbols=[ZBarSymbol.CODE128, ZBarSymbol.CODE39, ZBarSymbol.EAN13, ZBarSymbol.EAN8, ZBarSymbol.PDF417])
#                     barcodes += decode(rotated_enhanced_image, symbols=[ZBarSymbol.CODE128, ZBarSymbol.CODE39, ZBarSymbol.EAN13, ZBarSymbol.EAN8, ZBarSymbol.PDF417])
#                     for barcode_obj in barcodes:
#                         barcode_data = barcode_obj.data.decode('utf-8')
#                         if barcode_data.startswith('8'):
#                             print(f'Código de barras: {barcode_data}')
#                             count += 1
#                             barcode = barcode_data
#                         elif barcode_data.startswith('0'):
#                             print(f'Código de autorización: {barcode_data}')
#                             autorizacion_count += 1
#                             autorizacion = barcode_data
#                         if barcode or autorizacion:
#                             break
#                     if barcode or autorizacion:
#                         break
#                 if barcode or autorizacion:
#                     break
#             if not barcode and not autorizacion:
#                 cropped_and_resized_image = resize_and_crop(image)
#                 for attempt in range(1, 5):
#                     enhanced_image = enhance_image(cropped_and_resized_image, attempt)
#                     for angle in [0, 90, 180, 270]:
#                         rotated_image = rotate_image(cropped_and_resized_image, angle)
#                         rotated_enhanced_image = rotate_image(enhanced_image, angle)
#                         barcodes = decode(rotated_image, symbols=[ZBarSymbol.CODE128, ZBarSymbol.CODE39, ZBarSymbol.EAN13, ZBarSymbol.EAN8, ZBarSymbol.PDF417])
#                         barcodes += decode(rotated_enhanced_image, symbols=[ZBarSymbol.CODE128, ZBarSymbol.CODE39, ZBarSymbol.EAN13, ZBarSymbol.EAN8, ZBarSymbol.PDF417])
#                         for barcode_obj in barcodes:
#                             barcode_data = barcode_obj.data.decode('utf-8')
#                             if barcode_data.startswith('8'):
#                                 print(f'Código de barras: {barcode_data}')
#                                 count += 1
#                                 barcode = barcode_data
#                             elif barcode_data.startswith('0'):
#                                 print(f'Código de autorización: {barcode_data}')
#                                 autorizacion_count += 1
#                                 autorizacion = barcode_data
#                             if barcode or autorizacion:
#                                 break
#                         if barcode or autorizacion:
#                             break
#                     if barcode or autorizacion:
#                         break
#             if not barcode and not autorizacion:
#                 print(f'No se encontró un código de barras válido en la imagen {image_path} incluso después de técnicas adicionales')
#     except Exception as e:
#         print(f'Error procesando la imagen {image_path} con técnicas adicionales: {e}')
#     return count, autorizacion_count, barcode, autorizacion

def process_failed_image(image_path):
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"Error: No se pudo cargar la imagen {image_path}. Verifica la ruta o la integridad del archivo.")
        return 0, 0, None, None

    height, width = image.shape[:2]
    cropped_image = image[0:int(height * 0.2), 0:width]
    count = 0
    autorizacion_count = 0
    barcode = None
    autorizacion = None
    try:
        for sigma in [1, 2, 3]:
            blurred = cv2.GaussianBlur(cropped_image, (0, 0), sigma)
            unsharp_image = cv2.addWeighted(cropped_image, 1.5, blurred, -0.5, 0)
            for attempt in range(1, 5):
                enhanced_image = enhance_image(unsharp_image, attempt)
                for angle in [0, 90, 180, 270]:
                    rotated_image = rotate_image(unsharp_image, angle)
                    rotated_enhanced_image = rotate_image(enhanced_image, angle)
                    barcodes = decode(rotated_image, symbols=[
                        ZBarSymbol.CODE128, ZBarSymbol.CODE39, ZBarSymbol.EAN13, ZBarSymbol.EAN8, ZBarSymbol.PDF417,
                        ZBarSymbol.QRCODE, ZBarSymbol.ISBN10, ZBarSymbol.ISBN13, ZBarSymbol.I25, ZBarSymbol.UPCA,
                        ZBarSymbol.UPCE
                    ])
                    barcodes += decode(rotated_enhanced_image, symbols=[ZBarSymbol.CODE128, ZBarSymbol.CODE39, ZBarSymbol.EAN13, ZBarSymbol.EAN8, ZBarSymbol.PDF417])
                    for barcode_obj in barcodes:
                        barcode_data = barcode_obj.data.decode('utf-8')
                        if barcode_data.startswith('8'):
                            print(f'Código de barras: {barcode_data}')
                            count += 1
                            barcode = barcode_data
                        elif barcode_data.startswith('0'):
                            print(f'Código de autorización: {barcode_data}')
                            autorizacion_count += 1
                            autorizacion = barcode_data
                        if barcode or autorizacion:
                            break
                    if barcode or autorizacion:
                        break
                if barcode or autorizacion:
                    break
            if barcode or autorizacion:
                break
        if not barcode and not autorizacion:
            kernel = np.ones((5,5),np.uint8)
            morph_image = cv2.morphologyEx(cropped_image, cv2.MORPH_CLOSE, kernel)
            for attempt in range(1, 5):
                enhanced_image = enhance_image(morph_image, attempt)
                for angle in [0, 90, 180, 270]:
                    rotated_image = rotate_image(morph_image, angle)
                    rotated_enhanced_image = rotate_image(enhanced_image, angle)
                    barcodes = decode(rotated_image, symbols=[ZBarSymbol.CODE128, ZBarSymbol.CODE39, ZBarSymbol.EAN13, ZBarSymbol.EAN8, ZBarSymbol.PDF417])
                    barcodes += decode(rotated_enhanced_image, symbols=[ZBarSymbol.CODE128, ZBarSymbol.CODE39, ZBarSymbol.EAN13, ZBarSymbol.EAN8, ZBarSymbol.PDF417])
                    for barcode_obj in barcodes:
                        barcode_data = barcode_obj.data.decode('utf-8')
                        if barcode_data.startswith('8'):
                            print(f'Código de barras: {barcode_data}')
                            count += 1
                            barcode = barcode_data
                        elif barcode_data.startswith('0'):
                            print(f'Código de autorización: {barcode_data}')
                            autorizacion_count += 1
                            autorizacion = barcode_data
                        if barcode or autorizacion:
                            break
                    if barcode or autorizacion:
                        break
                if barcode or autorizacion:
                    break
            if not barcode and not autorizacion:
                print(f'No se encontró un código de barras válido en la imagen {image_path} incluso después de técnicas adicionales')
    except Exception as e:
        print(f'Error procesando la imagen {image_path} con técnicas adicionales: {e}')
    return count, autorizacion_count, barcode, autorizacion

# def read_barcodes_from_image(image_path):
#     image = cv2.imread(image_path)
#     height, width = image.shape[:2]
#     cropped_image = image[0:int(height * 0.2), 0:width]
#     count = 0
#     autorizacion_count = 0
#     barcode = None
#     autorizacion = None
#     try:
#         angles = [0, 90, 180, 270]
#         for attempt in range(1, 5):
#             enhanced_image = enhance_image(cropped_image, attempt)
#             for angle in angles:
#                 rotated_image = rotate_image(cropped_image, angle)
#                 rotated_enhanced_image = rotate_image(enhanced_image, angle)
#                 barcodes = decode(rotated_image, symbols=[ZBarSymbol.CODE128, ZBarSymbol.CODE39, ZBarSymbol.EAN13, ZBarSymbol.EAN8, ZBarSymbol.PDF417])
#                 barcodes += decode(rotated_enhanced_image, symbols=[ZBarSymbol.CODE128, ZBarSymbol.CODE39, ZBarSymbol.EAN13, ZBarSymbol.EAN8, ZBarSymbol.PDF417])
#                 for barcode_obj in barcodes:
#                     barcode_data = barcode_obj.data.decode('utf-8')
#                     if barcode_data.startswith('8'):
#                         print(f'Código de barras: {barcode_data}')
#                         count += 1
#                         barcode = barcode_data
#                     elif barcode_data.startswith('0'):
#                         print(f'Código de autorización: {barcode_data}')
#                         autorizacion_count += 1
#                         autorizacion = barcode_data
#                     if barcode or autorizacion:
#                         break
#                 if barcode or autorizacion:
#                     break
#             if barcode or autorizacion:
#                 break
#         if not barcode and not autorizacion:
#             print(f'No se encontró un código de barras válido en la imagen {image_path}')
#     except Exception as e:
#         print(f'Error procesando la imagen {image_path}: {e}')
#     return count, autorizacion_count, barcode, autorizacion

# def read_barcodes_from_image(image_path):
#     image = cv2.imread(image_path)
    
#     if image is None:
#         print(f"Error: No se pudo cargar la imagen {image_path}. Verifica la ruta o la integridad del archivo.")
#         return 0, 0, None, None

#     height, width = image.shape[:2]
#     cropped_image = image[0:int(height * 0.2), 0:width]
#     count = 0
#     autorizacion_count = 0
#     barcode = None
#     autorizacion = None
#     try:
#         angles = [0, 90, 180, 270]
#         for attempt in range(1, 5):
#             enhanced_image = enhance_image(cropped_image, attempt)
#             for angle in angles:
#                 rotated_image = rotate_image(cropped_image, angle)
#                 rotated_enhanced_image = rotate_image(enhanced_image, angle)
#                 barcodes = decode(rotated_image, symbols=[ZBarSymbol.CODE128, ZBarSymbol.CODE39, ZBarSymbol.EAN13, ZBarSymbol.EAN8, ZBarSymbol.PDF417])
#                 barcodes += decode(rotated_enhanced_image, symbols=[ZBarSymbol.CODE128, ZBarSymbol.CODE39, ZBarSymbol.EAN13, ZBarSymbol.EAN8, ZBarSymbol.PDF417])
#                 for barcode_obj in barcodes:
#                     barcode_data = barcode_obj.data.decode('utf-8')
#                     if barcode_data.startswith('8'):
#                         print(f'Código de barras: {barcode_data}')
#                         count += 1
#                         barcode = barcode_data
#                     elif barcode_data.startswith('0'):
#                         print(f'Código de autorización: {barcode_data}')
#                         autorizacion_count += 1
#                         autorizacion = barcode_data
#                     if barcode or autorizacion:
#                         break
#                 if barcode or autorizacion:
#                     break
#             if barcode or autorizacion:
#                 break
#         if not barcode and not autorizacion:
#             print(f'No se encontró un código de barras válido en la imagen {image_path}')
#     except Exception as e:
#         print(f'Error procesando la imagen {image_path}: {e}')
#     return count, autorizacion_count, barcode, autorizacion
def read_barcodes_from_image(image_path):
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"Error: No se pudo cargar la imagen {image_path}. Verifica la ruta o la integridad del archivo.")
        return 0, 0, None, None

    height, width = image.shape[:2]
    cropped_image = image[0:int(height * 0.2), 0:width]
    count = 0
    autorizacion_count = 0
    barcode = None
    autorizacion = None
    try:
        angles = [0, 90, 180, 270]
        for attempt in range(1, 5):
            enhanced_image = enhance_image(cropped_image, attempt)
            for angle in angles:
                rotated_image = rotate_image(cropped_image, angle)
                rotated_enhanced_image = rotate_image(enhanced_image, angle)
                barcodes = decode(rotated_image, symbols=[ZBarSymbol.CODE128, ZBarSymbol.CODE39, ZBarSymbol.EAN13, ZBarSymbol.EAN8, ZBarSymbol.PDF417])
                barcodes += decode(rotated_enhanced_image, symbols=[ZBarSymbol.CODE128, ZBarSymbol.CODE39, ZBarSymbol.EAN13, ZBarSymbol.EAN8, ZBarSymbol.PDF417])
                for barcode_obj in barcodes:
                    barcode_data = barcode_obj.data.decode('utf-8')
                    if barcode_data.startswith('8'):
                        print(f'Código de barras: {barcode_data}')
                        count += 1
                        barcode = barcode_data
                    elif barcode_data.startswith('0'):
                        print(f'Código de autorización: {barcode_data}')
                        autorizacion_count += 1
                        autorizacion = barcode_data
                    if barcode or autorizacion:
                        break
                if barcode or autorizacion:
                    break
            if barcode or autorizacion:
                break
        if not barcode and not autorizacion:
            print(f'No se encontró un código de barras válido en la imagen {image_path}')
    except Exception as e:
        print(f'Error procesando la imagen {image_path}: {e}')
    return count, autorizacion_count, barcode, autorizacion


def rotate_image(image, angle):
    height, width = image.shape[:2]
    center = (width // 2, height // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated_image = cv2.warpAffine(image, matrix, (width, height))
    return rotated_image

def resize_and_crop(image):
    height, width = image.shape[:2]
    cropped_image = image[0:int(height * 0.2), 0:width]
    resized_image = cv2.resize(cropped_image, (width * 2, height * 2))
    return resized_image

def save_results(barcodes, autorizaciones, directory):
    today = datetime.now().strftime("%Y-%m-%d")
    folder_name = f"{today} - {selected_farmacia.get()}"
    save_path = os.path.join(directory, folder_name)
    os.makedirs(save_path, exist_ok=True)
    result_file_path = os.path.join(save_path, 'resultados_barcodes.txt')
    with open(result_file_path, 'w') as file:
        for _, barcode in barcodes:
            file.write(f'{barcode}\n')
    autorizaciones_file_path = os.path.join(save_path, 'resultados_autorizaciones.txt')
    with open(autorizaciones_file_path, 'w') as file:
        for _, autorizacion in autorizaciones:
            file.write(f'{autorizacion}\n')
    print(f'Resultados guardados en {result_file_path} y {autorizaciones_file_path}')
    return result_file_path

def save_failed_images(failed_images, directory):
    today = datetime.now().strftime("%Y-%m-%d")
    folder_name = f"{today} - {selected_farmacia.get()}"
    save_path = os.path.join(directory, folder_name, 'imagenes_fallidas')
    os.makedirs(save_path, exist_ok=True)
    for file_path in failed_images:
        shutil.copy(file_path, save_path)
    print(f'Imágenes fallidas guardadas en la carpeta {save_path}')

def send_to_database(barcodes, autorizaciones, sucursal, failed_images):
    # Conexión a la base de datos
    conn = psycopg2.connect(
        "postgresql://postgres:TDXQSEjHNRoHGqlQmcuNuSClWoUlUujB@viaduct.proxy.rlwy.net:45221/railway"
    )
    cur = conn.cursor()

    sucursal_numero = get_sucursal_number(sucursal)
    fecha_creacion = date.today()

    print(f"Subiendo datos a la base de datos para la sucursal {sucursal} con número {sucursal_numero}")

    total_entries = len(barcodes) + len(autorizaciones)
    for i, (file_path, barcode) in enumerate(barcodes):
        try:
            print(f"Subiendo código de barras: {barcode}")
            cur.execute(
                """
                INSERT INTO recetas (numero, estado, sucursales, FechaCreacion)
                VALUES (%s, %s, %s, %s);
                """,
                [barcode, "P", sucursal_numero, fecha_creacion]
            )
        except Exception as e:
            print(f"Error al subir el código de barras {barcode}: {e}")
            failed_images.append(file_path)
            conn.rollback()  # Rollback para poder continuar con la próxima inserción
        else:
            conn.commit()  # Commit solo si la inserción tuvo éxito
        upload_progress_bar["value"] = i + 1
        root.update_idletasks()

    for i, (file_path, autorizacion) in enumerate(autorizaciones):
        try:
            print(f"Subiendo código de autorización: {autorizacion}")
            cur.execute(
                """
                INSERT INTO recetas (numero, autorizacion, estado, sucursales, FechaCreacion)
                VALUES (%s, %s, %s, %s, %s);
                """,
                [autorizacion, autorizacion, "P", sucursal_numero, fecha_creacion]
            )
        except Exception as e:
            print(f"Error al subir el código de autorización {autorizacion}: {e}")
            failed_images.append(file_path)
            conn.rollback()  # Rollback para poder continuar con la próxima inserción
        else:
            conn.commit()  # Commit solo si la inserción tuvo éxito
        upload_progress_bar["value"] = len(barcodes) + i + 1
        root.update_idletasks()

    cur.close()
    conn.close()

def create_gui():
    global root, file_count, progress_bar, file_paths, save_directory, manual_save_directory, save_directory_label, selected_farmacia
    global start_date_entry, end_date_entry, failed_images, upload_progress_bar

    file_paths = []
    save_directory = ""
    manual_save_directory = ""
    failed_images = []

    root = Tk()
    root.title("Lector de Códigos de Barras")
    root.geometry("800x500")
    root.resizable(True, True)

    style = ttk.Style(root)
    style.configure('TButton', font=('Helvetica', 12))
    style.configure('TLabel', font=('Helvetica', 12))

    file_count = StringVar()
    file_count.set("No se seleccionaron archivos.")

    save_directory_label = StringVar()
    save_directory_label.set("No se seleccionó un directorio de guardado.")

    selected_farmacia = StringVar(root)
    selected_farmacia.set("Seleccionar Farmacia")

    def open_date_picker():
        global start_date_entry, end_date_entry

        def set_date():
            start_date_str = start_date_entry.get_date()
            end_date_str = end_date_entry.get_date()
            try:
                start = datetime.strptime(start_date_str, '%Y-%m-%d')
                end = datetime.strptime(end_date_str, '%Y-%m-%d')
                if start > end:
                    messagebox.showerror("Error", "La fecha de inicio debe ser anterior a la fecha de fin.")
                else:
                    date_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha incorrecto.")

        date_window = Toplevel(root)
        date_window.title("Seleccionar Rango de Fechas")
        date_window.geometry("450x650")
        date_window.resizable(True, True)

        start_label = ttk.Label(date_window, text="Fecha de Inicio:")
        start_label.pack(pady=5)
        start_date_entry = Calendar(date_window, selectmode='day', date_pattern='yyyy-mm-dd')
        start_date_entry.pack(pady=5)

        end_label = ttk.Label(date_window, text="Fecha de Fin:")
        end_label.pack(pady=5)
        end_date_entry = Calendar(date_window, selectmode='day', date_pattern='yyyy-mm-dd')
        end_date_entry.pack(pady=5)

        set_date_button = ttk.Button(date_window, text="Establecer Fecha", command=set_date)
        set_date_button.pack(pady=10)

        fullscreen_button = ttk.Button(date_window, text="Pantalla Completa", command=lambda: date_window.attributes("-fullscreen", True))
        fullscreen_button.pack(pady=10)

        exit_fullscreen_button = ttk.Button(date_window, text="Salir de Pantalla Completa", command=lambda: date_window.attributes("-fullscreen", False))
        exit_fullscreen_button.pack(pady=10)
        
        
    # def update_save_directory(*args):
    #     global save_directory
    #     selected_code = farmacias[selected_farmacia.get()]
    #     # Define la ruta base como la unidad de red F:
    #     red_base = r"F:"
    #     resultados_path = os.path.join(red_base, 'resultados')
    #     save_directory = os.path.join(resultados_path, selected_farmacia.get())

    #     # Verificar si el directorio existe
    #     if not os.path.exists(resultados_path):
    #         messagebox.showerror("Error", f"No se encontró el directorio de guardado: {resultados_path}")
    #         save_directory_label.set("Directorio de guardado no encontrado.")
    #     else:
    #         save_directory_label.set(f"Directorio de guardado: {save_directory}")
    def update_save_directory(*args):
        global save_directory
        # Ruta de destino fija configurada a la carpeta en el escritorio
        save_directory = r"C:\Users\Administrador\Desktop\resultados"
        save_directory_label.set(f"Directorio de guardado: {save_directory}")




    selected_farmacia.trace("w", update_save_directory)

    date_button = ttk.Button(root, text="Seleccionar Rango de Fechas", command=open_date_picker)
    date_button.pack(pady=10)

    select_button = ttk.Button(root, text="Seleccionar Archivos desde Sucursal", command=select_images_from_sucursal)
    select_button.pack(pady=10)

    farmacia_menu = ttk.OptionMenu(root, selected_farmacia, *farmacias.keys())
    farmacia_menu.pack(pady=10)

    # save_directory_button = ttk.Button(root, text="Seleccionar Directorio de Guardado Manual", command=select_save_directory)
    # save_directory_button.pack(pady=10)

    save_directory_label_widget = ttk.Label(root, textvariable=save_directory_label)
    save_directory_label_widget.pack(pady=10)

    process_button = ttk.Button(root, text="Procesar Imágenes", command=lambda: threading.Thread(target=process_images).start())
    process_button.pack(pady=10)

    file_count_label = ttk.Label(root, textvariable=file_count)
    file_count_label.pack(pady=10)

    # Barra de progreso para el procesamiento de imágenes
    process_label = ttk.Label(root, text="Progreso de Procesamiento de Imágenes")
    process_label.pack(pady=5)
    progress_bar = ttk.Progressbar(root, orient="horizontal", mode="determinate", length=400)
    progress_bar.pack(pady=10)

    # Barra de progreso para la subida a la base de datos
    upload_label = ttk.Label(root, text="Progreso de Subida a la Base de Datos")
    upload_label.pack(pady=5)
    upload_progress_bar = ttk.Progressbar(root, orient="horizontal", mode="determinate", length=400)
    upload_progress_bar.pack(pady=10)


    root.mainloop()

create_gui()
