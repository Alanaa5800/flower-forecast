#!/usr/bin/env python3
"""
Тест подключения к Google Sheets для системы прогнозирования цветов
"""

import json
import os

def test_connection_simple():
    """Простой тест подключения без зависимостей"""
    
    print("🔐 Тест настройки Google Sheets интеграции")
    print("=" * 50)
    
    # Проверка наличия файла ключей
    key_file = "service_account_key.json"
    
    if os.path.exists(key_file):
        print(f"✅ Файл ключей найден: {key_file}")
        
        try:
            with open(key_file, 'r') as f:
                key_data = json.load(f)
                
            required_fields = [
                'type', 'project_id', 'private_key_id', 'private_key',
                'client_email', 'client_id', 'auth_uri', 'token_uri'
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in key_data:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ В файле ключей отсутствуют поля: {missing_fields}")
                return False
            else:
                print("✅ Структура файла ключей корректна")
                print(f"📧 Email сервисного аккаунта: {key_data['client_email']}")
                print(f"🏗️ Проект: {key_data['project_id']}")
                
        except json.JSONDecodeError:
            print("❌ Файл ключей поврежден (невалидный JSON)")
            return False
        except Exception as e:
            print(f"❌ Ошибка чтения файла ключей: {e}")
            return False
            
    else:
        print(f"❌ Файл ключей не найден: {key_file}")
        print("\n📝 Для создания файла ключей:")
        print("1. Перейдите в Google Cloud Console")
        print("2. Создайте сервисный аккаунт")
        print("3. Скачайте JSON ключ")
        print("4. Переименуйте в 'service_account_key.json'")
        print("5. Поместите в папку проекта")
        return False
    
    # Проверка конфигурации
    print("\n⚙️ Проверка конфигурации системы...")
    
    # Проверяем наличие основных файлов проекта
    required_files = [
        'streamlit_forecast_app.py',
        'google_sheets_integration.py',
        'multi_store_architecture.py'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} не найден")
    
    print("\n📋 Инструкции для завершения настройки:")
    print("-" * 50)
    print("1. Создайте Google Таблицу с листами:")
    print("   - Продажи")
    print("   - Остатки") 
    print("   - Прогноз")
    print("   - Корректировки")
    print()
    print("2. Поделитесь таблицей с сервисным аккаунтом:")
    if os.path.exists(key_file):
        try:
            with open(key_file, 'r') as f:
                key_data = json.load(f)
            print(f"   Email: {key_data['client_email']}")
        except:
            print("   Email: [из файла service_account_key.json]")
    print("   Права: Редактор")
    print()
    print("3. Скопируйте URL таблицы")
    print("4. Обновите SPREADSHEET_URL в конфигурации")
    print()
    print("5. Запустите тест с реальным подключением:")
    print("   python3 test_real_connection.py")
    
    return True

def create_real_connection_test():
    """Создание файла для реального теста подключения"""
    
    test_code = '''#!/usr/bin/env python3
"""
Реальный тест подключения к Google Sheets
Требует установленных gspread и google-auth
"""

try:
    import gspread
    from google.oauth2.service_account import Credentials
    
    # НАСТРОЙТЕ ЭТИ ПАРАМЕТРЫ:
    CREDENTIALS_PATH = "service_account_key.json"
    SPREADSHEET_URL = "ВСТАВЬТЕ_СЮДА_URL_ВАШЕЙ_ТАБЛИЦЫ"
    
    def test_real_connection():
        print("🔗 Тест реального подключения к Google Sheets")
        print("=" * 50)
        
        if SPREADSHEET_URL == "ВСТАВЬТЕ_СЮДА_URL_ВАШЕЙ_ТАБЛИЦЫ":
            print("❌ Обновите SPREADSHEET_URL в файле")
            return False
        
        try:
            # Подключение
            scope = ['https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive']
            
            creds = Credentials.from_service_account_file(
                CREDENTIALS_PATH, scopes=scope
            )
            
            gc = gspread.authorize(creds)
            sheet = gc.open_by_url(SPREADSHEET_URL)
            
            print("✅ Подключение успешно!")
            print(f"📊 Название таблицы: {sheet.title}")
            
            # Проверка листов
            worksheets = sheet.worksheets()
            print(f"📄 Найдено листов: {len(worksheets)}")
            
            required_sheets = ['Продажи', 'Остатки', 'Прогноз', 'Корректировки']
            existing_sheets = [ws.title for ws in worksheets]
            
            for sheet_name in required_sheets:
                if sheet_name in existing_sheets:
                    print(f"  ✅ {sheet_name}")
                else:
                    print(f"  ❌ {sheet_name} - отсутствует")
            
            # Тест записи
            try:
                test_sheet = sheet.worksheet('Прогноз')
                test_sheet.update('A1', 'Тест подключения')
                print("✅ Тест записи успешен")
                
                # Тест чтения
                value = test_sheet.acell('A1').value
                print(f"✅ Тест чтения успешен: {value}")
                
            except Exception as e:
                print(f"⚠️ Ошибка при тесте записи/чтения: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            print("\\n🔧 Возможные решения:")
            print("1. Проверьте URL таблицы")
            print("2. Убедитесь, что сервисный аккаунт добавлен в таблицу")
            print("3. Проверьте права доступа (Редактор)")
            print("4. Убедитесь, что API включены в Google Cloud")
            return False
    
    if __name__ == "__main__":
        test_real_connection()
        
except ImportError:
    print("❌ Модули gspread или google-auth не установлены")
    print("Установите их командой:")
    print("pip install gspread google-auth")
'''
    
    with open('test_real_connection.py', 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print(f"✅ Создан файл: test_real_connection.py")

if __name__ == "__main__":
    success = test_connection_simple()
    
    if success:
        create_real_connection_test()
        print(f"\n🎯 Базовая проверка пройдена!")
        print("📁 Следующий шаг: настройте Google Таблицу и запустите test_real_connection.py")