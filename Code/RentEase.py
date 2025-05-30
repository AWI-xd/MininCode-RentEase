import sqlite3
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw
from tkinter import Label, Button, Entry, StringVar
from plyer import notification
import threading
import time
import win10toast

connection = sqlite3.connect('users.db')
cursor = connection.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        fullname TEXT NOT NULL,
        email TEXT NOT NULL,
        password TEXT NOT NULL,
        admin INTEGER NOT NULL
    )
    ''')


# Категории
cursor.execute('''
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
)
''')
# Предметы товара
cursor.execute('''
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    price INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories (id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    item_id INTEGER NOT NULl,
    user_id INTEGER NOT NULL,
    date_start TEXT NOT NULL,
    date_end TEXT NOT NULL,
    hours INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (item_id) REFERENCES items (id)
)
''')

# Регистрация пользователя

def adding_a_user(root, user_name, user_email, user_password):
    #connection = sqlite3.connect('users.db')
    query = 'SELECT COUNT(*) FROM users WHERE email = ?'
    cursor.execute(query, (user_email,))
    result = cursor.fetchone()
    if result[0] > 0:
        #connection.close()
        print('Пользователь с таким email уже существует')
        messagebox.showinfo('Ошибка ввода данных', 'Пользователь с таким email уже существует')
        return 'error'
    else:
        # Добавление пользователя
        cursor.execute('INSERT INTO users (fullname, email, password, admin) VALUES (?, ?, ?, ?)',
                       (user_name, user_email, user_password, 0))
        connection.commit()
        connection.close()
        print('Пользователь успешно зарегистрирован')
        root.destroy()
        entrance()
        return 'ok'


def registration():
    def validation_check():
        # Получаем введенные данные из полей ввода
        user_name = user_name_entry.get()
        user_email = user_email_entry.get()
        user_password = user_password_entry.get()
        user_password_again = user_password_again_entry.get()

        # Сравниваем пароли и вызываем функцию регистрации, если они совпадают
        if user_password == user_password_again:
            adding_a_user(registration_window, user_name, user_email, user_password)
        else:
            print('Пароли не совпадают')
            messagebox.showinfo('Ошибка ввода данных', 'Пароли не совпадают. Повторите попытку.')

    registration_window = Tk()
    registration_window.title('Регистрация')
    registration_window.geometry("600x700+450+100")
    registration_window.resizable(False, False)

    # Овал и текст РЕГИСТРАЦИЯ
    canvas = Canvas(registration_window, width=600, height=450)
    canvas.pack()
    canvas.create_arc((-50, -170, 650, 120), start=180, extent=180, fill='#007FFF', outline='')
    canvas.create_text(302, 60, text='РЕГИСТРАЦИЯ', fill='white', font=('Arial', 25, 'bold'))

    # Поле для ввода имени пользователя
    canvas.create_text(300, 200, text='Имя пользователя', fill='black', font=('Arial', 10, 'bold'))
    user_name_entry = Entry(registration_window, font=('Arial', 10), width=35)
    canvas.create_window(300, 230, window=user_name_entry)

    # Поле для ввода email
    canvas.create_text(300, 270, text='Email', fill='black', font=('Arial', 10, 'bold'))
    user_email_entry = Entry(registration_window, font=('Arial', 10), width=35)
    canvas.create_window(300, 300, window=user_email_entry)

    # Поле для ввода пароля
    canvas.create_text(300, 340, text='Пароль', fill='black', font=('Arial', 10, 'bold'))
    user_password_entry = Entry(registration_window, font=('Arial', 10), width=35, show='*')
    canvas.create_window(300, 370, window=user_password_entry)

    # Поле для подтверждения пароля
    canvas.create_text(300, 410, text='Повторите пароль', fill='black', font=('Arial', 10, 'bold'))
    user_password_again_entry = Entry(registration_window, font=('Arial', 10), width=35, show='*')
    canvas.create_window(300, 440, window=user_password_again_entry)

    # Кнопка регистрации
    register_button = Button(registration_window, text="Регистрация", command=validation_check,
                             font=('Arial', 14, 'bold'), bg='#007FFF', fg='white',
                             activebackground='#45a049', activeforeground='white',
                             borderwidth=0, pady=10, padx=30, highlightthickness=0)
    register_button.pack(pady=20)

    login_button = Button(registration_window, text="Войти", command=lambda: entrance(registration_window),
                          font=('Arial', 9, 'bold'), bg='#007FFF', fg='white',
                          activebackground='#45a049', activeforeground='white',
                          borderwidth=0, pady=10, padx=20, highlightthickness=0)
    login_button.pack(pady=10)

    registration_window.mainloop()

# Вход пользователя
def entrance(registration_window=None):
    def user_login():
        email = user_email_entry.get()
        password = user_password_entry.get()

        try:
            connection = sqlite3.connect('users.db')
            cursor = connection.cursor()

            # Проверяем существование пользователя
            query = 'SELECT COUNT(*) FROM users WHERE email = ?'
            cursor.execute(query, (email,))
            result = cursor.fetchone()

            if result[0] > 0:
                # Извлекаем пароль и id пользователя
                cursor.execute('SELECT id, password FROM users WHERE email = ?', (email,))
                result = cursor.fetchone()
                user_id, pswrd = result

                if pswrd == password:
                    main_page()
                    print(f'User ID: {user_id}')
                else:
                    print('Error: Incorrect password')
                    messagebox.showinfo('Ошибка ввода данных', 'Неверный пароль. Повторите попытку.')
            else:
                print('Error: User not found')
                messagebox.showinfo('Ошибка ввода данных', 'Пользователь не найден.')
        except Exception as e:
            print(f'An error occurred: {e}')
        finally:
            connection.close()

    if registration_window is not None:
        registration_window.destroy()

    login = Tk()
    login.title('Вход')
    login.geometry("600x700+450+100")
    login.resizable(False, False)

    # Овал и текст Вход
    canvas = Canvas(login, width=600, height=378)
    canvas.pack()
    canvas.create_arc((-50, -170, 650, 120), start=180, extent=180, fill='#007FFF', outline='')
    canvas.create_text(302, 60, text='ВХОД', fill='white', font=('Arial', 25, 'bold'))

    # Поле для ввода email
    canvas.create_text(300, 270, text='Email', fill='black', font=('Arial', 10, 'bold'))
    user_email_entry = Entry(login, font=('Arial', 10), width=35)
    canvas.create_window(300, 300, window=user_email_entry)

    # Поле для ввода пароля
    canvas.create_text(300, 340, text='Пароль', fill='black', font=('Arial', 10, 'bold'))
    user_password_entry = Entry(login, font=('Arial', 10), width=35, show='*')
    canvas.create_window(300, 370, window=user_password_entry)

    # Кнопка "Вход"
    login_button = Button(login, text="Вход", command=user_login,
                          font=('Arial', 14, 'bold'), bg='#007FFF', fg='white',
                          activebackground='#45a049', activeforeground='white',
                          borderwidth=0, pady=10, padx=20, highlightthickness=0)
    login_button.pack(pady=20)

    login.mainloop()

# Главная страница
def main_page():
    def connect_db(db_name):
        connection = sqlite3.connect(db_name)
        return connection

    def get_all_products():
        conn = connect_db('products.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        conn.close()
        return products

    def create_rounded_rectangle_image(width, height, radius, color):
        image = Image.new("RGBA", (width, height), color)
        return image

    def show_product_details(image, name, describe, costs):
        detail_window = tk.Toplevel()
        detail_window.title('Карточка товара')
        detail_window.configure(bg='white')
        detail_window.geometry("1100x650")

        background_img = create_rounded_rectangle_image(500, 400, 20, 'white')

        try:
            original_image = Image.open(image).convert("RGBA")
            original_image = original_image.resize((460, 360), Image.LANCZOS)
        except FileNotFoundError:
            original_image = Image.new("RGBA", (460, 360), (255, 255, 255, 0))

        background_img.paste(original_image, (20, 20), original_image)

        img_tk = ImageTk.PhotoImage(background_img)
        image_label = Label(detail_window, image=img_tk, bg='white')
        image_label.img_tk = img_tk
        image_label.place(x=25, y=50)

        text_label = Label(detail_window, text=name, bg='#ffffff', fg='black', font=("Arial", 20))
        text_label.pack(pady=(0, 600), expand=True)

        res_describe = ''
        count = -1
        for i in describe:
            count += 1
            if count != 47:
                res_describe += i
            else:
                res_describe += '\\\\\\\\\\n'
                res_describe += i
                count = 0

        describe_label = Label(detail_window, text=res_describe, bg='#ffffff', fg='black', font=("Arial", 14))
        describe_label.place(x=575, y=70)

        cost_label = Label(detail_window, text=f"Цена: {costs} рублей", bg='#ffffff', fg='black', font=("Arial", 15))
        cost_label.place(x=575, y=500)

        rent_button = Button(detail_window, text="Арендовать", bg='#d3d3d3', fg='black', font=("Arial", 14),
                             command=create_rental_window)
        rent_button.place(x=920, y=495)

    def create_rental_window():
        rental_window = Toplevel()
        rental_window.title("Создать заказ")
        rental_window.geometry("300x600")
        rental_window.configure(bg='white')

        conn = connect_db('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, fullname, email FROM users")
        user_data = cursor.fetchone()  # Получение данных пользователя
        conn.close()

        user_id = user_data[0] if user_data else ""  # Получаем user_id
        fullname = user_data[1] if user_data else ""
        email = user_data[2] if user_data else ""

        Label(rental_window, text='Создать заказ', bg='white', font=("Arial", 18)).pack(pady=10)

        Label(rental_window, text='Имя пользователя:', bg='white', font=("Arial", 12)).pack(pady=5)
        fullname_entry = Entry(rental_window, width=30, font=("Arial", 12), bg='#d3d3d3')
        fullname_entry.insert(0, fullname)
        fullname_entry.pack(pady=5)

        Label(rental_window, text='Почта:', bg='white', font=("Arial", 12)).pack(pady=5)
        email_entry = Entry(rental_window, width=30, font=("Arial", 12), bg='#d3d3d3')
        email_entry.insert(0, email)
        email_entry.pack(pady=5)

        rent_duration_var = StringVar()
        Label(rental_window, text='Длительность аренды (в минутах):', bg='white', font=("Arial", 12)).pack(pady=10)
        rent_duration_entry = Entry(rental_window, textvariable=rent_duration_var, width=10, font=("Arial", 12), bg='#d3d3d3')
        rent_duration_entry.pack(pady=5)

        Button(rental_window, text='Подтвердить аренду', bg='#d3d3d3', font=("Arial", 12),
               command=lambda: confirm_rent(user_id, "sample_product", rent_duration_var.get())).pack(pady=20)

    def confirm_rent(user_id, product, duration):
        try:
            duration_minutes = int(duration)
            save_rent_to_db(user_id, product, duration_minutes)  # Сохранение в базу данных
            threading.Thread(target=rent_timer, args=(duration_minutes,)).start()
        except ValueError:
            # В случае некорректного ввода, ничего не делает
            pass

    def save_rent_to_db(user_id, product, duration):
        conn = connect_db('rentals.db')
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS user_orders (user_id INTEGER, product TEXT, duration INTEGER)")
        cursor.execute("INSERT INTO user_orders (user_id, product, duration) VALUES (?, ?, ?)",
                       (user_id, product, duration))
        conn.commit()
        conn.close()

    def rent_timer(minutes):
        time.sleep(minutes * 60)
        show_notification()

    def show_notification():
        notification.notify(
            title='Аренда завершена',
            message='Срок аренды вашего товара завершен.',
            app_name='RentLogict',
            timeout=10,
        )

    def get_orders_by_id(uid):
        conn = connect_db('rentals.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM user_orders WHERE user_id = ?', (uid,))
        result = cursor.fetchall()
        result = [i[0] for i in result]
        print(result)



    root = tk.Tk()
    root.title("Приложение аренды")
    root.geometry('800x600')
    canvas = Canvas(root, width=800, height=70)
    canvas.pack()
    canvas.create_text(397, 60, text='RentEase', fill='#007FFF', font=('Arial', 25, 'bold'))

    def show_profile_window():
        user_room = UserRoom()
        user_room.mainloop()

    profile_button = tk.Button(root, text="Профиль", command=show_profile_window)
    profile_button.pack(pady=10, anchor='ne')
    # Настройка поля для поиска
    search_var = tk.StringVar()
    search_entry = ttk.Entry(root, textvariable=search_var)
    search_entry.pack(pady=10)
    search_var.trace("w", lambda name, index, mode: update_product_list(search_var.get()))

    # Создание списка товаров
    listbox = tk.Listbox(root, height=20)
    listbox.pack(fill=tk.BOTH, expand=True)

    def update_product_list(query):
        matching_products = [product for product in all_products if query.lower() in product[2].lower()]
        listbox.delete(0, tk.END)
        for product in matching_products:
            listbox.insert(tk.END, product[2])

    def on_product_select(event):
        selected_idx = listbox.curselection()
        if selected_idx:
            selected_product = all_products[selected_idx[0]]
            image, name, describe, costs = selected_product[1], selected_product[2], selected_product[3], \
            selected_product[4]
            show_product_details(image, name, describe, costs)

    listbox.bind('<<ListboxSelect>>', on_product_select)

    all_products = get_all_products()
    update_product_list("")

    class UserRoom(tk.Tk):
        def __init__(self):
            super().__init__()
            self.geometry("400x750")
            self.title("Личный кабинет")
            self.zagolovok()
            self.current_order()
            self.history_zakaz()
            self.review()
            self.rating_input()

        def zagolovok(self):
            # Создаем заголовок окна
            title_label = ttk.Label(self, text="Личный кабинет", font=("Arial", 24))
            title_label.pack(pady=10)

        def current_order(self):
            # Отображение текущих заказов
            orders_label = ttk.Label(self, text="Действующие заказы", font=("Arial", 18))
            orders_label.pack(pady=10)
            # Текст текущих заказов
            orders_order = ttk.Label(self, text='Error 503, Сервис временно недоступен :(', font=("Arial", 18))
            orders_order.pack(pady=10)

        def history_zakaz(self):
            # Отображение истории заказов
            orders_label = ttk.Label(self, text="История заказов", font=("Arial", 18))
            orders_label.pack(pady=10)
            # Текстовая область для истории заказов
            orders_text = tk.Text(self, width=47, height=6)
            orders_text.pack(pady=10)

        def review(self):
            # Раздел для отзывов
            review_label = ttk.Label(self, text="Отзывы", font=("Arial", 18))
            review_label.pack(pady=10)
            # Текстовая область для ввода отзывов
            review_text = tk.Text(self, width=47, height=6)
            review_text.pack(pady=10)

        def rating_input(self):
            # Поле для ввода рейтинга
            rating_label = ttk.Label(self, text="Ваша репутация", font=("Arial", 18))
            rating_label.pack(pady=10)
            # Входное поле для рейтинга
            rating_entry = ttk.Entry(self, width=10)
            rating_entry.pack(pady=10)

    # Запуск основного цикла приложения
    if __name__ == "__main__":
        app = UserRoom()
        app.mainloop()


registration()