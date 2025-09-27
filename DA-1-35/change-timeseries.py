#!/usr/bin/env python3
# -*- coding: utf-8  -*-
# -*- mode:   python -*-

# This file is part of the educational Data Analysis tasks.
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
DA-1-35: Работа с timeseries.
Задача:
Создание, преобразование, и использование столбца с временными метками (timeseries).
"""

import os
import argparse
import pandas as pd


def load_dataframe_from_file(path: str) -> pd.DataFrame:
	"""
	Загрузка таблицы из CSV файла.

	Args:
		path (str): Путь до CSV файла.

	Returns:
		pd.DataFrame: Таблица с одним столбцом "timestamp".

	Raises:
		FileNotFoundError: Если файл не существует.
		ValueError: Если в файле неверная структура или данные не читаются.
	"""
	if not os.path.exists(path):
		raise FileNotFoundError(f"Файл не найден: {path}")

	try:
		df = pd.read_csv(path)
	except Exception as e:
		raise ValueError(f"Ошибка чтения CSV: {e}")

	if df.shape[1] != 1:
		raise ValueError("Ожидался ровно один столбец во входном CSV.")

	# Приводим имя столбца к "timestamp" для единообразия
	df.columns = ["timestamp"]

	return df


def create_periodic_dataframe(
		start_timedate_point: str, periods: int, freq: str
	) -> pd.DataFrame:
	"""
	Создание таблицы с временными метками
	в строковом представлении,
	синтетическим способом - через распределительную функцию.
	
	Args:
		start_timedate_point (str): Строка "YYYY-MM-DD HH:MM:SS"
		periods (int): Число создаваемых значений (число меток в столбце)
		freq (str): Шаг между значениями

	Returns:
		pd.DataFrame: Заполненная таблица при успехе, и пустая таблица при ошибке.

	Raises:
		Exception: Любые исключения, возникающие в процессе создания таблицы
	"""
	try:
		timestamps = pd.date_range(
			start=start_timedate_point,
			periods=periods,
			freq=freq
		)
		# .to_frame(index=False, name="timestamp")
		return pd.DataFrame({"timestamp": timestamps})
	
	except Exception as e:
	        print(f"Ошибка при создании строковых временных меток: {e}")


def convert_to_datetime(df: pd.DataFrame) -> pd.DataFrame:
	"""
	Преобразование строковых меток во временной формат datetime.

	Args:
		df (pd.DataFrame): Таблица, содержащая столбец "timestamp"
			(строковые или datetime-совместимые значения).

	Returns:
		pd.DataFrame: Копия таблицы, где столбец "timestamp" приведён к типу datetime64.

	Raises:
		KeyError: Если отсутствует столбец "timestamp".
		ValueError: Если значения в столбце нельзя преобразовать в datetime.
	"""

	if "timestamp" not in df.columns:
		raise KeyError("Отсутствует обязательный столбец 'timestamp'.")

	try:
		result = df.copy()
		
		result["timestamp"] = pd.to_datetime(result["timestamp"], errors="raise")
		return result

	except Exception as e:
		raise ValueError(f"Ошибка преобразования в datetime: {e}")


def extract_parts(df: pd.DataFrame) -> pd.DataFrame:
	"""
	Извлечение дня, месяца и года из временной метки.

	Args:
		in_df (pd.DataFrame): Таблица с датами в столбце "timestamp"
			(должен иметь тип datetime64).

	Returns:
		pd.DataFrame: Таблица с новыми столбцами:
		#	- "timestamp" (копия исходного)
			- "day" (день месяца, int)
			- "month" (номер месяца, int)
			- "year" (год, int)

	Raises:
		KeyError: Если отсутствует столбец "timestamp".
		TypeError: Если столбец "timestamp" не имеет тип datetime.
	"""
	if "timestamp" not in df.columns:
		raise KeyError("Отсутствует обязательный столбец 'timestamp'.")

	if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
		raise TypeError("Столбец 'timestamp' должен быть формата datetime.")

	new_df = pd.DataFrame()

	# Добавление полного столбца для проверки datetime правильности.
	# new_df["timestamp"] = df["timestamp"]

	# Извлечение искомых признаков
	new_df["day"]   = df["timestamp"].dt.day
	new_df["month"] = df["timestamp"].dt.month
	new_df["year"]  = df["timestamp"].dt.year

	return new_df.copy()  # копируем заполненный экземпляр из функции.


def example_main_synthetic():
	# 1. Создание столбца с временными метками. 
	input_df = create_periodic_dataframe(
		start_timedate_point="2025-09-16 02:35:00",
		periods=15, freq="14h"
	)
	# 2. Преобразование в datetime. 
	transformed_df = convert_to_datetime(input_df)
	# 3. Извлечение дня, месяца, года.
	result_df = extract_parts(transformed_df)
	# 4. Вывод плодов работы
	print(result_df)


def main_read_file(input_csv):
	# 1. Чтение столбца с временными метками. 
	input_df = load_dataframe_from_file(input_csv)
	# 2. Преобразование в datetime. 
	transformed_df = convert_to_datetime(input_df)
	# 3. Извлечение дня, месяца, года.
	result_df = extract_parts(transformed_df)
	# 4. Вывод плодов работы
	print(result_df)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		description="Работа с временными метками (timeseries)."
	)

	# Взаимоисключающие параметры
	group = parser.add_mutually_exclusive_group(required=True)  
	group.add_argument(
		"--example_synthetic",
		action="store_true",
		help="Сгенерировать синтетические временные метки."
	)
	group.add_argument(
		"--file",
		type=str,
		help="Загрузить данные из CSV файла."
	)

	args = parser.parse_args()

	if args.example_synthetic:
		example_main_synthetic()
	elif args.file:
		main_read_file(args.file)

