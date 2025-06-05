# Создаем пример интеграции с Inspiro
inspiro_integration = '''
import requests
import pandas as pd
import json
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
            export_instructions = f'''
            ИНСТРУКЦИЯ ПО ЭКСПОРТУ ДАННЫХ ИЗ INSPIRO:
            
            1. Войдите в систему florist.inspiro.pro
            2. Перейдите в раздел "Отчеты" → "Продажи"
            3. Установите период: с {start_date} по {end_date}
            4. Выберите магазины: {stores if stores else "Все магазины"}
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
            '''
            
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
    
    def export_inventory_data(self, stores: List[str] = None) -> pd.DataFrame:
        """
        Экспорт данных об остатках
        
        Args:
            stores: список магазинов
            
        Returns:
            pd.DataFrame: данные об остатках
        """
        if self.use_file_export:
            return self._export_inventory_file_method(stores)
        else:
            return self._export_inventory_api_method(stores)
    
    def _export_inventory_file_method(self, stores: List[str] = None) -> pd.DataFrame:
        """Экспорт остатков через файл"""
        try:
            export_instructions = f'''
            ИНСТРУКЦИЯ ПО ЭКСПОРТУ ОСТАТКОВ ИЗ INSPIRO:
            
            1. Войдите в систему florist.inspiro.pro
            2. Перейдите в раздел "Склад" → "Остатки"
            3. Выберите магазины: {stores if stores else "Все магазины"}
            4. Показать только товары с остатком > 0
            5. Формат экспорта: CSV
            6. Поля для экспорта:
               - Код магазина
               - Артикул товара (SKU)
               - Наименование товара
               - Остаток (штук)
               - Дата поступления
               - Срок годности
               - Поставщик
               - Цена закупки
            7. Сохраните как "inspiro_inventory_export.csv"
            '''
            
            print(export_instructions)
            
            try:
                df = pd.read_csv('inspiro_inventory_export.csv', encoding='utf-8')
                logger.info(f"Загружено {len(df)} позиций остатков")
                
                # Стандартизация колонок
                column_mapping = {
                    'Код магазина': 'Магазин',
                    'Артикул товара': 'SKU',
                    'Наименование товара': 'Название',
                    'Остаток (штук)': 'Остаток',
                    'Дата поступления': 'Дата_поступления',
                    'Срок годности': 'Срок_годности',
                    'Поставщик': 'Поставщик'
                }
                
                df = df.rename(columns=column_mapping)
                
                # Обработка данных
                df['Остаток'] = pd.to_numeric(df['Остаток'], errors='coerce')
                df['Дата_поступления'] = pd.to_datetime(df['Дата_поступления'], errors='coerce')
                df['Срок_годности'] = pd.to_datetime(df['Срок_годности'], errors='coerce')
                
                if stores:
                    df = df[df['Магазин'].isin(stores)]
                
                return df
                
            except FileNotFoundError:
                logger.warning("Файл inspiro_inventory_export.csv не найден")
                return self._generate_demo_inventory_data(stores)
                
        except Exception as e:
            logger.error(f"Ошибка экспорта остатков: {e}")
            return pd.DataFrame()
    
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
    
    def _generate_demo_inventory_data(self, stores: List[str] = None) -> pd.DataFrame:
        """Генерация демо-данных об остатках"""
        logger.info("Генерируем демо-данные об остатках")
        
        if not stores:
            stores = ['almaty_1', 'almaty_2', 'almaty_3']
        
        skus = [
            'Роза_красная_60см', 'Роза_белая_50см', 'Тюльпан_красный',
            'Тюльпан_белый', 'Хризантема_желтая', 'Лилия_белая',
            'Гвоздика_красная', 'Мимоза', 'Нарцисс_белый'
        ]
        
        demo_data = []
        
        for store in stores:
            for sku in skus:
                # Не все товары есть в остатках
                if np.random.random() > 0.2:
                    stock = np.random.randint(0, 50)
                    arrival_date = datetime.now() - timedelta(days=np.random.randint(1, 10))
                    expiry_date = arrival_date + timedelta(days=np.random.randint(3, 14))
                    
                    demo_data.append({
                        'Магазин': store,
                        'SKU': sku,
                        'Остаток': stock,
                        'Дата_поступления': arrival_date.strftime('%Y-%m-%d'),
                        'Срок_годности': expiry_date.strftime('%Y-%m-%d'),
                        'Поставщик': f'Поставщик_{np.random.randint(1, 5)}'
                    })
        
        return pd.DataFrame(demo_data)
    
    def export_products_catalog(self) -> pd.DataFrame:
        """Экспорт каталога товаров"""
        try:
            catalog_instructions = '''
            ИНСТРУКЦИЯ ПО ЭКСПОРТУ КАТАЛОГА ИЗ INSPIRO:
            
            1. Войдите в систему florist.inspiro.pro
            2. Перейдите в раздел "Товары" → "Каталог"
            3. Формат экспорта: CSV
            4. Поля для экспорта:
               - Артикул (SKU)
               - Наименование
               - Категория
               - Единица измерения
               - Срок годности (дни)
               - Минимальный остаток
               - Цена розничная
               - Активен (Да/Нет)
            5. Сохраните как "inspiro_catalog_export.csv"
            '''
            
            print(catalog_instructions)
            
            try:
                df = pd.read_csv('inspiro_catalog_export.csv', encoding='utf-8')
                logger.info(f"Загружен каталог: {len(df)} товаров")
                return df
            except FileNotFoundError:
                logger.warning("Файл каталога не найден, генерируем демо-каталог")
                return self._generate_demo_catalog()
                
        except Exception as e:
            logger.error(f"Ошибка экспорта каталога: {e}")
            return pd.DataFrame()
    
    def _generate_demo_catalog(self) -> pd.DataFrame:
        """Генерация демо-каталога"""
        catalog_data = [
            {'SKU': 'Роза_красная_60см', 'Название': 'Роза красная 60см', 'Категория': 'Розы', 'Срок_годности_дни': 7, 'Цена': 450},
            {'SKU': 'Роза_белая_50см', 'Название': 'Роза белая 50см', 'Категория': 'Розы', 'Срок_годности_дни': 7, 'Цена': 420},
            {'SKU': 'Тюльпан_красный', 'Название': 'Тюльпан красный', 'Категория': 'Тюльпаны', 'Срок_годности_дни': 5, 'Цена': 180},
            {'SKU': 'Тюльпан_белый', 'Название': 'Тюльпан белый', 'Категория': 'Тюльпаны', 'Срок_годности_дни': 5, 'Цена': 180},
            {'SKU': 'Хризантема_желтая', 'Название': 'Хризантема желтая', 'Категория': 'Хризантемы', 'Срок_годности_дни': 14, 'Цена': 220},
            {'SKU': 'Лилия_белая', 'Название': 'Лилия белая', 'Категория': 'Лилии', 'Срок_годности_дни': 10, 'Цена': 380},
            {'SKU': 'Гвоздика_красная', 'Название': 'Гвоздика красная', 'Категория': 'Гвоздики', 'Срок_годности_дни': 12, 'Цена': 150},
            {'SKU': 'Мимоза', 'Название': 'Мимоза', 'Категория': 'Сезонные', 'Срок_годности_дни': 3, 'Цена': 300},
            {'SKU': 'Нарцисс_белый', 'Название': 'Нарцисс белый', 'Категория': 'Луковичные', 'Срок_годности_дни': 6, 'Цена': 200}
        ]
        
        return pd.DataFrame(catalog_data)
    
    def validate_connection(self) -> Dict:
        """Проверка подключения к Inspiro"""
        validation_result = {
            'status': 'unknown',
            'method': 'file_export' if self.use_file_export else 'api',
            'timestamp': datetime.now().isoformat(),
            'details': {}
        }
        
        if self.use_file_export:
            # Проверяем наличие экспортных файлов
            files_to_check = [
                'inspiro_sales_export.csv',
                'inspiro_inventory_export.csv',
                'inspiro_catalog_export.csv'
            ]
            
            existing_files = []
            for file_name in files_to_check:
                try:
                    pd.read_csv(file_name, nrows=1)
                    existing_files.append(file_name)
                except FileNotFoundError:
                    pass
            
            validation_result['details']['existing_files'] = existing_files
            validation_result['status'] = 'ready' if existing_files else 'files_missing'
            
        else:
            # Проверяем API подключение
            try:
                response = self.session.get(f"{self.base_url}/health", timeout=10)
                if response.status_code == 200:
                    validation_result['status'] = 'connected'
                else:
                    validation_result['status'] = 'api_error'
                    validation_result['details']['error'] = f"HTTP {response.status_code}"
            except requests.exceptions.RequestException as e:
                validation_result['status'] = 'connection_error'
                validation_result['details']['error'] = str(e)
        
        return validation_result

# Пример использования
if __name__ == "__main__":
    # Создание интеграции
    inspiro = InspiroAPIIntegration(use_file_export=True)
    
    # Проверка подключения
    connection_status = inspiro.validate_connection()
    print("Статус подключения:", connection_status)
    
    # Экспорт данных о продажах
    sales_data = inspiro.export_sales_data('2025-05-01', '2025-06-06')
    print(f"Загружено продаж: {len(sales_data)} записей")
    
    # Экспорт остатков
    inventory_data = inspiro.export_inventory_data()
    print(f"Загружено остатков: {len(inventory_data)} позиций")
    
    # Экспорт каталога
    catalog_data = inspiro.export_products_catalog()
    print(f"Загружен каталог: {len(catalog_data)} товаров")
'''

# Сохраняем интеграцию с Inspiro
with open('inspiro_integration.py', 'w', encoding='utf-8') as f:
    f.write(inspiro_integration)

print("Файл inspiro_integration.py создан")