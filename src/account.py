import os
import json

class AccountManager:
    def __init__(self):
        """
        Инициализация менеджера аккаунтов.
        """
        self.accounts_file = "accounts.json"  # Имя файла для хранения данных аккаунтов
        self.current_user = None  # Имя текущего пользователя
        self.balance = 0  # Баланс текущего пользователя
        self.portfolio = {}  # Портфель акций текущего пользователя
        self.log_operations = []  # Лог операций текущего пользователя

    def load_accounts(self):
        """
        Загружает данные аккаунтов из файла.
        Если файл не существует, возвращает пустой словарь.
        """
        if os.path.exists(self.accounts_file):
            with open(self.accounts_file, "r") as f:
                return json.load(f)
        return {}

    def save_accounts(self, accounts):
        """
        Сохраняет данные аккаунтов в файл.
        """
        with open(self.accounts_file, "w") as f:
            json.dump(accounts, f)

    def register_account(self, username, password):
        """
        Регистрирация нового пользователя.
        """
        accounts = self.load_accounts()
        if username in accounts:
            return False, "Имя пользователя уже занято."  # Проверка, не занят ли логин
        # Добавление нового аккаунта в систему
        accounts[username] = {
            "password": password,
            "balance": 0,
            "portfolio": {},
            "log_operations": [],
        }
        self.save_accounts(accounts)
        return True, "Аккаунт успешно создан."

    def login_account(self, username, password):
        """
        Авторизация пользователя.
        """
        accounts = self.load_accounts()
        if username in accounts and accounts[username]["password"] == password:
            # Установка текущего пользователя и загрузка его данных
            self.current_user = username
            self.balance = accounts[username]["balance"]
            self.portfolio = accounts[username]["portfolio"]
            self.log_operations = accounts[username]["log_operations"]
            return True, f"Добро пожаловать, {username}!"
        return False, "Неверное имя пользователя или пароль."

    def logout_account(self):
        """
        Выход текущего пользователя. Данные сохраняются перед выходом.
        """
        if self.current_user:
            accounts = self.load_accounts()
            # Обновление данных текущего пользователя перед сохранением
            accounts[self.current_user].update(
                {
                    "balance": self.balance,
                    "portfolio": self.portfolio,
                    "log_operations": self.log_operations,
                }
            )
            self.save_accounts(accounts)
            # Сброс данных текущего пользователя
            self.current_user = None
            self.balance = 0
            self.portfolio = {}
            self.log_operations = []
