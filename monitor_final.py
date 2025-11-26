# monitor_final.py
import time
import psutil
from datetime import datetime
import csv
import os
import sqlite3
import threading

# CONFIG
INTERVALO_COLETA_SEG = 60 # 1 minuto
INTERVALO_ENVIO_SEG = 60 * 60 # 1 hora
ALPHA_EM_EXEMPLO = 0.3 # só pra referência

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

ARQUIVO_BUFFER = os.path.join(DATA_DIR, "buffer_medicoes.csv")
ARQUIVO_BANCO = os.path.join(DATA_DIR, "monitor.db")


def inicializar_buffer():
if not os.path.exists(ARQUIVO_BUFFER):
with open(ARQUIVO_BUFFER, mode="w", newline="", encoding="utf-8") as f:
writer = csv.writer(f)
writer.writerow(["timestamp", "cpu_percent", "ram_percent"])


def inicializar_banco():
conn = sqlite3.connect(ARQUIVO_BANCO)
cur = conn.cursor()
cur.execute(
"""
CREATE TABLE IF NOT EXISTS historico_medicoes (
id INTEGER PRIMARY KEY AUTOINCREMENT,
timestamp TEXT NOT NULL,
cpu_percent REAL NOT NULL,
ram_percent REAL NOT NULL
);
"""
)
conn.commit()
conn.close()


def enviar_buffer_para_banco():
if not os.path.exists(ARQUIVO_BUFFER):
print("Nenhum buffer encontrado para enviar.")
return

with open(ARQUIVO_BUFFER, mode="r", newline="", encoding="utf-8") as f:
reader = csv.reader(f)
linhas = list(reader)

if len(linhas) <= 1:
print("Buffer vazio, nada para enviar.")
return

dados = []
for row in linhas[1:]:
# validação simples
if len(row) >= 3:
dados.append((row[0], float(row[1]), float(row[2])))

conn = sqlite3.connect(ARQUIVO_BANCO)
cur = conn.cursor()
cur.executemany(
"INSERT INTO historico_medicoes (timestamp, cpu_percent, ram_percent) VALUES (?, ?, ?)",
dados,
)
conn.commit()
conn.close()

# recria o buffer só com cabeçalho
with open(ARQUIVO_BUFFER, mode="w", newline="", encoding="utf-8") as f:
writer = csv.writer(f)
writer.writerow(["timestamp", "cpu_percent", "ram_percent"])

print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Foram enviadas {len(dados)} medições para o banco.")


class MonitorThread:
def __init__(self, intervalo_coleta=INTERVALO_COLETA_SEG, intervalo_envio=INTERVALO_ENVIO_SEG):
self.intervalo_coleta = intervalo_coleta
self.intervalo_envio = intervalo_envio
self.stop_event = threading.Event()
self.thread = None

def start(self):
if self.thread and self.thread.is_alive():
print("Monitor já em execução.")
return
inicializar_buffer()
inicializar_banco()
self.thread = threading.Thread(target=self._loop, daemon=True)
self.thread.start()
print("Monitor iniciado.")

def stop(self):
if self.thread is None:
return
self.stop_event.set()
self.thread.join(timeout=5)
self.stop_event.clear()
print("Monitor parado.")

def _loop(self):
ultimo_envio = time.time()
while not self.stop_event.is_set():
# coleta
uso_cpu = psutil.cpu_percent(interval=1)
mem = psutil.virtual_memory()
uso_ram_percent = mem.percent
agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

print(f"[{agora}] CPU: {uso_cpu:.1f}% | RAM: {uso_ram_percent:.1f}%")

# grava no buffer CSV
with open(ARQUIVO_BUFFER, mode="a", newline="", encoding="utf-8") as f:
writer = csv.writer(f)
writer.writerow([agora, uso_cpu, uso_ram_percent])

# envio periódico
if time.time() - ultimo_envio >= self.intervalo_envio:
try:
enviar_buffer_para_banco()
except Exception as e:
print("Erro ao enviar buffer:", e)
ultimo_envio = time.time()

# espera: checa a flag a cada segundo para permitir parada rápida
seg_espera = 0
while seg_espera < self.intervalo_coleta and not self.stop_event.is_set():
time.sleep(1)
seg_espera += 1


if __name__ == "__main__":
# Modo standalone para testes
m = MonitorThread()
try:
m.start()
while True:
time.sleep(1)
except KeyboardInterrupt:
m.stop()
print("Monitor finalizado pelo usuário.")
