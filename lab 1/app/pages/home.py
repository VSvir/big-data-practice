from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st


def load_data():
    data_path = Path(__file__).parent.parent.parent / 'data' / 'accidents_info.csv'
    df = pd.read_csv(data_path)
    df['crash_date'] = pd.to_datetime(df['crash_date'])
    return df


def show():
    st.title("Анализ данных о ДТП")
    
    df = load_data()

    st.header("Основная статистика")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Всего записей", df.shape[0])
        st.metric("Уникальных типов аварий", df['crash_type'].nunique())
        
    with col2:
        st.metric("Период данных", 
                 f"{df['crash_date'].min().date()} - {df['crash_date'].max().date()}")
    
    st.header("Визуализация данных")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.countplot(x='crash_day_of_week', data=df, ax=ax)
    ax.set_title("Распределение аварий по дням недели")
    st.pyplot(fig)
    
    fig, ax = plt.subplots(figsize=(8, 8))
    df['crash_type'].value_counts().plot.pie(ax=ax, autopct='%1.1f%%')
    ax.set_ylabel('')
    st.pyplot(fig)
    
    heatmap_data = df.groupby(['crash_hour', 'crash_day_of_week']).size().unstack()
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(heatmap_data, cmap="YlGnBu", ax=ax)
    ax.set_title("Распределение аварий по времени и дням недели")
    st.pyplot(fig)
