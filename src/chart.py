from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker


class ChartManager:
    def __init__(self, canvas):
        """
        Инициализация менеджера графиков.
        """
        self.canvas = canvas  # Полотно, на котором будет размещен график
        self.fig = plt.Figure(figsize=(10, 6))  # Создание объекта фигуры для графика
        self.ax = self.fig.add_subplot(111)  # Добавление осей к фигуре
        self.canvas_agg = FigureCanvasTkAgg(self.fig, master=canvas)  # Интеграция Matplotlib в Tkinter
        self.canvas_agg.get_tk_widget().pack()  # Отображение графика в Tkinter

    def price_chart(self):
        """
        Построение графика стоимости выбранной акции за заданный период.
        Используются настройки отображения оси x в зависимости от выбранного временного интервала.
        """
        # Получение тикера выбранной акции и периода отображения
        stock_symbol = self.stocks[self.selected_stock.get()]  # Тикер акции
        period = self.selected_period.get()  # Период (например, "Год", "Месяц", "5 Дней")
        
        # Получение данных акций за указанный период
        stock_data = self.getData(stock_symbol, period)

        # Очистка графика перед построением нового
        self.fig.clear()
        ax = self.fig.add_subplot(111)  # Добавляем новые оси для нового графика

        # Построение графика с ценами закрытия
        ax.plot(stock_data.index, stock_data['Close'], label=stock_symbol, color="blue")

        # Настройка оси X в зависимости от периода
        if period == "Год":
            # Для годового периода: делаем отметки по месяцам
            ax.xaxis.set_major_locator(mdates.MonthLocator())  # Основные отметки — каждый месяц
            ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonthday=16))  # Дополнительные — середина месяца
            ax.xaxis.set_major_formatter(ticker.NullFormatter())  # Убираем подписи с основных отметок
            ax.xaxis.set_minor_formatter(mdates.DateFormatter('%b'))  # Отображаем сокращенные названия месяцев
        elif period == "Месяц":
            # Для месячного периода: делаем отметки по неделям и дням
            ax.xaxis.set_major_locator(mdates.WeekdayLocator())  # Основные отметки — начало недели
            ax.xaxis.set_minor_locator(mdates.DayLocator())  # Дополнительные — каждый день
            ax.xaxis.set_major_formatter(ticker.NullFormatter())  # Убираем подписи с основных отметок
            ax.xaxis.set_minor_formatter(mdates.DateFormatter('%d'))  # Отображаем дни месяца
        elif period == "5 Дней":
            # Для пятидневного периода: делаем отметки по дням и часам
            ax.xaxis.set_major_locator(mdates.DayLocator())  # Основные отметки — каждый день
            ax.xaxis.set_minor_locator(mdates.HourLocator(interval=12))  # Дополнительные — каждые 12 часов
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))  # Отображаем дату (день, месяц)
            ax.xaxis.set_minor_formatter(mdates.DateFormatter('%H:%M'))  # Отображаем время (часы:минуты)
        
        # Автоматическая настройка отображения дат на оси X
        self.fig.autofmt_xdate()

        # Настройка заголовка и подписей осей
        ax.set_title(f"График цены {stock_symbol}", color="darkred")  # Заголовок графика
        ax.set_xlabel("Дата", color="green")  # Подпись оси X
        ax.set_ylabel("Цена", color="green")  # Подпись оси Y
        ax.legend()  # Легенда графика
        ax.grid(True)  # Включение сетки на графике

        # Отрисовка обновленного графика
        self.canvas.draw()

        # Обновление отображения текущей цены акции
        self.label_current_price.config(
            text=f"Текущая цена {stock_symbol}: {stock_data['Close'][-1]:.2f}$", fg="blue"
        )

        # Обновление графика каждую секунду
        root.after(1000, self.price_chart)  # вызов функции через 1000 мс (1 секунда)
