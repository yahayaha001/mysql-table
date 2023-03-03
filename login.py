import tkinter as tk
from tkinter import messagebox
import pymysql
from app import MySQLTableInfo

class LoginFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("登录")
        self.master.geometry("300x200")
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.master, text="用户名").grid(row=0, column=0)
        tk.Label(self.master, text="密码").grid(row=1, column=0)
        self.username_entry = tk.Entry(self.master)
        self.password_entry = tk.Entry(self.master, show="*")
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self.master, text="登录", command=self.login).grid(row=2, column=1, padx=5, pady=5)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username == "" or password == "":
            messagebox.showwarning("提示", "请输入用户名和密码！")
            return
        try:
            conn = pymysql.connect(
                host='localhost',
                port=3306,
                user='gui',
                password='LBD8TrTBeMZFBa8t',
                db='gui',
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            with conn.cursor() as cursor:
                sql = f"SELECT * FROM user WHERE username='{username}' AND password='{password}'"
                cursor.execute(sql)
                result = cursor.fetchone()
                if result:
                    # 登录成功，关闭当前窗口，打开主界面
                    self.master.destroy()
                    root = tk.Tk()
                    app = MySQLTableInfo(root, username)
                    app.pack()
                    root.mainloop()
                else:
                    messagebox.showwarning("提示", "用户名或密码错误！")
        except pymysql.Error as e:
            messagebox.showerror("错误", f"数据库连接失败！\n{e}")
        finally:
            conn.close()


if __name__ == '__main__':
    root = tk.Tk()
    app = LoginFrame(root)
    app.mainloop()
