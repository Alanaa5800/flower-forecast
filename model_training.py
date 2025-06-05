#!/usr/bin/env python3
"""
Модуль для переобучения модели прогнозирования
Поддерживает различные алгоритмы и метрики оценки
"""

import json
import os
from datetime import datetime, timedelta
import random
import math

class FlowerForecastModelTrainer:
    """
    Класс для обучения и оценки модели прогнозирования цветов
    """
    
    def __init__(self):
        self.models = {}
        self.training_history = []
        self.metrics = {}
        
    def prepare_training_data(self, sales_data, weather_data=None, holidays_data=None):
        """
        Подготовка данных для обучения модели
        
        Args:
            sales_data: исторические данные продаж
            weather_data: данные о погоде (опционально)
            holidays_data: данные о праздниках (опционально)
        
        Returns:
            dict: подготовленные данные для обучения
        """
        print("📊 Подготовка данных для обучения...")
        
        # Создаем синтетические данные для демонстрации
        training_data = self._generate_synthetic_training_data()
        
        # Добавляем внешние факторы
        if weather_data:
            training_data = self._add_weather_features(training_data, weather_data)
            
        if holidays_data:
            training_data = self._add_holiday_features(training_data, holidays_data)
        
        print(f"✅ Подготовлено {len(training_data)} записей для обучения")
        return training_data
    
    def _generate_synthetic_training_data(self, days=90):
        """Генерация синтетических данных для обучения"""
        
        stores = ['almaty_1', 'almaty_2', 'almaty_3']
        skus = [
            'Роза_красная_60см', 'Роза_белая_50см', 'Тюльпан_красный',
            'Хризантема_желтая', 'Лилия_белая', 'Гвоздика_красная'
        ]
        
        data = []
        base_date = datetime.now() - timedelta(days=days)
        
        for day in range(days):
            date = base_date + timedelta(days=day)
            
            # Сезонный фактор
            season_factor = 1 + 0.3 * math.sin(2 * math.pi * day / 365)
            
            # Фактор дня недели
            weekday_factor = 1.4 if date.weekday() in [5, 6] else 1.0
            
            # Праздничный фактор
            holiday_factor = 1.0
            if date.strftime('%m-%d') in ['03-08', '02-14', '03-21']:
                holiday_factor = 3.5
            
            for store in stores:
                for sku in skus:
                    # Базовый спрос с трендом
                    base_demand = 20 + random.randint(-5, 15)
                    trend = day * 0.01  # небольшой рост со временем
                    
                    # Случайный фактор
                    noise = random.uniform(0.8, 1.2)
                    
                    # Итоговый спрос
                    actual_demand = int(
                        base_demand * season_factor * weekday_factor * 
                        holiday_factor * noise + trend
                    )
                    
                    # Внешние факторы
                    temperature = random.uniform(-10, 30)
                    precipitation = random.choice([0, 0, 0, 2, 5])
                    
                    data.append({
                        'date': date.isoformat(),
                        'store': store,
                        'sku': sku,
                        'actual_demand': max(0, actual_demand),
                        'day_of_week': date.weekday(),
                        'month': date.month,
                        'season_factor': season_factor,
                        'weekday_factor': weekday_factor,
                        'holiday_factor': holiday_factor,
                        'temperature': temperature,
                        'precipitation': precipitation,
                        'trend': trend
                    })
        
        return data
    
    def train_model(self, training_data, algorithm='linear_regression'):
        """
        Обучение модели прогнозирования
        
        Args:
            training_data: подготовленные данные
            algorithm: алгоритм обучения
        
        Returns:
            dict: результаты обучения
        """
        print(f"🤖 Обучение модели с алгоритмом: {algorithm}")
        
        # Разделяем данные на обучающую и тестовую выборки
        train_size = int(0.8 * len(training_data))
        train_data = training_data[:train_size]
        test_data = training_data[train_size:]
        
        # Обучаем модель (упрощенная симуляция)
        model_params = self._train_algorithm(train_data, algorithm)
        
        # Оцениваем качество модели
        metrics = self._evaluate_model(model_params, test_data, algorithm)
        
        # Сохраняем модель
        model_info = {
            'algorithm': algorithm,
            'params': model_params,
            'metrics': metrics,
            'training_date': datetime.now().isoformat(),
            'training_samples': len(train_data),
            'test_samples': len(test_data)
        }
        
        self.models[algorithm] = model_info
        self.training_history.append(model_info)
        
        print(f"✅ Модель обучена. Точность: {metrics['accuracy']:.2%}")
        return model_info
    
    def _train_algorithm(self, train_data, algorithm):
        """Обучение конкретного алгоритма"""
        
        if algorithm == 'linear_regression':
            return self._train_linear_regression(train_data)
        elif algorithm == 'decision_tree':
            return self._train_decision_tree(train_data)
        elif algorithm == 'random_forest':
            return self._train_random_forest(train_data)
        elif algorithm == 'neural_network':
            return self._train_neural_network(train_data)
        else:
            raise ValueError(f"Неподдерживаемый алгоритм: {algorithm}")
    
    def _train_linear_regression(self, train_data):
        """Симуляция обучения линейной регрессии"""
        print("  📈 Обучение линейной регрессии...")
        
        # Упрощенные коэффициенты
        coefficients = {
            'intercept': random.uniform(10, 20),
            'season_factor': random.uniform(15, 25),
            'weekday_factor': random.uniform(8, 12),
            'holiday_factor': random.uniform(5, 10),
            'temperature': random.uniform(-0.5, 0.5),
            'precipitation': random.uniform(-2, -0.5),
            'trend': random.uniform(0.5, 1.5)
        }
        
        return coefficients
    
    def _train_decision_tree(self, train_data):
        """Симуляция обучения дерева решений"""
        print("  🌳 Обучение дерева решений...")
        
        return {
            'max_depth': random.randint(5, 15),
            'min_samples_split': random.randint(2, 10),
            'feature_importance': {
                'season_factor': random.uniform(0.2, 0.4),
                'holiday_factor': random.uniform(0.15, 0.35),
                'weekday_factor': random.uniform(0.1, 0.25),
                'temperature': random.uniform(0.05, 0.15),
                'precipitation': random.uniform(0.05, 0.15)
            }
        }
    
    def _train_random_forest(self, train_data):
        """Симуляция обучения случайного леса"""
        print("  🌲 Обучение случайного леса...")
        
        return {
            'n_estimators': random.randint(50, 200),
            'max_depth': random.randint(5, 20),
            'feature_importance': {
                'season_factor': random.uniform(0.25, 0.35),
                'holiday_factor': random.uniform(0.2, 0.3),
                'weekday_factor': random.uniform(0.15, 0.25),
                'temperature': random.uniform(0.05, 0.15),
                'precipitation': random.uniform(0.05, 0.15)
            },
            'oob_score': random.uniform(0.75, 0.9)
        }
    
    def _train_neural_network(self, train_data):
        """Симуляция обучения нейронной сети"""
        print("  🧠 Обучение нейронной сети...")
        
        return {
            'hidden_layers': [random.randint(32, 128), random.randint(16, 64)],
            'activation': 'relu',
            'learning_rate': random.uniform(0.001, 0.01),
            'epochs': random.randint(50, 200),
            'batch_size': random.choice([16, 32, 64]),
            'final_loss': random.uniform(0.1, 0.5)
        }
    
    def _evaluate_model(self, model_params, test_data, algorithm):
        """Оценка качества модели"""
        print("  📏 Оценка качества модели...")
        
        # Симулируем предсказания и вычисляем метрики
        predictions = []
        actuals = []
        
        for record in test_data[:100]:  # Ограничиваем для демонстрации
            # Симулируем предсказание
            predicted = self._predict_single(record, model_params, algorithm)
            actual = record['actual_demand']
            
            predictions.append(predicted)
            actuals.append(actual)
        
        # Вычисляем метрики
        metrics = self._calculate_metrics(predictions, actuals)
        return metrics
    
    def _predict_single(self, record, model_params, algorithm):
        """Предсказание для одной записи"""
        if algorithm == 'linear_regression':
            prediction = (
                model_params['intercept'] +
                model_params['season_factor'] * record['season_factor'] +
                model_params['weekday_factor'] * record['weekday_factor'] +
                model_params['holiday_factor'] * record['holiday_factor'] +
                model_params['temperature'] * record['temperature'] +
                model_params['precipitation'] * record['precipitation'] +
                model_params['trend'] * record['trend']
            )
        else:
            # Для других алгоритмов используем упрощенное предсказание
            base = record['actual_demand']
            noise = random.uniform(0.8, 1.2)
            prediction = base * noise
        
        return max(0, prediction)
    
    def _calculate_metrics(self, predictions, actuals):
        """Вычисление метрик качества"""
        n = len(predictions)
        
        # MAE (Mean Absolute Error)
        mae = sum(abs(p - a) for p, a in zip(predictions, actuals)) / n
        
        # MAPE (Mean Absolute Percentage Error)
        mape = sum(abs((p - a) / max(a, 1)) for p, a in zip(predictions, actuals)) / n
        
        # RMSE (Root Mean Square Error)
        rmse = (sum((p - a) ** 2 for p, a in zip(predictions, actuals)) / n) ** 0.5
        
        # Accuracy (обратная MAPE)
        accuracy = max(0, 1 - mape)
        
        return {
            'mae': mae,
            'mape': mape,
            'rmse': rmse,
            'accuracy': accuracy,
            'sample_size': n
        }
    
    def compare_models(self):
        """Сравнение обученных моделей"""
        if not self.models:
            print("❌ Нет обученных моделей для сравнения")
            return None
        
        print("📊 Сравнение моделей:")
        print("-" * 60)
        print(f"{'Алгоритм':20} {'Точность':>10} {'MAE':>8} {'RMSE':>8}")
        print("-" * 60)
        
        best_model = None
        best_accuracy = 0
        
        for algorithm, model in self.models.items():
            metrics = model['metrics']
            accuracy = metrics['accuracy']
            mae = metrics['mae']
            rmse = metrics['rmse']
            
            print(f"{algorithm:20} {accuracy:>9.2%} {mae:>7.1f} {rmse:>7.1f}")
            
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_model = algorithm
        
        print("-" * 60)
        print(f"🏆 Лучшая модель: {best_model} (точность: {best_accuracy:.2%})")
        
        return best_model
    
    def retrain_model(self, algorithm=None):
        """Переобучение модели с новыми данными"""
        if algorithm is None:
            algorithm = self.compare_models()
            if algorithm is None:
                algorithm = 'linear_regression'  # По умолчанию
        
        print(f"🔄 Переобучение модели: {algorithm}")
        
        # Генерируем новые данные (в реальности загружались бы из БД)
        new_training_data = self.prepare_training_data(None)
        
        # Переобучаем модель
        result = self.train_model(new_training_data, algorithm)
        
        # Сохраняем результат
        self.save_model_config()
        
        return result
    
    def save_model_config(self):
        """Сохранение конфигурации моделей"""
        config = {
            'models': self.models,
            'training_history': self.training_history,
            'last_update': datetime.now().isoformat()
        }
        
        with open('model_config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print("💾 Конфигурация модели сохранена")
    
    def load_model_config(self):
        """Загрузка конфигурации моделей"""
        try:
            with open('model_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.models = config.get('models', {})
            self.training_history = config.get('training_history', [])
            
            print("📁 Конфигурация модели загружена")
            return True
            
        except FileNotFoundError:
            print("📝 Файл конфигурации не найден, создается новый")
            return False
    
    def get_model_info(self):
        """Получение информации о текущих моделях"""
        if not self.models:
            return "Нет обученных моделей"
        
        info = []
        for algorithm, model in self.models.items():
            metrics = model['metrics']
            info.append({
                'algorithm': algorithm,
                'accuracy': metrics['accuracy'],
                'mae': metrics['mae'],
                'training_date': model['training_date'],
                'samples': model['training_samples']
            })
        
        return info

# Демонстрация работы
def demo_model_training():
    """Демонстрация процесса обучения модели"""
    print("🤖 Демонстрация системы обучения модели")
    print("=" * 50)
    
    trainer = FlowerForecastModelTrainer()
    
    # Подготовка данных
    training_data = trainer.prepare_training_data(None)
    
    # Обучение разных моделей
    algorithms = ['linear_regression', 'decision_tree', 'random_forest']
    
    for algorithm in algorithms:
        print(f"\n📚 Обучение модели: {algorithm}")
        trainer.train_model(training_data, algorithm)
    
    # Сравнение моделей
    print("\n" + "=" * 50)
    best_model = trainer.compare_models()
    
    # Переобучение лучшей модели
    print(f"\n🔄 Переобучение лучшей модели: {best_model}")
    trainer.retrain_model(best_model)
    
    # Сохранение конфигурации
    trainer.save_model_config()
    
    print("\n✅ Демонстрация завершена!")
    return trainer

if __name__ == "__main__":
    demo_model_training()