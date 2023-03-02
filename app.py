import tkinter
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import pymysql
import tkinter as tk
from tkinter import ttk
import pandas as pd
from tkinter import filedialog
from openpyxl import Workbook
from tkinter import simpledialog
from tkinter import messagebox
from datetime import datetime
# 连接 MySQL 数据库


# class MySQLTableInfo(tk.Frame):
def get_db_connection():
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='gui',
        password='LBD8TrTBeMZFBa8t',
        db='gui',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn
def close_connection(conn, cursor):
    cursor.close()
    conn.close()
    # print("MySQL connection is closed")


# 创建 tkinter 窗口
root = tk.Tk()
root.geometry("1280x500")
root.title("MySQL Table Info")

style = ttk.Style()
style.theme_use("default")

style.configure("Custom.Treeview", font=("Calibri", 13), bordercolor='red',  borderwidth=1, relief="solid")

tree = ttk.Treeview(root, style="Custom.Treeview", selectmode='browse', show='headings')
tree.pack(side='left', fill='both', expand=True)



table_header = ['库名', '备注', '日期', '总量', '已搜索', '搜索有的', '待搜索', '异常']
tree["columns"] = table_header
# 设置第一列宽度为200
tree.column('#0', width=100)
# 设置其它列宽度为100
for col in table_header[1:]:

    if col=='日期':
        tree.column(col, width=180)
    elif col == '备注':
        tree.column(col, width=180)
    else:
        tree.column(col, width=70)

# 表头
for i in table_header:
    tree.column(i, anchor="center")
    tree.heading(i, text=i, anchor='center')

# 查询所有表名
conn = get_db_connection()
cursor = conn.cursor()
cursor = conn.cursor()
cursor.execute("show tables")
tables = cursor.fetchall()
close_connection(conn, cursor)
# conn = get_db_connection()
# cursor = conn.cursor()
# 每页显示的条数
page_size = 10

# 获取数据总数
total_count = len(tables)

# 分页页数
page_count = (total_count + page_size - 1) // page_size

# 分页数据
pages = [tables[i:i+page_size] for i in range(0, total_count, page_size)]

# 当前页码
current_page = 1

# 显示指定页码的表格数据
def show_table_data(page_num):
    conn = get_db_connection()
    cursor = conn.cursor()
    tree.delete(*tree.get_children())
    # 查询ordea_all表中的数据
    cursor.execute(f"SELECT * FROM ordea_all ORDER BY 日期 DESC LIMIT {page_size} OFFSET {(page_num - 1) * page_size}")
    data = cursor.fetchall()
    # print(data)
    for row in data:
        tree.insert('', 'end', values=(row['库名'], row['备注'], row['日期'], row['总量'], row['已搜索'], row['搜索有'], row['待搜索'], row['异常']))
    close_connection(conn, cursor)


# 显示第一页的数据
show_table_data(current_page)

# 分页标签
page_label = tk.Label(root, text=f"页数： {current_page} / {page_count}")
page_label.pack(side='bottom', padx=3, pady=3)

# 上一页按钮
def previous_page():
    global current_page
    if current_page > 1:
        current_page -= 1
        show_table_data(current_page)
        page_label.config(text=f"页数： {current_page} / {page_count}")

previous_button = tk.Button(root, text="上一页", command=previous_page)
previous_button.pack(side='bottom', padx=3, pady=3)

# 下一页按钮
def next_page():
    global current_page
    if current_page < page_count:
        current_page += 1
        show_table_data(current_page)
        page_label.config(text=f"页数： {current_page} / {page_count}")

next_button = tk.Button(root, text="下一页", command=next_page)
next_button.pack(side='bottom', padx=3, pady=3)




# 创建添加表的对话框
def create_table_dialog():
    dialog = tk.Toplevel(root)
    dialog.geometry("300x100")
    dialog.title("添加库")

    # 添加表名输入框
    label = tk.Label(dialog, text="输入库名")
    label.pack(side='top')
    entry = tk.Entry(dialog)
    entry.pack(side='top')

    # 添加确认按钮
    def confirm():
        table_name = entry.get()
        if not table_name:
            return
        create_table(table_name)
        dialog.destroy()

    confirm_button = tk.Button(dialog, text="确认", command=confirm)
    confirm_button.pack(side='bottom',padx=3, pady=3)







