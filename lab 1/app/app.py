import streamlit as st


def main():
    st.set_page_config(
        page_title="Crash Analytics",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.sidebar.title("Навигация")
    page = st.sidebar.radio("Выберите страницу:", 
                           ("Анализ данных", "Метрики модели"))

    if page == "Анализ данных":
        from pages import home
        home.show()
    elif page == "Метрики модели":
        from pages import model
        model.show()

if __name__ == "__main__":
    main()
