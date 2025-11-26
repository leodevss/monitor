import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "monitor.db")

def carregar_dados(start=None, end=None):
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
query = "SELECT timestamp, cpu_percent, ram_percent FROM historico_medicoes"
params = []
if start and end:
query += " WHERE timestamp BETWEEN ? AND ?"
params = [start, end]
query += " ORDER BY timestamp ASC"
cur.execute(query, params)
rows = cur.fetchall()
conn.close()
return rows

def calcular_ema(values, alpha=0.3):
ema = []
if not values:
return ema
ema.append(values[0])
for v in values[1:]:
ema.append(alpha * v + (1 - alpha) * ema[-1])
return ema

def main():
rows = carregar_dados()

if not rows:
print("Sem dados no banco.")
return

times = [datetime.strptime(r[0], "%Y-%m-%d %H:%M:%S") for r in rows]
cpu = [r[1] for r in rows]
ram = [r[2] for r in rows]

cpu_ema = calcular_ema(cpu)
ram_ema = calcular_ema(ram)

# CPU
plt.figure(figsize=(10,5))
plt.plot(times, cpu, label="CPU (%)")
plt.plot(times, cpu_ema, label="CPU EMA", linewidth=2)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d\n%H:%M"))
plt.legend()
plt.title("Histórico CPU")
plt.tight_layout()
plt.show()

# RAM
plt.figure(figsize=(10,5))
plt.plot(times, ram, label="RAM (%)")
plt.plot(times, ram_ema, label="RAM EMA", linewidth=2)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d\n%H:%M"))
plt.legend()
plt.title("Histórico RAM")
plt.tight_layout()
plt.show()

if __name__ == "__main__":
main()