# 删除库
def delete_table():
    # 获取选中的表名

    conn = get_db_connection()
    cursor = conn.cursor()
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("错误", "未选中任何表格！")
        return
    table_name = tree.item(selected_item)['values'][0]
    if not table_name.startswith('ordea_'):
        messagebox.showerror("错误", "无法删除此表格！")
        return
    # 弹出确认删除对话框
    if not tkinter.messagebox.askyesno("确认", f"是否确定删除 '{table_name}'？"):
        return
    # 删除 ordea_all 表中对应的记录
    try:
        cursor.execute(f"DELETE FROM ordea_all WHERE 库名='{table_name}'")
        conn.commit()
    except Exception as e:
        print(e)
        conn.rollback()
        messagebox.showerror("错误", "删除记录失败！")
        return
    # 弹出是否删除数据表的对话框
    if tkinter.messagebox.askyesno("确认", f"订单删除成功，是否也请客 '{table_name}'所有数据？"):
        # 删除数据表
        try:
            cursor.execute(f"DROP TABLE `{table_name}`")
            conn.commit()
        except Exception as e:
            print(e)
            conn.rollback()
            messagebox.showerror("错误", "删除数据表失败！")
            return
    # 刷新表格内容
    close_connection(conn, cursor)
    refresh_table_data()



# 创建删除库按钮
delete_button = tk.Button(root, text="删除库",  command=delete_table)
delete_button.pack(side='bottom', padx=3, pady=3)


# 创建导出按钮
def export_to_excel():
    conn = get_db_connection()
    cursor = conn.cursor()
    selected_items = tree.selection()
    if not selected_items:
        return

    file_path = filedialog.asksaveasfilename(defaultextension='.xlsx')
    if not file_path:
        return

    wb = Workbook()
    ws = wb.active
    for item in selected_items:
        table_name = tree.item(item, 'values')[0]
        cursor.execute(f"select * from {table_name}")
        data = cursor.fetchall()
        for i, row in enumerate(data):
            for j, value in enumerate(row):
                ws.cell(row=i + 1, column=j + 1, value=value)
    wb.save(file_path)
    close_connection(conn, cursor)


export_button = tk.Button(root, text="导出到Excel表格", command=export_to_excel)
export_button.pack(side='bottom',padx=3, pady=3)


# 新增“修改备注”的对话框
def modify_remark_dialog():
    conn = get_db_connection()
    cursor = conn.cursor()
    # 获取当前选中行的数据
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select a row first.")
        return
    values = tree.item(selected_item, 'values')
    table_name = values[0]
    remark = values[1]

    dialog = tk.Toplevel(root)
    dialog.geometry("300x200")
    dialog.title("修改备注")

    # 显示库名和当前备注信息
    label1 = tk.Label(dialog, text=f"库名：{table_name}")
    label1.pack(side='top')
    label2 = tk.Label(dialog, text="当前备注：")
    label2.pack(side='top')
    old_remark = tk.Label(dialog, text=remark)
    old_remark.pack(side='top')

    # 添加输入框和确认按钮
    label3 = tk.Label(dialog, text="新备注：")
    label3.pack(side='top')
    entry = tk.Entry(dialog)
    entry.pack(side='top')

    def confirm():
        conn = get_db_connection()
        cursor = conn.cursor()
        new_remark = entry.get()
        if not new_remark:
            messagebox.showwarning("Warning", "Please enter new remark.")
            return
        # 更新数据库中的备注信息
        cursor.execute(f"UPDATE ordea_all SET 备注='{new_remark}' WHERE 库名='{table_name}'")
        conn.commit()
        # 更新表格中的备注信息
        tree.item(selected_item, values=(table_name, new_remark, values[2]))
        dialog.destroy()

    close_connection(conn, cursor)
    confirm_button = tk.Button(dialog, text="确认", command=confirm)
    confirm_button.pack(side='bottom',padx=3, pady=3)


# 新增“修改备注”按钮
modify_remark_button = tk.Button(root, text="修改备注", command=modify_remark_dialog)
modify_remark_button.pack(side='bottom',padx=3, pady=3)


