from monitor_final import MonitorThread
import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import sys

monitor = MonitorThread()

def on_start():
monitor.start()
btn_start.config(state="disabled")
btn_stop.config(state="normal")

def on_stop():
monitor.stop()
btn_start.config(state="normal")
btn_stop.config(state="disabled")

def on_consultar():
def run():
subprocess.run([sys.executable, "consulta_graficos.py"])
threading.Thread(target=run, daemon=True).start()

root = tk.Tk()
root.title("Monitor - Tela Inicial")

btn_start = tk.Button(root, text="Iniciar monitoramento", command=on_start)
btn_start.pack(padx=10, pady=5)

btn_stop = tk.Button(root, text="Parar monitoramento", command=on_stop, state="disabled")
btn_stop.pack(padx=10, pady=5)

btn_consultar = tk.Button(root, text="Consultar histórico / gráficos", command=on_consultar)
btn_consultar.pack(padx=10, pady=15)

root.mainloop()
