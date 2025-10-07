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