def import_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    # 获取选中的表名
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("错误", "未选中任何表格！")
        return
    table_name = tree.item(selected_item)['values'][0]
    if not table_name.startswith('ordea_'):
        messagebox.showerror("错误", "无法导入数据到此表格！")
        return

    # 弹出文件选择对话框
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if not file_path:
        return

    # 弹出导入进度对话框
    import_progress = tk.Toplevel(root)
    import_progress.title("导入进度")
    import_progress.geometry("400x100")  # 设置弹窗大小
    progress_label = tk.Label(import_progress, text="正在导入数据，请稍等...", font=("Helvetica", 16))
    progress_label.pack(pady=20)

    def import_thread():
        # 打开文件并读取数据
        with open(file_path, 'r') as f:
            lines = f.readlines()
            total_count = len(lines)
            current_count = 0
            success_count = 0
            repeat_count = 0
            # 分批导入数据
            batch_size = 10000
            for i in range(0, total_count, batch_size):
                batch_data = []
                for line in lines[i:i+batch_size]:
                    data = line.strip().split()
                    batch_data.append(data)

                # 插入数据到数据库
                try:
                    cursor.executemany(f"INSERT IGNORE INTO `{table_name}` (`phone`, `status`) VALUES (%s, 0)", batch_data)
                    conn.commit()
                    success_count += cursor.rowcount
                    repeat_count += len(batch_data) - cursor.rowcount
                except Exception as e:
                    print(e)
                    conn.rollback()
                    messagebox.showerror("错误", "插入数据失败，请检查是否非11位手机号。")
                    close_connection(conn, cursor)
                    return

                # 更新导入进度
                current_count += len(batch_data)
                progress_percent = current_count * 100 / total_count
                progress_label.config(text=f"已导入 {current_count} / {total_count} 行数据 ({progress_percent:.2f}%)")
                import_progress.update_idletasks()

        # 关闭导入进度对话框
        import_progress.destroy()
        messagebox.showinfo("信息", f"数据导入完成！成功导入 {success_count} 行数据，重复数据 {repeat_count} 行。")
        close_connection(conn, cursor)

    # 启动后台线程导入数据
    import_thread = threading.Thread(target=import_thread)
    import_thread.start()
    refresh_table_data()

# 创建导入数据的按钮
import_button = tk.Button(root, text="导入数据", command=import_data)
import_button.pack(side='bottom', padx=3, pady=3)



def open_upload_dialog():
    conn = get_db_connection()
    cursor = conn.cursor()
    # 获取选中的表名
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("错误", "未选中任何表格！")
        return
    table_name = tree.item(selected_item)['values'][0]
    if not table_name.startswith('ordea_'):
        messagebox.showerror("错误", "无法导入数据到此表格！")
        return

    # 弹出文本输入框
    upload_window = tk.Toplevel(root)
    upload_window.title("输入上传数据")
    upload_text = tk.Text(upload_window, width=50, height=10)
    upload_text.pack(padx=10, pady=10)

    def import_data_from_text():
        # 读取输入的数据
        data = upload_text.get("1.0", "end").strip().split()
        if not data:
            messagebox.showwarning("警告", "输入数据为空！")
            return

        # 弹出导入进度对话框
        import_progress = tk.Toplevel(root)
        import_progress.title("导入进度")
        progress_label = tk.Label(import_progress, text="正在导入数据，请稍等...")
        progress_label.pack()

        # 插入数据到数据库
        try:
            cursor.executemany(f"INSERT IGNORE INTO `{table_name}` (`phone`, `status`) VALUES (%s, 0)", data)
            conn.commit()
        except Exception as e:
            print(e)
            conn.rollback()
            messagebox.showerror("错误", "插入数据失败,请检查是否数据重复，或者非11位手机号。")
            return

        # 关闭导入进度对话框
        import_progress.destroy()
        messagebox.showinfo("信息", "数据导入完成！")

        # 关闭输入上传数据的对话框
        upload_window.destroy()

    close_connection(conn, cursor)
    # 添加导入按钮
    import_button = tk.Button(upload_window, text="导入", command=import_data_from_text)
    import_button.pack(pady=10)

# 创建上传数据按钮
upload_button = tk.Button(root, text="输入数据", command=open_upload_dialog)
upload_button.pack(side='bottom',padx=3, pady=3)


