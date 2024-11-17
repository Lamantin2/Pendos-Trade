import tkinter as tk
import yfinance as yf
from tkinter import messagebox


class PortfolioManager:
    def __init__(self, portfolio_table):
        """
        Инициализация менеджера портфеля.
        """
        self.balance = 0  # Баланс пользователя
        self.portfolio = {}  # Словарь с акциями и их количеством
        self.log_operations = []  # Лог операций пользователя
        self.portfolio_table = portfolio_table  # Таблица для отображения портфеля
    
    def update_portfolio_table(self):
        """
        Обновляет таблицу с портфелем, включая текущую стоимость акций.
        """
        # Удаляем все строки из таблицы перед обновлением
        for row in self.portfolio_table.get_children():
            self.portfolio_table.delete(row)

        # Добавляем обновленные данные
        for stock, quantity in self.portfolio.items():
            stock_data = yf.Ticker(stock)  # Получаем данные о компании
            current_price = stock_data.history(period="1d")['Close'].iloc[-1]  # Текущая цена акции
            value = current_price * quantity  # Общая стоимость всех акций этого типа
            self.portfolio_table.insert("", "end", values=(stock, quantity, f"{value:.2f}"))

    def buy_stock(self):
        """
        Покупает акции выбранной компании.
        Проверяет, достаточно ли средств на балансе, и обновляет данные портфеля.
        """
        stock = self.selected_stock.get()  # Выбранная акция
        stock_symbol = self.stocks[stock]  # Символ акции (тикер)
        quantity = self.entry_quantity.get()  # Количество акций, которые хочет купить пользователь
        
        try:
            quantity = int(quantity)  # Убедимся, что введено целое число
            # Получаем текущую цену акции
            data = yf.Ticker(stock_symbol).history(period="1d")
            price = data['Close'].iloc[-1]  # Закрывающая цена акции
            cost = price * quantity  # Общая стоимость покупки
            
            if self.balance >= cost:
                # Обновляем баланс и портфель
                self.balance -= cost
                if stock_symbol in self.portfolio:
                    self.portfolio[stock_symbol] += quantity
                else:
                    self.portfolio[stock_symbol] = quantity

                messagebox.showinfo("Успешная покупка", f"Вы купили {quantity} акций {stock_symbol} за {cost:.2f}$.")
                self.log_operations.append(f"Куплено {quantity} акций {stock} по цене {price:.2f}$")  # Логируем операцию
                self.update_portfolio_table()  # Обновляем таблицу с портфелем
                self.update_balance_and_portfolio()  # Обновляем баланс и портфель
                self.calculate_portfolio_value()  # Пересчитываем общую стоимость портфеля
            else:
                messagebox.showwarning("Ошибка", "Недостаточно средств")
        except ValueError:
            messagebox.showwarning("Ошибка", "Неправильное количество акций")  # Обработка некорректного ввода

    def sell_stock(self):
        """
        Продает акции выбранной компании.
        Проверяет, достаточно ли акций для продажи, и обновляет баланс и портфель.
        """
        stock = self.selected_stock.get()  # Выбранная акция
        stock_symbol = self.stocks[stock]  # Символ акции (тикер)
        quantity = self.entry_quantity.get()  # Количество акций, которые хочет продать пользователь
        
        try:
            quantity = int(quantity)  # Убедимся, что введено целое число
            if stock_symbol in self.portfolio and self.portfolio[stock_symbol] >= quantity:
                # Получаем текущую цену акции
                data = yf.Ticker(stock_symbol).history(period="1d")
                price = data['Close'].iloc[-1]  # Закрывающая цена акции
                revenue = price * quantity  # Доход от продажи
                
                # Обновляем баланс и портфель
                self.balance += revenue
                self.portfolio[stock_symbol] -= quantity
                if self.portfolio[stock_symbol] == 0:
                    del self.portfolio[stock_symbol]  # Удаляем из портфеля, если больше нет акций этого типа

                self.log_operations.append(f"Продано {quantity} акций {stock} по цене {price:.2f}$")  # Логируем операцию
                messagebox.showinfo("Успешная продажа", f"Вы продали {quantity} акций {stock_symbol} за {revenue:.2f}$.")
                self.update_portfolio_table()  # Обновляем таблицу с портфелем
                self.update_balance_and_portfolio()  # Обновляем баланс и портфель
                self.calculate_portfolio_value()  # Пересчитываем общую стоимость портфеля
            else:
                messagebox.showwarning("Ошибка", "Недостаточно акций для продажи")
        except ValueError:
            messagebox.showwarning("Ошибка", "Неправильное количество акций")  # Обработка некорректного ввода

    def add_balance(self):
        """
        Пополняет баланс пользователя.
        
        Проверяет корректность введенной суммы и обновляет баланс.
        """
        try:
            amount = float(self.entry_add_balance.get())  # Получаем сумму пополнения
            if amount > 0:
                self.balance += amount
                messagebox.showinfo("Пополнение", f"Баланс пополнен на {amount:.2f}$.")  # Уведомление об успешном пополнении
                self.log_operations.append(f"Пополнен баланс на {amount:.2f}$")  # Логируем операцию
                self.update_balance_and_portfolio()  # Обновляем отображение баланса и портфеля
                self.entry_add_balance.delete(0, tk.END)  # Очищаем поле ввода
            else:
                messagebox.showerror("Ошибка", "Введите положительное значение")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное значение")  # Обработка некорректного ввода
