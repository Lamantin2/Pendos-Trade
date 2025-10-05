import tkinter as tk
from newsapi import NewsApiClient


class NewsManager:
    def __init__(self):
        self.api_key = "50fa805dc5684679bd7275c9647c94f4" 
        self.newsapi = NewsApiClient(api_key=self.api_key)
    
    # Обновление новостей для каждой компании
    def update_news(self):
        companies = ["Apple", "Microsoft", "Amazon", "Nvidia"]
        self.news_text.config(state="normal")
        self.news_text.delete(1.0, tk.END)

        # Запрос новостей для каждой компании
        for company in companies:
            # Вставка заголовка компании с выделением
            self.news_text.insert(tk.END, f"\n--- Новости {company} ---\n", "company_name")
            
            articles = self.fetch_news(company)
            if articles:
                for article in articles[:5]:  # Ограничим до 5 новостей на компанию
                    self.news_text.insert(tk.END, f"{article['title']}\n", "company_name")
                    self.news_text.insert(tk.END, f"{article['description']}\n")
                    self.news_text.insert(tk.END, f"Источник: {article['source']['name']}\n")
                    self.news_text.insert(tk.END, "-" * 50 + "\n")
            else:
                self.news_text.insert(tk.END, "Новостей не найдено.\n\n")

        # Отключение редактирования
        self.news_text.config(state="disabled")

    # Метод для запроса новостей
    def fetch_news(self, query):
        try:
            # Запрос новостей без указания даты для большей гибкости
            response = self.newsapi.get_everything(q=query, language="ru", sort_by="relevancy", page_size=5)
            return response["articles"]
        except Exception as e:
            print(f"Ошибка при получении новостей: {e}")
            return []
        