def create_table(table_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    # 查询表名是否已经存在
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    result = cursor.fetchone()
    if result:
        messagebox.showerror("Error", "Table already exists!")
        return
    table_name='ordea_'+table_name
    # 创建表
    sql = f'''
            CREATE TABLE `{table_name}` (
              `id` INT NOT NULL AUTO_INCREMENT,
              `phone` VARCHAR(11) NOT NULL,
              `name` VARCHAR(30),
              `gender` VARCHAR(10),
              `nickname` VARCHAR(30),
              `account` VARCHAR(30),
              `province` VARCHAR(30),
              `city` VARCHAR(30),
              `member` INT,
              `avatar` VARCHAR(100),
              `province_code` VARCHAR(10),
              `city_code` VARCHAR(10),
              `status` INT,
              PRIMARY KEY (`id`),
              UNIQUE KEY `unique_phone` (`phone`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    '''
    try:
        cursor.execute(sql.format(table_name=table_name))
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(f"INSERT INTO ordea_all (库名, 备注, 日期) VALUES ('{table_name}', '', '{now}')")
        conn.commit()
        tree.insert('', 'end', values=(table_name, 0))
        show_table_data(current_page)  # 刷新整个表格的内容显示
    except Exception as e:
        print(e)
        conn.rollback()
        messagebox.showerror("Error", "Create table failed!")

    close_connection(conn, cursor)


create_table_button = tk.Button(root, text="添加库", command=create_table_dialog)
create_table_button.pack(side='bottom', padx=3, pady=3)


# 刷新表格内容
def refresh_table_data():
    global tables
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ordea_all")
    tables = cursor.fetchall()
    tree.delete(*tree.get_children())
    print(tables)
    for table in tables:
        table_name = table['库名']
        remark = table['备注']
        date = table['日期']
        cursor.execute(f"select count(*) from `{table_name}`")
        count = cursor.fetchone()['count(*)']
        tree.insert('', 'end', values=(table_name, remark, date, count))
    # 更新分页相关数据
    global total_count, page_count, pages
    total_count = len(tables)
    page_count = (total_count + page_size - 1) // page_size
    pages = [tables[i:i+page_size] for i in range(0, total_count, page_size)]
    # 显示第一页的数据
    global current_page
    current_page = 1
    show_table_data(current_page)
    # 更新分页标签
    page_label.config(text=f"分页： {current_page} / {page_count}")
    close_connection(conn, cursor)


# 新增“刷新”按钮
def refresh():
    # 清空表格
    conn = get_db_connection()
    cursor = conn.cursor()
    tree.delete(*tree.get_children())
    # 查询数据库
    cursor.execute("SELECT * FROM ordea_all ORDER BY 日期 DESC")
    data = cursor.fetchall()
    if not data:
        return
    for row in data:
        table_name = row['库名']
        cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
        result = cursor.fetchone()
        # print(f"Result: {result}")

        count = result.get('COUNT(*)', 0)

        cursor.execute(f"SELECT COUNT(*) FROM `{table_name}` WHERE `status` IN (0, 2)")
        result = cursor.fetchone()
        pending_count = result.get('COUNT(*)', 0)

        cursor.execute(f"SELECT COUNT(*) FROM `{table_name}` WHERE `status` = 1")
        result = cursor.fetchone()
        searched_count = result.get('COUNT(*)', 0)

        cursor.execute(f"SELECT COUNT(*) FROM `{table_name}` WHERE `status` = 3")
        result = cursor.fetchone()
        exception_count = result.get('COUNT(*)', 0)

        cursor.execute(f"SELECT COUNT(*) FROM `{table_name}` WHERE `gender` IS NOT NULL AND `gender` != ''")
        result = cursor.fetchone()
        search_success_count = result.get('COUNT(*)', 0)

        cursor.execute(f"UPDATE ordea_all SET `总量`={count}, `待搜索`={pending_count}, `已搜索`={searched_count}, `异常`={exception_count}, `搜索有`={search_success_count} WHERE `库名`='{table_name}'")
        conn.commit()

        # tree.insert('', 'end', values=(row['库名'], row['备注'], count, pending_count, searched_count, exception_count, search_success_count, row['日期']))

    # 更新页码和分页数据
    global total_count, page_count, pages
    total_count = len(data)
    page_count = (total_count + page_size - 1) // page_size
    pages = [data[i:i+page_size] for i in range(0, total_count, page_size)]
    # 更新当前页码和分页标签
    global current_page
    current_page = 1
    page_label.config(text=f"页数： {current_page} / {page_count}")

    # 显示第一页的数据
    show_table_data(current_page)
    close_connection(conn, cursor)


refresh_button = tk.Button(root, text="刷新", command=refresh)
refresh_button.pack(side='bottom',padx=3, pady=3)



# 窗口循环
root.mainloop()

# 关闭数据库连接
close_connection(conn, cursor)


