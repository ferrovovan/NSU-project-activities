#!/usr/bin/env python3
# -*- coding: utf-8  -*-
# -*- mode:   python -*-

"""
CV-2-04: Объединение нескольких масок цветов
Описание задачи:
На основе CV-1-12 объединить маски для нескольких цветов (например, красный и синий).
"""

import os
import argparse
import cv2
import numpy as np

# Импортируем всё необходимое из CV-1-12
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../CV-1-12"))
from pixel_counting import load_image, HSV_RED_LOWER_1, HSV_RED_UPPER_1, HSV_RED_LOWER_2, HSV_RED_UPPER_2


# --- Шаг 1. Создание маски для красного ---
def create_red_mask(image_bgr: np.ndarray) -> np.ndarray:
	"""
	Создание маски для красного цвета.

	Args:
		image_bgr (np.ndarray): Изображение в формате BGR.

	Returns:
		np.ndarray: Двоичная маска (одноцветное изображение, где
		белым цветом выделены все пиксели, попавшие в диапазон красного).

	Raises:
		ValueError: Если передано пустое или некорректное изображение.
	"""
	image_hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
	mask1 = cv2.inRange(image_hsv, HSV_RED_LOWER_1, HSV_RED_UPPER_1)
	mask2 = cv2.inRange(image_hsv, HSV_RED_LOWER_2, HSV_RED_UPPER_2)
	mask = cv2.bitwise_or(mask1, mask2)
	return mask


# --- Шаг 2. Создание маски для синего ---
def create_blue_mask(image_bgr: np.ndarray) -> np.ndarray:
	"""
	Создание маски для синего цвета.

	Args:
		image_bgr (np.ndarray): Изображение в формате BGR.

	Returns:
		np.ndarray: Двоичная маска (одноцветное изображение, где
		белым цветом выделены все пиксели, попавшие в диапазон синего).

	Raises:
		ValueError: Если передано пустое или некорректное изображение.
	"""
	image_hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
	lower_blue = np.array([100, 100, 100])
	upper_blue = np.array([130, 255, 255])
	mask = cv2.inRange(image_hsv, lower_blue, upper_blue)
	return mask


# --- Шаг 3. Объединение масок ---
def combine_masks(mask1: np.ndarray, mask2: np.ndarray) -> np.ndarray:
	"""
	Объединение двух масок с помощью побитового OR.

	Args:
		mask1 (np.ndarray): Первая маска (двоичное изображение).
		mask2 (np.ndarray): Вторая маска (двоичное изображение).

	Returns:
		np.ndarray: Итоговая маска, где белым цветом выделены пиксели,
		принадлежащие хотя бы одной из масок.

	Raises:
		ValueError: Если размеры или типы масок не совпадают.
	"""

	return cv2.bitwise_or(mask1, mask2)


# --- Шаг 4. Применение маски к изображению ---
def apply_mask(image_bgr: np.ndarray, mask: np.ndarray) -> np.ndarray:
	"""
	Применение маски к изображению.

	Args:
		image_bgr (np.ndarray): Исходное изображение в формате BGR.
		mask (np.ndarray): Двоичная маска (одноканальное изображение).

	Returns:
		np.ndarray: Новое изображение, где сохраняются только пиксели,
		соответствующие белым областям маски, остальные зануляются.

	Raises:
		ValueError: Если входное изображение или маска пусты,
		либо если размеры не совпадают.
	"""
	return cv2.bitwise_and(image_bgr, image_bgr, mask=mask)


# --- Шаг 5. Отобразить результат ---
def show_result(original: np.ndarray, mask: np.ndarray, result: np.ndarray) -> None:
	"""
	Отображение исходного изображения, маски и результата.

	Args:
		original (np.ndarray): Исходное изображение в формате BGR.
		mask (np.ndarray): Двоичная маска.
		result (np.ndarray): Изображение после применения маски.

	Returns:
		None: Функция только выводит изображения в окна.

	Raises:
		ValueError: Если одно из изображений пустое.
	"""

	cv2.imshow("Original", original)
	cv2.imshow("Combined Mask", mask)
	cv2.imshow("Result", result)
	cv2.waitKey(0)
	cv2.destroyAllWindows()


# --- Основная логика ---
def main_process_file(img_path: str) -> None:
	"""
	Основная функция обработки файла-изображения:
	загрузка, создание масок, объединение и отображение.

	Args:
		img_path (str): Путь до входного файла-изображения.

	Returns:
		None: Функция выполняет обработку и отображает результат.

	Raises:
		FileNotFoundError: Если файл по указанному пути отсутствует.
		ValueError: Если изображение не удалось загрузить
			или его формат некорректен.
	"""
	if not os.path.isfile(img_path):
		raise FileNotFoundError(f"Файл '{img_path}' не существует.")

	img = load_image(img_path)
	if img is None:
		raise ValueError(f"Не удалось загрузить изображение: {img_path}")

	mask_red = create_red_mask(img)
	mask_blue = create_blue_mask(img)
	combined_mask = combine_masks(mask_red, mask_blue)
	result = apply_mask(img, combined_mask)

	show_result(img, combined_mask, result)


def example_synthetic() -> None:
	"""
	Пример на синтетическом изображении:
	рисуем красный и синий круги.
	"""
	img = np.zeros((200, 200, 3), dtype=np.uint8)     # изображение 200*200 BGR.
	cv2.circle(img, (65, 100), 40, (0, 0, 255), -1)   # красный (BGR)
	cv2.circle(img, (135, 100), 40, (255, 0, 0), -1)  # синий (BGR)

	mask_red = create_red_mask(img)
	mask_blue = create_blue_mask(img)
	combined_mask = combine_masks(mask_red, mask_blue)
	result = apply_mask(img, combined_mask)

	show_result(img, combined_mask, result)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		description="CV-2-04: Объединение масок для красного и синего цветов."
	)

	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument(
		"--example_synthetic",
		action="store_true",
		help="Сгенерировать синтетическое изображение с красным и синим объектами."
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

