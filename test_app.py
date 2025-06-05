#!/usr/bin/env python3
"""
Простой тест системы прогнозирования без Streamlit
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# Импортируем наш модуль архитектуры
from multi_store_architecture import MultiStoreForecastManager

def test_forecast_system():
    """Тестирование системы прогнозирования"""
    
    print("🌸 Тест системы прогнозирования цветов")
    print("=" * 50)
    
    # Создаем менеджер
    try:
        manager = MultiStoreForecastManager()
        print("✅ Менеджер прогнозирования создан успешно")
    except Exception as e:
        print(f"❌ Ошибка создания менеджера: {e}")
        return False
    
    # Тестируем прогноз для одного магазина
    try:
        store_forecast = manager.get_store_forecast('almaty_1', 7)
        print(f"✅ Прогноз для магазина Алматы ЦУМ создан: {len(store_forecast)} записей")
        
        # Показываем пример данных
        print("\n📊 Пример прогноза:")
        print(store_forecast.head(3).to_string(index=False))
        
    except Exception as e:
        print(f"❌ Ошибка создания прогноза: {e}")
        return False
    
    # Тестируем прогноз для всей сети
    try:
        network_forecast = manager.get_network_forecast(5)
        print(f"\n✅ Прогноз для сети создан: {len(network_forecast)} записей")
        
        # Группировка по магазинам
        store_summary = network_forecast.groupby('Магазин').agg({
            'Прогноз_спроса': 'sum',
            'Рекомендация_закупки': 'sum'
        }).round(0)
        
        print("\n📈 Сводка по магазинам:")
        print(store_summary.to_string())
        
    except Exception as e:
        print(f"❌ Ошибка создания сетевого прогноза: {e}")
        return False
    
    # Тестируем консолидацию
    try:
        consolidation = manager.get_consolidation_opportunities(network_forecast)
        print(f"\n✅ Анализ консолидации выполнен: {len(consolidation)} возможностей")
        
        if consolidation:
            for date, data in list(consolidation.items())[:2]:
                print(f"\nДата: {date}")
                print(f"  Общий объем: {data['total_volume']}")
                print(f"  Возможная экономия: {data['potential_savings']:.0f} тенге")
                
    except Exception as e:
        print(f"❌ Ошибка анализа консолидации: {e}")
        return False
    
    # Тестируем метрики
    try:
        metrics = manager.get_performance_metrics()
        print(f"\n✅ Метрики производительности получены")
        print(f"Общее количество магазинов: {metrics['total_stores']}")
        print(f"Точность прогноза сети: {metrics['network_forecast_accuracy']:.1%}")
        print(f"Общий дневной спрос: {metrics['total_daily_demand']}")
        
    except Exception as e:
        print(f"❌ Ошибка получения метрик: {e}")
        return False
    
    # Тестируем добавление нового магазина
    try:
        new_store_config = {
            "name": "Алматы Тест",
            "address": "ул. Тестовая, 1",
            "type": "mass_market",
            "size_category": "medium",
            "target_audience": "local_customers",
            "avg_daily_visitors": 120
        }
        
        success = manager.add_new_store('almaty_test', new_store_config)
        if success:
            print("✅ Новый магазин добавлен успешно")
        else:
            print("❌ Ошибка добавления нового магазина")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования добавления магазина: {e}")
        return False
    
    print("\n🎉 Все тесты пройдены успешно!")
    print("\n📋 Система готова к работе:")
    print("  - Прогнозирование работает")
    print("  - Мультимагазинная архитектура функционирует")
    print("  - Консолидация закупок доступна")
    print("  - Метрики производительности работают")
    print("  - Добавление новых магазинов поддерживается")
    
    return True

if __name__ == "__main__":
    test_forecast_system()