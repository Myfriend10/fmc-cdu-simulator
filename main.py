import tkinter as tk
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import requests
from playsound import playsound
import threading

class FMC_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CDU - Flight Management Computer")
        self.root.configure(bg="black")

        self.speed = 450
        self.fuel_burn_per_nm = 2.5
        self.total_distance = 0
        self.total_fuel = 0
        self.total_time = 0
        self.remaining_time = 0
        self.waypoints = []
        self.eta = None
        self.flight_started = False
        self.flight_start_time = None

        self.real_gps = None
        self.alert_fuel_played = False
        self.alert_arrival_played = False

        self.display = tk.Text(root, width=70, height=20, bg="black", fg="lime", font=("Courier", 12))
        self.display.grid(row=0, column=0, columnspan=5, padx=10, pady=10)
        self.display.insert(tk.END, "FMC CDU INTERFACE\n----------------------------------------------\n")
        self.display.insert(tk.END, "WAYPOINT     LATITUDE    LONGITUDE    DIST(NM)   TIME(min)   FUEL(kg)\n")

        self.entry = tk.Entry(root, width=60, font=("Courier", 12))
        self.entry.grid(row=1, column=0, columnspan=3, padx=10, pady=5)

        self.enter_btn = tk.Button(root, text="EXEC", command=self.insert_command, width=10, bg="gray20", fg="lime", font=("Courier", 12))
        self.enter_btn.grid(row=1, column=3)

        self.clear_btn = tk.Button(root, text="CLEAR", command=self.clear_all, width=10, bg="gray20", fg="red", font=("Courier", 12))
        self.clear_btn.grid(row=1, column=4)

        self.start_btn = tk.Button(root, text="INICIAR VOO", command=self.start_flight, width=12, bg="darkgreen", fg="white", font=("Courier", 12))
        self.start_btn.grid(row=2, column=4, padx=10)

        self.map_btn = tk.Button(root, text="MAPA", command=self.show_map, width=10, bg="navy", fg="white", font=("Courier", 12))
        self.map_btn.grid(row=2, column=3, pady=5)

        self.progress_label = tk.Label(root, text="", bg="black", fg="lime", font=("Courier", 12))
        self.progress_label.grid(row=2, column=0, columnspan=3)

        self.gps_label = tk.Label(root, text="POSIÇÃO GPS: ---, ---", bg="black", fg="lime", font=("Courier", 12))
        self.gps_label.grid(row=3, column=0, columnspan=5, pady=(5,10))

        self.get_real_gps()

    def play_sound_async(self, filename):
        threading.Thread(target=playsound, args=(filename,), daemon=True).start()

    def insert_command(self):
        cmd = self.entry.get().strip()
        if not cmd:
            return

        parts = cmd.split()
        if len(parts) == 4:
            try:
                wp = parts[0].upper()
                lat = float(parts[1])
                lon = float(parts[2])
                dist = float(parts[3])
            except ValueError:
                self.display.insert(tk.END, f"\n> Valores inválidos. Use: NOME LAT LON DISTANCIA\n")
                self.entry.delete(0, tk.END)
                return

            self.waypoints.append((wp, lat, lon, dist))

            time_min = (dist / self.speed) * 60
            fuel = dist * self.fuel_burn_per_nm

            self.total_distance += dist
            self.total_time += time_min
            self.total_fuel += fuel
            self.remaining_time = self.total_time

            self.display.insert(tk.END,
                f"{wp:<12}{lat:<12.5f}{lon:<12.5f}{dist:<10.1f}{time_min:<12.1f}{fuel:<10.1f}\n")

            if self.total_fuel > 2000 and not self.alert_fuel_played:
                self.display.insert(tk.END, "\n⚠️  ALERTA: Consumo estimado de combustível CRÍTICO!\n")
                self.play_sound_async("alerta_combustivel.wav")
                self.alert_fuel_played = True

            now = datetime.now()
            self.eta = now + timedelta(minutes=self.total_time)
            eta_str = self.eta.strftime("%H:%M")
            self.display.insert(tk.END,
                f"TOTAL      {'':<12}{'':<12}{self.total_distance:.1f} NM  {self.total_time:.1f} min  {self.total_fuel:.1f} kg\n")
            self.display.insert(tk.END, f"ETA PREVISTA (LOCAL): {eta_str}\n")

        else:
            self.display.insert(tk.END, f"\n> Comando inválido: {cmd}\nFormato: NOME LATITUDE LONGITUDE DISTANCIA\nEx: KOVON -10.1234 -48.5678 100\n")

        self.entry.delete(0, tk.END)

    def get_real_gps(self):
        try:
            res = requests.get("http://ip-api.com/json/")
            data = res.json()
            if data['status'] == 'success':
                self.real_gps = (data['lat'], data['lon'])
        except:
            self.real_gps = None

    def start_flight(self):
        if self.flight_started or self.total_time == 0:
            return
        self.flight_started = True
        self.flight_start_time = datetime.now()
        self.update_flight()
        self.update_map_position()
        self.update_gps_position()

    def update_flight(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            elapsed_min = (datetime.now() - self.flight_start_time).total_seconds() / 60
            percent_complete = (elapsed_min / self.total_time) * 100
            percent_complete = max(0, min(percent_complete, 100))
            eta_updated = datetime.now() + timedelta(minutes=self.remaining_time)

            if percent_complete < 25:
                fase = "SUBIDA"
            elif percent_complete < 75:
                fase = "CRUZEIRO"
            else:
                fase = "DESCIDA"

            bar = "█" * int(percent_complete // 5) + "-" * (20 - int(percent_complete // 5))
            self.progress_label.config(
                text=f"[{bar}] {percent_complete:.1f}% - FASE: {fase} - ETA: {eta_updated.strftime('%H:%M')}")

            self.root.after(1000, self.update_flight)
        else:
            self.progress_label.config(text="🛬 Voo concluído! Chegamos ao destino.")
            if not self.alert_arrival_played:
                self.play_sound_async("alerta_chegada.wav")
                self.alert_arrival_played = True

    def clear_all(self):
        self.entry.delete(0, tk.END)
        self.waypoints.clear()
        self.total_distance = 0
        self.total_fuel = 0
        self.total_time = 0
        self.remaining_time = 0
        self.flight_started = False
        self.alert_fuel_played = False
        self.alert_arrival_played = False
        self.display.delete(1.0, tk.END)
        self.display.insert(tk.END, "FMC CDU INTERFACE\n----------------------------------------------\n")
        self.display.insert(tk.END, "WAYPOINT     LATITUDE    LONGITUDE    DIST(NM)   TIME(min)   FUEL(kg)\n")
        self.progress_label.config(text="")
        self.gps_label.config(text="POSIÇÃO GPS: ---, ---")

    def show_map(self):
        if not self.waypoints:
            return

        self.map_coords = [(wp[1], wp[2]) for wp in self.waypoints]
        names = [wp[0] for wp in self.waypoints]

        lats, lons = zip(*self.map_coords)

        fig, ax = plt.subplots()
        ax.set_title("Mapa de Rota")
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.plot(lons, lats, marker='o', color='blue', label='Waypoints')

        for name, lat, lon in zip(names, lats, lons):
            ax.text(lon, lat, f' {name}', fontsize=9, color='darkblue', verticalalignment='bottom')

        self.aircraft_dot, = ax.plot([], [], marker='o', color='red', label='Aeronave')

        ax.legend()
        ax.grid(True)

        self.map_fig = fig
        self.map_ax = ax
        self.map_canvas = fig.canvas

        self.update_map_position()
        plt.show()

    def update_map_position(self):
        if not hasattr(self, 'map_coords') or not self.flight_started:
            return

        total_coords = len(self.map_coords)
        if self.total_time == 0 or total_coords < 2:
            return

        elapsed = (datetime.now() - self.flight_start_time).total_seconds() / 60
        progress = elapsed / self.total_time
        progress = min(max(progress, 0), 1)

        segment = int(progress * (total_coords - 1))
        frac = (progress * (total_coords - 1)) - segment

        if segment >= total_coords - 1:
            current_lat, current_lon = self.map_coords[-1]
        else:
            lat1, lon1 = self.map_coords[segment]
            lat2, lon2 = self.map_coords[segment + 1]
            current_lat = lat1 + (lat2 - lat1) * frac
            current_lon = lon1 + (lon2 - lon1) * frac

        # Corrigido para passar listas ao set_data
        self.aircraft_dot.set_data([current_lon], [current_lat])
        self.map_fig.canvas.draw_idle()
        self.root.after(1000, self.update_map_position)

    def update_gps_position(self):
        if not hasattr(self, 'map_coords') or not self.flight_started:
            self.gps_label.config(text="POSIÇÃO GPS: ---, ---")
            return

        total_coords = len(self.map_coords)
        if self.total_time == 0 or total_coords < 2:
            self.gps_label.config(text="POSIÇÃO GPS: ---, ---")
            return

        elapsed = (datetime.now() - self.flight_start_time).total_seconds() / 60
        progress = elapsed / self.total_time
        progress = min(max(progress, 0), 1)

        segment = int(progress * (total_coords - 1))
        frac = (progress * (total_coords - 1)) - segment

        if segment >= total_coords - 1:
            sim_lat, sim_lon = self.map_coords[-1]
        else:
            lat1, lon1 = self.map_coords[segment]
            lat2, lon2 = self.map_coords[segment + 1]
            sim_lat = lat1 + (lat2 - lat1) * frac
            sim_lon = lon1 + (lon2 - lon1) * frac

        if self.real_gps:
            real_lat, real_lon = self.real_gps
            lat = real_lat * 0.3 + sim_lat * 0.7
            lon = real_lon * 0.3 + sim_lon * 0.7
        else:
            lat, lon = sim_lat, sim_lon

        self.gps_label.config(text=f"POSIÇÃO GPS: {lat:.5f}, {lon:.5f}")
        self.root.after(1000, self.update_gps_position)

if __name__ == "__main__":
    root = tk.Tk()
    app = FMC_GUI(root)
    root.mainloop()





