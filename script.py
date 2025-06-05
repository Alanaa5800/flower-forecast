# Создаем пример таблицы с праздниками и их влиянием на спрос
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Данные о праздниках Казахстана в 2025 году и их влиянии на продажи цветов
holidays_data = {
    'holiday_code': ['WOMENS_DAY', 'VALENTINES', 'NAURYZ', 'VICTORY_DAY', 'MOTHERS_DAY', 
                     'DEFENDERS_DAY', 'CONSTITUTION_DAY', 'INDEPENDENCE_DAY', 'NEW_YEAR'],
    'holiday_name': ['Международный женский день', 'День святого Валентина', 'Наурыз мейрамы',
                     'День Победы', 'День матери', 'День защитника Отечества', 
                     'День Конституции', 'День независимости', 'Новый год'],
    'date_2025': ['2025-03-08', '2025-02-14', '2025-03-21', '2025-05-09', '2025-05-11',
                  '2025-05-07', '2025-08-30', '2025-12-16', '2025-01-01'],
    'demand_multiplier': [4.2, 1.8, 2.1, 1.3, 1.9, 1.2, 1.1, 1.2, 1.4],
    'peak_start_days_before': [5, 3, 2, 1, 2, 1, 0, 1, 2],
    'peak_duration_days': [3, 2, 3, 1, 2, 1, 1, 1, 3],
    'primary_flowers': ['Розы, тюльпаны, мимоза', 'Розы красные', 'Тюльпаны, нарциссы',
                       'Гвоздики', 'Розы, пионы', 'Гвоздики', 'Смешанные букеты',
                       'Национальные цветы', 'Хризантемы, ели'],
    'description': ['Пик года, рост до 420%', 'Второй по важности', 'Национальный праздник',
                   'Памятная дата', 'Семейный праздник', 'Мужской праздник',
                   'Государственный праздник', 'Национальный день', 'Зимние праздники']
}

holidays_df = pd.DataFrame(holidays_data)
print("Таблица праздников и их влияния на спрос:")
print(holidays_df.to_string(index=False))

# Сохраняем в CSV
holidays_df.to_csv('kazakhstan_holidays_2025.csv', index=False, encoding='utf-8')
print("\nФайл kazakhstan_holidays_2025.csv создан")