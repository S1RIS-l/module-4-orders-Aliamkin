"""Каталог товаров"""

import tkinter as tk
from PIL import Image, ImageTk
import os

from styles import (
    COLOR_HIGHLIGHT, COLOR_MAIN_BG, FONT_FAMILY,
    FONT_SIZE_NORMAL, FONT_SIZE_HEADER, font
)
from resources import get_product_image


FONT_SIZE_NORMAL = 11
FONT_SIZE_HEADER = 14


def _get_card_color(qty):
    """Возвращает цвет фона карточки (подсветка ≤3)."""
    return COLOR_HIGHLIGHT if qty <= 3 else COLOR_MAIN_BG


def _indicator(qty):
    """
    Индикатор «много/мало» (порог 5).

    :param qty: количество товара
    :return: «много» или «мало»
    """
    return "много" if qty > 5 else "мало"


def _add_label(parent, text, bg_color, bold=False,
               size=FONT_SIZE_NORMAL, align="w"):
    """Добавляет метку с текстом."""
    tk.Label(parent, text=text,
             font=font(size, bold=bold),
             bg=bg_color, anchor=align).pack(fill="x")


def _add_image(card, product, bg_color):
    """
    Добавляет изображение товара (или заглушку).

    :param card: карточка (tk.Frame)
    :param product: кортеж из БД
    :param bg_color: цвет фона
    """
    img_frame = tk.Frame(card, bg=bg_color)
    img_frame.pack(side="left", padx=10, pady=10)

    image_name = product[7] if product[7] else None

    photo = get_product_image(image_name, size=(100, 100))

    if photo:
        img_label = tk.Label(img_frame, image=photo, bg=bg_color)
        img_label.image = photo  # сохраняем ссылку
        img_label.pack()
    else:
        tk.Label(img_frame, text="[НЕТ ФОТО]", bg=bg_color,
                 width=10, height=5).pack()


def _add_text_info(card, product, bg_color, qty):
    """
    Добавляет текстовую информацию о товаре.

    :param card: карточка
    :param product: кортеж из БД
    :param bg_color: цвет фона
    :param qty: количество
    """
    text_frame = tk.Frame(card, bg=bg_color)
    text_frame.pack(side="left", fill="both", expand=True,
                    padx=10, pady=10)


    name = product[1] if product[1] else "[Без названия]"
    category = product[2] if product[2] else "[Без категории]"
    manufacturer = product[3] if product[3] else "[Без производителя]"
    specs = product[4] if product[4] else "[Без характеристик]"
    price = product[5] if product[5] is not None else 0
    model = product[8] if product[8] else "—"

    _add_label(text_frame, f"{name} | {manufacturer}",
               bg_color, bold=True, size=FONT_SIZE_HEADER)

    _add_label(text_frame, f"Категория: {category}", bg_color)

    _add_label(text_frame, f"Модель: {model}", bg_color)

    _add_label(text_frame, f"Характеристики: {specs}", bg_color)

    indicator = _indicator(qty)
    _add_label(text_frame, f"Количество: {indicator} ({qty})", bg_color)

    # Цена
    price_text = f"{price:,.0f} руб."
    _add_label(text_frame, price_text, bg_color,
               bold=True, size=FONT_SIZE_HEADER, align="e")


def _open_view(parent, product, refresh=None):
    """
    Открывает форму просмотра товара.

    :param parent: родительский контейнер
    :param product: кортеж из БД
    :param refresh: callback для обновления каталога
    """
    from view_form import ViewForm
    ViewForm(parent, product, on_add_to_order=refresh)


def create_product_card(parent, product, refresh=None):
    """
    Создаёт карточку товара по макету.

    :param parent: родительский контейнер
    :param product: кортеж из БД
    :param refresh: callback для обновления каталога
    """
    qty = product[6]
    bg_color = _get_card_color(qty)

    card = tk.Frame(parent, bg=bg_color, bd=1, relief="solid")
    card.pack(fill="x", padx=10, pady=5)

    _add_image(card, product, bg_color)
    _add_text_info(card, product, bg_color, qty)

    def _on_card_click(event=None):
        _open_view(parent, product, refresh)

    card.bind("<Button-1>", _on_card_click)

    for child in card.winfo_children():
        child.bind("<Button-1>", _on_card_click)
        for subchild in child.winfo_children():
            subchild.bind("<Button-1>", _on_card_click)

    return card