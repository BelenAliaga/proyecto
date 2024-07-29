import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk  # Asegúrate de que Pillow esté instalado
import matplotlib
matplotlib.use('TkAgg')  # Configurar el backend de matplotlib para Tkinter
import matplotlib.pyplot as plt

class ETLGUI:
    def __init__(self, master):
        self.master = master
        master.title("Proceso ETL")
        master.geometry("600x400")

        # Widgets
        self.folder_path = tk.StringVar()
        self.folder_label = tk.Label(master, text="Carpeta de datos:")
        self.folder_entry = tk.Entry(master, textvariable=self.folder_path, width=50)
        self.folder_button = tk.Button(master, text="Seleccionar", command=self.select_folder)

        self.col_range_label = tk.Label(master, text="Rango de columnas (ej. A:D):")
        self.col_range_entry = tk.Entry(master)

        self.start_row_label = tk.Label(master, text="Fila inicial:")
        self.start_row_entry = tk.Entry(master)

        self.process_button = tk.Button(master, text="Procesar", command=self.process_data)

        self.progress_bar = ttk.Progressbar(master, orient="horizontal", length=300, mode="determinate")

        # Layout
        self.folder_label.pack(pady=5)
        self.folder_entry.pack(pady=5)
        self.folder_button.pack(pady=5)
        self.col_range_label.pack(pady=5)
        self.col_range_entry.pack(pady=5)
        self.start_row_label.pack(pady=5)
        self.start_row_entry.pack(pady=5)
        self.process_button.pack(pady=10)
        self.progress_bar.pack(pady=10)

    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        self.folder_path.set(folder_selected)

    def process_data(self):
        folder_path = self.folder_path.get()
        col_range = self.col_range_entry.get()
        try:
            start_row = int(self.start_row_entry.get()) - 1  # Ajustar para índice basado en 0
        except ValueError:
            messagebox.showerror("Error", "Fila inicial debe ser un número entero.")
            return

        if not folder_path or not col_range or start_row < 0:
            messagebox.showerror("Error", "Por favor, complete todos los campos correctamente.")
            return

        try:
            # Obtener la lista de archivos Excel en la carpeta
            excel_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx') and f.startswith('AvanceVentasINTI')]

            if not excel_files:
                messagebox.showerror("Error", "No se encontraron archivos Excel en la carpeta seleccionada.")
                return

            all_data = []
            self.progress_bar["maximum"] = len(excel_files)

            for i, file in enumerate(excel_files):
                file_path = os.path.join(folder_path, file)
                
                # Extraer año, mes y día del nombre del archivo
                date_str = file.split('.')[1:4]
                if len(date_str) < 3:
                    messagebox.showwarning("Advertencia", f"Nombre de archivo {file} no tiene formato esperado.")
                    continue
                year, month, day = date_str

                try:
                    df = pd.read_excel(file_path, sheet_name='ITEM_O', usecols=col_range, skiprows=start_row)
                except Exception as e:
                    messagebox.showerror("Error de Lectura", f"Error al leer el archivo {file_path}: {str(e)}")
                    continue

                # Añadir columnas de año, mes y día
                df['ANIO'] = year
                df['MES'] = month
                df['DIA'] = day

                all_data.append(df)

                # Actualizar la barra de progreso
                self.progress_bar["value"] = i + 1
                self.master.update_idletasks()

            # Consolidar todos los DataFrames
            final_df = pd.concat(all_data, ignore_index=True)

            # Exportar a Excel
            output_path = os.path.join(folder_path, 'Out.xlsx')
            final_df.to_excel(output_path, index=False)

            messagebox.showinfo("Éxito", f"Proceso completado. Archivo guardado en {output_path}")

            # Mostrar el DataFrame final
            self.show_dataframe(final_df)

            # Calcular y mostrar gráficos
            self.show_plots(final_df)

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error durante el proceso: {str(e)}")

    def show_dataframe(self, df):
        # Crear una nueva ventana para mostrar el DataFrame
        data_window = tk.Toplevel(self.master)
        data_window.title("Dataset Final")
        data_window.geometry("800x600")

        # Crear un widget Text para mostrar el DataFrame
        text_widget = tk.Text(data_window)
        text_widget.pack(expand=True, fill='both')

        # Insertar el DataFrame en el widget Text
        text_widget.insert(tk.END, df.to_string())

    def show_plots(self, df):
        # Seleccionar solo las columnas numéricas
        numeric_df = df.select_dtypes(include=['number'])

        # Verificar si hay datos numéricos
        if numeric_df.empty:
            messagebox.showwarning("Advertencia", "No se encontraron columnas numéricas para graficar.")
            return

        # Calcular promedios por columna
        column_averages = numeric_df.mean()

        # Ordenar promedios de menor a mayor y seleccionar los N más bajos
        top_n = 10  # Número de promedios más bajos a mostrar
        bottom_averages = column_averages.sort_values(ascending=True).head(top_n)

        if bottom_averages.empty:
            messagebox.showwarning("Advertencia", "No hay suficientes datos numéricos para mostrar los gráficos.")
            return

        try:
            # Crear una figura con subgráficos
            fig, axs = plt.subplots(2, 1, figsize=(10, 8))

            # Gráfico de barras
            bottom_averages.plot(kind='bar', ax=axs[0])
            axs[0].set_title('Bottom Promedios por Columna')
            axs[0].set_xlabel('Columnas')
            axs[0].set_ylabel('Promedio')

            # Gráfico de torta
            bottom_averages.plot(kind='pie', ax=axs[1], autopct='%1.1f%%')
            axs[1].set_title('Distribución de Bottom Promedios')

            plt.tight_layout()
            
            # Mostrar la figura en una ventana separada
            plt.show()  # No usar block=True

        except Exception as e:
            messagebox.showerror("Error de Visualización", f"Error al mostrar gráficos: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    etl_gui = ETLGUI(root)
    root.mainloop()
