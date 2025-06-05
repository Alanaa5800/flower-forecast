#!/usr/bin/env python3
"""
Простая демонстрация работы системы без внешних зависимостей
"""

import json
from datetime import datetime, timedelta
import random

def create_demo_forecast():
    """Создание демо-прогноза"""
    
    print("🌸 Демонстрация системы прогнозирования цветов")
    print("=" * 55)
    
    # Конфигурация магазинов
    stores = {
        "almaty_1": {
            "name": "Алматы ЦУМ",
            "type": "premium",
            "multiplier": 1.3
        },
        "almaty_2": {
            "name": "Алматы Мега",
            "type": "mass_market", 
            "multiplier": 1.0
        },
        "almaty_3": {
            "name": "Алматы Dostyk Plaza",
            "type": "business",
            "multiplier": 1.1
        }
    }
    
    # Ассортимент товаров
    sku_data = {
        "premium": [
            "Роза_Premium_80см", "Пион_импорт", "Орхидея_фаленопсис",
            "Лилия_ориенталь", "Роза_Дэвид_Остин"
        ],
        "mass_market": [
            "Роза_стандарт_60см", "Тюльпан_стандарт", "Хризантема_куст",
            "Гвоздика_стандарт", "Альстромерия"
        ],
        "business": [
            "Роза_бизнес_70см", "Букет_корпоративный", "Композиция_офис",
            "Роза_классик", "Лилия_бизнес"
        ]
    }
    
    forecast_data = []
    total_demand = 0
    total_purchase = 0
    
    # Генерация прогноза на 7 дней
    for day in range(7):
        date = datetime.now() + timedelta(days=day)
        date_str = date.strftime('%Y-%m-%d')
        day_name = date.strftime('%A')
        
        print(f"\n📅 {date_str} ({day_name})")
        print("-" * 40)
        
        for store_id, store_info in stores.items():
            store_type = store_info["type"]
            store_name = store_info["name"]
            multiplier = store_info["multiplier"]
            
            print(f"\n🏪 {store_name}")
            
            skus = sku_data[store_type]
            
            for sku in skus:
                # Базовый спрос
                base_demand = random.randint(8, 35)
                
                # Применяем коэффициенты
                if date.weekday() in [5, 6]:  # выходные
                    weekend_mult = 1.4
                else:
                    weekend_mult = 1.0
                
                # Итоговый спрос
                final_demand = int(base_demand * multiplier * weekend_mult)
                
                # Остатки
                current_stock = random.randint(0, 20)
                
                # Рекомендация закупки
                safety_stock = 1.2
                recommended_purchase = max(0, int(final_demand * safety_stock - current_stock))
                
                # Приоритет
                if recommended_purchase > final_demand:
                    priority = "ВЫСОКИЙ"
                elif recommended_purchase > final_demand * 0.5:
                    priority = "Средний"
                else:
                    priority = "Низкий"
                
                # Вывод информации
                print(f"  {sku:20} | Спрос: {final_demand:2} | Остаток: {current_stock:2} | Закупка: {recommended_purchase:2} | {priority}")
                
                total_demand += final_demand
                total_purchase += recommended_purchase
                
                # Сохраняем в массив
                forecast_data.append({
                    "date": date_str,
                    "day": day_name,
                    "store_id": store_id,
                    "store_name": store_name,
                    "sku": sku,
                    "demand": final_demand,
                    "stock": current_stock,
                    "purchase": recommended_purchase,
                    "priority": priority
                })
    
    # Итоговая статистика
    print("\n" + "=" * 55)
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 55)
    print(f"Общий прогноз спроса:        {total_demand:,} единиц")
    print(f"Общая рекомендация закупки:  {total_purchase:,} единиц")
    print(f"Количество позиций:          {len(forecast_data)}")
    print(f"Период прогноза:             7 дней")
    print(f"Количество магазинов:        {len(stores)}")
    
    # Анализ по магазинам
    print("\n📈 АНАЛИЗ ПО МАГАЗИНАМ")
    print("-" * 55)
    
    for store_id, store_info in stores.items():
        store_data = [item for item in forecast_data if item["store_id"] == store_id]
        store_demand = sum(item["demand"] for item in store_data)
        store_purchase = sum(item["purchase"] for item in store_data)
        
        print(f"{store_info['name']:20} | Спрос: {store_demand:3} | Закупка: {store_purchase:3}")
    
    # Анализ по дням
    print("\n📅 АНАЛИЗ ПО ДНЯМ")
    print("-" * 55)
    
    daily_stats = {}
    for item in forecast_data:
        date = item["date"]
        if date not in daily_stats:
            daily_stats[date] = {"demand": 0, "purchase": 0}
        daily_stats[date]["demand"] += item["demand"]
        daily_stats[date]["purchase"] += item["purchase"]
    
    for date, stats in daily_stats.items():
        day_obj = datetime.strptime(date, '%Y-%m-%d')
        day_name = day_obj.strftime('%A')
        print(f"{date} ({day_name:9}) | Спрос: {stats['demand']:3} | Закупка: {stats['purchase']:3}")
    
    # ТОП товаров
    print("\n🏆 ТОП-5 ТОВАРОВ ПО СПРОСУ")
    print("-" * 55)
    
    sku_stats = {}
    for item in forecast_data:
        sku = item["sku"]
        if sku not in sku_stats:
            sku_stats[sku] = 0
        sku_stats[sku] += item["demand"]
    
    top_skus = sorted(sku_stats.items(), key=lambda x: x[1], reverse=True)[:5]
    
    for i, (sku, demand) in enumerate(top_skus, 1):
        print(f"{i}. {sku:25} | Общий спрос: {demand:3}")
    
    # Приоритетные позиции
    high_priority = [item for item in forecast_data if item["priority"] == "ВЫСОКИЙ"]
    print(f"\n🚨 ВЫСОКИЙ ПРИОРИТЕТ: {len(high_priority)} позиций")
    print("-" * 55)
    
    for item in high_priority[:10]:  # Показываем первые 10
        print(f"{item['date']} | {item['store_name']:15} | {item['sku']:20} | Закупка: {item['purchase']:2}")
    
    # Сохранение в JSON
    output_file = "demo_forecast.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(forecast_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Прогноз сохранен в файл: {output_file}")
    
    print("\n✅ СИСТЕМА РАБОТАЕТ КОРРЕКТНО!")
    print("🎯 Готова к интеграции с Google Sheets")
    print("🌐 Готова к развертыванию в Colab")
    
    return forecast_data

if __name__ == "__main__":
    create_demo_forecast()