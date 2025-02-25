import streamlit as st
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


def load_metrics():
    metrics_path = Path(__file__).parent.parent.parent / 'data' / 'metrics.json'
    try:
        with open(metrics_path) as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    
def plot_confusion_matrix(cm):
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax)
    ax.set_xlabel('Predicted')
    ax.set_ylabel('True')
    ax.set_title('Confusion Matrix')
    return fig

def show():
    st.title("Метрики модели")
    
    metrics = load_metrics()
    
    if not metrics:
        st.warning("Метрики еще не доступны")
        return
    
    st.header("Основные показатели")
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Образцов", metrics['samples'])
    col2.metric("Accuracy", f"{metrics['accuracy']:.2%}")
    col3.metric("Precision", f"{metrics['precision']:.2%}")
    col4.metric("Recall", f"{metrics['recall']:.2%}")
    
    st.header("Матрица ошибок")
    cm = np.array(metrics['confusion_matrix'])
    st.pyplot(plot_confusion_matrix(cm))
    
    st.header("Динамика метрик")
    st.info("Реализация требует сохранения истории метрик")
