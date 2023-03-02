import hashlib
import tkinter as tk
import pymysql


class LoginWindow:
    def __init__(self, on_login_success):
        self.conn = pymysql.connect(host='localhost', user='gui', password='LBD8TrTBeMZFBa8t', database='gui')
        self.cursor = self.conn.cursor()

        self.root = tk.Tk()
        self.root.geometry('300x200')
        self.root.title('登录')

        tk.Label(self.root, text='用户名：').place(x=50, y=50)
        tk.Label(self.root, text='密码：').place(x=50, y=80)

        self.username_entry = tk.Entry(self.root)
        self.username_entry.place(x=110, y=50)

        self.password_entry = tk.Entry(self.root, show='*')
        self.password_entry.place(x=110, y=80)

        tk.Button(self.root, text='登录', command=self.login).place(x=110, y=120)

        self.on_login_success = on_login_success

        self.root.mainloop()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # 将密码进行 MD5 加密
        password_md5 = hashlib.md5(password.encode('utf-8')).hexdigest()

        sql = f"SELECT * FROM users WHERE username='{username}' AND password='{password_md5}'"
        self.cursor.execute(sql)
        result = self.cursor.fetchone()

        if result is None:
            tk.messagebox.showerror('错误', '用户名或密码错误')
        else:
            # 登录成功，关闭数据库连接
            self.cursor.close()
            self.conn.close()

            # 调用登录成功回调函数，并传递用户名参数
            self.on_login_success(username)
