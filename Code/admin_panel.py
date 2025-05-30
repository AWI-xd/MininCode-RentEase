import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter import messagebox, filedialog

conn = sqlite3.connect("products.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image TEXT,
    name TEXT NOT NULL,
    description TEXT,
    costs REAL
)
""")
conn.commit()


class ProductAdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Административная панель (Товары)")

        # Элементы интерфейса
        self.name_var = tk.StringVar()
        self.desc_var = tk.StringVar()
        self.img_var = tk.StringVar()
        self.costs_var = tk.DoubleVar()

        # Создание полей ввода
        tk.Label(root, text="Название товара").grid(row=0, column=0, pady=5)
        tk.Entry(root, textvariable=self.name_var).grid(row=0, column=1, pady=5)

        tk.Label(root, text="Описание товара").grid(row=1, column=0, pady=5)
        tk.Entry(root, textvariable=self.desc_var).grid(row=1, column=1, pady=5)

        tk.Label(root, text="Изображение товара").grid(row=2, column=0, pady=5)
        tk.Entry(root, textvariable=self.img_var).grid(row=2, column=1, pady=5)

        tk.Label(root, text="Цена").grid(row=3, column=0, pady=5)
        tk.Entry(root, textvariable=self.costs_var).grid(row=3, column=1, pady=5)

        tk.Button(root, text="Выбрать изображение", command=self.select_image).grid(row=2, column=2, pady=5)

        # Кнопки добавления, редактирования и удаления
        tk.Button(root, text="Добавить", command=self.add_product).grid(row=4, column=0, pady=10)
        tk.Button(root, text="Редактировать", command=self.update_product).grid(row=4, column=1, pady=10)
        tk.Button(root, text="Удалить", command=self.delete_product).grid(row=4, column=2, pady=10)

        # Список товаров
        self.product_list = ttk.Treeview(root, columns=("ID", "Name", "Description", 'Cost'), show="headings")
        self.product_list.heading("ID", text="ID")
        self.product_list.heading("Name", text="Название")
        self.product_list.heading("Description", text="Описание")
        self.product_list.heading("Cost", text="Цена")
        self.product_list.grid(row=5, column=0, columnspan=3, pady=10)

        self.product_list.bind("<<TreeviewSelect>>", self.on_product_select)
        self.load_products()  # Загрузка товаров в список

#Выбор изображения
    def select_image(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])

        if filepath:
            self.img_var.set(filepath)

# Добавление товара
    def add_product(self):
        name = self.name_var.get()
        description = self.desc_var.get()
        image = self.img_var.get()
        costs = self.costs_var.get()

        if not name or not image:
            messagebox.showwarning("Ошибка", "Заполните все поля!")
            return

        # Вставляем данные о товаре в таблицу
        cursor.execute("INSERT INTO products (name, description, image, costs) VALUES (?, ?, ?, ?)",
                       (name, description, image, costs))
        conn.commit()

        # Очищаем поля ввода и обновляем список товаров
        self.clear_fields()
        self.load_products()

    def update_product(self):
        selected_item = self.product_list.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите товар для редактирования")
            return

        product_id = self.product_list.item(selected_item)["values"][0]
        name = self.name_var.get()
        description = self.desc_var.get()
        image = self.img_var.get()
        costs = self.costs_var.get()

        if not name or not image:
            messagebox.showwarning("Ошибка", "Заполните все поля!")
            return

        # Обновляем данные в таблице
        cursor.execute("""
        UPDATE products SET name = ?, description = ?, image = ?, costs = ? WHERE id = ?
        """, (name, description, image, costs, product_id))
        conn.commit()

        # Очищаем поля ввода и обновляем список товаров
        self.clear_fields()
        self.load_products()

# Удаление товара
    def delete_product(self):
        selected_item = self.product_list.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите товар для удаления")
            return

        product_id = self.product_list.item(selected_item)["values"][0]

        # Удаляем товар из таблицы
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()

        # Очищаем поля ввода и обновляем список товаров
        self.clear_fields()
        self.load_products()

# Загрузка и отображение товара в списке
    def load_products(self):
        for item in self.product_list.get_children():
            self.product_list.delete(item)

        # Извлекаем все товары из таблицы и добавляем их в список
        cursor.execute("SELECT id, name, description, costs FROM products")
        for row in cursor.fetchall():
            self.product_list.insert("", "end", values=row)

    def clear_fields(self):
        self.name_var.set("")
        self.desc_var.set("")
        self.img_var.set("")
        self.costs_var.set(0)

    def on_product_select(self, event):
        selected_item = self.product_list.selection()
        if not selected_item:
            return
        product_id = self.product_list.item(selected_item)["values"][0]

        # Извлекаем данные о товаре из таблицы
        cursor.execute("SELECT name, description, image, costs FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()

        # Заполняем поля ввода извлеченными данными
        if product:
            self.name_var.set(product[0])
            self.desc_var.set(product[1])
            self.img_var.set(product[2])
            self.costs_var.set(product[3])


class RentalAdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Пользователи")
        self.root.geometry("600x400")

        # Подключение к базе данных
        self.user_conn = sqlite3.connect('users.db')
        self.order_conn = sqlite3.connect('user_orders.db')
        self.user_cursor = self.user_conn.cursor()
        self.order_cursor = self.order_conn.cursor()

        # Проверка существования таблицы rentals, если не существует, создаем её
        self.create_rentals_table()

        # Создание интерфейса приложения
        self.create_gui()

    def create_rentals_table(self):
        # Создаем таблицу rentals, если она не существует
        self.order_cursor.execute('''
            CREATE TABLE IF NOT EXISTS rentals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                product TEXT,
                duration TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

        self.order_conn.commit()

    def create_gui(self):
        # Создание и размещение таблицы с пользователями и их арендами
        self.tree = ttk.Treeview(self.root, columns=("Имя", "Почта", "Аренда", "Срок"), show='headings')
        self.tree.heading("Имя", text="Имя")
        self.tree.heading("Почта", text="Почта")
        self.tree.heading("Аренда", text="Аренда")
        self.tree.heading("Срок", text="Срок")

        self.tree.pack(expand=True, fill=tk.BOTH)

        # Кнопка удаления пользователя
        self.delete_button = ttk.Button(self.root, text="Удалить пользователя", command=self.delete_user)
        self.delete_button.pack(side=tk.BOTTOM, pady=10)

        # Кнопка обновления информации
        self.refresh_button = ttk.Button(self.root, text="Обновить", command=self.refresh_data)
        self.refresh_button.pack(side=tk.BOTTOM, pady=10)

        # Изначальное заполнение таблицы данными
        self.refresh_data()

    def refresh_data(self):
        # Очистка существующих данных в таблице
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Проверка наличия столбца "fullname" в таблице users
        self.user_cursor.execute("PRAGMA table_info(users)")
        columns_info = self.user_cursor.fetchall()
        column_names = [column[1] for column in columns_info]  # Извлекаем имена столбцов из структуры таблицы

        if 'fullname' not in column_names:
            # Если столбец "fullname" отсутствует, предупреждаем пользователя
            print("Ошибка: В таблице 'users' отсутствует столбец 'fullname'")
            return

        # Извлечение данных из базы и заполнение таблицы
        self.user_cursor.execute("SELECT id, fullname, email FROM users")
        users = self.user_cursor.fetchall()

        if not users:
            # В случае отсутствия пользователей выводим предупреждение или сообщение
            print("В базе данных отсутствуют пользователи.")
            return

        for user in users:
            user_id, fullname, email = user
            # Получение аренды и сроков для каждого пользователя
            self.order_cursor.execute("SELECT product, duration FROM rentals WHERE user_id=?", (user_id,))
            rentals = self.order_cursor.fetchall()

            # Если данные по аренде отсутствуют, заполняем только информацию о пользователе
            if not rentals:
                self.tree.insert("", "end", values=(fullname, email, "Нет аренды", ""))
            else:
                for rental in rentals:
                    product, duration = rental
                    self.tree.insert("", "end", values=(fullname, email, product, duration))

    def delete_user(self):
        # Получение выбранного элемента
        selected_item = self.tree.selection()
        if not selected_item:
            print("Нет выбранного элемента.")
            return
        item = self.tree.item(selected_item)
        fullname = item['values'][0]

        # Находим id пользователя по его имени
        self.user_cursor.execute("SELECT id FROM users WHERE fullname=?", (fullname,))
        user_id = self.user_cursor.fetchone()
        if not user_id:
            print("Пользователь не найден.")
            return

        # Удаляем пользователя из таблиц
        self.user_cursor.execute("DELETE FROM users WHERE id=?", (user_id[0],))
        self.order_cursor.execute("DELETE FROM rentals WHERE user_id=?", (user_id[0],))

        self.user_conn.commit()
        self.order_conn.commit()

        # Обновляем данные в таблице
        self.refresh_data()


admin_window = Tk()
admin_window.title("Панель администратора")
admin_window.geometry("500x350")


def show_admin_users():
    # Создаем новое окно для отображения пользователей
    user_window = Toplevel(admin_window)
    app = RentalAdminApp(user_window)


def test():
    user_window = Toplevel(admin_window)
    app = ProductAdminApp(user_window)


all_products = Button(admin_window, text="Панель администратора (Товары)", command=test,
                      font=('Arial', 14, 'bold'), bg='#007FFF', fg='white',
                      activebackground='#45a049', activeforeground='white',
                      borderwidth=0, pady=10, padx=30, highlightthickness=0)
all_products.pack(pady=20)

list_of_users_button = Button(admin_window, text="Панель администратора (Users)", command=show_admin_users,
                              font=('Arial', 14, 'bold'), bg='#007FFF', fg='white',
                              activebackground='#45a049', activeforeground='white',
                              borderwidth=0, pady=10, padx=30, highlightthickness=0)
list_of_users_button.pack(pady=20)

admin_window.mainloop()