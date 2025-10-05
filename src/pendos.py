import tkinter as tk
from tkinter import ttk, messagebox
from account import AccountManager
from news import NewsManager
from portfolio import PortfolioManager

class PendosTradeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pendos Trade")

        self.account_manager = AccountManager()
        self.portfolio_table = None
        self.portfolio_manager = None
        self.news = NewsManager()

        self.stocks = {
            "Apple": "AAPL",
            "Microsoft": "MSFT",
            "Nvidia": "NVDA",
            "Amazon": "AMZN",
        }

        self.create_login_frame()
        self.create_main_tabs()
        self.switch_to_login()

    def create_login_frame(self):
        self.login_frame = tk.Frame(self.root)
        tk.Label(self.login_frame, text="Имя пользователя:").pack(pady=10)
        self.entry_username = tk.Entry(self.login_frame)
        self.entry_username.pack(pady=10)

        tk.Label(self.login_frame, text="Пароль:").pack(pady=10)
        self.entry_password = tk.Entry(self.login_frame, show="*")
        self.entry_password.pack(pady=10)

        tk.Button(
            self.login_frame, text="Регистрация", command=self.handle_register
        ).pack(pady=5)
        tk.Button(self.login_frame, text="Вход", command=self.handle_login).pack(
            pady=5
        )

    def create_main_tabs(self):
        self.tab_control = ttk.Notebook(self.root)
        self.create_portfolio_tab()
        self.create_market_tab()
        self.create_news_tab()
        self.create_balance_tab()
        self.create_operations_tab()
        self.tab_control.pack(expand=1, fill="both")

    def create_portfolio_tab(self):
        self.tab_portfolio = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_portfolio, text="Портфель")

        # Кнопка выхода
        tk.Button(
            self.tab_portfolio, text="Выйти", command=self.account_manager.logout_account, bg="red", fg="white"
        ).pack(anchor="ne", padx=5, pady=5)

        # Баланс и стоимость портфеля
        self.label_cash_balance = tk.Label(
            self.tab_portfolio, text=f"Баланс наличных: {self.account_manager.balance:.2f}$",
            font=("Arial", 14), fg="green"
        )
        self.label_cash_balance.pack(pady=5)

        self.label_portfolio_value = tk.Label(
            self.tab_portfolio, text="Стоимость портфеля: 0.00$", font=("Arial", 12), fg="blue"
        )
        self.label_portfolio_value.pack(pady=5)

        self.label_total_assets = tk.Label(
            self.tab_portfolio, text="Общая стоимость активов: 0.00$", font=("Arial", 12), fg="purple"
        )
        self.label_total_assets.pack(pady=5)

        # Создаем таблицу портфеля
        self.portfolio_table = ttk.Treeview(
            self.tab_portfolio, columns=("stock", "quantity", "value"), show="headings"
        )
        self.portfolio_table.heading("stock", text="Акции")
        self.portfolio_table.heading("quantity", text="Количество")
        self.portfolio_table.heading("value", text="Цена")
        self.portfolio_table.pack(pady=10)

        # Инициализация менеджера портфеля после создания таблицы
        self.portfolio_manager = PortfolioManager(self.portfolio_table)

        # Обновляем таблицу портфеля через менеджер
        self.portfolio_manager.update_portfolio_table()



    def create_market_tab(self):
        self.tab_market = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_market, text="Рынок")

        self.tab_market.grid_columnconfigure(0, weight=1)
        self.tab_market.grid_columnconfigure(1, weight=1)

        tk.Label(self.tab_market, text="Выберите компанию:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.selected_stock = tk.StringVar(value="Apple")
        tk.OptionMenu(self.tab_market, self.selected_stock, *self.stocks.keys()).grid(
            row=0, column=1, padx=10, pady=10, sticky="w"
        )

        tk.Label(self.tab_market, text="Количество акций:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.entry_quantity = tk.Spinbox(self.tab_market, from_=1, to=1000, increment=1, width=10)
        self.entry_quantity.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        tk.Button(
            self.tab_market, text="Купить", command=self.portfolio_manager.buy_stock, bg="green", fg="white"
        ).grid(row=2, column=0, padx=10, pady=10, sticky="e")
        tk.Button(
            self.tab_market, text="Продать", command=self.portfolio_manager.sell_stock, bg="red", fg="white"
        ).grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.label_current_price = tk.Label(
            self.tab_market, text="Текущая цена: ...", font=("Arial", 12), fg="blue"
        )
        self.label_current_price.grid(row=3, columnspan=2, pady=10)

    def create_news_tab(self):
        self.tab_news = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_news, text="Новости")

    def create_balance_tab(self):
        self.tab_balance = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_balance, text="Пополнение")

        tk.Label(self.tab_balance, text="Введите сумму для пополнения:").pack(pady=10)
        self.entry_add_balance = tk.Entry(self.tab_balance)
        self.entry_add_balance.pack(pady=10)

        tk.Button(
            self.tab_balance, text="Пополнить", command=self.portfolio_manager.add_balance, bg="orange", fg="black"
        ).pack(pady=10)

    def create_operations_tab(self):
        self.tab_operations = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_operations, text="Операции")

        self.label_log = tk.Label(
            self.tab_operations, text="Лог операций: пусто", font=("Arial", 10), fg="black"
        )
        self.label_log.pack(pady=10)

    def handle_register(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        success, message = self.account_manager.register_account(username, password)
        messagebox.showinfo("Регистрация", message)
        if success:
            self.entry_username.delete(0, tk.END)
            self.entry_password.delete(0, tk.END)

    def handle_login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        success, message = self.account_manager.login_account(username, password)
        messagebox.showinfo("Вход", message)
        if success:
            self.switch_to_main_app()

    def switch_to_login(self):
        self.tab_control.pack_forget()
        self.login_frame.pack(expand=1, fill="both")

    def switch_to_main_app(self):
        self.login_frame.pack_forget()
        self.tab_control.pack(expand=1, fill="both")
        self.portfolio_manager.balance = self.account_manager.balance
        self.portfolio_manager.portfolio = self.account_manager.portfolio
        self.portfolio_manager.update_portfolio_table()
        