#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python -*-
# vim: set filetype=python :
"""
DA-1-35: Создание временной метки.
Задача: работа с временными метками.
"""

import pandas as pd


def create_dataframe(periods: int = 100, freq: str = "14h") -> pd.DataFrame:
    """
    Создание датафрейма с синтетическими временными метками (строками).
    """
    timestamps = pd.date_range(
        start="2025-01-01 02:35:00",  # начальная точка
        periods=periods,                   # количество меток
        freq=freq                    # шаг = 9 часов
    )
    return pd.DataFrame({"timestamp": timestamps})


def convert_to_datetime(df: pd.DataFrame) -> pd.DataFrame:
    """
    Преобразование строковых меток во временной формат datetime.
    """
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def extract_parts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Извлечение дня, месяца и года из временной метки.
    """
    new_df = pd.DataFrame()
    new_df["timestamp"] = df["timestamp"]
    new_df["day"] = df["timestamp"].dt.day
    new_df["month"] = df["timestamp"].dt.month
    new_df["year"] = df["timestamp"].dt.year
    return new_df.copy()


def main():
    # 1. Создание столбеца с временными метками. 
    df = create_dataframe(periods=80, freq="20h20s")
    # 2. Преобразование в datetime. 
    df = convert_to_datetime(df)
    # 3. Извлечение дня, месяца, года.
    df = extract_parts(df)
    print(df)


if __name__ == "__main__":
    main()

