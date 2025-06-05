
import gspread
import pandas as pd
import os
from google.oauth2.service_account import Credentials
import time
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FlowerForecastGSheetsIntegration:
    """
    Класс для интеграции системы прогнозирования с Google Sheets
    """

    def __init__(self, credentials_path, spreadsheet_url):
        """
        Инициализация подключения к Google Sheets

        Args:
            credentials_path: путь к JSON файлу с ключами сервисного аккаунта
            spreadsheet_url: ссылка на Google Таблицу
        """
        self.credentials_path = credentials_path
        self.spreadsheet_url = spreadsheet_url
        self.gc = None
        self.sheet = None
        self._connect()

    def _connect(self):
        """Установка соединения с Google Sheets API"""
        try:
            # Области доступа для Google Sheets и Google Drive
            scope = ['https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive']

            # Аутентификация через сервисный аккаунт
            creds = Credentials.from_service_account_file(
                self.credentials_path, 
                scopes=scope
            )

            self.gc = gspread.authorize(creds)
            self.sheet = self.gc.open_by_url(self.spreadsheet_url)

            logger.info("✅ Успешное подключение к Google Sheets")

        except Exception as e:
            logger.error(f"❌ Ошибка подключения к Google Sheets: {e}")
            raise

    def load_sales_data(self, worksheet_name="Продажи"):
        """
        Загрузка данных о продажах из Google Sheets

        Args:
            worksheet_name: название листа с данными о продажах

        Returns:
            pandas.DataFrame: данные о продажах
        """
        try:
            worksheet = self.sheet.worksheet(worksheet_name)
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)

            # Преобразование типов данных
            if 'Дата' in df.columns:
                df['Дата'] = pd.to_datetime(df['Дата'], errors='coerce')
            if 'Количество' in df.columns:
                df['Количество'] = pd.to_numeric(df['Количество'], errors='coerce')
            if 'Цена' in df.columns:
                df['Цена'] = pd.to_numeric(df['Цена'], errors='coerce')

            logger.info(f"📊 Загружено {len(df)} записей о продажах")
            return df

        except Exception as e:
            logger.error(f"❌ Ошибка загрузки данных продаж: {e}")
            return pd.DataFrame()

    def load_inventory_data(self, worksheet_name="Остатки"):
        """
        Загрузка данных об остатках из Google Sheets

        Args:
            worksheet_name: название листа с остатками

        Returns:
            pandas.DataFrame: данные об остатках
        """
        try:
            worksheet = self.sheet.worksheet(worksheet_name)
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)

            # Преобразование типов
            if 'Остаток' in df.columns:
                df['Остаток'] = pd.to_numeric(df['Остаток'], errors='coerce')

            logger.info(f"📦 Загружено данных об остатках: {len(df)} записей")
            return df

        except Exception as e:
            logger.error(f"❌ Ошибка загрузки остатков: {e}")
            return pd.DataFrame()

    def save_forecast(self, forecast_df, worksheet_name="Прогноз"):
        """
        Сохранение прогноза в Google Sheets

        Args:
            forecast_df: DataFrame с прогнозом
            worksheet_name: название листа для сохранения
        """
        try:
            # Проверяем существование листа
            try:
                worksheet = self.sheet.worksheet(worksheet_name)
                worksheet.clear()  # Очищаем существующие данные
            except gspread.WorksheetNotFound:
                # Создаем новый лист
                worksheet = self.sheet.add_worksheet(
                    title=worksheet_name, 
                    rows=len(forecast_df)+10, 
                    cols=len(forecast_df.columns)+2
                )

            # Конвертируем DataFrame в список списков
            data_to_upload = [forecast_df.columns.tolist()] + forecast_df.values.tolist()

            # Загружаем данные
            worksheet.update('A1', data_to_upload)

            # Форматирование заголовков
            worksheet.format('A1:Z1', {
                'backgroundColor': {'red': 0.8, 'green': 0.8, 'blue': 0.8},
                'textFormat': {'bold': True}
            })

            logger.info(f"💾 Прогноз сохранен в лист '{worksheet_name}'")

        except Exception as e:
            logger.error(f"❌ Ошибка сохранения прогноза: {e}")

    def load_user_corrections(self, worksheet_name="Корректировки"):
        """
        Загрузка пользовательских корректировок прогноза

        Args:
            worksheet_name: название листа с корректировками

        Returns:
            pandas.DataFrame: корректировки пользователей
        """
        try:
            worksheet = self.sheet.worksheet(worksheet_name)
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)

            if len(df) > 0:
                logger.info(f"✏️ Загружено {len(df)} корректировок")

            return df

        except gspread.WorksheetNotFound:
            logger.info("📝 Лист корректировок не найден, создаем новый")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки корректировок: {e}")
            return pd.DataFrame()

# Пример использования
if __name__ == "__main__":
    # Параметры подключения
    CREDENTIALS_PATH = "service_account_key.json"
    SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/your_spreadsheet_id/edit"

    # Создание интеграции
    integrator = FlowerForecastGSheetsIntegration(CREDENTIALS_PATH, SPREADSHEET_URL)

    # Загрузка данных
    sales_data = integrator.load_sales_data()
    inventory_data = integrator.load_inventory_data()

    # Пример данных прогноза
    forecast_example = pd.DataFrame({
        'Дата': ['2025-06-07', '2025-06-08', '2025-06-09'],
        'Магазин': ['Алматы_1', 'Алматы_1', 'Алматы_1'],
        'SKU': ['Роза_красная_60см', 'Тюльпан_белый', 'Хризантема_желтая'],
        'Прогноз_спроса': [45, 23, 18],
        'Текущий_остаток': [12, 35, 8],
        'Рекомендация_закупки': [40, 0, 15],
        'Приоритет': ['Высокий', 'Низкий', 'Средний']
    })

    # Сохранение прогноза
    integrator.save_forecast(forecast_example)
    print("Скрипт интеграции с Google Sheets создан")
