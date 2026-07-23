import customtkinter as ctk
from tkinter import messagebox, filedialog, ttk
from datetime import datetime, timedelta
import math

from models import Plant, PlantPhase, GerminationPlant, PHASE_COLORS
from database import Database


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


class PlantCatalogTab(ctk.CTkFrame):
    def __init__(self, master, db: Database, **kwargs):
        super().__init__(master, **kwargs)
        self.db = db
        self.current_plant_id: int | None = None
        self.phase_widgets: list[dict] = []

        self.grid_columnconfigure(0, weight=0, minsize=250)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_list_panel()
        self._build_editor_panel()
        self._load_plant_list()

    def _build_list_panel(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=0, column=0, sticky="nsew", padx=(5, 2), pady=5)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame, text="Plantas", font=("", 16, "bold")).grid(row=0, column=0, pady=5)

        self.plant_listbox = tk_listbox = ctk.CTkTextbox(frame, state="disabled", font=("Consolas", 12))
        tk_listbox.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        tk_listbox._textbox.bind("<ButtonRelease-1>", self._on_list_click)
        self.plant_list_items: list[int] = []

        btn_frame = ctk.CTkFrame(frame)
        btn_frame.grid(row=2, column=0, pady=5, padx=5, sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(btn_frame, text="Nueva", command=self._new_plant).grid(row=0, column=0, padx=2, sticky="ew")
        ctk.CTkButton(btn_frame, text="Eliminar", command=self._delete_plant).grid(row=0, column=1, padx=2, sticky="ew")

        ctk.CTkButton(frame, text="Importar JSON", command=self._import_json).grid(row=3, column=0, pady=2, padx=5, sticky="ew")
        ctk.CTkButton(frame, text="Exportar JSON", command=self._export_json).grid(row=4, column=0, pady=2, padx=5, sticky="ew")

    def _build_editor_panel(self):
        frame = ctk.CTkScrollableFrame(self)
        frame.grid(row=0, column=1, sticky="nsew", padx=(2, 5), pady=5)
        frame.grid_columnconfigure(1, weight=1)

        self.editor_frame = frame
        row = 0

        ctk.CTkLabel(frame, text="Editor de Plantas", font=("", 16, "bold")).grid(
            row=row, column=0, columnspan=2, pady=5
        )
        row += 1

        self.plant_name_var = ctk.StringVar()
        ctk.CTkLabel(frame, text="Nombre:").grid(row=row, column=0, sticky="w", pady=2)
        ctk.CTkEntry(frame, textvariable=self.plant_name_var).grid(row=row, column=1, sticky="ew", pady=2, padx=5)
        row += 1

        self.group_var = ctk.StringVar()
        ctk.CTkLabel(frame, text="Grupo:").grid(row=row, column=0, sticky="w", pady=2)
        group_menu = ctk.CTkOptionMenu(frame, values=["", "hoja", "raiz", "fruto", "leguminosa"], variable=self.group_var)
        group_menu.grid(row=row, column=1, sticky="ew", pady=2, padx=5)
        row += 1

        ctk.CTkLabel(frame, text="Meses siembra:").grid(row=row, column=0, sticky="w", pady=2)
        month_frame = ctk.CTkFrame(frame)
        month_frame.grid(row=row, column=1, sticky="ew", pady=2, padx=5)
        self.month_min_var = ctk.StringVar()
        self.month_max_var = ctk.StringVar()
        ctk.CTkEntry(month_frame, textvariable=self.month_min_var, width=50).pack(side="left", padx=2)
        ctk.CTkLabel(month_frame, text="a").pack(side="left", padx=2)
        ctk.CTkEntry(month_frame, textvariable=self.month_max_var, width=50).pack(side="left", padx=2)
        row += 1

        self.semillero_var = ctk.BooleanVar()
        ctk.CTkCheckBox(frame, text="Siembra semillero", variable=self.semillero_var).grid(
            row=row, column=0, columnspan=2, sticky="w", pady=2
        )
        row += 1

        self.directa_var = ctk.BooleanVar()
        ctk.CTkCheckBox(frame, text="Siembra directa", variable=self.directa_var).grid(
            row=row, column=0, columnspan=2, sticky="w", pady=2
        )
        row += 1

        self.tiempo_cosechar_var = ctk.StringVar()
        ctk.CTkLabel(frame, text="Tiempo a cosechar (meses):").grid(row=row, column=0, sticky="w", pady=2)
        ctk.CTkEntry(frame, textvariable=self.tiempo_cosechar_var).grid(row=row, column=1, sticky="ew", pady=2, padx=5)
        row += 1

        self.templado_var = ctk.BooleanVar()
        ctk.CTkCheckBox(frame, text="Clima templado", variable=self.templado_var).grid(
            row=row, column=0, columnspan=2, sticky="w", pady=2
        )
        row += 1

        self.frio_var = ctk.BooleanVar()
        ctk.CTkCheckBox(frame, text="Clima frío", variable=self.frio_var).grid(
            row=row, column=0, columnspan=2, sticky="w", pady=2
        )
        row += 1

        self.fase_cosechar_var = ctk.StringVar()
        ctk.CTkLabel(frame, text="Fase lunar cosecha:").grid(row=row, column=0, sticky="w", pady=2)
        ctk.CTkEntry(frame, textvariable=self.fase_cosechar_var).grid(row=row, column=1, sticky="ew", pady=2, padx=5)
        row += 1

        ctk.CTkLabel(frame, text="", font=("", 10)).grid(row=row, column=0, columnspan=2, pady=5)
        row += 1

        ctk.CTkLabel(frame, text="Fases de Crecimiento", font=("", 14, "bold")).grid(
            row=row, column=0, columnspan=2, pady=5
        )
        row += 1

        self.phases_container = ctk.CTkScrollableFrame(frame, orientation="vertical")
        self.phases_container.grid(row=row, column=0, columnspan=2, sticky="nsew", pady=5)
        row += 1

        ctk.CTkButton(frame, text="+ Añadir Fase", command=self._add_phase_ui).grid(
            row=row, column=0, columnspan=2, pady=5
        )
        row += 1

        ctk.CTkButton(frame, text="Guardar Planta", command=self._save_plant).grid(
            row=row, column=0, columnspan=2, pady=10, ipadx=20
        )

        # start with one phase row
        self._add_phase_ui()

    def _add_phase_ui(self, data: PlantPhase | None = None):
        idx = len(self.phase_widgets)
        f = ctk.CTkFrame(self.phases_container)
        f.pack(fill="x", pady=2, padx=5)

        name_var = ctk.StringVar(value=data.name if data else "")
        dur_min_var = ctk.StringVar(value=str(data.duration_min_days) if data is not None and data.duration_min_days is not None else "")
        dur_max_var = ctk.StringVar(value=str(data.duration_max_days) if data is not None and data.duration_max_days is not None else "")
        light_in_var = ctk.StringVar(value=data.light_indoor if data else "")
        light_out_var = ctk.StringVar(value=data.light_outdoor if data else "")
        water_var = ctk.StringVar(value=data.water if data else "")
        ph_min_var = ctk.StringVar(value=str(data.water_ph_min) if data is not None and data.water_ph_min is not None else "")
        ph_max_var = ctk.StringVar(value=str(data.water_ph_max) if data is not None and data.water_ph_max is not None else "")
        td_min_var = ctk.StringVar(value=str(data.temp_day_min) if data is not None and data.temp_day_min is not None else "")
        td_max_var = ctk.StringVar(value=str(data.temp_day_max) if data is not None and data.temp_day_max is not None else "")
        tn_min_var = ctk.StringVar(value=str(data.temp_night_min) if data is not None and data.temp_night_min is not None else "")
        tn_max_var = ctk.StringVar(value=str(data.temp_night_max) if data is not None and data.temp_night_max is not None else "")
        hum_min_var = ctk.StringVar(value=str(data.humidity_min) if data is not None and data.humidity_min is not None else "")
        hum_max_var = ctk.StringVar(value=str(data.humidity_max) if data is not None and data.humidity_max is not None else "")
        notes_var = ctk.StringVar(value=data.notes if data else "")

        # collapsible header
        header = ctk.CTkFrame(f)
        header.pack(fill="x")
        ctk.CTkLabel(header, text=f"Fase {idx + 1}:", width=60).pack(side="left", padx=2)
        ctk.CTkEntry(header, textvariable=name_var, width=150).pack(side="left", padx=2)
        ctk.CTkLabel(header, text="Duración (días):").pack(side="left", padx=(10, 2))
        ctk.CTkEntry(header, textvariable=dur_min_var, width=40).pack(side="left", padx=2)
        ctk.CTkLabel(header, text="a").pack(side="left", padx=2)
        ctk.CTkEntry(header, textvariable=dur_max_var, width=40).pack(side="left", padx=2)
        ctk.CTkButton(header, text="X", width=30, fg_color="red",
                       command=lambda: self._remove_phase_ui(f)).pack(side="right", padx=5)

        details_scroll = ctk.CTkScrollableFrame(f, orientation="horizontal", height=70)
        details_scroll.pack(fill="x", padx=10)
        details = ctk.CTkFrame(details_scroll)
        details.pack(fill="x")

        fields = [
            ("Luz indoor (hrs):", light_in_var),
            ("Luz outdoor:", light_out_var),
            ("Agua:", water_var),
            ("pH min:", ph_min_var),
            ("pH max:", ph_max_var),
            ("Temp día min °C:", td_min_var),
            ("Temp día max °C:", td_max_var),
            ("Temp noche min °C:", tn_min_var),
            ("Temp noche max °C:", tn_max_var),
            ("Humedad min %:", hum_min_var),
            ("Humedad max %:", hum_max_var),
            ("Notas:", notes_var),
        ]
        for label, var in fields:
            c = ctk.CTkFrame(details)
            c.pack(side="left", padx=2)
            ctk.CTkLabel(c, text=label, font=("", 10)).pack(anchor="w")
            ctk.CTkEntry(c, textvariable=var, font=("", 10), width=80).pack(fill="x")

        self.phase_widgets.append({
            "frame": f,
            "name": name_var,
            "dur_min": dur_min_var,
            "dur_max": dur_max_var,
            "light_in": light_in_var,
            "light_out": light_out_var,
            "water": water_var,
            "ph_min": ph_min_var,
            "ph_max": ph_max_var,
            "td_min": td_min_var,
            "td_max": td_max_var,
            "tn_min": tn_min_var,
            "tn_max": tn_max_var,
            "hum_min": hum_min_var,
            "hum_max": hum_max_var,
            "notes": notes_var,
        })

    def _remove_phase_ui(self, frame):
        self.phase_widgets = [w for w in self.phase_widgets if w["frame"] != frame]
        frame.destroy()

    def _load_plant_list(self):
        plants = self.db.get_all_plants()
        self.plant_list_items.clear()
        tb = self.plant_listbox
        tb.configure(state="normal")
        tb.delete("1.0", "end")
        for p in plants:
            self.plant_list_items.append(p.id)
            tb.insert("end", f"{p.name}\n")
        tb.configure(state="disabled")

    def _on_list_click(self, event=None):
        tb = self.plant_listbox._textbox
        index = tb.index(f"@{event.x},{event.y}")
        line = int(index.split(".")[0])
        if 1 <= line <= len(self.plant_list_items):
            self.current_plant_id = self.plant_list_items[line - 1]
            self._load_plant_editor(self.current_plant_id)

    def _on_list_select(self, event=None):
        pass

    def _load_plant_editor(self, plant_id: int):
        plant = self.db.get_plant(plant_id)
        if not plant:
            return
        self.plant_name_var.set(plant.name)
        self.group_var.set(plant.plant_group or "")
        self.month_min_var.set(str(plant.month_plant_min) if plant.month_plant_min is not None else "")
        self.month_max_var.set(str(plant.month_plant_max) if plant.month_plant_max is not None else "")
        self.semillero_var.set(plant.siembra_semillero)
        self.directa_var.set(plant.siembra_directa)
        self.tiempo_cosechar_var.set(str(plant.tiempo_cosechar) if plant.tiempo_cosechar is not None else "")
        self.templado_var.set(plant.clima_templado)
        self.frio_var.set(plant.clima_frio)
        self.fase_cosechar_var.set(plant.fase_cosechar or "")

        for w in list(self.phase_widgets):
            self._remove_phase_ui(w["frame"])
        for ph in plant.phases:
            self._add_phase_ui(ph)

    def _new_plant(self):
        self.current_plant_id = None
        self.plant_name_var.set("")
        self.group_var.set("")
        self.month_min_var.set("")
        self.month_max_var.set("")
        self.semillero_var.set(False)
        self.directa_var.set(False)
        self.tiempo_cosechar_var.set("")
        self.templado_var.set(False)
        self.frio_var.set(False)
        self.fase_cosechar_var.set("")
        for w in list(self.phase_widgets):
            self._remove_phase_ui(w["frame"])
        self._add_phase_ui()

    def _delete_plant(self):
        if self.current_plant_id is None:
            return
        if messagebox.askyesno("Confirmar", "¿Eliminar esta planta?"):
            self.db.delete_plant(self.current_plant_id)
            self.current_plant_id = None
            self._load_plant_list()
            self._new_plant()

    def _save_plant(self):
        name = self.plant_name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return

        def _int(v):
            try:
                return int(v)
            except (ValueError, TypeError):
                return None

        def _float(v):
            try:
                return float(v)
            except (ValueError, TypeError):
                return None

        phases = []
        for i, w in enumerate(self.phase_widgets):
            phases.append(PlantPhase(
                name=w["name"].get(),
                phase_order=i,
                duration_min_days=_int(w["dur_min"].get()),
                duration_max_days=_int(w["dur_max"].get()),
                light_indoor=w["light_in"].get(),
                light_outdoor=w["light_out"].get(),
                water=w["water"].get(),
                water_ph_min=_float(w["ph_min"].get()),
                water_ph_max=_float(w["ph_max"].get()),
                temp_day_min=_float(w["td_min"].get()),
                temp_day_max=_float(w["td_max"].get()),
                temp_night_min=_float(w["tn_min"].get()),
                temp_night_max=_float(w["tn_max"].get()),
                humidity_min=_float(w["hum_min"].get()),
                humidity_max=_float(w["hum_max"].get()),
                notes=w["notes"].get(),
            ))

        plant = Plant(
            id=self.current_plant_id,
            name=name,
            plant_group=self.group_var.get(),
            month_plant_min=_int(self.month_min_var.get()),
            month_plant_max=_int(self.month_max_var.get()),
            siembra_semillero=self.semillero_var.get(),
            siembra_directa=self.directa_var.get(),
            tiempo_cosechar=_int(self.tiempo_cosechar_var.get()),
            clima_templado=self.templado_var.get(),
            clima_frio=self.frio_var.get(),
            fase_cosechar=self.fase_cosechar_var.get(),
            phases=phases,
        )
        self.db.save_plant(plant)
        self.current_plant_id = plant.id
        self._load_plant_list()
        messagebox.showinfo("Éxito", "Planta guardada correctamente")

    def _import_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not path:
            return
        try:
            count = self.db.import_from_json(path)
            self._load_plant_list()
            messagebox.showinfo("Importado", f"Se importaron {count} plantas")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _export_json(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not path:
            return
        try:
            self.db.export_to_json(path)
            messagebox.showinfo("Exportado", f"Datos exportados a {path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))


class GerminationTrackerTab(ctk.CTkFrame):
    PHASE_COLORS = ["#4CAF50", "#81C784", "#2E7D32", "#FF9800", "#795548", "#42A5F5", "#AB47BC", "#EF5350"]

    def __init__(self, master, db: Database, **kwargs):
        super().__init__(master, **kwargs)
        self.db = db
        self.canvas = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_add_panel()
        self._build_main_area()

    def _build_add_panel(self):
        top = ctk.CTkFrame(self)
        top.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        top.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(top, text="Añadir Planta en Germinación", font=("", 14, "bold")).grid(
            row=0, column=0, columnspan=4, pady=5
        )

        ctk.CTkLabel(top, text="Tipo:").grid(row=1, column=0, sticky="w", padx=5)
        self.plant_select_var = ctk.StringVar()
        self.plant_select_menu = ctk.CTkOptionMenu(top, values=[""], variable=self.plant_select_var)
        self.plant_select_menu.grid(row=1, column=1, sticky="ew", padx=5)

        ctk.CTkLabel(top, text="Nombre:").grid(row=1, column=2, sticky="w", padx=5)
        self.gp_name_var = ctk.StringVar()
        ctk.CTkEntry(top, textvariable=self.gp_name_var).grid(row=1, column=3, sticky="ew", padx=5)

        ctk.CTkLabel(top, text="Fecha germinación (YYYY-MM-DD):").grid(row=2, column=0, sticky="w", padx=5)
        self.gp_date_var = ctk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ctk.CTkEntry(top, textvariable=self.gp_date_var).grid(row=2, column=1, sticky="ew", padx=5)

        ctk.CTkLabel(top, text="Notas:").grid(row=2, column=2, sticky="w", padx=5)
        self.gp_notes_var = ctk.StringVar()
        ctk.CTkEntry(top, textvariable=self.gp_notes_var).grid(row=2, column=3, sticky="ew", padx=5)

        ctk.CTkButton(top, text="Añadir", command=self._add_germination_plant).grid(
            row=3, column=0, columnspan=4, pady=5
        )

    def _build_main_area(self):
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.main_frame, text="Plantas en Seguimiento", font=("", 14, "bold")).grid(
            row=0, column=0, pady=5
        )

        self.scroll_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.scroll_frame.grid(row=1, column=0, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

    def refresh(self):
        self._refresh_plant_list()
        self._refresh_germination_view()

    def _refresh_plant_list(self):
        plants = self.db.get_all_plants()
        names = [p.name for p in plants]
        self.plant_select_menu.configure(values=names if names else [""])
        if names and not self.plant_select_var.get():
            self.plant_select_var.set(names[0])

    def _add_germination_plant(self):
        plant_name = self.plant_select_var.get()
        if not plant_name:
            messagebox.showerror("Error", "Seleccione un tipo de planta")
            return
        plants = self.db.get_all_plants()
        match = [p for p in plants if p.name == plant_name]
        if not match:
            messagebox.showerror("Error", "Planta no encontrada")
            return
        plant = match[0]
        name = self.gp_name_var.get().strip() or plant_name
        date = self.gp_date_var.get().strip()
        if not date:
            messagebox.showerror("Error", "Ingrese una fecha")
            return
        gp = GerminationPlant(
            plant_id=plant.id,
            name=name,
            germination_date=date,
            notes=self.gp_notes_var.get(),
        )
        self.db.save_germination_plant(gp)
        self.gp_name_var.set("")
        self.gp_notes_var.set("")
        self._refresh_germination_view()

    def _refresh_germination_view(self):
        for w in self.scroll_frame.winfo_children():
            w.destroy()

        gps = self.db.get_all_germination_plants()
        if not gps:
            ctk.CTkLabel(self.scroll_frame, text="No hay plantas en germinación").pack(pady=20)
            return

        for gp in gps:
            plant = self.db.get_plant(gp.plant_id)
            if not plant:
                continue
            card = GerminationPlantCard(self.scroll_frame, gp, plant, self.db)
            card.pack(fill="x", pady=3, padx=5)


class GerminationPlantCard(ctk.CTkFrame):
    def __init__(self, master, gp: GerminationPlant, plant: Plant, db: Database, **kwargs):
        super().__init__(master, **kwargs)
        self.gp = gp
        self.plant = plant
        self.db = db

        self.grid_columnconfigure(0, weight=1)
        self._build()

    def _build(self):
        try:
            germ_date = datetime.strptime(self.gp.germination_date, "%Y-%m-%d")
        except ValueError:
            germ_date = datetime.now()

        today = datetime.now()
        current_phase_idx, current_phase_name, progress, current_phase = self._get_current_phase(germ_date)

        # Header
        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header, text=self.gp.name, font=("", 14, "bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text=f"({self.plant.name})", font=("", 11)).pack(side="left", padx=2)

        status_color = "#4CAF50" if current_phase_name else "#FF9800"
        ctk.CTkLabel(header, text=f"Fase actual: {current_phase_name or 'Completada'}", 
                     text_color=status_color, font=("", 12, "bold")).pack(side="right", padx=5)

        ctk.CTkButton(header, text="Eliminar", width=60, fg_color="#c0392b",
                       command=self._delete).pack(side="right", padx=5)

        # Info line
        info = ctk.CTkFrame(self)
        info.grid(row=1, column=0, sticky="ew", padx=5, pady=2)
        ctk.CTkLabel(info, text=f"Germinación: {self.gp.germination_date}").pack(side="left", padx=5)
        if self.gp.notes:
            ctk.CTkLabel(info, text=f"Notas: {self.gp.notes}").pack(side="left", padx=10)

        if self.plant.tiempo_cosechar:
            harvest_est = self._estimate_harvest_date(germ_date)
            if harvest_est:
                remaining = (harvest_est - today).days
                rem_text = f"({remaining} días restantes)" if remaining >= 0 else "(¡tiempo de cosecha!)"
                ctk.CTkLabel(info, text=f"Cosecha estimada: {harvest_est.strftime('%Y-%m-%d')} {rem_text}",
                             font=("", 11)).pack(side="left", padx=10)

        # Phase progress bar
        if self.plant.phases and current_phase_idx is not None and current_phase_idx < len(self.plant.phases):
            bar_frame = ctk.CTkFrame(self)
            bar_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=3)
            bar_frame.grid_columnconfigure(0, weight=1)

            prog = ctk.CTkProgressBar(bar_frame, height=8)
            prog.pack(fill="x", padx=5, pady=2)
            prog.set(min(progress, 1.0))

            phase_labels = []
            for i, ph in enumerate(self.plant.phases):
                label = ph.name or f"Fase {i + 1}"
                color = PHASE_COLORS.get(label.lower(), "#888888")
                if i == current_phase_idx:
                    phase_labels.append(f"[{label}]")
                else:
                    phase_labels.append(label)

            ctk.CTkLabel(bar_frame, text=" → ".join(phase_labels), font=("", 10)).pack(padx=5, pady=2)

        # Current phase info
        if current_phase:
            info_frame = ctk.CTkFrame(self)
            info_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=2)
            info_frame.grid_columnconfigure(0, weight=1)

            chips = ctk.CTkFrame(info_frame)
            chips.pack(fill="x", padx=5, pady=2)

            def add_chip(parent, icon, text):
                if not text:
                    return
                lbl = ctk.CTkLabel(parent, text=f"{icon} {text}", font=("", 10),
                                   fg_color="#3a3a3a", corner_radius=4)
                lbl.pack(side="left", padx=3, pady=1)

            if current_phase.light_indoor:
                add_chip(chips, "☀", f"Luz interior: {current_phase.light_indoor}h")
            if current_phase.light_outdoor:
                add_chip(chips, "☀", f"Exterior: {current_phase.light_outdoor}")
            if current_phase.water:
                add_chip(chips, "💧", current_phase.water)
            if current_phase.water_ph_min is not None and current_phase.water_ph_max is not None:
                add_chip(chips, "⚗", f"pH {current_phase.water_ph_min}-{current_phase.water_ph_max}")
            elif current_phase.water_ph_min is not None:
                add_chip(chips, "⚗", f"pH {current_phase.water_ph_min}")
            if current_phase.temp_day_min is not None and current_phase.temp_day_max is not None:
                add_chip(chips, "🌡", f"{current_phase.temp_day_min}-{current_phase.temp_day_max}°C día")
            if current_phase.temp_night_min is not None and current_phase.temp_night_max is not None:
                add_chip(chips, "🌡", f"{current_phase.temp_night_min}-{current_phase.temp_night_max}°C noche")
            if current_phase.humidity_min is not None and current_phase.humidity_max is not None:
                add_chip(chips, "💨", f"Humedad {current_phase.humidity_min}-{current_phase.humidity_max}%")

            if current_phase.notes:
                ctk.CTkLabel(info_frame, text=f"📝 {current_phase.notes}",
                             font=("", 10), text_color="#aaaaaa").pack(anchor="w", padx=5, pady=1)

    def _get_current_phase(self, germ_date):
        today = datetime.now()
        if not self.plant.phases:
            return None, "Sin fases", 0, None

        total_days = (today - germ_date).days
        if total_days < 0:
            ph = self.plant.phases[0]
            return 0, ph.name or "Fase 1", 0, ph

        cumulative_min = 0
        cumulative_max = 0

        for i, ph in enumerate(self.plant.phases):
            d_min = ph.duration_min_days or 0
            d_max = ph.duration_max_days or d_min or 30

            cumulative_max += d_max
            if total_days < cumulative_max:
                phase_start = cumulative_min
                phase_duration = d_max
                progress_in_phase = (total_days - phase_start) / phase_duration if phase_duration > 0 else 1
                return i, ph.name or f"Fase {i + 1}", min(progress_in_phase, 1.0), ph

            cumulative_min += d_min

        return len(self.plant.phases), "", 1.0, None

    def _estimate_harvest_date(self, germ_date):
        if self.plant.phases:
            total_days = sum(
                (ph.duration_max_days or ph.duration_min_days or 30)
                for ph in self.plant.phases
            )
            return germ_date + timedelta(days=total_days)
        if self.plant.tiempo_cosechar:
            try:
                from dateutil.relativedelta import relativedelta
                return germ_date + relativedelta(months=self.plant.tiempo_cosechar)
            except ImportError:
                return germ_date + timedelta(days=self.plant.tiempo_cosechar * 30)
        return None

    def _delete(self):
        if messagebox.askyesno("Confirmar", f"¿Eliminar {self.gp.name}?"):
            self.db.delete_germination_plant(self.gp.id)
            self.master.master._refresh_germination_view()


class CalendarTab(ctk.CTkFrame):
    def __init__(self, master, db: Database, **kwargs):
        super().__init__(master, **kwargs)
        self.db = db
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.label = ctk.CTkLabel(self, text="Calendario Anual de Fases", font=("", 16, "bold"))
        self.label.pack(pady=5)

        self.canvas_frame = ctk.CTkFrame(self)
        self.canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        self.canvas_frame.grid_rowconfigure(0, weight=1)

        self.calendar_canvas = ctk.CTkCanvas(self.canvas_frame, bg="#2b2b2b", highlightthickness=0)
        self.calendar_canvas.grid(row=0, column=0, sticky="nsew")

        v_scroll = ctk.CTkScrollbar(self.canvas_frame, orientation="vertical", command=self.calendar_canvas.yview)
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll = ctk.CTkScrollbar(self.canvas_frame, orientation="horizontal", command=self.calendar_canvas.xview)
        h_scroll.grid(row=1, column=0, sticky="ew")
        self.calendar_canvas.configure(
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set,
        )

        self.calendar_canvas.bind("<Configure>", self._on_resize)

    def refresh(self):
        self._draw_calendar()

    def _on_resize(self, event):
        self._draw_calendar()

    def _draw_calendar(self):
        canvas = self.calendar_canvas
        canvas.delete("all")

        gps = self.db.get_all_germination_plants()
        if not gps:
            canvas.create_text(
                400, 150, text="No hay plantas en germinación.\nAñada plantas en la pestaña 'Seguimiento'.",
                fill="#888888", font=("", 14)
            )
            return

        margin_left = 140
        margin_right = 60
        margin_top = 60
        row_height = 50
        month_bar_height = 25
        MIN_PX_PER_DAY = 3

        # -- calculate full timeline range --
        today = datetime.now()
        all_germ_dates = []
        plant_data = []
        for gp in gps:
            try:
                gd = datetime.strptime(gp.germination_date, "%Y-%m-%d")
            except ValueError:
                continue
            plant = self.db.get_plant(gp.plant_id)
            if not plant:
                continue
            total_d = sum(
                (ph.duration_max_days or ph.duration_min_days or 30)
                for ph in plant.phases
            ) if plant.phases else (plant.tiempo_cosechar or 3) * 30
            all_germ_dates.append(gd)
            plant_data.append((gp, plant, gd, total_d))

        if not plant_data:
            return

        start_date = min(all_germ_dates)
        end_date = max(gd + timedelta(days=d) for _, _, gd, d in plant_data)
        total_days_span = max((end_date - start_date).days, 366)

        chart_width = total_days_span * MIN_PX_PER_DAY
        chart_top = margin_top

        # -- draw month headers --
        cur = datetime(start_date.year, start_date.month, 1)
        end_marker = datetime(end_date.year, end_date.month, 1)
        months_abbr = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
                       "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

        while cur <= end_marker:
            month_days = (
                31 if cur.month in (1, 3, 5, 7, 8, 10, 12) else
                30 if cur.month in (4, 6, 9, 11) else
                29 if self._is_leap_year(cur.year) else 28
            )
            day_offset = (cur - start_date).days
            x1 = margin_left + (day_offset / total_days_span) * chart_width
            x2 = margin_left + ((day_offset + month_days) / total_days_span) * chart_width

            label = months_abbr[cur.month - 1]
            if cur.month == 1 or cur == start_date.replace(day=1):
                label = f"{months_abbr[cur.month - 1]} {cur.year}"

            canvas.create_rectangle(x1, chart_top, x2, chart_top + month_bar_height,
                                     outline="#555555", fill="#3a3a3a")
            canvas.create_text((x1 + x2) / 2, chart_top + month_bar_height / 2,
                                text=label, fill="#cccccc", font=("", 10))

            if cur.month == 12:
                cur = cur.replace(year=cur.year + 1, month=1)
            else:
                cur = cur.replace(month=cur.month + 1)

        # -- today marker --
        if start_date <= today <= end_date:
            day_offset = (today - start_date).days
            today_x = margin_left + (day_offset / total_days_span) * chart_width
            total_rows_h = chart_top + month_bar_height + len(plant_data) * row_height + 50
            canvas.create_line(today_x, chart_top, today_x, total_rows_h - 10,
                                fill="#FF5252", width=2, dash=(4, 2))
            canvas.create_text(today_x, total_rows_h + 5,
                                text="Hoy", fill="#FF5252", font=("", 9))
        else:
            total_rows_h = chart_top + month_bar_height + len(plant_data) * row_height + 50

        # -- draw plants --
        for idx, (gp, plant, germ_date, total_d) in enumerate(plant_data):
            y = chart_top + month_bar_height + 10 + idx * row_height
            day_offset_start = (germ_date - start_date).days

            canvas.create_text(margin_left - 10, y + row_height / 2, text=gp.name,
                                fill="#ffffff", font=("", 11), anchor="e")

            if plant.phases:
                cumulative_days = 0
                for pi, ph in enumerate(plant.phases):
                    d = ph.duration_max_days or ph.duration_min_days or 30

                    s = day_offset_start + cumulative_days
                    e = s + d

                    x1 = margin_left + (s / total_days_span) * chart_width
                    x2 = margin_left + (e / total_days_span) * chart_width

                    phase_name = ph.name.lower() if ph.name else ""
                    color = PHASE_COLORS.get(
                        phase_name,
                        GerminationTrackerTab.PHASE_COLORS[pi % len(GerminationTrackerTab.PHASE_COLORS)]
                    )
                    canvas.create_rectangle(x1, y, x2, y + row_height - 5,
                                             fill=color, outline="#555555", width=1)

                    if x2 - x1 > 30:
                        label = ph.name or f"F{pi + 1}"
                        canvas.create_text((x1 + x2) / 2, y + (row_height - 5) / 2,
                                            text=label, fill="#ffffff", font=("", 9))

                    cumulative_days += d

            else:
                x1 = margin_left + (day_offset_start / total_days_span) * chart_width
                x2 = margin_left + ((day_offset_start + total_d) / total_days_span) * chart_width
                canvas.create_rectangle(x1, y, x2, y + row_height - 5,
                                         fill="#4CAF50", outline="#555555")
                canvas.create_text((x1 + x2) / 2, y + (row_height - 5) / 2,
                                    text=gp.name, fill="#ffffff", font=("", 9))

        canvas.configure(scrollregion=(
            0, 0,
            margin_left + chart_width + margin_right,
            total_rows_h + 40
        ))

    def _is_leap_year(self, year):
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gestor de Fases de Plantas")
        self.geometry("1200x800")
        self.minsize(900, 600)

        self.db = Database()

        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_catalog = self.tab_view.add("Catálogo de Plantas")
        self.tab_tracker = self.tab_view.add("Seguimiento")
        self.tab_calendar = self.tab_view.add("Calendario")

        self.catalog_tab = PlantCatalogTab(self.tab_catalog, self.db)
        self.catalog_tab.pack(fill="both", expand=True)

        self.tracker_tab = GerminationTrackerTab(self.tab_tracker, self.db)
        self.tracker_tab.pack(fill="both", expand=True)

        self.calendar_tab = CalendarTab(self.tab_calendar, self.db)
        self.calendar_tab.pack(fill="both", expand=True)

        self.tab_view.configure(command=self._on_tab_change)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_tab_change(self):
        selected = self.tab_view.get()
        if selected == "Seguimiento":
            self.tracker_tab.refresh()
        elif selected == "Calendario":
            self.calendar_tab.refresh()

    def _on_close(self):
        self.db.close()
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
