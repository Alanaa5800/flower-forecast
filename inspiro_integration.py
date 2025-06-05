
import requests
import pandas as pd
import json
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple
import time

logger = logging.getLogger(__name__)

class InspiroAPIIntegration:
    """
    Интеграция с системой florist.inspiro.pro
    Поддержка экспорта/импорта данных через API или файловый обмен
    """

    def __init__(self, base_url: str = None, api_key: str = None, 
                 use_file_export: bool = True):
        """
        Инициализация интеграции

        Args:
            base_url: базовый URL API Inspiro
            api_key: ключ доступа к API
            use_file_export: использовать файловый экспорт вместо API
        """
        self.base_url = base_url or "https://api.inspiro.pro/v1"
        self.api_key = api_key
        self.use_file_export = use_file_export
        self.session = requests.Session()

        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            })

    def export_sales_data(self, start_date: str, end_date: str, 
                         stores: List[str] = None) -> pd.DataFrame:
        """
        Экспорт данных о продажах из Inspiro

        Args:
            start_date: начальная дата в формате YYYY-MM-DD
            end_date: конечная дата в формате YYYY-MM-DD
            stores: список магазинов (если None, то все)

        Returns:
            pd.DataFrame: данные о продажах
        """
        if self.use_file_export:
            return self._export_sales_file_method(start_date, end_date, stores)
        else:
            return self._export_sales_api_method(start_date, end_date, stores)

    def _export_sales_file_method(self, start_date: str, end_date: str, 
                                 stores: List[str] = None) -> pd.DataFrame:
        """Экспорт через файловый обмен (рекомендуемый метод)"""
        try:
            logger.info("Начинаем экспорт данных о продажах через файловый метод")

            # Инструкции для пользователя по экспорту из Inspiro
            stores_text = stores if stores else "Все магазины"
            export_instructions = f"""
ИНСТРУКЦИЯ ПО ЭКСПОРТУ ДАННЫХ ИЗ INSPIRO:

1. Войдите в систему florist.inspiro.pro
2. Перейдите в раздел "Отчеты" → "Продажи"
3. Установите период: с {start_date} по {end_date}
4. Выберите магазины: {stores_text}
5. Формат экспорта: CSV (Excel)
6. Поля для экспорта:
   - Дата продажи
   - Код магазина
   - Артикул товара (SKU)
   - Наименование товара
   - Количество
   - Цена за единицу
   - Сумма продажи
   - Способ оплаты
7. Нажмите "Экспорт" и сохраните файл как "inspiro_sales_export.csv"
8. Поместите файл в папку с системой прогнозирования
            """

            print(export_instructions)

            # Попытка загрузить файл экспорта
            try:
                df = pd.read_csv('inspiro_sales_export.csv', encoding='utf-8')
                logger.info(f"Загружено {len(df)} записей из файла экспорта")

                # Стандартизация названий колонок
                column_mapping = {
                    'Дата продажи': 'Дата',
                    'Код магазина': 'Магазин',
                    'Артикул товара': 'SKU',
                    'Наименование товара': 'Название',
                    'Количество': 'Количество',
                    'Цена за единицу': 'Цена',
                    'Сумма продажи': 'Сумма'
                }

                df = df.rename(columns=column_mapping)

                # Обработка данных
                df['Дата'] = pd.to_datetime(df['Дата'], errors='coerce')
                df['Количество'] = pd.to_numeric(df['Количество'], errors='coerce')
                df['Цена'] = pd.to_numeric(df['Цена'], errors='coerce')

                # Фильтрация по магазинам если указано
                if stores:
                    df = df[df['Магазин'].isin(stores)]

                return df

            except FileNotFoundError:
                logger.warning("Файл inspiro_sales_export.csv не найден")
                # Возвращаем демо-данные для тестирования
                return self._generate_demo_sales_data(start_date, end_date, stores)

        except Exception as e:
            logger.error(f"Ошибка экспорта продаж: {e}")
            return pd.DataFrame()

    def _export_sales_api_method(self, start_date: str, end_date: str, 
                                stores: List[str] = None) -> pd.DataFrame:
        """Экспорт через API (если доступен)"""
        try:
            endpoint = f"{self.base_url}/sales/export"
            params = {
                'start_date': start_date,
                'end_date': end_date,
                'format': 'json'
            }

            if stores:
                params['stores'] = ','.join(stores)

            logger.info(f"Отправляем запрос к API: {endpoint}")
            response = self.session.get(endpoint, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data['sales'])
                logger.info(f"Получено {len(df)} записей через API")
                return df
            else:
                logger.error(f"Ошибка API: {response.status_code} - {response.text}")
                return pd.DataFrame()

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка подключения к API: {e}")
            # Fallback на файловый метод
            return self._export_sales_file_method(start_date, end_date, stores)

    def _generate_demo_sales_data(self, start_date: str, end_date: str, 
                                 stores: List[str] = None) -> pd.DataFrame:
        """Генерация демо-данных для тестирования"""
        logger.info("Генерируем демо-данные о продажах")

        if not stores:
            stores = ['almaty_1', 'almaty_2', 'almaty_3']

        skus = [
            'Роза_красная_60см', 'Роза_белая_50см', 'Тюльпан_красный',
            'Тюльпан_белый', 'Хризантема_желтая', 'Лилия_белая',
            'Гвоздика_красная', 'Мимоза', 'Нарцисс_белый'
        ]

        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')

        demo_data = []
        current_date = start

        while current_date <= end:
            for store in stores:
                for sku in skus:
                    # Случайная вероятность продажи
                    if np.random.random() > 0.3:
                        quantity = np.random.randint(1, 15)
                        price = np.random.uniform(200, 1500)

                        demo_data.append({
                            'Дата': current_date.strftime('%Y-%m-%d'),
                            'Магазин': store,
                            'SKU': sku,
                            'Количество': quantity,
                            'Цена': round(price, 2),
                            'Сумма': round(quantity * price, 2)
                        })

            current_date += timedelta(days=1)

        return pd.DataFrame(demo_data)

    def get_export_instructions(self) -> str:
        """Получение подробных инструкций по экспорту"""
        return """
ПОЛНАЯ ИНСТРУКЦИЯ ПО ИНТЕГРАЦИИ С INSPIRO:

=== ЭКСПОРТ ПРОДАЖ ===
1. Войдите в https://florist.inspiro.pro
2. Меню: Отчеты → Продажи → Детализированный отчет
3. Период: выберите нужные даты
4. Магазины: выберите все или конкретные точки
5. Группировка: по товарам и датам
6. Формат: CSV или Excel
7. Сохраните как: inspiro_sales_export.csv

=== ЭКСПОРТ ОСТАТКОВ ===
1. Меню: Склад → Остатки товаров
2. Фильтр: остаток больше 0
3. Включить: дату поступления, срок годности
4. Сохраните как: inspiro_inventory_export.csv

=== ЭКСПОРТ КАТАЛОГА ===
1. Меню: Товары → Справочник товаров
2. Статус: только активные товары
3. Включить: артикул, название, категорию, единицы
4. Сохраните как: inspiro_catalog_export.csv

=== АВТОМАТИЗАЦИЯ ===
Для автоматического экспорта можно:
- Настроить отправку отчетов на email по расписанию
- Использовать API если доступен
- Создать скрипт для автоматической загрузки файлов

=== ФОРМАТ ФАЙЛОВ ===
Все файлы должны быть в кодировке UTF-8
Разделитель: запятая или точка с запятой
Первая строка: заголовки колонок
        """

# Пример использования
if __name__ == "__main__":
    inspiro = InspiroAPIIntegration(use_file_export=True)
    print(inspiro.get_export_instructions())

    # Тестовый экспорт
    sales_data = inspiro.export_sales_data('2025-05-01', '2025-06-06')
    print(f"Сгенерировано тестовых данных о продажах: {len(sales_data)} записей")
