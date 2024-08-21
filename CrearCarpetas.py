import os
import customtkinter as ctk
from tkinter import messagebox

# Diccionario de farmacias con sus respectivos códigos
farmacias = {
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

def check_folders():
    desktop_dir = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    resultados_dir = os.path.join(desktop_dir, "resultados")
    
    all_exist = all(os.path.exists(os.path.join(resultados_dir, codigo)) for codigo in farmacias.values())
    if all_exist:
        create_button.configure(state="disabled", text="Carpetas ya existen", fg_color="red")
    else:
        create_button.configure(state="normal", text="Crear Carpetas", fg_color="green")

def create_folders():
    desktop_dir = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    resultados_dir = os.path.join(desktop_dir, "resultados")
    if not os.path.exists(resultados_dir):
        os.makedirs(resultados_dir)
    
    already_exists = []
    for codigo in farmacias.values():
        carpeta_path = os.path.join(resultados_dir, codigo)
        if not os.path.exists(carpeta_path):
            os.makedirs(carpeta_path)
        else:
            already_exists.append(codigo)
    
    if already_exists:
        messagebox.showwarning("Advertencia", f"Las siguientes carpetas ya existen: {', '.join(already_exists)}")
    else:
        messagebox.showinfo("Éxito", "Todas las carpetas han sido creadas.")
    
    check_folders()

def main():
    global create_button
    
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.title("Creador de Carpetas")
    root.geometry("400x200")
    root.resizable(False, False)

    label = ctk.CTkLabel(root, text="Pulse el botón para crear las carpetas", font=("Helvetica", 14))
    label.pack(pady=20)

    create_button = ctk.CTkButton(root, text="Crear Carpetas", font=("Helvetica", 14), command=create_folders)
    create_button.pack(pady=20)
    
    check_folders()
    
    root.mainloop()

if __name__ == "__main__":
    main()
