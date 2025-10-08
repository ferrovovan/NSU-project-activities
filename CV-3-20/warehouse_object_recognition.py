#!/usr/bin/env python3
# -*- coding: utf-8  -*-
# -*- mode:   python -*-

# This file is part of the educational OpenCV tasks.
#
# Copyright (C) 2025  ferrovovan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
CV-3-20: Система распознавания объектов на складе.
Описание задачи:
Сбор статистики по цвету и размеру объектов с изображения и формирование отчёта.
"""

import argparse
import cv2
import numpy as np
import csv
import sys, os



# ------------------------------------------------------------
# ИМПОРТЫ ВНУТРЕННИХ МОДУЛЕЙ
# ------------------------------------------------------------

# Определяем абсолютный путь к текущему файлу
current_dir = os.path.dirname(os.path.abspath(__file__))

# Добавляем в sys.path нужные директории
sys.path.append(os.path.join(current_dir, "CV-2-04"))
sys.path.append(os.path.join(current_dir, "CV-2-01"))

from combine_color_masks import ColorMask, apply_mask
from coins_contour_detection import counting_contours



# ===================================================================
# БЛОК 1. ПРЕДВАРИТЕЛЬНЫЕ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ===================================================================

def create_base_color_masks() -> list[ColorMask]:
	"""Создаёт набор масок для основных цветов (красный, синий, зелёный)."""
	red_mask = ColorMask("red")
	red_mask += (np.array([0, 100, 100]), np.array([10, 255, 255]))
	red_mask += (np.array([170, 100, 100]), np.array([180, 255, 255]))

	blue_mask = ColorMask("blue")
	blue_mask += (np.array([100, 150, 0]), np.array([140, 255, 255]))

	green_mask = ColorMask("green")
	green_mask += (np.array([40, 70, 70]), np.array([80, 255, 255]))
	
	return [red_mask, blue_mask, green_mask]

def create_extra_color_masks() -> list[ColorMask]:
	"""
	Создаёт набор масок для дополнительных цветов:
	жёлтый, ораньжевый, чёрный, белый, серый.
	"""
	yellow_mask = ColorMask("yellow")
	yellow_mask += (np.array([20, 100, 100]), np.array([35, 255, 255]))

	orange_mask = ColorMask("orange")
	orange_mask += (np.array([10, 100, 100]), np.array([20, 255, 255]))

	black_mask = ColorMask("black")
	black_mask += (np.array([0, 0, 0]), np.array([180, 255, 50]))

	white_mask = ColorMask("white")
	white_mask += (np.array([0, 0, 200]), np.array([180, 50, 255]))

	gray_mask = ColorMask("gray")
	gray_mask += (np.array([0, 0, 50]), np.array([180, 50, 200]))

	return [yellow_mask, orange_mask, black_mask, white_mask, gray_mask]

def analyze_contour_size(cnt: np.ndarray) -> str:
	"""
	Классифицирует контур по размеру площади.

	Args:
		cnt (np.ndarray): Контур (массив точек).

	Returns:
		str: 'малый', 'средний' или 'большой'
	"""
	area = cv2.contourArea(cnt)
	if area < 1000:
		return 'small' # 'малый'
	elif area < 5000:
		return 'medium' # средний
	else:
		return 'big'  # большой

def classify_contour_color(image_bgr: np.ndarray,
			contour: np.ndarray,
			color_masks: list[ColorMask]) -> str:
	"""
	Определяет преобладающий цвет внутри контура.

	Args:
		image_bgr (np.ndarray): Исходное изображение BGR.
		contour (np.ndarray): Контур объекта.
		masks (list[ColorMask]): Обрабатываемые цветовые маски

	Returns:
		str: Название цвета ('красный', 'синий', 'зелёный', 'неизвестный').
	"""
	mask = np.zeros(image_bgr.shape[:2], dtype=np.uint8)
	cv2.drawContours(mask, [contour], -1, 255, -1)
	hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

	# Подсчёт количества пикселей каждого цвета внутри маски контура
	color_counts = {}
	for color_mask in color_masks:
		img_mask_color = color_mask.create_mask(hsv)
		overlap = cv2.bitwise_and(mask, img_mask_color)
		color_counts[color_mask.name] = np.count_nonzero(overlap)

	best_color = max(color_counts, key=color_counts.get)
	if color_counts[best_color] < 10:  # если пикселей мало — неизвестный
		return 'unknown'
	return best_color

def analyze_contour_shape(cnt: np.ndarray) -> str:
	"""Заглушка для определения формы."""
	return "unknown"

def save_to_csv(results: list[dict], filename: str = "warehouse_report.csv") -> None:
	"""
	Сохраняет результаты в CSV-файл.

	Args:
		results (list[dict]): Список словарей с ключами:
			'id', 'color', 'size', 'shape', 'area'.
		filename (str): Имя CSV-файла.
	"""
	#	with open(output_path, "w", newline="", encoding="utf-8") as f:
	#		writer = csv.writer(f)
	#		writer.writerow(["size", "color", "shape"])
	#		writer.writerows(data)
	#	print(f"[INFO] Отчёт сохранён в {output_path}")

	with open(filename, "w", newline="", encoding="utf-8") as f:
		writer = csv.DictWriter(f, fieldnames=['id', 'color', 'size', 'shape', 'area'])
		writer.writeheader()
		writer.writerows(results)

	print(f"[INFO] Отчёт сохранён в {filename}")



# ===================================================================
# БЛОК 2. ОСНОВНОЙ АНАЛИЗ
# ===================================================================

def process_image(image: np.ndarray) -> tuple[list[dict], np.ndarray]:
	"""
	Главная функция анализа изображения.
	Возвращает список данных и изображение с визуализацией.

	1. Переводит изображение в оттенки серого.
	2. Находит контуры объектов.
	3. Определяет для каждого:
		- площадь,
		- размер (малый/средний/большой),
		- цвет (по HSV),
		- форму (пока 'не определена').

	Args:
		image (np.ndarray): Входное изображение BGR.

	Returns:
		list[dict]: Список описаний объектов.
	"""
	masks = create_base_color_masks()
	extra_masks = create_extra_color_masks()
	masks.extend(extra_masks)
	imgray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	# Контуры через модуль CV-2-01
	contours = counting_contours(
		imgray=imgray,
		lowThreshCanny=50,
		highThreshCanny=150,
		lowThresh=20,
		highThresh=255,
		minArea=200,
		maxArea=20000
	)
	result_img = image.copy()
	results = []

	for idx, cnt in enumerate(contours, start=1):
		size_label = analyze_contour_size(cnt)
		color_label = classify_contour_color(image, cnt, masks)
		shape_label = analyze_contour_shape(cnt)
		area = cv2.contourArea(cnt)

		# Выделяем контур на изображении
		cv2.drawContours(result_img, [cnt], -1, (0, 255, 255), 2)
		cv2.putText(
			result_img,
			f"{idx}:{color_label},{size_label}",
			tuple(cnt[0][0]),
			cv2.FONT_HERSHEY_SIMPLEX,
			0.8,
			(255, 255, 255),
			1,
			cv2.LINE_AA,
		)

		results.append({
			"id": idx,
			"color": color_label,
			"size": size_label,
			"shape": shape_label,
			"area": int(area),
		})

	return results, result_img


def show_result(image: np.ndarray, title: str = "Result") -> None:
	"""
	Показывает итоговое изображение.
	Args:
		original (np.ndarray): Исходное изображение в формате BGR.
	Returns:
		None: Функция только выводит изображения в окна.
	Raises:
		ValueError: Если одно из изображений пустое.
	"""
	cv2.imshow(title, image)
	print("[INFO] Нажмите любую клавишу для закрытия окна.")
	cv2.waitKey(0)
	cv2.destroyAllWindows()



# ===================================================================
# БЛОК 3. ПРИМЕНЕНИЕ
# ===================================================================

def example_synthetic():
	"""
	Генерация синтетического тестового изображения
	"""
	img = np.zeros((400, 400, 3), dtype=np.uint8)
	cv2.circle(img, (100, 100), 20, (5, 5, 255), -1)  # красный
	cv2.rectangle(img, (50, 50), (100, 100), (30, 0, 200), -1)  # красный
	cv2.rectangle(img, (200, 50), (250, 100), (255, 0, 0), -1)  # синий
	cv2.ellipse(img, (210, 330), (20, 10), 0, 0, 360, (0, 250, 0), -1)  # зелёный
	cv2.rectangle(img, (50, 220), (100, 320), (0, 128, 255), -1)  # ораньжевый

	results, result_img = process_image(img)
	save_to_csv(results, "report_synthetic.csv")
	print(f"[INFO] Синтетическое изображение обработано. Найдено объектов: {len(results)}")
	show_result(result_img, "Synthetic Result")

def main_process_file(img_path: str) -> np.ndarray:
	"""
	Основная функция обработки файла-изображения:
	загрузка, создание цветовых масок, определение размера, 

	Args:
		img_path (str): Путь до входного файла-изображения.

	Returns:
		np.ndarray: Итоговое изображение.

	Raises:
		FileNotFoundError: Если файл по указанному пути отсутствует.
		ValueError: Если изображение не удалось загрузить
			или его формат некорректен.
	"""
	if not os.path.isfile(img_path):
		raise FileNotFoundError(f"Файл '{img_path}' не существует.")

	img_bgr = cv2.imread(img_path, cv2.IMREAD_COLOR)
	if img_bgr is None:
		print(f"[ERROR] Не удалось прочитать изображение {filepath}.")
		raise ValueError(f"Не удалось загрузить изображение: {img_path}")

	results, result_img = process_image(img_bgr)
	save_to_csv(results)
	print("[INFO] Обработка завершена. Найдено объектов:", len(results))
	show_result(result_img, f"Result: {img_path}")



# ===================================================================
# БЛОК 4. CLI-ИНТЕРФЕЙС
# ===================================================================

if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		description="CV-3-20: Система распознавания объектов на складе."
	)
	
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument(
		"--example_synthetic",
		action="store_true",
		help="Сгенерировать синтетическое изображение с подходящими объектами."
	)
	group.add_argument(
		"--file",
		type=str,
		help="Путь к изображению для обработки."
	)

	args = parser.parse_args()

	if args.example_synthetic:
		example_synthetic()
	elif args.file:
		main_process_file(args.file)

