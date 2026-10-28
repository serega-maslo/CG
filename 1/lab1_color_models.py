import colorsys
import re
import tkinter as tk
from tkinter import colorchooser, messagebox, ttk


class ColorModelsApp:
    PALETTE = [
        "#000000", "#434343", "#666666", "#999999", "#CCCCCC", "#FFFFFF",
        "#FF0000", "#FF9900", "#FFFF00", "#00FF00", "#00FFFF", "#0000FF",
        "#9900FF", "#FF00FF", "#F4CCCC", "#D9EAD3", "#CFE2F3", "#FCE5CD",
    ]

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Лабораторная работа №1 — Цветовые модели")
        self.root.geometry("1160x790")
        self.root.minsize(1030, 730)

        self._updating = False
        self.current_rgb = (66, 133, 244)
        self.current_hex = "#4285F4"

        self.model_values = {
            "RGB": {key: tk.StringVar() for key in ("R", "G", "B")},
            "CMYK": {key: tk.StringVar() for key in ("C", "M", "Y", "K")},
            "HSV": {key: tk.StringVar() for key in ("H", "S", "V")},
        }
        self.slider_values = {
            "RGB": {key: tk.DoubleVar(value=0) for key in ("R", "G", "B")},
            "CMYK": {key: tk.DoubleVar(value=0) for key in ("C", "M", "Y", "K")},
            "HSV": {key: tk.DoubleVar(value=0) for key in ("H", "S", "V")},
        }

        self._build_ui()
        self._apply_rgb(*self.current_rgb)

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=(18, 14))
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)

        ttk.Label(
            outer,
            text="Цветовые модели: CMYK · RGB · HSV",
            font=("TkDefaultFont", 18, "bold"),
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            outer,
            text=(
                "Введите значение, передвиньте ползунок или выберите цвет — "
                "остальные модели обновятся автоматически. Значения других "
                "компонент выбранной модели сохраняются."
            ),
            wraplength=1080,
        ).grid(row=1, column=0, sticky="w", pady=(5, 13))

        top = ttk.Frame(outer)
        top.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        top.columnconfigure(0, weight=1)

        preview_box = ttk.LabelFrame(top, text="Предпросмотр цвета", padding=10)
        preview_box.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        preview_box.columnconfigure(0, weight=1)
        self.preview = tk.Label(
            preview_box,
            text="#4285F4",
            font=("TkDefaultFont", 16, "bold"),
            relief="sunken",
            bd=1,
            height=3,
        )
        self.preview.grid(row=0, column=0, sticky="ew")

        hex_box = ttk.Frame(preview_box)
        hex_box.grid(row=1, column=0, sticky="w", pady=(9, 0))
        ttk.Label(hex_box, text="HEX:").pack(side="left", padx=(0, 7))
        self.hex_var = tk.StringVar(value="#4285F4")
        self.hex_entry = ttk.Entry(
            hex_box, textvariable=self.hex_var, width=12, font=("TkFixedFont", 11)
        )
        self.hex_entry.pack(side="left")
        self.hex_entry.bind("<Return>", self._commit_hex)
        self.hex_entry.bind("<FocusOut>", self._commit_hex)
        ttk.Label(hex_box, text="  (например, #2F80ED)").pack(side="left")

        actions = ttk.Frame(top)
        actions.grid(row=0, column=1, sticky="ns")
        ttk.Button(
            actions, text="Выбрать цвет…", command=self._choose_color
        ).pack(fill="x", pady=(3, 7))
        ttk.Button(
            actions, text="Формулы и справка", command=self._show_help
        ).pack(fill="x", pady=3)
        ttk.Button(
            actions,
            text="Сбросить",
            command=lambda: self._apply_rgb(66, 133, 244),
        ).pack(fill="x", pady=3)

        palette_box = ttk.LabelFrame(outer, text="Быстрая палитра", padding=(9, 7))
        palette_box.grid(row=3, column=0, sticky="ew", pady=(0, 13))
        for i, color in enumerate(self.PALETTE):
            swatch = tk.Button(
                palette_box,
                bg=color,
                activebackground=color,
                width=4,
                height=1,
                relief="raised",
                bd=1,
                command=lambda selected=color: self._apply_hex(selected),
                takefocus=True,
            )
            swatch.grid(row=i // 9, column=i % 9, padx=4, pady=3, sticky="ew")
        for col in range(9):
            palette_box.columnconfigure(col, weight=1)

        models = ttk.Frame(outer)
        models.grid(row=4, column=0, sticky="nsew")
        for col in range(3):
            models.columnconfigure(col, weight=1, uniform="model")
        outer.rowconfigure(4, weight=1)

        self._build_model_panel(models, "RGB", 0, [
            ("R", "Красный", 0, 255, ""),
            ("G", "Зелёный", 0, 255, ""),
            ("B", "Синий", 0, 255, ""),
        ])
        self._build_model_panel(models, "CMYK", 1, [
            ("C", "Cyan — голубой", 0, 100, "%"),
            ("M", "Magenta — пурпурный", 0, 100, "%"),
            ("Y", "Yellow — жёлтый", 0, 100, "%"),
            ("K", "Key — чёрный", 0, 100, "%"),
        ])
        self._build_model_panel(models, "HSV", 2, [
            ("H", "Hue — тон", 0, 360, "°"),
            ("S", "Saturation — насыщенность", 0, 100, "%"),
            ("V", "Value — яркость", 0, 100, "%"),
        ])

        ttk.Label(
            outer,
            text=(
                "RGB: 0–255  •  CMYK: 0–100%  •  HSV: H = 0–360°, S и V = 0–100%.  "
                "Поля применяются клавишей Enter или при переходе к другому элементу."
            ),
            foreground="#555555",
            wraplength=1080,
        ).grid(row=5, column=0, sticky="w", pady=(12, 0))

    def _build_model_panel(
        self, parent: ttk.Frame, model: str, column: int, fields: list
    ) -> None:
        panel = ttk.LabelFrame(parent, text=model, padding=(10, 9))
        panel.grid(
            row=0,
            column=column,
            sticky="nsew",
            padx=(0 if column == 0 else 6, 6 if column < 2 else 0),
        )
        panel.columnconfigure(0, weight=1)

        descriptions = {
            "RGB": "Сложение красного, зелёного и синего света",
            "CMYK": "Голубая, пурпурная, жёлтая и чёрная краски",
            "HSV": "Тон, насыщенность и воспринимаемая яркость",
        }
        ttk.Label(
            panel,
            text=descriptions[model],
            wraplength=300,
            foreground="#555555",
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        for i, (key, label, minimum, maximum, unit) in enumerate(fields):
            base_row = 1 + i * 2
            row_header = ttk.Frame(panel)
            row_header.grid(row=base_row, column=0, sticky="ew", pady=(2, 0))
            row_header.columnconfigure(0, weight=1)
            ttk.Label(row_header, text=label).grid(row=0, column=0, sticky="w")
            entry = ttk.Entry(
                row_header,
                textvariable=self.model_values[model][key],
                width=9,
                justify="right",
            )
            entry.grid(row=0, column=1, sticky="e", padx=(7, 2))
            if unit:
                ttk.Label(row_header, text=unit, width=2).grid(
                    row=0, column=2, sticky="w"
                )
            entry.bind("<Return>", lambda event, m=model: self._commit_model(m))
            entry.bind("<FocusOut>", lambda event, m=model: self._commit_model(m))

            resolution = 1 if model == "RGB" else 0.1
            scale = tk.Scale(
                panel,
                from_=minimum,
                to=maximum,
                orient="horizontal",
                resolution=resolution,
                showvalue=False,
                variable=self.slider_values[model][key],
                command=lambda _value, m=model: self._on_slider(m),
                highlightthickness=0,
                bd=0,
                sliderlength=16,
                length=285,
                takefocus=True,
            )
            scale.grid(row=base_row + 1, column=0, sticky="ew", pady=(0, 5))

    @staticmethod
    def _model_to_rgb(model: str, values: dict) -> tuple[int, int, int]:
        """Convert one model to 8-bit RGB without recalculating its components."""
        if model == "RGB":
            rgb_values = []
            for key in ("R", "G", "B"):
                value = float(values[key])
                if not value.is_integer():
                    raise ValueError(f"{key}: в RGB нужно целое число от 0 до 255.")
                if not 0 <= value <= 255:
                    raise ValueError(f"{key}: значение должно быть от 0 до 255.")
                rgb_values.append(int(value))
            return tuple(rgb_values)

        if model == "CMYK":
            for key in ("C", "M", "Y", "K"):
                value = float(values[key])
                if not 0 <= value <= 100:
                    raise ValueError(f"{key}: значение CMYK должно быть от 0 до 100%.")
            c, m, y, k = (float(values[key]) / 100.0 for key in ("C", "M", "Y", "K"))
            return tuple(
                round(255 * channel)
                for channel in (
                    (1.0 - c) * (1.0 - k),
                    (1.0 - m) * (1.0 - k),
                    (1.0 - y) * (1.0 - k),
                )
            )

        if model == "HSV":
            h = float(values["H"])
            s = float(values["S"])
            v = float(values["V"])
            if not 0 <= h <= 360:
                raise ValueError("H (тон) должен быть от 0 до 360 градусов.")
            if not 0 <= s <= 100:
                raise ValueError("S должен быть от 0 до 100%.")
            if not 0 <= v <= 100:
                raise ValueError("V должен быть от 0 до 100%.")
            red, green, blue = colorsys.hsv_to_rgb((h % 360.0) / 360.0, s / 100.0, v / 100.0)
            return tuple(round(channel * 255) for channel in (red, green, blue))

        raise ValueError(f"Неизвестная цветовая модель: {model}")

    @staticmethod
    def _format_preserved_values(model: str, values: dict) -> dict:
        """Keep the selected model's numbers instead of round-tripping them via RGB."""
        if model == "RGB":
            return {key: str(int(round(float(values[key])))) for key in ("R", "G", "B")}
        if model == "CMYK" and float(values["K"]) >= 100:
            return {"C": "0.0", "M": "0.0", "Y": "0.0", "K": "100.0"}
        keys = ("C", "M", "Y", "K") if model == "CMYK" else ("H", "S", "V")
        return {key: f"{float(values[key]):.1f}" for key in keys}

    def _on_slider(self, model: str) -> None:
        if self._updating:
            return
        try:
            values = {
                key: float(var.get())
                for key, var in self.slider_values[model].items()
            }
            rgb = self._model_to_rgb(model, values)
            self._apply_rgb(*rgb, preserve_model=model, preserve_values=values)
        except (ValueError, tk.TclError):
            return

    def _commit_model(self, model: str) -> None:
        if self._updating:
            return
        raw_values = {
            key: self.model_values[model][key].get().strip()
            for key in self.model_values[model]
        }
        try:
            parsed = {}
            for key, raw in raw_values.items():
                if not raw:
                    raise ValueError(f"Поле {key} не должно быть пустым.")
                parsed[key] = float(raw.replace(",", "."))

            rgb = self._model_to_rgb(model, parsed)
            self._apply_rgb(*rgb, preserve_model=model, preserve_values=parsed)
        except (ValueError, tk.TclError) as exc:
            messagebox.showerror(
                "Некорректное значение", str(exc), parent=self.root
            )
            self._apply_rgb(*self.current_rgb)

    def _commit_hex(self, _event=None) -> str:
        if self._updating:
            return "break"
        value = self.hex_var.get().strip()
        if not value.startswith("#"):
            value = "#" + value
        if re.fullmatch(r"#[0-9a-fA-F]{3}", value):
            value = "#" + "".join(ch * 2 for ch in value[1:])
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
            messagebox.showerror(
                "Некорректный HEX",
                "Введите цвет в формате #RRGGBB, например #2F80ED.",
                parent=self.root,
            )
            self._apply_rgb(*self.current_rgb)
            return "break"
        self._apply_hex(value.upper())
        return "break"

    def _apply_hex(self, hex_color: str) -> None:
        color = hex_color.lstrip("#")
        self._apply_rgb(
            int(color[0:2], 16),
            int(color[2:4], 16),
            int(color[4:6], 16),
        )

    def _choose_color(self) -> None:
        chosen = colorchooser.askcolor(
            color=self.current_hex,
            title="Выберите цвет",
            parent=self.root,
        )
        if chosen and chosen[0]:
            self._apply_rgb(*(int(round(channel)) for channel in chosen[0]))

    def _apply_rgb(
        self,
        r: int,
        g: int,
        b: int,
        preserve_model: str | None = None,
        preserve_values: dict | None = None,
    ) -> None:
        r, g, b = (
            max(0, min(255, int(round(value))))
            for value in (r, g, b)
        )
        self.current_rgb = (r, g, b)
        self.current_hex = f"#{r:02X}{g:02X}{b:02X}"
        rn, gn, bn = (channel / 255.0 for channel in (r, g, b))

        k = 1.0 - max(rn, gn, bn)
        if k >= 1.0:
            c = m = y = 0.0
        else:
            c = (1.0 - rn - k) / (1.0 - k)
            m = (1.0 - gn - k) / (1.0 - k)
            y = (1.0 - bn - k) / (1.0 - k)

        h, s, v = colorsys.rgb_to_hsv(rn, gn, bn)

        all_values = {
            "RGB": {"R": str(r), "G": str(g), "B": str(b)},
            "CMYK": {
                "C": f"{c * 100:.1f}",
                "M": f"{m * 100:.1f}",
                "Y": f"{y * 100:.1f}",
                "K": f"{k * 100:.1f}",
            },
            "HSV": {
                "H": f"{h * 360.0:.1f}",
                "S": f"{s * 100.0:.1f}",
                "V": f"{v * 100.0:.1f}",
            },
        }

        if preserve_model and preserve_values is not None:
            all_values[preserve_model] = self._format_preserved_values(
                preserve_model, preserve_values
            )

        self._updating = True
        try:
            for model, components in all_values.items():
                for key, text in components.items():
                    self.model_values[model][key].set(text)
                    self.slider_values[model][key].set(float(text))

            self.hex_var.set(self.current_hex)
            luminance = 0.2126 * rn + 0.7152 * gn + 0.0722 * bn
            foreground = "#000000" if luminance > 0.55 else "#FFFFFF"
            self.preview.configure(
                text=self.current_hex,
                bg=self.current_hex,
                fg=foreground,
            )
        finally:
            self._updating = False

    def _show_help(self) -> None:
        help_window = tk.Toplevel(self.root)
        help_window.title("Справка: цветовые модели")
        help_window.transient(self.root)
        help_window.geometry("690x500")
        help_window.minsize(600, 430)

        content = ttk.Frame(help_window, padding=18)
        content.pack(fill="both", expand=True)
        text = (
            "RGB — аддитивная модель света\n"
            "R (Red), G (Green), B (Blue) задаются числами 0–255. Чем выше значение канала, тем больше света этого цвета.\n"
            "Примеры: (255, 0, 0) — красный; (0, 0, 0) — чёрный; (255, 255, 255) — белый.\n\n"
            "CMYK — субтрактивная модель печати\n"
            "C (Cyan) — голубая краска, M (Magenta) — пурпурная, Y (Yellow) — жёлтая, K (Key) — чёрная.\n"
            "Каждая компонента указывается в процентах. Используемые формулы:\n"
            "R = 255 × (1 − C) × (1 − K), G = 255 × (1 − M) × (1 − K), "
            "B = 255 × (1 − Y) × (1 − K), где C/M/Y/K — доли от 0 до 1.\n\n"
            "HSV — описание цвета через тон, насыщенность и яркость\n"
            "H (Hue) — тон в градусах: 0° — красный, около 120° — зелёный, около 240° — синий.\n"
            "S (Saturation) — насыщенность: 0% означает оттенок серого, 100% — максимально насыщенный цвет.\n"
            "V (Value) — яркость: 0% даёт чёрный, 100% — максимальную яркость выбранного тона.\n\n"
            "Точность и округление\n"
            "RGB представлен 8-битными целыми каналами. При редактировании CMYK или HSV "
            "окрашенный результат округляется до ближайшего значения RGB; остальные модели "
            "пересчитываются из RGB, а введённые компоненты редактируемой модели сохраняются.\n"
            "Для серого цвета тон HSV математически не определён; программа показывает H = 0°."
        )
        label = ttk.Label(content, text=text, justify="left", wraplength=645)
        label.pack(fill="both", expand=True, anchor="nw")
        ttk.Button(
            content, text="Закрыть", command=help_window.destroy
        ).pack(anchor="e", pady=(12, 0))


def main() -> None:
    root = tk.Tk()
    try:
        ttk.Style().theme_use("clam")
    except tk.TclError:
        pass
    ColorModelsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
