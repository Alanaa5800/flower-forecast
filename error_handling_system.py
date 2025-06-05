
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import warnings

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('flower_forecast_errors.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FlowerForecastErrorHandler:
    """
    Система обработки ошибок для прогнозирования продаж цветов
    """

    def __init__(self):
        self.error_stats = {
            'missing_data': 0,
            'new_sku': 0,
            'anomaly_high': 0,
            'anomaly_low': 0,
            'integration_errors': 0
        }

    def validate_sales_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Валидация данных о продажах

        Args:
            df: DataFrame с данными о продажах

        Returns:
            Tuple[pd.DataFrame, List[str]]: очищенные данные и список ошибок
        """
        errors = []

        try:
            # Проверка наличия обязательных колонок
            required_columns = ['Дата', 'Магазин', 'SKU', 'Количество']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                error_msg = f"Отсутствуют обязательные колонки: {missing_columns}"
                errors.append(error_msg)
                logger.error(error_msg)
                return df, errors

            # Проверка типов данных
            df = self._fix_data_types(df, errors)

            # Обработка пропущенных значений
            df = self._handle_missing_values(df, errors)

            # Проверка на аномалии
            df = self._detect_and_handle_anomalies(df, errors)

            # Проверка дубликатов
            df = self._handle_duplicates(df, errors)

            logger.info(f"Валидация завершена. Найдено {len(errors)} ошибок")
            return df, errors

        except Exception as e:
            error_msg = f"Критическая ошибка валидации: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg, exc_info=True)
            return df, errors

    def _fix_data_types(self, df: pd.DataFrame, errors: List[str]) -> pd.DataFrame:
        """Исправление типов данных"""
        try:
            # Преобразование даты
            if 'Дата' in df.columns:
                df['Дата'] = pd.to_datetime(df['Дата'], errors='coerce')
                invalid_dates = df['Дата'].isna().sum()
                if invalid_dates > 0:
                    errors.append(f"Найдено {invalid_dates} некорректных дат")
                    self.error_stats['missing_data'] += invalid_dates

            # Преобразование количества
            if 'Количество' in df.columns:
                df['Количество'] = pd.to_numeric(df['Количество'], errors='coerce')
                invalid_quantities = df['Количество'].isna().sum()
                if invalid_quantities > 0:
                    errors.append(f"Найдено {invalid_quantities} некорректных значений количества")
                    self.error_stats['missing_data'] += invalid_quantities

            # Преобразование цены (если есть)
            if 'Цена' in df.columns:
                df['Цена'] = pd.to_numeric(df['Цена'], errors='coerce')

            return df

        except Exception as e:
            logger.error(f"Ошибка при исправлении типов данных: {e}")
            return df

    def _handle_missing_values(self, df: pd.DataFrame, errors: List[str]) -> pd.DataFrame:
        """Обработка пропущенных значений"""
        try:
            initial_count = len(df)

            # Удаляем строки с пропущенными критическими данными
            df = df.dropna(subset=['Дата', 'Магазин', 'SKU'])

            # Заполняем пропущенные количества нулями (может означать отсутствие продаж)
            if 'Количество' in df.columns:
                missing_quantities = df['Количество'].isna().sum()
                if missing_quantities > 0:
                    df['Количество'] = df['Количество'].fillna(0)
                    errors.append(f"Заполнено {missing_quantities} пропущенных значений количества нулями")

            # Заполняем пропущенные цены медианными значениями по SKU
            if 'Цена' in df.columns:
                df['Цена'] = df.groupby('SKU')['Цена'].transform(
                    lambda x: x.fillna(x.median())
                )

                # Если всё ещё есть пропуски, заполняем общей медианой
                if df['Цена'].isna().any():
                    df['Цена'] = df['Цена'].fillna(df['Цена'].median())

            removed_count = initial_count - len(df)
            if removed_count > 0:
                errors.append(f"Удалено {removed_count} строк с критическими пропусками")
                self.error_stats['missing_data'] += removed_count

            return df

        except Exception as e:
            logger.error(f"Ошибка при обработке пропущенных значений: {e}")
            return df

    def _detect_and_handle_anomalies(self, df: pd.DataFrame, errors: List[str]) -> pd.DataFrame:
        """Детекция и обработка аномалий"""
        try:
            if 'Количество' not in df.columns:
                return df

            # Аномально высокие значения (больше 99.5 перцентиля)
            high_threshold = df['Количество'].quantile(0.995)
            high_anomalies = df['Количество'] > high_threshold
            high_count = high_anomalies.sum()

            if high_count > 0:
                # Ограничиваем аномально высокие значения
                df.loc[high_anomalies, 'Количество'] = high_threshold
                errors.append(f"Обнаружено и исправлено {high_count} аномально высоких значений")
                self.error_stats['anomaly_high'] += high_count

            # Аномально низкие значения (отрицательные количества)
            low_anomalies = df['Количество'] < 0
            low_count = low_anomalies.sum()

            if low_count > 0:
                df.loc[low_anomalies, 'Количество'] = 0
                errors.append(f"Обнаружено и исправлено {low_count} отрицательных значений")
                self.error_stats['anomaly_low'] += low_count

            return df

        except Exception as e:
            logger.error(f"Ошибка при детекции аномалий: {e}")
            return df

    def _handle_duplicates(self, df: pd.DataFrame, errors: List[str]) -> pd.DataFrame:
        """Обработка дубликатов"""
        try:
            initial_count = len(df)

            # Проверяем дубликаты по ключевым полям
            duplicate_mask = df.duplicated(subset=['Дата', 'Магазин', 'SKU'], keep='last')
            duplicates_count = duplicate_mask.sum()

            if duplicates_count > 0:
                df = df[~duplicate_mask]
                errors.append(f"Удалено {duplicates_count} дубликатов")
                logger.warning(f"Найдено и удалено {duplicates_count} дубликатов")

            return df

        except Exception as e:
            logger.error(f"Ошибка при обработке дубликатов: {e}")
            return df

    def handle_new_sku(self, sku: str, store: str) -> Dict:
        """
        Обработка нового SKU

        Args:
            sku: артикул товара
            store: магазин

        Returns:
            Dict: рекомендации для нового SKU
        """
        try:
            self.error_stats['new_sku'] += 1
            logger.info(f"Обработка нового SKU: {sku} в магазине {store}")

            # Базовая логика для нового товара
            recommendations = {
                'initial_forecast': 5,  # консервативный прогноз
                'recommended_purchase': 10,  # минимальная закупка
                'confidence': 'Низкая',
                'strategy': 'Тестовая закупка',
                'monitoring_period': 14,  # дней наблюдения
                'notes': f'Новый SKU {sku}. Требуется наблюдение в течение {14} дней.'
            }

            # Попытка найти похожие товары для трансферного обучения
            similar_sku_forecast = self._find_similar_sku_forecast(sku)
            if similar_sku_forecast:
                recommendations['initial_forecast'] = similar_sku_forecast
                recommendations['recommended_purchase'] = similar_sku_forecast * 2
                recommendations['confidence'] = 'Средняя'
                recommendations['strategy'] = 'На основе похожих товаров'

            return recommendations

        except Exception as e:
            logger.error(f"Ошибка при обработке нового SKU {sku}: {e}")
            return {
                'initial_forecast': 5,
                'recommended_purchase': 10,
                'confidence': 'Низкая',
                'strategy': 'Ошибка обработки',
                'error': str(e)
            }

    def _find_similar_sku_forecast(self, sku: str) -> Optional[int]:
        """Поиск прогноза для похожих товаров"""
        try:
            # Простая логика поиска похожих товаров по названию
            flower_types = {
                'роза': 25,
                'тюльпан': 15,
                'хризантема': 10,
                'лилия': 12,
                'гвоздика': 8,
                'мимоза': 20,
                'нарцисс': 10
            }

            sku_lower = sku.lower()
            for flower_type, forecast in flower_types.items():
                if flower_type in sku_lower:
                    return forecast

            return None

        except Exception:
            return None

    def validate_forecast_output(self, forecast_df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Валидация выходных данных прогноза

        Args:
            forecast_df: DataFrame с прогнозом

        Returns:
            Tuple[pd.DataFrame, List[str]]: валидированный прогноз и ошибки
        """
        errors = []

        try:
            # Проверка аномально высоких прогнозов
            if 'Прогноз_спроса' in forecast_df.columns:
                high_forecast_threshold = forecast_df['Прогноз_спроса'].quantile(0.99) * 2
                high_forecasts = forecast_df['Прогноз_спроса'] > high_forecast_threshold

                if high_forecasts.any():
                    count = high_forecasts.sum()
                    # Помечаем аномальные прогнозы для ручной проверки
                    forecast_df.loc[high_forecasts, 'Требует_проверки'] = True
                    forecast_df.loc[high_forecasts, 'Причина_проверки'] = 'Аномально высокий прогноз'

                    errors.append(f"Обнаружено {count} аномально высоких прогнозов")
                    self.error_stats['anomaly_high'] += count

            # Проверка нереалистично низких прогнозов
            if 'Прогноз_спроса' in forecast_df.columns:
                zero_forecasts = forecast_df['Прогноз_спроса'] == 0
                if zero_forecasts.any():
                    count = zero_forecasts.sum()
                    forecast_df.loc[zero_forecasts, 'Требует_проверки'] = True
                    forecast_df.loc[zero_forecasts, 'Причина_проверки'] = 'Нулевой прогноз'

                    errors.append(f"Обнаружено {count} нулевых прогнозов")

            return forecast_df, errors

        except Exception as e:
            error_msg = f"Ошибка валидации прогноза: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg, exc_info=True)
            return forecast_df, errors

    def handle_integration_error(self, error_type: str, details: str) -> Dict:
        """
        Обработка ошибок интеграции

        Args:
            error_type: тип ошибки (google_sheets, inspiro, weather_api)
            details: детали ошибки

        Returns:
            Dict: рекомендации по устранению
        """
        self.error_stats['integration_errors'] += 1

        recommendations = {
            'google_sheets': {
                'immediate_action': 'Проверить права доступа к таблице',
                'backup_plan': 'Использовать локальные файлы CSV',
                'retry_interval': 300,  # 5 минут
                'escalation_threshold': 3
            },
            'inspiro': {
                'immediate_action': 'Проверить статус системы Inspiro',
                'backup_plan': 'Использовать последние загруженные данные',
                'retry_interval': 600,  # 10 минут
                'escalation_threshold': 2
            },
            'weather_api': {
                'immediate_action': 'Проверить API ключ',
                'backup_plan': 'Использовать исторические погодные данные',
                'retry_interval': 1800,  # 30 минут
                'escalation_threshold': 5
            }
        }

        logger.error(f"Ошибка интеграции {error_type}: {details}")

        return recommendations.get(error_type, {
            'immediate_action': 'Проверить подключение',
            'backup_plan': 'Использовать резервные данные',
            'retry_interval': 300,
            'escalation_threshold': 3
        })

    def get_error_report(self) -> Dict:
        """Получение отчета об ошибках"""
        total_errors = sum(self.error_stats.values())

        return {
            'total_errors': total_errors,
            'error_breakdown': self.error_stats.copy(),
            'error_rate': {
                'missing_data_rate': self.error_stats['missing_data'] / max(total_errors, 1),
                'anomaly_rate': (self.error_stats['anomaly_high'] + self.error_stats['anomaly_low']) / max(total_errors, 1),
                'integration_error_rate': self.error_stats['integration_errors'] / max(total_errors, 1)
            },
            'recommendations': self._generate_improvement_recommendations()
        }

    def _generate_improvement_recommendations(self) -> List[str]:
        """Генерация рекомендаций по улучшению качества данных"""
        recommendations = []

        if self.error_stats['missing_data'] > 10:
            recommendations.append("Улучшить процедуры сбора данных для снижения количества пропусков")

        if self.error_stats['anomaly_high'] > 5:
            recommendations.append("Внедрить проверки качества данных на этапе ввода")

        if self.error_stats['new_sku'] > 3:
            recommendations.append("Разработать процедуру вводы новых товаров с базовыми прогнозами")

        if self.error_stats['integration_errors'] > 2:
            recommendations.append("Проверить стабильность интеграционных подключений")

        return recommendations

# Пример использования
if __name__ == "__main__":
    error_handler = FlowerForecastErrorHandler()

    # Создаем тестовые данные с ошибками
    test_data = pd.DataFrame({
        'Дата': ['2025-06-07', '2025-06-08', 'invalid_date', '2025-06-09'],
        'Магазин': ['Алматы_1', 'Алматы_2', 'Алматы_1', 'Алматы_3'],
        'SKU': ['Роза_красная', 'Тюльпан_белый', 'Роза_красная', 'Новый_товар'],
        'Количество': [25, 'invalid', -5, 1000]
    })

    # Валидация данных
    cleaned_data, errors = error_handler.validate_sales_data(test_data)

    print("Очищенные данные:")
    print(cleaned_data)
    print("\nОшибки:", errors)

    # Отчет об ошибках
    error_report = error_handler.get_error_report()
    print("\nОтчет об ошибках:", error_report)
