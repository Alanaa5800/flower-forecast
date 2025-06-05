# Создаем архитектуру мульти-магазинной системы
multi_store_architecture = '''
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import logging

logger = logging.getLogger(__name__)

class MultiStoreForecastManager:
    """
    Менеджер прогнозирования для сети магазинов
    Поддерживает масштабирование и индивидуальные настройки для каждого магазина
    """
    
    def __init__(self, config_path: str = "stores_config.json"):
        """
        Инициализация менеджера
        
        Args:
            config_path: путь к файлу конфигурации магазинов
        """
        self.stores_config = self._load_stores_config(config_path)
        self.store_models = {}
        self.store_metrics = {}
        
    def _load_stores_config(self, config_path: str) -> Dict:
        """Загрузка конфигурации магазинов"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Создаем базовую конфигурацию если файл не найден
            default_config = self._create_default_config()
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            return default_config
    
    def _create_default_config(self) -> Dict:
        """Создание конфигурации по умолчанию"""
        return {
            "stores": {
                "almaty_1": {
                    "name": "Алматы ЦУМ",
                    "address": "пр. Абылай хана, 62",
                    "type": "premium",
                    "size_category": "large",
                    "opening_hours": {"start": "09:00", "end": "22:00"},
                    "target_audience": "premium_customers",
                    "avg_daily_visitors": 200,
                    "seasonal_multipliers": {
                        "winter": 0.8,
                        "spring": 1.2,
                        "summer": 1.0,
                        "autumn": 1.1
                    },
                    "holiday_multipliers": {
                        "WOMENS_DAY": 4.5,
                        "VALENTINES": 2.0,
                        "NAURYZ": 2.2
                    },
                    "weather_sensitivity": 0.3,
                    "forecast_horizon_days": 14,
                    "safety_stock_ratio": 1.2,
                    "active": True
                },
                "almaty_2": {
                    "name": "Алматы Мега",
                    "address": "ул. Розыбакиева, 247а",
                    "type": "mass_market",
                    "size_category": "large",
                    "opening_hours": {"start": "10:00", "end": "22:00"},
                    "target_audience": "families",
                    "avg_daily_visitors": 350,
                    "seasonal_multipliers": {
                        "winter": 0.9,
                        "spring": 1.3,
                        "summer": 1.1,
                        "autumn": 1.0
                    },
                    "holiday_multipliers": {
                        "WOMENS_DAY": 4.0,
                        "VALENTINES": 1.8,
                        "NAURYZ": 2.5
                    },
                    "weather_sensitivity": 0.2,
                    "forecast_horizon_days": 7,
                    "safety_stock_ratio": 1.5,
                    "active": True
                },
                "almaty_3": {
                    "name": "Алматы Dostyk Plaza",
                    "address": "пр. Достык, 111",
                    "type": "premium",
                    "size_category": "medium",
                    "opening_hours": {"start": "10:00", "end": "21:00"},
                    "target_audience": "business_customers",
                    "avg_daily_visitors": 150,
                    "seasonal_multipliers": {
                        "winter": 0.7,
                        "spring": 1.1,
                        "summer": 0.9,
                        "autumn": 1.2
                    },
                    "holiday_multipliers": {
                        "WOMENS_DAY": 3.8,
                        "VALENTINES": 2.2,
                        "NAURYZ": 1.8
                    },
                    "weather_sensitivity": 0.4,
                    "forecast_horizon_days": 10,
                    "safety_stock_ratio": 1.3,
                    "active": True
                }
            },
            "global_settings": {
                "model_retrain_frequency_days": 7,
                "anomaly_detection_threshold": 2.5,
                "min_historical_data_days": 30,
                "max_forecast_horizon_days": 30,
                "default_safety_stock_ratio": 1.2,
                "currency": "KZT",
                "timezone": "Asia/Almaty"
            }
        }
    
    def add_new_store(self, store_id: str, store_config: Dict) -> bool:
        """
        Добавление нового магазина в систему
        
        Args:
            store_id: уникальный ID магазина
            store_config: конфигурация магазина
            
        Returns:
            bool: успешность добавления
        """
        try:
            # Валидация конфигурации
            required_fields = [
                'name', 'address', 'type', 'size_category', 
                'target_audience', 'avg_daily_visitors'
            ]
            
            for field in required_fields:
                if field not in store_config:
                    raise ValueError(f"Отсутствует обязательное поле: {field}")
            
            # Установка значений по умолчанию
            default_values = {
                'seasonal_multipliers': {
                    'winter': 0.9, 'spring': 1.1, 'summer': 1.0, 'autumn': 1.0
                },
                'holiday_multipliers': {
                    'WOMENS_DAY': 4.0, 'VALENTINES': 1.8, 'NAURYZ': 2.0
                },
                'weather_sensitivity': 0.25,
                'forecast_horizon_days': 7,
                'safety_stock_ratio': 1.2,
                'active': True
            }
            
            for key, value in default_values.items():
                if key not in store_config:
                    store_config[key] = value
            
            # Добавление в конфигурацию
            self.stores_config['stores'][store_id] = store_config
            
            # Сохранение конфигурации
            self._save_config()
            
            logger.info(f"Добавлен новый магазин: {store_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления магазина {store_id}: {e}")
            return False
    
    def get_store_forecast(self, store_id: str, forecast_days: int = None) -> pd.DataFrame:
        """
        Получение прогноза для конкретного магазина
        
        Args:
            store_id: ID магазина
            forecast_days: количество дней для прогноза
            
        Returns:
            pd.DataFrame: прогноз для магазина
        """
        if store_id not in self.stores_config['stores']:
            raise ValueError(f"Магазин {store_id} не найден в конфигурации")
        
        store_config = self.stores_config['stores'][store_id]
        
        if not store_config.get('active', True):
            logger.warning(f"Магазин {store_id} неактивен")
            return pd.DataFrame()
        
        if forecast_days is None:
            forecast_days = store_config.get('forecast_horizon_days', 7)
        
        # Генерация прогноза с учетом специфики магазина
        forecast = self._generate_store_specific_forecast(store_id, forecast_days)
        
        return forecast
    
    def _generate_store_specific_forecast(self, store_id: str, forecast_days: int) -> pd.DataFrame:
        """Генерация прогноза с учетом специфики магазина"""
        store_config = self.stores_config['stores'][store_id]
        
        # Список товаров по типу магазина
        premium_skus = [
            'Роза_Premium_80см', 'Пион_импорт', 'Орхидея_фаленопсис',
            'Лилия_ориенталь', 'Роза_Дэвид_Остин', 'Гортензия_крупная'
        ]
        
        mass_market_skus = [
            'Роза_стандарт_60см', 'Тюльпан_стандарт', 'Хризантема_куст',
            'Гвоздика_стандарт', 'Альстромерия', 'Герберы_микс'
        ]
        
        business_skus = [
            'Роза_бизнес_70см', 'Букет_корпоративный', 'Композиция_офис',
            'Роза_классик', 'Лилия_бизнес', 'Хризантема_одногол'
        ]
        
        # Выбор ассортимента в зависимости от типа магазина
        store_type = store_config.get('type', 'mass_market')
        if store_type == 'premium':
            skus = premium_skus
            base_demand_range = (15, 40)
        elif store_type == 'mass_market':
            skus = mass_market_skus
            base_demand_range = (25, 60)
        else:  # business
            skus = business_skus
            base_demand_range = (10, 35)
        
        forecast_data = []
        
        for day in range(forecast_days):
            date = datetime.now() + timedelta(days=day)
            
            for sku in skus:
                # Базовый спрос
                base_demand = np.random.randint(*base_demand_range)
                
                # Применение сезонных коэффициентов
                season = self._get_season(date)
                seasonal_mult = store_config['seasonal_multipliers'].get(season, 1.0)
                
                # Применение коэффициентов выходных
                if date.weekday() in [5, 6]:
                    weekend_mult = 1.3
                else:
                    weekend_mult = 1.0
                
                # Проверка праздников
                holiday_mult = self._get_holiday_multiplier(date, store_config)
                
                # Влияние погоды (упрощенная модель)
                weather_mult = self._get_weather_multiplier(store_config)
                
                # Итоговый прогноз
                final_demand = int(
                    base_demand * seasonal_mult * weekend_mult * 
                    holiday_mult * weather_mult
                )
                
                # Текущий остаток (случайное значение для демонстрации)
                current_stock = np.random.randint(0, 25)
                
                # Рекомендация закупки
                safety_stock_ratio = store_config.get('safety_stock_ratio', 1.2)
                recommended_purchase = max(0, int(final_demand * safety_stock_ratio - current_stock))
                
                # Приоритет
                if recommended_purchase > final_demand:
                    priority = 'Высокий'
                elif recommended_purchase > final_demand * 0.5:
                    priority = 'Средний'
                else:
                    priority = 'Низкий'
                
                forecast_data.append({
                    'Дата': date.strftime('%Y-%m-%d'),
                    'День_недели': date.strftime('%A'),
                    'Магазин': store_id,
                    'Название_магазина': store_config['name'],
                    'SKU': sku,
                    'Прогноз_спроса': final_demand,
                    'Текущий_остаток': current_stock,
                    'Рекомендация_закупки': recommended_purchase,
                    'Приоритет': priority,
                    'Сезонный_коэф': seasonal_mult,
                    'Праздничный_коэф': holiday_mult,
                    'Погодный_коэф': weather_mult
                })
        
        return pd.DataFrame(forecast_data)
    
    def get_network_forecast(self, forecast_days: int = 7) -> pd.DataFrame:
        """
        Получение прогноза для всей сети магазинов
        
        Args:
            forecast_days: количество дней для прогноза
            
        Returns:
            pd.DataFrame: сводный прогноз по сети
        """
        network_forecast = pd.DataFrame()
        
        for store_id in self.stores_config['stores']:
            if self.stores_config['stores'][store_id].get('active', True):
                store_forecast = self.get_store_forecast(store_id, forecast_days)
                network_forecast = pd.concat([network_forecast, store_forecast], 
                                           ignore_index=True)
        
        return network_forecast
    
    def get_consolidation_opportunities(self, forecast_df: pd.DataFrame) -> Dict:
        """
        Анализ возможностей консолидации закупок между магазинами
        
        Args:
            forecast_df: прогноз по сети
            
        Returns:
            Dict: рекомендации по консолидации
        """
        consolidation_opportunities = {}
        
        # Группируем по SKU и дате
        grouped = forecast_df.groupby(['Дата', 'SKU']).agg({
            'Рекомендация_закупки': 'sum',
            'Магазин': 'count'
        }).reset_index()
        
        # Переименовываем колонку для ясности
        grouped.rename(columns={'Магазин': 'Количество_магазинов'}, inplace=True)
        
        # Находим SKU с высоким общим спросом
        high_volume_items = grouped[grouped['Рекомендация_закупки'] >= 50]
        
        # Анализ по датам
        for date in grouped['Дата'].unique():
            date_data = high_volume_items[high_volume_items['Дата'] == date]
            
            if not date_data.empty:
                consolidation_opportunities[date] = {
                    'total_volume': date_data['Рекомендация_закупки'].sum(),
                    'top_items': date_data.nlargest(5, 'Рекомендация_закупки').to_dict('records'),
                    'potential_savings': date_data['Рекомендация_закупки'].sum() * 0.05  # 5% экономия
                }
        
        return consolidation_opportunities
    
    def get_performance_metrics(self, store_id: str = None) -> Dict:
        """
        Получение метрик производительности
        
        Args:
            store_id: ID магазина (если None, то по всей сети)
            
        Returns:
            Dict: метрики производительности
        """
        if store_id:
            # Метрики для конкретного магазина
            store_config = self.stores_config['stores'].get(store_id, {})
            return {
                'store_id': store_id,
                'store_name': store_config.get('name', 'Неизвестно'),
                'forecast_accuracy': np.random.uniform(0.75, 0.95),  # Заглушка
                'avg_daily_demand': np.random.randint(100, 300),
                'stock_turnover': np.random.uniform(2.5, 4.0),
                'waste_percentage': np.random.uniform(0.02, 0.08),
                'service_level': np.random.uniform(0.92, 0.98)
            }
        else:
            # Метрики по всей сети
            active_stores = [
                store_id for store_id, config in self.stores_config['stores'].items()
                if config.get('active', True)
            ]
            
            return {
                'total_stores': len(active_stores),
                'network_forecast_accuracy': np.random.uniform(0.80, 0.92),
                'total_daily_demand': np.random.randint(500, 1500),
                'avg_stock_turnover': np.random.uniform(3.0, 4.5),
                'network_waste_percentage': np.random.uniform(0.03, 0.06),
                'avg_service_level': np.random.uniform(0.94, 0.97)
            }
    
    def _get_season(self, date: datetime) -> str:
        """Определение сезона по дате"""
        month = date.month
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:
            return 'autumn'
    
    def _get_holiday_multiplier(self, date: datetime, store_config: Dict) -> float:
        """Получение праздничного коэффициента"""
        # Упрощенная логика - проверяем близость к основным праздникам
        holidays = {
            '03-08': store_config['holiday_multipliers'].get('WOMENS_DAY', 1.0),
            '02-14': store_config['holiday_multipliers'].get('VALENTINES', 1.0),
            '03-21': store_config['holiday_multipliers'].get('NAURYZ', 1.0)
        }
        
        date_str = date.strftime('%m-%d')
        return holidays.get(date_str, 1.0)
    
    def _get_weather_multiplier(self, store_config: Dict) -> float:
        """Получение погодного коэффициента"""
        # Упрощенная модель влияния погоды
        sensitivity = store_config.get('weather_sensitivity', 0.25)
        weather_impact = np.random.uniform(-sensitivity, sensitivity)
        return 1.0 + weather_impact
    
    def _save_config(self):
        """Сохранение конфигурации в файл"""
        try:
            with open('stores_config.json', 'w', encoding='utf-8') as f:
                json.dump(self.stores_config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения конфигурации: {e}")

# Пример использования
if __name__ == "__main__":
    # Создание менеджера
    manager = MultiStoreForecastManager()
    
    # Прогноз для одного магазина
    store_forecast = manager.get_store_forecast('almaty_1', 7)
    print("Прогноз для магазина Алматы ЦУМ:")
    print(store_forecast.head())
    
    # Прогноз для всей сети
    network_forecast = manager.get_network_forecast(7)
    print(f"\\nПрогноз для сети ({len(network_forecast)} записей)")
    
    # Возможности консолидации
    consolidation = manager.get_consolidation_opportunities(network_forecast)
    print(f"\\nВозможности консолидации: {len(consolidation)} дат")
    
    # Добавление нового магазина
    new_store_config = {
        "name": "Алматы Esentai Mall",
        "address": "пр. Аль-Фараби, 77/8",
        "type": "premium",
        "size_category": "large",
        "target_audience": "luxury_customers",
        "avg_daily_visitors": 180
    }
    
    success = manager.add_new_store('almaty_4', new_store_config)
    print(f"\\nДобавление нового магазина: {'успешно' if success else 'ошибка'}")
'''

# Сохраняем архитектуру мульти-магазинной системы
with open('multi_store_architecture.py', 'w', encoding='utf-8') as f:
    f.write(multi_store_architecture)

print("Файл multi_store_architecture.py создан")