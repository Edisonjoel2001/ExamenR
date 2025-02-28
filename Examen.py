from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
import re
import time  # Importar el módulo time para obtener la hora y fecha actuales

# Conexión a la base de datos
def conectar_db():
    conn = sqlite3.connect("alumnos.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alumnos (
            dni TEXT PRIMARY KEY,
            apellidos TEXT,
            nombre TEXT,
            nota REAL,
            calificacion TEXT
        )
    """)
    conn.commit()
    conn.close()


conectar_db()


# Clase de Login
class Login:
    def __init__(self, root, callback):
        self.root = root
        self.root.title("Bienvenido Maestro")
        self.root.geometry("300x200")
        self.callback = callback

        self.root.config(bg="#f0f0f0")  # Fondo suave para el login

        tk.Label(root, text="DNI:", font=("Times New Roman", 14), bg="#f0f0f0").pack(pady=10)
        self.dni_entry = tk.Entry(root, font=("Times New Roman", 14), bd=2, relief="solid")
        self.dni_entry.pack(pady=5)

        tk.Button(root, text="Ingresar", font=("Times New Roman", 14), bg="#4CAF50", fg="white", command=self.verificar_login).pack(pady=10)

    def verificar_login(self):
        dni = self.dni_entry.get()
        if not re.fullmatch(r"\d{10}", dni):
            messagebox.showerror("Error", "El DNI debe tener exactamente 10 dígitos.")
            return

        self.root.destroy()
        self.callback()


# Interfaz para la gestión de alumnos
class GestionAlumnos(ABC):
    @abstractmethod
    def mostrar_alumnos(self):
        pass

    @abstractmethod
    def introducir_alumno(self, dni, apellidos, nombre, nota):
        pass

    @abstractmethod
    def eliminar_alumno(self, dni):
        pass

    @abstractmethod
    def consultar_nota(self, dni):
        pass

    @abstractmethod
    def modificar_nota(self, dni, nueva_nota):
        pass

    @abstractmethod
    def mostrar_suspensos(self):
        pass

    @abstractmethod
    def mostrar_aprobados(self):
        pass

    @abstractmethod
    def mostrar_candidatos_mh(self):
        pass


# Clase principal que maneja los alumnos
class Gestion(GestionAlumnos):
    def __init__(self):
        self.conectar_db()

    def conectar_db(self):
        self.conn = sqlite3.connect("alumnos.db")
        self.cursor = self.conn.cursor()

    def cerrar_db(self):
        self.conn.close()

    def calcular_calificacion(self, nota):
        if nota < 5:
            return "SS"
        elif 5 <= nota < 7:
            return "AP"
        elif 7 <= nota < 9:
            return "NT"
        else:
            return "SB"

    def mostrar_alumnos(self):
        self.cursor.execute("SELECT * FROM alumnos")
        alumnos = self.cursor.fetchall()
        resultado = "\n".join(
            f"{dni} {apellidos}, {nombre} {nota} {calificacion}" for dni, apellidos, nombre, nota, calificacion in
            alumnos)
        messagebox.showinfo("Lista de Alumnos", resultado if resultado else "No hay alumnos registrados")

    def introducir_alumno(self, dni, apellidos, nombre, nota):
        if not re.fullmatch(r"\d{10}", dni):
            messagebox.showerror("Error", "El DNI debe tener exactamente 10 dígitos.")
            return

        self.cursor.execute("SELECT * FROM alumnos WHERE dni = ?", (dni,))
        if self.cursor.fetchone():
            messagebox.showerror("Error", "Ya existe un alumno con este DNI.")
            return

        calificacion = self.calcular_calificacion(nota)
        self.cursor.execute("INSERT INTO alumnos VALUES (?, ?, ?, ?, ?)", (dni, apellidos, nombre, nota, calificacion))
        self.conn.commit()
        messagebox.showinfo("Éxito", "Alumno agregado correctamente.")

    def eliminar_alumno(self, dni):
        self.cursor.execute("DELETE FROM alumnos WHERE dni = ?", (dni,))
        self.conn.commit()
        messagebox.showinfo("Éxito", "Alumno eliminado.")

    def consultar_nota(self, dni):
        self.cursor.execute("SELECT nota, calificacion FROM alumnos WHERE dni = ?", (dni,))
        resultado = self.cursor.fetchone()
        if resultado:
            messagebox.showinfo("Consulta", f"Nota: {resultado[0]}, Calificación: {resultado[1]}")
        else:
            messagebox.showerror("Error", "No existe un alumno con este DNI.")

    def modificar_nota(self, dni, nueva_nota):
        nueva_calificacion = self.calcular_calificacion(nueva_nota)
        self.cursor.execute("UPDATE alumnos SET nota = ?, calificacion = ? WHERE dni = ?",
                            (nueva_nota, nueva_calificacion, dni))
        self.conn.commit()
        messagebox.showinfo("Éxito", "Nota modificada.")

    def mostrar_suspensos(self):
        self.cursor.execute("SELECT * FROM alumnos WHERE calificacion = 'SS'")
        alumnos = self.cursor.fetchall()
        resultado = "\n".join(
            f"{dni} {apellidos}, {nombre} {nota} {calificacion}" for dni, apellidos, nombre, nota, calificacion in
            alumnos)
        messagebox.showinfo("Suspensos", resultado if resultado else "No hay alumnos suspendidos.")

    def mostrar_aprobados(self):
        self.cursor.execute("SELECT * FROM alumnos WHERE calificacion = 'AP' OR calificacion = 'NT' OR calificacion = 'SB'")
        alumnos = self.cursor.fetchall()
        resultado = "\n".join(
            f"{dni} {apellidos}, {nombre} {nota} {calificacion}" for dni, apellidos, nombre, nota, calificacion in
            alumnos)
        messagebox.showinfo("Aprobados", resultado if resultado else "No hay alumnos aprobados.")

    def mostrar_candidatos_mh(self):
        self.cursor.execute("SELECT * FROM alumnos WHERE calificacion = 'SB'")
        alumnos = self.cursor.fetchall()
        resultado = "\n".join(
            f"{dni} {apellidos}, {nombre} {nota} {calificacion}" for dni, apellidos, nombre, nota, calificacion in
            alumnos)
        messagebox.showinfo("Candidatos a Matrícula de Honor", resultado if resultado else "No hay candidatos.")


# Clase principal de la aplicación
class Aplicacion:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Calificaciones")
        self.gestion = Gestion()

        self.root.config(bg="#f0f0f0")  # Fondo suave para la ventana principal

        frame = tk.Frame(root, padx=20, pady=20, bg="#f0f0f0")
        frame.pack()

        tk.Label(frame, text="Menú Principal", font=("Times New Roman", 14, "bold"), bg="#f0f0f0", fg="#333").pack(pady=10)

        # Hora y fecha
        self.hora_label = tk.Label(frame, font=("Times New Roman", 14), bg="#f0f0f0", fg="#333")
        self.hora_label.pack(pady=5)

        # Botones del menú con colores atractivos
        tk.Button(frame, text="Agregar Alumno", font=("Times New Roman", 14), bg="#8BC34A", fg="white", command=self.agregar_alumno).pack(fill="x", pady=5)
        tk.Button(frame, text="Mostrar Alumnos", font=("Times New Roman", 14), bg="#4CAF50", fg="white", command=self.gestion.mostrar_alumnos).pack(fill="x", pady=5)
        tk.Button(frame, text="Mostrar Aprobados", font=("Times New Roman", 14), bg="#2196F3", fg="white", command=self.gestion.mostrar_aprobados).pack(fill="x", pady=5)
        tk.Button(frame, text="Mostrar Suspensos", font=("Times New Roman", 14), bg="#FF5722", fg="white", command=self.gestion.mostrar_suspensos).pack(fill="x", pady=5)
        tk.Button(frame, text="Mostrar Candidatos a Matrícula de Honor", font=("Times New Roman", 14), bg="#9C27B0", fg="white", command=self.gestion.mostrar_candidatos_mh).pack(fill="x", pady=5)
        tk.Button(frame, text="Salir", font=("Times New Roman", 14), bg="#f44336", fg="white", command=root.quit).pack(fill="x", pady=10)



        # Actualizar hora y fecha cada segundo
        self.actualizar_hora()

    def actualizar_hora(self):
        # Obtener hora y fecha actual
        tiempo_actual = time.strftime("%Y-%m-%d %H:%M:%S")
        self.hora_label.config(text=tiempo_actual)
        self.root.after(1000, self.actualizar_hora)  # Actualizar cada 1000 ms (1 segundo)

    def agregar_alumno(self):
        def guardar_alumno():
            dni = dni_entry.get()
            apellidos = apellidos_entry.get()
            nombre = nombre_entry.get()
            try:
                nota = float(nota_entry.get())
                if nota < 0 or nota > 10:
                    messagebox.showerror("Error", "La nota debe estar entre 0 y 10.")
                    return
            except ValueError:
                messagebox.showerror("Error", "La nota debe ser un número.")
                return

            self.gestion.introducir_alumno(dni, apellidos, nombre, nota)
            add_window.destroy()

        # Crear ventana emergente para agregar alumno
        add_window = tk.Toplevel(self.root)
        add_window.title("Agregar Alumno")
        add_window.geometry("300x250")
        add_window.config(bg="#f0f0f0")

        tk.Label(add_window, text="DNI:", font=("Arial", 12), bg="#f0f0f0").pack(pady=5)
        dni_entry = tk.Entry(add_window, font=("Arial", 12), bd=2, relief="solid")
        dni_entry.pack(pady=5)

        tk.Label(add_window, text="Apellidos:", font=("Arial", 12), bg="#f0f0f0").pack(pady=5)
        apellidos_entry = tk.Entry(add_window, font=("Arial", 12), bd=2, relief="solid")
        apellidos_entry.pack(pady=5)

        tk.Label(add_window, text="Nombre:", font=("Arial", 12), bg="#f0f0f0").pack(pady=5)
        nombre_entry = tk.Entry(add_window, font=("Arial", 12), bd=2, relief="solid")
        nombre_entry.pack(pady=5)

        tk.Label(add_window, text="Nota:", font=("Arial", 12), bg="#f0f0f0").pack(pady=5)
        nota_entry = tk.Entry(add_window, font=("Arial", 12), bd=2, relief="solid")
        nota_entry.pack(pady=5)

        tk.Button(add_window, text="Guardar", font=("Arial", 12), bg="#4CAF50", fg="white", command=guardar_alumno).pack(pady=10)
        tk.Button(add_window, text="Cancelar", font=("Arial", 12), bg="#f44336", fg="white", command=add_window.destroy).pack(pady=5)


# Ejecutar la aplicación con login
if __name__ == "__main__":
    def iniciar_app():
        root = tk.Tk()
        app = Aplicacion(root)
        root.mainloop()


    login_root = tk.Tk()
    login = Login(login_root, iniciar_app)
    login_root.mainloop()