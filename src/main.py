import os
import json
import tkinter as tk
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from newsapi import NewsApiClient
import matplotlib.ticker as ticker
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PendosTradeApp:
    def __init__(self, root):
        # Инициализация основного окна приложения
        self.root = root
        self.root.title("Pendos Trade")
        self.root.geometry("1200x950")
        
        # Основные параметры пользователя
        self.balance = 0 # Баланс
        self.portfolio = {} # Портфель
        self.stocks = {'Apple': 'AAPL', 'Amazon': 'AMZN', 'Microsoft': 'MSFT', 'Nvidia': 'NVDA'} # Акции для торговли
        self.log_operations = [] # Лог операций
        self.current_user = None # Аккаунт

        self.news_api_key = "50fa805dc5684679bd7275c9647c94f4" 
        self.newsapi = NewsApiClient(api_key=self.news_api_key)

        # Создаем фрейм авторизации и основной интерфейс приложения
        self.create_login_frame()
        self.create_main_tabs()

        # Переход к окну авторизации
        self.switch_to_login()

    # Регистрации нового пользователя
    def register_account(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        if not username or not password:
            messagebox.showerror("Ошибка", "Введите имя пользователя и пароль")
            return
        accounts = self.load_accounts()
        if username in accounts:
            messagebox.showerror("Ошибка", "Имя пользователя уже занято")
        else:
            # Создаем новую учетную запись и сразу сохраняем её данные в .json файл
            accounts[username] = {
                "password": password,
                "balance": 0,
                "portfolio": {},
                "log_operations": []
            }
            with open("accounts.json", "w") as f:
                json.dump(accounts, f)
            
            # Устанавливаем текущего пользователя и сохраняем начальные данные
            self.current_user = username
            self.balance = 0
            self.portfolio = {}
            self.log_operations = []
            self.save_account_data()
            
            messagebox.showinfo("Успешно", f"Аккаунт '{username}' успешно создан.")
            self.switch_to_main_app()

    # Метод для входа в аккаунт
    def login_account(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        accounts = self.load_accounts()
        # Устанавливаем текущего пользователя и данные
        if username in accounts and accounts[username]["password"] == password:
            self.current_user = username
            self.balance = accounts[username]["balance"]
            self.portfolio = accounts[username]["portfolio"]
            self.log_operations = accounts[username]["log_operations"]
            messagebox.showinfo("Успешный вход", f"Добро пожаловать, {username}!")
            self.switch_to_main_app()
        else:
            messagebox.showerror("Ошибка", "Неверное имя пользователя или пароль")

    # Сохраняем данные аккаунта и сбрасываем текущие данные
    def logout_account(self):
        self.save_account_data()
        self.current_user = None
        self.balance = 0
        self.portfolio = {}
        self.log_operations = []
        
        messagebox.showinfo("Выход", "Вы успешно вышли из аккаунта")
        self.switch_to_login()

    # Загрузка данных учетных записей из JSON файла
    def load_accounts(self):
        if os.path.exists("accounts.json"):
            with open("accounts.json", "r") as f:
                return json.load(f)
        return {}
    
    # Сохранение текущих данных пользователя в файл
    def save_account_data(self):
        if self.current_user is None:
            return

        accounts = self.load_accounts()
        if self.current_user not in accounts:
            return 

        accounts[self.current_user] = {
            "password": accounts[self.current_user]["password"],
            "balance": self.balance,
            "portfolio": self.portfolio,
            "log_operations": self.log_operations
        }
        with open("accounts.json", "w") as f:
            json.dump(accounts, f)

    # Создаем фрейм для логина с полями ввода, кнопками регистрации и входа
    def create_login_frame(self):
        self.login_frame = tk.Frame(self.root)
        
        tk.Label(self.login_frame, text="Введите имя пользователя:").pack(pady=10)
        self.entry_username = tk.Entry(self.login_frame)
        self.entry_username.pack(pady=10)
        
        tk.Label(self.login_frame, text="Введите пароль:").pack(pady=10)
        self.entry_password = tk.Entry(self.login_frame, show="*")
        self.entry_password.pack(pady=10)
        
        tk.Button(self.login_frame, text="Зарегистрироваться", command=self.register_account, bg="blue", fg="white").pack(pady=5)
        tk.Button(self.login_frame, text="Войти", command=self.login_account, bg="green", fg="white").pack(pady=5)

    # Создаем основные вкладки интерфейса (Портфель, Рынок, Новости, Пополнение, Операции)
    def create_main_tabs(self):
        self.tab_control = ttk.Notebook(self.root)
        self.tab_portfolio = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_portfolio, text="Портфель")
        
        tk.Button(self.tab_portfolio, text="Выйти", command=self.logout_account, bg="red", fg="white").pack(anchor="ne", padx=5, pady=5)
        # Баланс пользователя, стоимость портфеля и активов
        self.label_cash_balance = tk.Label(self.tab_portfolio, text=f"Баланс наличных: {self.balance:.2f}$", font=("Arial", 14), fg="green")
        self.label_cash_balance.pack(pady=5)
        
        self.label_portfolio_value = tk.Label(self.tab_portfolio, text="Стоимость портфеля: 0.00$", font=("Arial", 12), fg="blue")
        self.label_portfolio_value.pack(pady=5)
        
        self.label_total_assets = tk.Label(self.tab_portfolio, text="Общая стоимость активов: 0.00$", font=("Arial", 12), fg="purple")
        self.label_total_assets.pack(pady=5)

        # Таблица для отображения портфеля пользователя
        self.portfolio_table = ttk.Treeview(self.tab_portfolio, columns=("stock", "quantity", "value"), show="headings")
        self.portfolio_table.heading("stock", text="Акции")
        self.portfolio_table.heading("quantity", text="Количество")
        self.portfolio_table.heading("value", text="Цена")
        self.portfolio_table.pack(pady=10)
        
        self.update_portfolio_table()

        # Создаем вкладку для работы с рынком акций
        self.tab_market = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_market, text="Рынок")

        self.tab_market.grid_columnconfigure(0, weight=1)
        self.tab_market.grid_columnconfigure(1, weight=1)
        self.tab_market.grid_rowconfigure(0, weight=1)
        self.tab_market.grid_rowconfigure(1, weight=1)
        self.tab_market.grid_rowconfigure(2, weight=1)
        self.tab_market.grid_rowconfigure(3, weight=1)
        self.tab_market.grid_rowconfigure(4, weight=1)
        self.tab_market.grid_rowconfigure(5, weight=1)

        # Выбор компании и количества акций для покупки/продажи
        tk.Label(self.tab_market, text="Выберите компанию:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.selected_stock = tk.StringVar(value='Apple')
        tk.OptionMenu(self.tab_market, self.selected_stock, *self.stocks.keys()).grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        tk.Label(self.tab_market, text="Количество акций:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.entry_quantity = tk.Spinbox(self.tab_market, from_=1, to=1000, increment=1, width=10)
        self.entry_quantity.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        tk.Button(self.tab_market, text="Купить", command=self.buy_stock, bg="green", fg="white").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        tk.Button(self.tab_market, text="Продать", command=self.sell_stock, bg="red", fg="white").grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        self.label_current_price = tk.Label(self.tab_market, text="Текущая цена: ...", font=("Arial", 12), fg="blue")
        self.label_current_price.grid(row=3, columnspan=2, pady=10)

        tk.Label(self.tab_market, text="Выберите период:").grid(row=4, column=0, padx=10, pady=10, sticky="e")
        self.selected_period = tk.StringVar(value="Год")
        tk.OptionMenu(self.tab_market, self.selected_period, "Год", "Месяц", "5 Дней").grid(row=4, column=1, padx=10, pady=10, sticky="w")
        
        # График цен на акции
        frame_chart = tk.Frame(self.tab_market)
        frame_chart.grid(row=5, columnspan=5, padx=10, pady=10)
        
        self.fig = plt.Figure(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_chart)
        self.canvas.get_tk_widget().pack()

        # Вкладка для отображения новостей о компаниях
        self.tab_news = tk.Frame(self.tab_control)
        self.tab_control.add(self.tab_news, text="Новости")

        # Вкладка для пополнения баланса
        self.tab_balance = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_balance, text="Пополнение")
        
        tk.Label(self.tab_balance, text="Введите сумму для пополнения:").pack(pady=10)
        self.entry_add_balance = tk.Entry(self.tab_balance)
        self.entry_add_balance.pack(pady=10)
        
        tk.Button(self.tab_balance, text="Пополнить", command=self.add_balance, bg="orange", fg="black").pack(pady=10)
        
        # Вкладка для отображения операций
        self.tab_operations = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_operations, text="Операции")
        
        self.label_log = tk.Label(self.tab_operations, text="Лог операций: пусто", font=("Arial", 10), fg="black")
        self.label_log.pack(pady=10)
        
        self.tab_control.pack(expand=1, fill="both")
        
        # Обновление баланса, построение графика, обновление новостей и расчет стоимости портфеля
        self.update_balance_and_portfolio()
        self.price_chart()
        self.create_news_tab()
        self.calculate_portfolio_value()

    # Скрываем фрейм для входа и показываем основное приложение    
    def switch_to_main_app(self):
        self.login_frame.pack_forget()
        self.tab_control.pack(expand=1, fill="both")
        self.update_balance_and_portfolio()
        self.calculate_portfolio_value()

    # Скрываем основное приложение и возвращаемся к экрану входа
    def switch_to_login(self):
        self.tab_control.pack_forget()
        self.login_frame.pack(expand=1, fill="both")

    # Создаем вкладку новостей
    def create_news_tab(self):
        # Заголовок для вкладки новостей
        tk.Label(self.tab_news, text="Новости о компаниях", font=("Arial", 14)).pack(pady=10)

        # Кнопка обновления новостей
        self.btn_refresh_news = tk.Button(self.tab_news, text="Обновить новости", command=self.update_news)
        self.btn_refresh_news.pack(pady=5)

        # Рамка для новостей и скроллбара
        news_frame = tk.Frame(self.tab_news)
        news_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Текстовое поле для отображения новостей
        self.news_text = tk.Text(news_frame, wrap="word", font=("Arial", 10), state="disabled")
        self.news_text.pack(side="left", expand=True, fill="both")

        # Добавляем скроллбар
        scrollbar = tk.Scrollbar(news_frame, command=self.news_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.news_text.config(yscrollcommand=scrollbar.set)

        self.news_text.tag_configure("company_name", font=("Arial", 12, "bold"), foreground="blue")

        # Загрузка новостей при старте
        self.update_news()

    # Получение данных о стоимости акций за указанный период
    def getData(self, stock_symbol, period):
        if period == "Год":
            period = "1y"
        elif period == "Месяц":
            period = "1mo"
        else:
            period = "5d"
        stock_data = yf.Ticker(stock_symbol)
        return stock_data.history(period=period)

    # Построение графика стоимости выбранной акции
    def price_chart(self):
        stock_symbol = self.stocks[self.selected_stock.get()]
        period = self.selected_period.get()
        stock_data = self.getData(stock_symbol, period)
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.plot(stock_data.index, stock_data['Close'], label=stock_symbol, color="blue")

        # Настройка отображения оси x в зависимости от выбранного периода
        if period == "Год":
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonthday=16))
            ax.xaxis.set_major_formatter(ticker.NullFormatter())
            ax.xaxis.set_minor_formatter(mdates.DateFormatter('%b'))
        elif period == "Месяц":
            ax.xaxis.set_major_locator(mdates.WeekdayLocator())
            ax.xaxis.set_minor_locator(mdates.DayLocator())
            ax.xaxis.set_major_formatter(ticker.NullFormatter())
            ax.xaxis.set_minor_formatter(mdates.DateFormatter('%d'))
        elif period == "5 Дней":  
            ax.xaxis.set_major_locator(mdates.DayLocator())
            ax.xaxis.set_minor_locator(mdates.HourLocator(interval=12)) 
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))  
            ax.xaxis.set_minor_formatter(mdates.DateFormatter('%H:%M'))  
        self.fig.autofmt_xdate()

        # Настройка заголовка и осей
        ax.set_title(f"График цены {stock_symbol}", color="darkred")
        ax.set_xlabel("Дата", color="green")
        ax.set_ylabel("Цена", color="green")
        ax.legend()
        ax.grid(True)

        # Отрисовка графика
        self.canvas.draw()

        # Отображение текущей цены
        self.label_current_price.config(text=f"Текущая цена {stock_symbol}: {stock_data['Close'][-1]:.2f}$", fg="blue")
        
        root.after(1000, self.price_chart) # Обновляем данные каждую секунду

    # Обновление таблицы с портфелем
    def update_portfolio_table(self):
        for row in self.portfolio_table.get_children():
            self.portfolio_table.delete(row)

        for stock, quantity in self.portfolio.items():
            stock_data = yf.Ticker(stock)
            current_price = stock_data.history(period="1d")['Close'].iloc[-1]
            value = current_price * quantity
            self.portfolio_table.insert("", "end", values=(stock, quantity, f"{value:.2f}"))

    # Покупка акций
    def buy_stock(self):
        stock = self.selected_stock.get()
        stock_symbol = self.stocks[stock]
        quantity = self.entry_quantity.get()
        
        try:
            quantity = int(quantity)
            data = yf.Ticker(stock_symbol).history(period="1d")
            price = data['Close'].iloc[-1]
            cost = price * quantity
            
            # Обновляем баланс и портфель
            if self.balance >= cost:
                self.balance -= cost
                if stock_symbol in self.portfolio:
                    self.portfolio[stock_symbol] += quantity
                else:
                    self.portfolio[stock_symbol] = quantity
                messagebox.showinfo("Успешная покупка", f"Вы купили {quantity} акций {stock_symbol} за {cost:.2f}$.")
                # Записываем операцию покупки в лог
                self.log_operations.append(f"Куплено {quantity} акций {stock} по цене {price:.2f}$")
                self.update_portfolio_table()
                self.update_balance_and_portfolio()
                self.calculate_portfolio_value()
            else:
                messagebox.showwarning("Ошибка", "Недостаточно средств")
        except ValueError:
            messagebox.showwarning("Ошибка", "Неправильное количество акций")

    # Продажа акций
    def sell_stock(self):
        stock = self.selected_stock.get()
        stock_symbol = self.stocks[stock]
        quantity = self.entry_quantity.get()
        
        try:
            quantity = int(quantity)
            if stock_symbol in self.portfolio and self.portfolio[stock_symbol] >= quantity:
                data = yf.Ticker(stock_symbol).history(period="1d")
                price = data['Close'].iloc[-1]
                revenue = price * quantity
                
                # Обновляем баланс и портфель
                self.balance += revenue
                self.portfolio[stock_symbol] -= quantity
                if self.portfolio[stock_symbol] == 0:
                    del self.portfolio[stock_symbol]

                # Записываем операцию продажи в лог
                self.log_operations.append(f"Продано {quantity} акций {stock} по цене {price:.2f}$")
                messagebox.showinfo("Успешная продажа", f"Вы продали {quantity} акций {stock_symbol} за {price * quantity:.2f}$.")
                self.update_portfolio_table()
                self.update_balance_and_portfolio()
                self.calculate_portfolio_value()
            else:
                messagebox.showwarning("Ошибка", "Недостаточно акций для продажи")
        except ValueError:
            messagebox.showwarning("Ошибка", "Неправильное количество акций")

    # Обновляем информацию о балансе и портфеле
    def update_balance_and_portfolio(self):
        self.label_cash_balance.config(text=f"Баланс наличных: {self.balance:.2f}$")
        portfolio_value = sum(
            yf.Ticker(stock).history(period="1d")['Close'].iloc[-1] * quantity
            for stock, quantity in self.portfolio.items()
        )
        self.label_portfolio_value.config(text=f"Стоимость портфеля: {portfolio_value:.2f}$")
        total_assets = self.balance + portfolio_value
        self.label_total_assets.config(text=f"Общая стоимость активов: {total_assets:.2f}$")
        self.label_log.config(text="\n".join(self.log_operations[::]))
        self.update_portfolio_table()

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

    # Пополнение баланса пользователя
    def add_balance(self):
        try:
            amount = float(self.entry_add_balance.get())
            if amount > 0:
                self.balance += amount
                messagebox.showinfo("Пополнение", f"Баланс пополнен на {amount:.2f}$.")
                self.log_operations.append(f"Пополнен баланс на {amount:.2f}$")
                self.update_balance_and_portfolio()
                self.entry_add_balance.delete(0, tk.END)
            else:
                messagebox.showerror("Ошибка", "Введите положительное значение")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное значение")

    # Рассчитываем общую стоимость портфеля
    def calculate_portfolio_value(self):
        total_value = sum(
            yf.Ticker(stock).history(period="1d")['Close'].iloc[-1] * quantity
            for stock, quantity in self.portfolio.items()
        )
        self.label_portfolio_value.config(text=f"Стоимость портфеля: {total_value:.2f}$")
        total_assets = self.balance + total_value
        self.label_total_assets.config(text=f"Общая стоимость активов: {total_assets:.2f}$")


if __name__ == "__main__":
    root = tk.Tk()
    app = PendosTradeApp(root)
    root.mainloop()
