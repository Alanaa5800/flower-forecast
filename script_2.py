# Создаем Streamlit интерфейс для системы прогнозирования
streamlit_app = '''
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json
from google_sheets_integration import FlowerForecastGSheetsIntegration

# Конфигурация страницы
st.set_page_config(
    page_title="🌸 Система прогнозирования продаж цветов",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Стили CSS
st.markdown("""
<style>
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.25rem;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 0.75rem;
        border-radius: 0.25rem;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

class FlowerForecastApp:
    def __init__(self):
        self.weather_api_key = st.secrets.get("WEATHER_API_KEY", "demo_key")
        self.init_session_state()
    
    def init_session_state(self):
        """Инициализация состояния сессии"""
        if 'forecast_data' not in st.session_state:
            st.session_state.forecast_data = pd.DataFrame()
        if 'corrections' not in st.session_state:
            st.session_state.corrections = {}
        if 'weather_data' not in st.session_state:
            st.session_state.weather_data = {}
    
    def get_weather_data(self, city="Almaty"):
        """Получение данных о погоде"""
        try:
            # Простая заглушка для демонстрации
            # В реальном проекте здесь будет API call
            weather_data = {
                'temperature': np.random.normal(15, 10),
                'humidity': np.random.randint(40, 80),
                'precipitation': np.random.choice([0, 0, 0, 2, 5, 10], p=[0.6, 0.1, 0.1, 0.1, 0.05, 0.05]),
                'wind_speed': np.random.normal(3, 2),
                'forecast': [
                    {'date': datetime.now() + timedelta(days=i), 
                     'temp': np.random.normal(15, 5), 
                     'rain': np.random.choice([0, 1, 2, 5], p=[0.7, 0.15, 0.1, 0.05])}
                    for i in range(7)
                ]
            }
            return weather_data
        except Exception as e:
            st.error(f"Ошибка получения данных о погоде: {e}")
            return {}
    
    def load_holidays(self):
        """Загрузка данных о праздниках"""
        try:
            holidays_df = pd.read_csv('kazakhstan_holidays_2025.csv')
            holidays_df['date_2025'] = pd.to_datetime(holidays_df['date_2025'])
            return holidays_df
        except Exception as e:
            st.error(f"Ошибка загрузки праздников: {e}")
            return pd.DataFrame()
    
    def generate_sample_forecast(self, days=7, stores=['Алматы_1', 'Алматы_2', 'Алматы_3']):
        """Генерация примера прогноза"""
        np.random.seed(42)
        
        skus = [
            'Роза_красная_60см', 'Роза_белая_50см', 'Тюльпан_красный', 
            'Тюльпан_белый', 'Хризантема_желтая', 'Лилия_белая',
            'Гвоздика_красная', 'Мимоза', 'Нарцисс_белый'
        ]
        
        data = []
        for day in range(days):
            date = datetime.now() + timedelta(days=day)
            for store in stores:
                for sku in skus:
                    base_demand = np.random.randint(5, 50)
                    
                    # Модификация спроса в зависимости от дня недели
                    if date.weekday() in [5, 6]:  # выходные
                        base_demand *= 1.5
                    
                    # Модификация в зависимости от SKU
                    if 'роза' in sku.lower():
                        base_demand *= 1.3
                    
                    current_stock = np.random.randint(0, 30)
                    recommended_purchase = max(0, int(base_demand * 1.2 - current_stock))
                    
                    priority = 'Низкий'
                    if recommended_purchase > base_demand:
                        priority = 'Высокий'
                    elif recommended_purchase > base_demand * 0.5:
                        priority = 'Средний'
                    
                    data.append({
                        'Дата': date.strftime('%Y-%m-%d'),
                        'День_недели': date.strftime('%A'),
                        'Магазин': store,
                        'SKU': sku,
                        'Прогноз_спроса': int(base_demand),
                        'Текущий_остаток': current_stock,
                        'Рекомендация_закупки': recommended_purchase,
                        'Приоритет': priority
                    })
        
        return pd.DataFrame(data)
    
    def main(self):
        """Основная функция приложения"""
        st.title("🌸 Система прогнозирования продаж цветов")
        st.markdown("**Алматы | Интеллектуальное планирование для цветочного бизнеса**")
        
        # Боковая панель
        with st.sidebar:
            st.header("⚙️ Настройки")
            
            # Выбор магазинов
            available_stores = ['Алматы_1', 'Алматы_2', 'Алматы_3', 'Алматы_4', 'Алматы_5']
            selected_stores = st.multiselect(
                "Выберите магазины:",
                available_stores,
                default=['Алматы_1', 'Алматы_2']
            )
            
            # Горизонт прогнозирования
            forecast_days = st.slider("Дней для прогноза:", 1, 30, 7)
            
            # Обновление данных
            if st.button("🔄 Обновить прогноз"):
                with st.spinner("Генерация прогноза..."):
                    st.session_state.forecast_data = self.generate_sample_forecast(
                        days=forecast_days,
                        stores=selected_stores
                    )
                st.success("Прогноз обновлен!")
        
        # Основные вкладки
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Прогноз", "✏️ Корректировки", "🌤️ Погода", "📈 Аналитика", "⚙️ Настройки"
        ])
        
        with tab1:
            self.show_forecast_tab(selected_stores, forecast_days)
        
        with tab2:
            self.show_corrections_tab()
        
        with tab3:
            self.show_weather_tab()
        
        with tab4:
            self.show_analytics_tab()
        
        with tab5:
            self.show_settings_tab()
    
    def show_forecast_tab(self, selected_stores, forecast_days):
        """Вкладка с прогнозом"""
        st.header("📊 Прогноз продаж")
        
        # Генерация данных если их нет
        if st.session_state.forecast_data.empty:
            st.session_state.forecast_data = self.generate_sample_forecast(
                days=forecast_days,
                stores=selected_stores
            )
        
        df = st.session_state.forecast_data
        
        if not df.empty:
            # Основные метрики
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_demand = df['Прогноз_спроса'].sum()
                st.metric("Общий прогноз спроса", f"{total_demand:,}")
            
            with col2:
                total_purchase = df['Рекомендация_закупки'].sum()
                st.metric("Рекомендуемая закупка", f"{total_purchase:,}")
            
            with col3:
                high_priority = len(df[df['Приоритет'] == 'Высокий'])
                st.metric("Позиций высокого приоритета", high_priority)
            
            with col4:
                avg_stock = df['Текущий_остаток'].mean()
                st.metric("Средний остаток", f"{avg_stock:.1f}")
            
            # Фильтры
            st.subheader("🔍 Фильтры")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                date_filter = st.selectbox("Дата:", ['Все'] + df['Дата'].unique().tolist())
            
            with col2:
                store_filter = st.selectbox("Магазин:", ['Все'] + df['Магазин'].unique().tolist())
            
            with col3:
                priority_filter = st.selectbox("Приоритет:", ['Все'] + df['Приоритет'].unique().tolist())
            
            # Применение фильтров
            filtered_df = df.copy()
            if date_filter != 'Все':
                filtered_df = filtered_df[filtered_df['Дата'] == date_filter]
            if store_filter != 'Все':
                filtered_df = filtered_df[filtered_df['Магазин'] == store_filter]
            if priority_filter != 'Все':
                filtered_df = filtered_df[filtered_df['Приоритет'] == priority_filter]
            
            # Таблица прогноза
            st.subheader("📋 Детальный прогноз")
            st.dataframe(
                filtered_df,
                use_container_width=True,
                hide_index=True
            )
            
            # График прогноза по дням
            st.subheader("📈 Динамика спроса")
            daily_forecast = df.groupby('Дата')['Прогноз_спроса'].sum().reset_index()
            
            fig = px.line(
                daily_forecast,
                x='Дата',
                y='Прогноз_спроса',
                title="Прогноз спроса по дням",
                markers=True
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Экспорт
            if st.button("📤 Экспорт в Excel"):
                # Здесь будет логика экспорта
                st.download_button(
                    label="Скачать прогноз",
                    data=filtered_df.to_csv(index=False),
                    file_name=f"forecast_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    
    def show_corrections_tab(self):
        """Вкладка корректировок"""
        st.header("✏️ Корректировка прогноза")
        
        st.markdown("""
        <div class="warning-box">
        ⚠️ Внимание: Корректировки влияют на обучение модели. 
        Обязательно укажите причину изменения.
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.forecast_data.empty:
            df = st.session_state.forecast_data
            
            # Выбор записи для корректировки
            st.subheader("Выберите позицию для корректировки:")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                selected_date = st.selectbox("Дата:", df['Дата'].unique())
            with col2:
                selected_store = st.selectbox("Магазин:", df['Магазин'].unique())
            with col3:
                filtered_skus = df[(df['Дата'] == selected_date) & 
                                 (df['Магазин'] == selected_store)]['SKU'].unique()
                selected_sku = st.selectbox("SKU:", filtered_skus)
            
            # Текущие значения
            current_row = df[(df['Дата'] == selected_date) & 
                           (df['Магазин'] == selected_store) & 
                           (df['SKU'] == selected_sku)]
            
            if not current_row.empty:
                current_forecast = current_row['Прогноз_спроса'].iloc[0]
                current_purchase = current_row['Рекомендация_закупки'].iloc[0]
                
                st.subheader("Текущие значения:")
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"Прогноз спроса: {current_forecast}")
                with col2:
                    st.info(f"Рекомендация закупки: {current_purchase}")
                
                # Форма корректировки
                st.subheader("Новые значения:")
                with st.form("correction_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_forecast = st.number_input(
                            "Новый прогноз спроса:",
                            min_value=0,
                            value=current_forecast
                        )
                    
                    with col2:
                        new_purchase = st.number_input(
                            "Новая рекомендация закупки:",
                            min_value=0,
                            value=current_purchase
                        )
                    
                    reason = st.text_area(
                        "Причина корректировки:",
                        placeholder="Например: запланирована акция, ожидается поставка..."
                    )
                    
                    submitted = st.form_submit_button("💾 Сохранить корректировку")
                    
                    if submitted and reason:
                        # Сохранение корректировки
                        correction_key = f"{selected_date}_{selected_store}_{selected_sku}"
                        st.session_state.corrections[correction_key] = {
                            'original_forecast': current_forecast,
                            'new_forecast': new_forecast,
                            'original_purchase': current_purchase,
                            'new_purchase': new_purchase,
                            'reason': reason,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        # Обновление данных прогноза
                        mask = ((df['Дата'] == selected_date) & 
                               (df['Магазин'] == selected_store) & 
                               (df['SKU'] == selected_sku))
                        st.session_state.forecast_data.loc[mask, 'Прогноз_спроса'] = new_forecast
                        st.session_state.forecast_data.loc[mask, 'Рекомендация_закупки'] = new_purchase
                        
                        st.success("✅ Корректировка сохранена!")
                        st.rerun()
        
        # История корректировок
        if st.session_state.corrections:
            st.subheader("📋 История корректировок")
            corrections_list = []
            for key, correction in st.session_state.corrections.items():
                date, store, sku = key.split('_', 2)
                corrections_list.append({
                    'Дата': date,
                    'Магазин': store,
                    'SKU': sku,
                    'Было': correction['original_forecast'],
                    'Стало': correction['new_forecast'],
                    'Причина': correction['reason']
                })
            
            corrections_df = pd.DataFrame(corrections_list)
            st.dataframe(corrections_df, use_container_width=True)
    
    def show_weather_tab(self):
        """Вкладка с погодой"""
        st.header("🌤️ Погодные условия")
        
        weather_data = self.get_weather_data()
        
        if weather_data:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Температура", f"{weather_data['temperature']:.1f}°C")
            with col2:
                st.metric("Влажность", f"{weather_data['humidity']}%")
            with col3:
                st.metric("Осадки", f"{weather_data['precipitation']} мм")
            with col4:
                st.metric("Ветер", f"{weather_data['wind_speed']:.1f} м/с")
            
            # Прогноз погоды на неделю
            st.subheader("📅 Прогноз погоды на неделю")
            
            if 'forecast' in weather_data:
                forecast_df = pd.DataFrame(weather_data['forecast'])
                forecast_df['date'] = pd.to_datetime(forecast_df['date'])
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=forecast_df['date'],
                    y=forecast_df['temp'],
                    mode='lines+markers',
                    name='Температура',
                    line=dict(color='red')
                ))
                
                fig.add_trace(go.Bar(
                    x=forecast_df['date'],
                    y=forecast_df['rain'],
                    name='Осадки',
                    yaxis='y2',
                    opacity=0.7
                ))
                
                fig.update_layout(
                    title='Прогноз температуры и осадков',
                    xaxis_title='Дата',
                    yaxis_title='Температура (°C)',
                    yaxis2=dict(
                        title='Осадки (мм)',
                        overlaying='y',
                        side='right'
                    ),
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    def show_analytics_tab(self):
        """Вкладка аналитики"""
        st.header("📈 Аналитика и метрики")
        
        if not st.session_state.forecast_data.empty:
            df = st.session_state.forecast_data
            
            # Анализ по магазинам
            st.subheader("🏪 Анализ по магазинам")
            store_analysis = df.groupby('Магазин').agg({
                'Прогноз_спроса': 'sum',
                'Рекомендация_закупки': 'sum',
                'Текущий_остаток': 'mean'
            }).round(1)
            
            fig = px.bar(
                store_analysis.reset_index(),
                x='Магазин',
                y='Прогноз_спроса',
                title='Прогноз спроса по магазинам'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # ТОП товаров
            st.subheader("🏆 ТОП товаров по спросу")
            top_skus = df.groupby('SKU')['Прогноз_спроса'].sum().nlargest(10)
            
            fig = px.bar(
                x=top_skus.values,
                y=top_skus.index,
                orientation='h',
                title='ТОП-10 товаров по прогнозируемому спросу'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def show_settings_tab(self):
        """Вкладка настроек"""
        st.header("⚙️ Настройки системы")
        
        with st.expander("🔗 Интеграция с Google Sheets"):
            spreadsheet_url = st.text_input(
                "URL Google Таблицы:",
                placeholder="https://docs.google.com/spreadsheets/d/..."
            )
            
            if st.button("🔄 Загрузить данные из Google Sheets"):
                if spreadsheet_url:
                    st.info("Подключение к Google Sheets...")
                    # Здесь будет логика подключения
                else:
                    st.error("Введите URL таблицы")
        
        with st.expander("📊 Параметры модели"):
            st.slider("Сезонность (дни):", 1, 30, 7)
            st.slider("Влияние праздников (%):", 0, 500, 200)
            st.slider("Влияние погоды (%):", 0, 100, 20)
        
        with st.expander("🚨 Уведомления"):
            st.checkbox("Email уведомления")
            st.checkbox("Уведомления о низких остатках")
            st.checkbox("Уведомления о высоком спросе")

# Запуск приложения
if __name__ == "__main__":
    app = FlowerForecastApp()
    app.main()
'''

# Сохраняем Streamlit приложение
with open('streamlit_forecast_app.py', 'w', encoding='utf-8') as f:
    f.write(streamlit_app)

print("Файл streamlit_forecast_app.py создан")