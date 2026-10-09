"""Форма просмотра товара"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk

from styles import (
    COLOR_MAIN_BG, COLOR_SECONDARY_BG, COLOR_ACCENT,
    FONT_SIZE_NORMAL, FONT_SIZE_HEADER, FONT_SIZE_TITLE, font
)
from resources import get_product_image
from error_handler import validate_positive_int
from order_manager import (
    create_order,
    get_product_quantity
)


class ViewForm:
    """Форма просмотра выбранного товара."""

    def __init__(self, parent, product, on_add_to_order=None):
        self.product = product
        self.on_add_to_order = on_add_to_order

        self.window = tk.Toplevel(parent)
        self.window.title(f"Просмотр — {product[1]}")
        self.window.geometry("700x650")
        self.window.configure(bg=COLOR_MAIN_BG)
        self.build_ui()

    def build_ui(self):
        """Строит интерфейс формы."""
        # Шапка
        header = tk.Frame(self.window, bg=COLOR_SECONDARY_BG, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="КАРТОЧКА ТОВАРА",
                 font=font(FONT_SIZE_TITLE, bold=True),
                 bg=COLOR_SECONDARY_BG).pack(pady=15)

        main = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        main.pack(fill="both", expand=True, padx=20, pady=20)

        img_frame = tk.Frame(main, bg=COLOR_MAIN_BG)
        img_frame.pack(side="left", padx=10, anchor="n")

        photo = get_product_image(self.product[7], size=(200, 200))
        if photo:
            img_label = tk.Label(img_frame, image=photo,
                                 bg=COLOR_MAIN_BG)
            img_label.image = photo
            img_label.pack()
        else:
            tk.Label(img_frame, text="[НЕТ ФОТО]", bg=COLOR_MAIN_BG,
                     width=15, height=10).pack()

        info_frame = tk.Frame(main, bg=COLOR_MAIN_BG)
        info_frame.pack(side="left", fill="both", expand=True, padx=20)

        name = self.product[1] if self.product[1] else "[Без названия]"
        category = self.product[2] if self.product[2] else "[Без категории]"
        manufacturer = self.product[3] if self.product[3] else "[Без производителя]"
        specs = self.product[4] if self.product[4] else "[Без характеристик]"
        price = self.product[5] if self.product[5] is not None else 0
        qty = self.product[6] if self.product[6] is not None else 0
        model = self.product[8] if self.product[8] else "—"

        self._add_field(info_frame, "Название", name)
        self._add_field(info_frame, "Категория", category)
        self._add_field(info_frame, "Производитель", manufacturer)
        self._add_field(info_frame, "Модель", model)
        self._add_field(info_frame, "Характеристики", specs)
        self._add_field(info_frame, "В наличии", f"{qty} шт.")
        self._add_field(info_frame, "Цена", f"{price:,.0f} руб.")

        qty_frame = tk.Frame(info_frame, bg=COLOR_MAIN_BG)
        qty_frame.pack(fill="x", pady=10)

        tk.Label(qty_frame, text="Количество:",
                 font=font(FONT_SIZE_NORMAL, bold=True),
                 bg=COLOR_MAIN_BG).pack(side="left")

        self.qty_var = tk.StringVar(value="1")
        tk.Entry(qty_frame, textvariable=self.qty_var,
                 width=10).pack(side="left", padx=10)

        tk.Button(qty_frame, text="Проверить",
                  command=self._check_qty,
                  bg=COLOR_ACCENT, fg="white",
                  font=font(FONT_SIZE_NORMAL)).pack(side="left")

        btn_frame = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        btn_frame.pack(fill="x", pady=10)

        tk.Button(btn_frame, text="Добавить в заказ",
                  command=self.add_to_order,
                  bg=COLOR_ACCENT, fg="white",
                  font=font(FONT_SIZE_NORMAL),
                  padx=15, pady=5).pack(side="left", padx=20)

        tk.Button(btn_frame, text="Назад",
                  command=self.window.destroy,
                  bg=COLOR_ACCENT, fg="white",
                  font=font(FONT_SIZE_NORMAL),
                  padx=15, pady=5).pack(side="right", padx=20)

    def _add_field(self, parent, label, value):
        """Добавляет поле в форму."""
        row = tk.Frame(parent, bg=COLOR_MAIN_BG)
        row.pack(fill="x", pady=2)

        tk.Label(row, text=f"{label}:",
                 font=font(FONT_SIZE_NORMAL, bold=True),
                 width=15, anchor="w",
                 bg=COLOR_MAIN_BG).pack(side="left")

        tk.Label(row, text=str(value),
                 font=font(FONT_SIZE_NORMAL),
                 anchor="w",
                 bg=COLOR_MAIN_BG).pack(side="left")

    def _check_qty(self):
        """Проверяет введённое количество."""
        ok, result = validate_positive_int(
            self.qty_var.get(), "Количество"
        )
        if ok:
            messagebox.showinfo("OK", f"Введено: {result}")
        else:
            messagebox.showerror("Ошибка", result)

    def add_to_order(self):
        """Обработчик кнопки «Добавить в заказ»."""
        if self.product is None:
            messagebox.showerror("Ошибка", "Товар не выбран")
            return

        ok, result = validate_positive_int(
            self.qty_var.get(), "Количество"
        )
        if not ok:
            messagebox.showwarning("Ошибка ввода", result)
            return
        qty = result

        product_id = self.product[0]
        current_qty = get_product_quantity(product_id)

        if qty > current_qty:
            messagebox.showwarning(
                "Ошибка", f"Доступно только {current_qty} шт."
            )
            return

        try:
            client = "Иванов Иван Иванович"
            price = self.product[5] or 0
            model = self.product[8] or "—"

            items = [(product_id, model, qty, price)]
            order_id = create_order(client, items)

            if order_id is None:
                messagebox.showerror("Ошибка",
                                     "Не удалось создать заказ")
                return

            new_qty = get_product_quantity(product_id)

            if new_qty <= 3:
                messagebox.showwarning(
                    "Внимание",
                    f"Товар «{self.product[1]}» заканчивается!\n"
                    f"Осталось {new_qty} шт."
                )

            messagebox.showinfo(
                "Успех",
                f"Заказ №{order_id} оформлен\n"
                f"Остаток: {new_qty} шт."
            )

            if self.on_add_to_order is not None:
                self.on_add_to_order()

            self.window.destroy()

        except Exception as e:
            messagebox.showerror(
                "Ошибка заказа",
                f"Не удалось оформить заказ:\n{e}"
            )