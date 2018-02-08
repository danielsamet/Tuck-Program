from tkinter import *
from tkinter import filedialog  # work out why this is greyed out
import tkinter.messagebox
import math
import sqlite3
import date_picker
import datetime
from collections import OrderedDict

# currently working on: data correction; ??

__author__ = 'Daniel Samet'


class TuckProgram:

    def __init__(self):  # initialises the window and creates the top_bar for navigation and main_frame to be
        # populated by the appropriate function with the relevant page details
        root = Tk()
        root.config(bg='grey11')
        width, height = 1400, 760
        root.minsize(width, height)
        x = (root.winfo_screenwidth() / 2) - (width / 2)
        y = (root.winfo_screenheight() / 2.2) - (height / 2)
        root.geometry('%dx%d+%d+%d' % (width, height, x, y))
        Grid.rowconfigure(root, 0, weight=1)
        Grid.rowconfigure(root, 1, weight=1000)
        Grid.columnconfigure(root, 0, weight=1)

        top_bar = Frame(root, bg="blue2")
        top_bar.grid(row=0, column=0, sticky=E + W)
        self.title_var = StringVar()
        self.back_btn = Button(top_bar, text="<--", font=("Calibri", "24", "bold"),
                               command=lambda: self.main_menu())
        self.back_btn.grid(row=0, column=0, sticky=W, padx=20, pady=20, ipadx=30)
        self.title = Label(top_bar, textvariable=self.title_var, font=("Calibri", "24", "bold"))
        self.title.grid(row=0, column=1, sticky=E+W, padx=20, pady=20, ipadx=30)
        self.home_btn = Button(top_bar, text="Home", font=("Calibri", "24", "bold"), command=lambda: self.main_menu())
        self.home_btn.grid(row=0, column=2, sticky=E, padx=20, pady=20, ipadx=10)
        Grid.rowconfigure(top_bar, 0, weight=1)
        Grid.columnconfigure(top_bar, 0, weight=1), Grid.columnconfigure(top_bar, 1, weight=5)
        Grid.columnconfigure(top_bar, 2, weight=1)

        self.main_frame = Frame(root, bg='grey10')
        self.main_frame.grid(row=1, column=0, sticky=N+E+S+W)
        self.main_menu()

        self.letters, self.numbers = 'abcdefghijklmnopqrstuvwxyz', '0123456789'

        self.delete = []
        self.page_items_height, self.page_items_width = 5, 3

        self.connection = sqlite3.connect("tuck.db")
        self.cursor = self.connection.cursor()
        self.search = list()

        # self.font_1, self.font_2, self.font_3 = ("Calibri", "14", "bold"), ("Calibri", "14", "bold"),
        # ("Calibri", "14", "bold")

        self.db_initialisation()

        root.mainloop()

    def db_initialisation(self):
        sql_command = list()
        sql_command.append(
            """
            CREATE TABLE accounts (
            account_no INTEGER PRIMARY KEY,
            f_name VARCHAR(20) NOT NULL,
            l_name VARCHAR(30) NOT NULL,
            budget INTEGER NOT NULL,
            discount_1 INTEGER,
            discount_2 VARCHAR(11),
            discount_3 VARCHAR(11),
            discount_4 VARCHAR(11),
            discount_5 VARCHAR(11),
            spending_limit_1 INTEGER,
            spending_limit_2 VARCHAR(9),
            spending_limit_3 VARCHAR(11),
            spending_limit_4 VARCHAR(11),
            spending_limit_5 VARCHAR(11),
            spending_limit_6 VARCHAR(11),
            sub_zero_allowance_1 INTEGER,
            sub_zero_allowance_2 VARCHAR(11),
            sub_zero_allowance_3 VARCHAR(11),
            sub_zero_allowance_4 VARCHAR(11),
            sub_zero_allowance_5 VARCHAR(11),
            notes VARCHAR(255),
            added DATE NOT NULL);
            """)
        # extended discounts, spending limit and sub_zero_balance are for recording time periods.
        sql_command.append(
            """
            CREATE TABLE products (
            product_no INTEGER PRIMARY KEY,
            p_name VARCHAR(20) NOT NULL,
            cost_price INTEGER,
            selling_price INTEGER NOT NULL,
            quantity INTEGER,
            discount INTEGER,
            offer_1 INTEGER,
            offer_2 INTEGER,
            offer_3 INTEGER,
            offer_4 INTEGER,
            offer_5 VARCHAR(11),
            purchase_limit_1 INTEGER,
            purchase_limit_2 VARCHAR(9),
            sub_zero_allowance INTEGER
            notes VARCHAR(255),
            added DATE NOT NULL);
            """)
        sql_command.append(
            """
            CREATE TABLE settings (
            setting_no INTEGER PRIMARY KEY,
            setting_name VARCHAR(20),
            setting_val VARCHAR(20));
            """)
        try:
            for command in sql_command:
                self.cursor.execute(command)
            self.connection.commit()
        except sqlite3.OperationalError:  # tables already exist
            pass

    def main_menu(self):  # populates the main_frame with the main menu consisting of 3 buttons: Setup, Shop and Data
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.back_btn.config(command=lambda: NONE), self.home_btn.config(command=lambda: NONE)
        Grid.rowconfigure(self.main_frame, 0, weight=1)
        for i in range(1, 6):
            Grid.rowconfigure(self.main_frame, i, weight=0)  # necessary to reset row configuration when navigating from
        # other pages to main menu
        Grid.columnconfigure(self.main_frame, 0, weight=1)
        Grid.columnconfigure(self.main_frame, 1, weight=1)
        Grid.columnconfigure(self.main_frame, 2, weight=1)
        self.title_var.set("Main Menu")

        setup_btn = Button(self.main_frame, text="Setup", font=("Calibri", "32", "bold"), bg='grey60',
                           command=lambda: self.setup())
        setup_btn.grid(row=0, column=0, ipadx=120, ipady=60)
        shop_btn = Button(self.main_frame, text="Shop", font=("Calibri", "32", "bold"), bg='grey60',
                          command=lambda: self.shop())
        shop_btn.grid(row=0, column=1, ipadx=120, ipady=60)
        data_btn = Button(self.main_frame, text="Data", font=("Calibri", "30", "bold"), bg='grey60',
                          command=lambda: self.data())
        data_btn.grid(row=0, column=2, ipadx=120, ipady=60)

        self.main_frame.bind_all(1, lambda event: self.setup())
        self.main_frame.bind_all(2, lambda event: self.shop())
        self.main_frame.bind_all(3, lambda event: self.data())

    def setup(self):  # populates the main_frame with the two setup options: Accounts and Products
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.back_btn.config(command=lambda: self.main_menu()), self.home_btn.config(command=lambda: self.main_menu())
        self.title_var.set("Setup")
        self.unbind(title_cut=False)

        Grid.columnconfigure(self.main_frame, 0, weight=1)
        Grid.columnconfigure(self.main_frame, 1, weight=1)
        Grid.columnconfigure(self.main_frame, 2, weight=0)

        accounts_btn = Button(self.main_frame, text="Accounts", font=("Calibri", "32", "bold"), bg='grey60',
                              command=lambda: self.accounts())
        accounts_btn.grid(row=0, column=0, ipadx=70, ipady=30)
        products_btn = Button(self.main_frame, text="Products", font=("Calibri", "32", "bold"), bg='grey60',
                              command=lambda: self.products())
        products_btn.grid(row=0, column=1, ipadx=70, ipady=30)

        self.main_frame.bind_all(1, lambda event: self.accounts())
        self.main_frame.bind_all(2, lambda event: self.products())
        self.main_frame.bind_all('<Control-BackSpace>', lambda event: self.main_menu())

    def shop(self, page_num=1, user=list()):  # populates the main_frame with the list of accounts for one to be
        # selected so that a transaction can be made on the chosen account
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.back_btn.config(command=lambda: self.main_menu()), self.home_btn.config(command=lambda: self.main_menu())
        self.title_var.set("Shop ({}){}".format(len(self.table_reader('products')), ' - {}'.format(
            ''.join(self.search).upper()) if len(self.search) != 0 else ''))

        page = IntVar()
        page.set(page_num)

        font = ("Calibri", "14", "bold")

        # frame initialisation
        sales = OrderedDict()
        item_frame = Frame(self.main_frame, bg='red4')
        item_frame.grid(row=0, column=0, sticky=N + E + S + W)
        sale_frame = Frame(self.main_frame, bg='lightblue', width=250)
        sale_frame.grid(row=0, column=1, rowspan=2, sticky=N + E + S + W)
        sale_frame.grid_propagate(False)
        sale_itemised = Frame(sale_frame, bg='lightblue')
        sale_itemised.grid(row=0, column=0, sticky=N + E + S + W)
        sale_totals = Frame(sale_frame, bg='red2')
        sale_totals.grid(row=1, column=0, sticky=N + E + S + W)
        operation_btn_frame = Frame(self.main_frame, bg='green1')
        operation_btn_frame.grid(row=1, column=0, ipady=10, sticky=N + E + S + W)

        scrollbar = Scrollbar(sale_itemised)
        scrollbar.grid(row=0, column=1, sticky=N + S)
        listbox = Listbox(sale_itemised, yscrollcommand=scrollbar.set, font=("Calibri", "18", "bold"))
        listbox.bindtags((listbox, sale_itemised, "all"))
        listbox.grid(row=0, column=0, sticky=N + E + S + W)
        scrollbar.config(command=listbox.yview)

        Grid.rowconfigure(sale_itemised, 0, weight=1)
        Grid.columnconfigure(sale_itemised, 0, weight=10), Grid.columnconfigure(sale_itemised, 1, weight=0)

        total_product_pages = math.ceil(len(self.table_reader('products'))
                                        / (self.page_items_width * self.page_items_height))
        total_product_pages = 1 if total_product_pages == 0 else total_product_pages
        total_user_pages = math.ceil(len(self.table_reader('accounts'))
                                     / (self.page_items_width * self.page_items_height))
        total_user_pages = 1 if total_user_pages == 0 else total_user_pages

        items = self.table_reader('products', self.get_columns('products')[1])

        details_amount_var, details_total_var = list(), list()

        for i in range(len(self.table_reader('products'))):
            if len(details_amount_var) < len(self.table_reader('products')):
                details_amount_var.append(StringVar()), details_amount_var[i].set("x0")
            if len(details_total_var) < len(self.table_reader('products')):
                details_total_var.append(StringVar()), details_total_var[i].set("£0.00")

        def product_populator():  # page populator specific for the products previewed in the shop page
            for item in item_frame.grid_slaves():
                item.destroy()

            self.bind(product_populator, page.get())

            offset = (page.get() - 1) * self.page_items_width * self.page_items_height

            product_frame, product_lbl, increase_qty, decrease_qty, m = dict(), dict(), dict(), dict(), int()
            product_details1, product_details2, product_details3 = dict(), dict(), dict()

            def qty_changer(no, change):
                if int(details_amount_var[no].get()[1:]) != items[no][7] or items[no][7] == 0:
                    details_amount_var[no].set('x{}'.format(int(details_amount_var[no].get()[1:]) + change))
                    details_total_var[no].set('£{:.2f}'.format(int(details_amount_var[no].get()[1:]) *
                                                               float(items[no][3])))
                    sales_setter(no, int(details_amount_var[no].get()[1:]))
                    details_updater()
                else:
                    tkinter.messagebox.showinfo("Purchase Limit", "There is a purchase limit for \'{}\' of {}.".format(
                        items[no][1], items[no][7]))

            for j in range(self.page_items_height):
                Grid.rowconfigure(item_frame, j, weight=1)
                for k in range(self.page_items_width):
                    if j == 0:
                        Grid.columnconfigure(item_frame, k, weight=1)
                    try:
                        items[m + offset]  # strangest thing ever! lines occur in the item_frame unless the items array
                        # is referenced with the offset provided.
                        product_frame[m] = Frame(item_frame, bg='pink', height=100, width=10)
                        product_frame[m].grid(row=j, column=k, padx=10, pady=5, sticky=E + W)
                        product_frame[m].grid_propagate(False)
                        product_lbl[m] = Label(product_frame[m], text="{}".format(items[m + offset][1]), font=font)
                        product_lbl[m].grid(row=0, column=1, columnspan=3, sticky=E + W)
                        product_details1[m] = Label(product_frame[m], text="£{}".format(
                            "{:.2f}".format(items[m + offset][3])), font=font, width=6)
                        product_details1[m].grid(row=1, column=1, sticky=E + W)

                        product_details2[m] = Label(product_frame[m], textvariable=details_amount_var[m + offset],
                                                    font=font, width=6)
                        product_details2[m].grid(row=1, column=2, sticky=E + W)
                        product_details3[m] = Label(product_frame[m], textvariable=details_total_var[m + offset],
                                                    font=font, width=7)
                        product_details3[m].grid(row=1, column=3, sticky=E + W)
                        increase_qty[m] = Button(product_frame[m], text='+', font=font,
                                                 command=lambda offset_m=m + offset: qty_changer(offset_m, 1))
                        increase_qty[m].grid(row=0, column=0, sticky=E + W)
                        decrease_qty[m] = Button(product_frame[m], text='-', font=font,
                                                 command=lambda offset_m=m + offset: qty_changer(offset_m, -1)
                                                 if float(details_amount_var[offset_m].get()[1:]) > 0 else None)
                        decrease_qty[m].grid(row=1, column=0, sticky=E + W)

                        Grid.columnconfigure(product_frame[m], 0, weight=2)
                        Grid.columnconfigure(product_frame[m], 1, weight=1)
                        Grid.columnconfigure(product_frame[m], 2, weight=1)
                        Grid.columnconfigure(product_frame[m], 3, weight=1)
                        Grid.rowconfigure(product_frame[m], 0, weight=1)
                        Grid.rowconfigure(product_frame[m], 1, weight=1)
                    except IndexError:
                        break
                    m += 1

        def sales_setter(product_no, quantity):
            item = items[product_no]
            sales[item[0]] = "{0:}x{1:>6} @£{2:.2f} = £{3:.2f}".format(quantity, item[1], item[3], quantity*item[3])
            if item[5] > 0:
                total = float(sales[item[0]][sales[item[0]].rfind('£') + 1:])
                sales[int(item[0]) + .5] = "{0:>6}% off = £{1:.2f}".format(
                    item[5], total - (total * float(item[5]) / 100))
            if quantity == 0:
                del sales[item[0]]
                if int(item[0]) + .5 in sales:
                    del sales[int(item[0]) + .5]

            listbox.delete(0, END)
            for m in sales.values():
                listbox.insert(END, m)

        def account_populator():  # page populator specific for the accounts previewed in the shop page
            for item in item_frame.grid_slaves():
                item.destroy()

            self.bind(account_populator, page.get())

            items = self.table_reader('accounts', self.get_columns('accounts')[2], self.get_columns('accounts')[1])
            offset = (page.get() - 1) * self.page_items_width * self.page_items_height
            btn, i = dict(), int()

            for j in range(self.page_items_height):
                Grid.rowconfigure(item_frame, j, weight=1)
                for k in range(self.page_items_width):
                    if j == 0:
                        Grid.columnconfigure(item_frame, k, weight=1)
                    try:
                        btn[i] = Button(item_frame, text="{} {}".format(items[i + offset][1], items[i + offset][2]),
                                        font=font, width=6, height=2,
                                        command=lambda item_=items[i + offset]: self.combine_funcs(
                                            [user.pop() for _ in range(7)] if user else None, user.extend(item_),
                                            set_user_details(), details_updater(), page.set(1), self.unbind(),
                                            self.title_var.set("Shop"), user_select.set(False), product_populator()))
                        btn[i].grid(row=j, column=k, padx=15, pady=5, sticky=E + W)
                    except IndexError:
                        break
                    i += 1

        def details_updater():  # updates the relevant details previewed at the bottom of the shop page (e.g. New
            # Balance)
            total = float()
            for individual_total in details_total_var:
                total += float(individual_total.get()[1:])
            total = round(float(total), 3)
            subtotal_var.set("Subtotal: £{:.2f}".format(total))
            user_discount_var.set("User Discount: £{:.2f} ({}%)".format(
                float(subtotal_var.get()[11:]) * (user[4] / 100), user[4])) if user else None

            total_discounts = float()
            for key in [key for key in sales.keys() if '.' in str(key)]:  # loops through discount keys, adding just
                # the discount values
                total_discounts += float(sales[int(key)][sales[int(key)].rfind('£') + 1:]) \
                                   - float(sales[key][sales[key].rfind('£') + 1:])
            total_item_discounts_var.set("Total Items Discount: £{:.2f}".format(total_discounts))

            total -= total_discounts
            total = total - total * (user[4] / 100) if user else total
            total_var.set("Total: £{:.2f}".format(total))
            new_balance_var.set("New Balance: £{:.2f}".format(float(user_budget_var.get()[9:]) - total))

        product_populator()

        user_select = BooleanVar()  # for the sake of scrolling pages when selecting user (as opposed to products)
        user_select.set(False)

        username_var, user_budget_var, total_var, new_balance_var = StringVar(), StringVar(), StringVar(), StringVar()

        username = Button(operation_btn_frame, textvariable=username_var, font=font,
                          command=lambda: self.combine_funcs(
                              page.set(1), self.unbind(), self.title_var.set('Shop (Select Account)'),
                              account_populator(), user_select.set(True)))
        username.grid(row=0, column=0, ipadx=40, ipady=0, pady=0, padx=30, sticky=E + W)
        user_budget_lbl = Label(operation_btn_frame, textvariable=user_budget_var, font=font)
        user_budget_lbl.grid(row=1, column=0, ipadx=40, ipady=0, pady=10, padx=30, sticky=E + W)
        previous_page_btn = Button(operation_btn_frame, text='<-', font=font,
                                   command=lambda: self.combine_funcs(
                                       page.set(page.get() - 1), product_populator() if not user_select.get()
                                       else account_populator())
                                   if page.get() > 1 else None)
        previous_page_btn.grid(row=0, column=1, rowspan=2, ipadx=15, padx=0)
        purchase_btn = Button(operation_btn_frame, text='Purchase', font=font,
                              command=lambda: self.combine_funcs(
                                  self.cursor.execute("UPDATE accounts SET Budget = ? WHERE account_no = ?;",
                                                      (new_balance_var.get()[14:], user[0])), self.connection.commit(),
                                  self.shop(user=[user[0], user[1], user[2], new_balance_var.get()[14:], user[4],
                                                  user[5], user[6]])) if float(new_balance_var.get()[14:]) > 0
                              else tkinter.messagebox.showerror(
                                  "Not Enough Money", "Sorry, you don't have enough money to make this transaction."))
        purchase_btn.grid(row=0, column=2, rowspan=2, ipadx=40, ipady=0, pady=0, padx=30, sticky=E + W)
        next_page_btn = Button(operation_btn_frame, text='->', font=font,
                               command=lambda: self.combine_funcs(
                                   self.combine_funcs(page.set(page.get() + 1), product_populator())
                                   if page.get() < total_product_pages else None)
                               if not user_select.get() else self.combine_funcs(
                                   page.set(page.get() + 1), account_populator())
                               if page.get() < total_user_pages else None)
        next_page_btn.grid(row=0, column=3, rowspan=2, ipadx=15, padx=0)

        # Sale_totals Frame
        subtotal_var, user_discount_var, total_item_discounts_var, pady = StringVar(), StringVar(), StringVar(), 0
        subtotal_var.set("Subtotal: £0.00")
        user_discount_var.set("User Discount: £0.00 (0%)")
        total_item_discounts_var.set("Total Items Discount: £0.00")

        subtotal_lbl = Label(sale_totals, textvariable=subtotal_var, font=font)
        subtotal_lbl.grid(row=0, column=0, pady=pady, sticky=E + W)
        user_discount_lbl = Label(sale_totals, textvariable=user_discount_var, font=font)
        user_discount_lbl.grid(row=1, column=0, sticky=E + W)
        total_item_discounts_lbl = Label(sale_totals, textvariable=total_item_discounts_var, font=font)
        total_item_discounts_lbl.grid(row=2, column=0, pady=pady, sticky=E + W)
        total_lbl = Label(sale_totals, textvariable=total_var, font=font)
        total_lbl.grid(row=3, column=0, ipadx=40, ipady=0, pady=0, padx=0, sticky=E + W)
        new_balance_budget_lbl = Label(sale_totals, textvariable=new_balance_var, font=font)
        new_balance_budget_lbl.grid(row=4, column=0, ipadx=40, ipady=0, pady=pady, padx=0, sticky=E + W)

        # row and column configuration
        Grid.rowconfigure(self.main_frame, 0, weight=1000), Grid.rowconfigure(self.main_frame, 1, weight=1)
        Grid.columnconfigure(self.main_frame, 0, weight=5), Grid.columnconfigure(self.main_frame, 1, weight=1)
        Grid.columnconfigure(self.main_frame, 2, weight=0)

        Grid.rowconfigure(sale_frame, 0, weight=6), Grid.rowconfigure(sale_frame, 1, weight=1)
        Grid.columnconfigure(sale_frame, 0, weight=1)

        Grid.rowconfigure(sale_totals, 0, weight=1), Grid.rowconfigure(sale_totals, 1, weight=1)
        Grid.rowconfigure(sale_totals, 2, weight=1), Grid.rowconfigure(sale_totals, 3, weight=1)
        Grid.rowconfigure(sale_totals, 4, weight=1), Grid.columnconfigure(sale_totals, 0, weight=1)

        Grid.rowconfigure(operation_btn_frame, 0, weight=1), Grid.columnconfigure(operation_btn_frame, 0, weight=1)
        Grid.columnconfigure(operation_btn_frame, 1, weight=1), Grid.columnconfigure(operation_btn_frame, 2, weight=1)
        Grid.columnconfigure(operation_btn_frame, 3, weight=1), Grid.columnconfigure(operation_btn_frame, 4, weight=1)

        def set_user_details():  # to enable dynamic setting of user details
            username_var.set("{} {}".format(user[1], user[2]))
            user_budget_var.set("Budget: £{:.2f}".format(float(user[3])))
            user_discount_var.set("User Discount: £{:.2f} ({}%)".format(float(subtotal_var.get()[11:])
                                                                        * (user[4] / 100), user[4]))

        username_var.set("Select User"), user_budget_var.set("Budget: £0.00")
        if user:
            set_user_details()
        total_var.set("Total: £0.00")
        new_balance_var.set("New Balance: £{:.2f}".format(float(user_budget_var.get()[9:])))

        self.main_frame.bind_all('<Control-BackSpace>', lambda event: self.main_menu())

    def data(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.back_btn.config(command=lambda: self.main_menu()), self.home_btn.config(command=lambda: self.main_menu())
        self.title_var.set("Data")
        self.unbind(title_cut=False)
        self.main_frame.bind_all('<Control-BackSpace>', lambda event: self.main_menu())

    def accounts(self, page_num=1):
        # provides the appropriate data for the setup_window_generator to generate the accounts window (see the
        # generator itself for functionality)

        for widget in self.main_frame.winfo_children():
            widget.destroy()
        # Grid.columnconfigure(self.main_frame, 1, weight=0)

        self.setup_window_generator(page_num, 'accounts', self.item_form, self.table_reader, self.accounts)

    def setup_window_generator(self, page_num, table, add_command, page_command, caller):
        # populates the main_frame with items along with buttons to: import new accounts, edit current account
        # information, add new accounts and delete accounts as well as page interaction (moving between pages)
        self.back_btn.config(command=lambda: self.setup())
        self.title_var.set("{} ({}){}".format(table.capitalize(), len(self.table_reader(table)),
                                              ' - {}'.format(''.join(self.search).upper())
                                              if len(self.search) != 0 else ''))

        total_items = len(self.table_reader(table))
        total_pages = math.ceil(total_items / (self.page_items_width * self.page_items_height))
        total_pages = 1 if total_pages == 0 else total_pages

        page = IntVar()
        page.set(page_num)

        item_frame, operation_btn_frame = Frame(self.main_frame, bg='red1'), Frame(self.main_frame, bg='green1')
        item_frame.grid(row=0, column=0, sticky=N + E + S + W)
        operation_btn_frame.grid(row=1, column=0, sticky=N + E + S + W)

        Grid.rowconfigure(self.main_frame, 0, weight=1000), Grid.rowconfigure(self.main_frame, 1, weight=1)
        Grid.columnconfigure(self.main_frame, 1, weight=0), Grid.columnconfigure(self.main_frame, 2, weight=0)
        Grid.columnconfigure(self.main_frame, 3, weight=0)

        import_btn = Button(operation_btn_frame, text='Import', font=("Calibri", "14", "bold"))
        import_btn.grid(row=0, column=0, ipadx=40, ipady=0, pady=20, padx=30, sticky=E + W)
        add_btn = Button(operation_btn_frame, text='Add', font=("Calibri", "14", "bold"),
                         command=lambda page=page.get(): add_command(0, page, table, caller))
        add_btn.grid(row=0, column=1, ipadx=40, ipady=0, pady=20, padx=30, sticky=E + W)
        previous_page_btn = Button(operation_btn_frame, text='Previous Page', font=("Calibri", "14", "bold"),
                                   command=lambda: self.combine_funcs(
                                       self.page_populator(item_frame, page_command(
                                           table, self.get_columns(table)[2]
                                           if table == 'accounts' else self.get_columns(table)[1],
                                           self.get_columns(table)[1] if table == 'accounts' else None),
                                                           page.get() - 1, table, caller),
                                       page.set(page.get() - 1)) if page.get() > 1 else NONE)
        previous_page_btn.grid(row=0, column=2, ipadx=40, ipady=0, pady=20, padx=30, sticky=E + W)
        page_no_lbl = Label(operation_btn_frame, textvariable=page)
        page_no_lbl.grid(row=0, column=3, ipadx=40, ipady=0, pady=20, padx=30, sticky=E + W)
        page_no_of_lbl = Label(operation_btn_frame, text="of {}".format(total_pages))
        page_no_of_lbl.grid(row=0, column=4, ipadx=40, ipady=0, pady=20, padx=30, sticky=E + W)
        next_page_btn = Button(operation_btn_frame, text='Next Page', font=("Calibri", "14", "bold"),
                               command=lambda page_=page.get(): self.combine_funcs(
                                   self.page_populator(item_frame, page_command(
                                       table, self.get_columns(table)[2]
                                       if table == 'accounts' else self.get_columns(table)[1],
                                       self.get_columns(table)[1] if table == 'accounts' else None),
                                                       page.get() + 1, table, caller),
                                   page.set(page.get() + 1)) if page.get() < total_pages
                               else NONE)
        next_page_btn.grid(row=0, column=5, ipadx=40, ipady=0, pady=20, padx=30, sticky=E + W)

        Grid.rowconfigure(operation_btn_frame, 0, weight=1)
        Grid.columnconfigure(operation_btn_frame, 0, weight=2), Grid.columnconfigure(operation_btn_frame, 1, weight=2)
        Grid.columnconfigure(operation_btn_frame, 2, weight=2), Grid.columnconfigure(operation_btn_frame, 3, weight=1)
        Grid.columnconfigure(operation_btn_frame, 4, weight=1), Grid.columnconfigure(operation_btn_frame, 5, weight=2)

        path, initial_dir, title_1 = StringVar(), "%documents%", "Select the File to Import From"
        file_types = ('csv files only', '*.csv')
        import_btn.config(command=lambda: self.combine_funcs(
            self.importer(tkinter.filedialog.askopenfilename(initialdir=initial_dir, title=title_1,
                                                             filetypes=[file_types]), table), caller(1)))
        
        self.page_populator(item_frame, page_command(table, self.get_columns(table)[2]
                                                     if table == 'accounts' else self.get_columns(table)[1],
                                                     self.get_columns(table)[1] if table == 'accounts' else None),
                            page.get(), table, caller)

        self.delete.clear()

        self.bind(caller, page.get())
        self.main_frame.bind_all('<Control-BackSpace>', lambda event: self.setup())

    def bind(self, caller, page):  # this function binds all relevant characters for the sake of name searching
        if len(self.search) < 30:  # Until widget size is made more dynamic or is changed permanently buttons in the
            # top_bar will not fit properly if search query is larger than 30 chars
            for letter in self.letters:
                self.main_frame.bind_all(
                    letter, lambda event, title=self.title_var.get(): self.combine_funcs(
                        self.search.append(event.keysym),
                        self.title_var.set('{} - {}'.format(title[:title.find('-') - 1] if '-' in title else title,
                                                            ''.join(self.search).upper())), caller(page)
                        if caller.__name__ not in ['product_populator', 'account_populator'] else caller()))
            for number in self.numbers:
                self.main_frame.bind_all(
                    number, lambda event, title=self.title_var.get(): self.combine_funcs(
                        self.search.append(event.keysym),
                        self.title_var.set('{} - {}'.format(title[:title.find('-') - 1] if '-' in title else title,
                                                            ''.join(self.search).upper())), caller(page)
                        if caller.__name__ not in ['product_populator', 'account_populator'] else caller()))
            self.main_frame.bind_all('<space>', lambda event, title=self.title_var.get(): self.combine_funcs(
                        self.search.append(' '),
                        self.title_var.set('{} - {}'.format(title[:title.find('-') - 1] if '-' in title else title,
                                                            ''.join(self.search).upper())), caller(page)
                        if caller.__name__ not in ['product_populator', 'account_populator'] else caller()))

        else:
            self.unbind(keep_search=True)

        if len(self.search) != 0:
            self.main_frame.bind_all('<BackSpace>', lambda event, title=self.title_var.get(): self.combine_funcs(
                        self.search.pop(),
                        self.title_var.set('{} - {}'.format(title[:title.find('-') - 1] if '-' in title else title,
                                                            ''.join(self.search).upper())), caller(page)
                        if caller.__name__ not in ['product_populator', 'account_populator'] else caller()))
        else:
            self.main_frame.unbind_all('<BackSpace>')

    def unbind(self, keep_search=False, title_cut=True):
        if title_cut:
            self.title_var.set(self.title_var.get()[:self.title_var.get().find('-') - 1])
        for letter in self.letters:
            self.main_frame.unbind_all(letter)
        for number in self.numbers:
            self.main_frame.unbind_all(number)
            self.main_frame.unbind_all('<BackSpace>')
        if not keep_search:
            self.search = list()

    def item_form(self, action, page_num, table, caller, info=None):
        # creates form for adding (action=0) or editing (action=1) item

        [widget.destroy() for widget in self.main_frame.winfo_children()]
        self.back_btn.config(command=lambda: caller(page_num))

        center_frame = Frame(self.main_frame, bg='purple', width=1200, height=100)
        center_frame.grid_propagate(False)

        self.unbind()
        self.main_frame.bind_all('<Control-BackSpace>', lambda event: caller(page_num))

        if action == 0:
            action_ = "Add"
            center_frame.grid(row=0, column=0, sticky=N+S)
            Grid.columnconfigure(self.main_frame, 0, weight=1)
        else:
            action_ = "Edit"

            prev_account, next_account, page_num_prev, page_num_next = list(), list(), int(), int()
            
            prev_account_btn = Button(self.main_frame, text="<-", width=4, font=("Calibri", "28", "bold"),
                                      command=lambda: self.item_form(1, page_num_prev, table, caller, prev_account))
            prev_account_btn.grid(row=0, column=0, padx=5)
            next_account_btn = Button(self.main_frame, text="->", width=4, font=("Calibri", "28", "bold"),
                                      command=lambda: self.item_form(1, page_num_next, table, caller, next_account))
            next_account_btn.grid(row=0, column=2, padx=5)

            items = self.table_reader(table)
            for i in range(len(items)):
                if items[i][0] == info[0] and items[i][1] == info[1]:
                    if i == 0:
                        prev_account_btn.config(command=lambda: None, bg='grey45')
                    else:
                        prev_account = items[i-1]
                        page_num_prev = math.ceil(i/(self.page_items_width * self.page_items_height))
                    if i == len(items) - 1:
                        next_account_btn.config(command=lambda: None, bg='grey45')
                    else:
                        next_account = items[i+1]
                        page_num_next = math.ceil((i+2)/(self.page_items_width * self.page_items_height))

            center_frame.grid(row=0, column=1, pady=5, sticky=N+S)
            Grid.columnconfigure(self.main_frame, 0, weight=1)
            Grid.columnconfigure(self.main_frame, 1, weight=1)
            Grid.columnconfigure(self.main_frame, 2, weight=1)

        self.title_var.set("{} - {}".format(table.capitalize(), action_))

        def time_period_frame_setter(frame, entry):  # adds necessary buttons, entries and labels for
            # time bound details such as an offer

            btn_1 = Button(frame, text='Add', font=font2, bg='green', command=lambda: self.combine_funcs(
                btn_1.grid_forget(),
                btn_2.grid(row=0, column=1, padx=padx, pady=pady, ipadx=ipadx, ipady=ipady, sticky=E + W),
                btn_3.grid(row=0, column=2, padx=padx, pady=pady, ipadx=ipadx, ipady=ipady, sticky=E + W),
                btn_4.grid(row=0, column=3, padx=padx, pady=pady, ipadx=ipadx, ipady=ipady, sticky=E + W),
                Grid.columnconfigure(frame, 2, weight=1), Grid.columnconfigure(frame, 3, weight=1)
            ))

            btn_2 = Button(frame, text='INDEFINITELY', font=font2, width=width, bg='green', command=lambda:
                           self.combine_funcs(
                               btn_2.destroy(), btn_3.destroy(), btn_4.destroy(),
                               entry.grid(row=0, column=1, padx=(padx, 0), sticky=E),
                               [Grid.columnconfigure(frame, k, weight=0) for k in range(1, 4)],
                               Grid.columnconfigure(frame, 2, weight=1),
                               Label(frame, text='to be applied indefinitely', font=font2,
                                     bg='green').grid(row=0, column=2, sticky=W),
                               btn_1.grid(row=0, column=3, ipadx=ipadx, ipady=ipady, padx=padx, pady=pady, sticky=W),
                               btn_1.config(text='DELETE', width=int(width / 3), bg='red',
                                            command=lambda: self.combine_funcs(
                                                [widget.grid_forget() for widget in frame.winfo_children()[2:]],
                                                frame.winfo_children()[0].grid_forget(),  # this is the frame inside of
                                                # 'frame'
                                                [Grid.columnconfigure(frame, k + 1, weight=0) for k in range(3)],
                                                time_period_frame_setter(frame, entry)))
                           ))

            date_entry = Frame(frame, bg='green')
            btn_3 = Button(frame, text='UNTIL GIVEN DATE', font=font2, width=width, bg='green',
                           command=lambda: self.combine_funcs(
                               btn_2.destroy(), btn_3.destroy(), btn_4.destroy(),
                               entry.grid(row=0, column=1, padx=(padx, 0), sticky=E),
                               [Grid.columnconfigure(frame, k, weight=0) for k in range(1, 4)],
                               Grid.columnconfigure(frame, 4, weight=1),
                               Label(frame, text='until', font=font2, bg='green').grid(row=0, column=2, padx=0),
                               date_entry.grid(row=0, column=3, sticky=N + S),
                               date_picker.Datepicker(date_entry, font=font2, entrywidth=10).pack(fill=BOTH,
                                                                                                  pady=pady*6),
                               btn_1.grid(row=0, column=4, ipadx=ipadx, ipady=ipady, padx=padx, pady=pady, sticky=E),
                               btn_1.config(text='DELETE', width=int(width / 3), bg='red',
                                            command=lambda: self.combine_funcs(
                                                [widget.grid_forget() for widget in frame.winfo_children()[2:]],
                                                frame.winfo_children()[0].grid_forget(),  # this is the frame inside of
                                                # 'frame'
                                                [Grid.columnconfigure(frame, k + 1, weight=0) for k in range(1, 5)],
                                                time_period_frame_setter(frame, entry)))
                           ))

            var_ = StringVar()
            var_.set("week(s)")
            opt_menu = OptionMenu(frame, var_, "purchase(s)", "hour(s)", "day(s)", "week(s)", "month(s)", "year(s)")
            opt_menu.config(font=font2, bg='green')
            opt_menu.nametowidget(opt_menu.menuname).configure(font=font2, bg='green')

            btn_4 = Button(frame, text='FOR GIVEN TIME', width=width, wraplength=230, font=font2, bg='green',
                           command=lambda: self.combine_funcs(
                               btn_2.destroy(), btn_3.destroy(), btn_4.destroy(),
                               entry.grid(row=0, column=1, padx=(padx, 0), sticky=E),
                               [Grid.columnconfigure(frame, k, weight=0) for k in range(1, 4)],
                               Grid.columnconfigure(frame, 5, weight=1),
                               Label(frame, text='for', font=font2, bg='green').grid(row=0, column=2),
                               Entry(frame, font=font2, bg='green', width=int(width / 3)).grid(row=0, column=3),
                               opt_menu.grid(row=0, column=4),
                               btn_1.grid(row=0, column=5, ipadx=ipadx, ipady=ipady, padx=padx, pady=pady, sticky=E),
                               btn_1.config(text='DELETE', width=int(width / 3), bg='red',
                                            command=lambda: self.combine_funcs(
                                                [widget.grid_forget() for widget in frame.winfo_children()[2:]],
                                                frame.winfo_children()[0].grid_forget(),  # this is the frame inside of
                                                # 'frame'
                                                [Grid.columnconfigure(frame, k + 1, weight=0) for k in range(1, 6)],
                                                time_period_frame_setter(frame, entry)))
                           ))

            btn_1.grid(row=0, column=1, ipadx=ipadx, ipady=ipady, padx=padx, pady=pady, sticky=E + W)
            Grid.columnconfigure(frame, 1, weight=1)

        font1, font2 = ("Calibri", "18", "bold"), ("Calibri", "18")
        ipadx, ipady, padx, pady, width = 10, 8, 20, 5, 18
        lbl, data, var, i = list(), list(), list(), int()

        if table == 'accounts':
            [var.append(StringVar()) for _ in range(len(self.get_columns(table)[1:-1]))]

            frames = list()
            for i in range(7):
                frames.append(Frame(center_frame, bg='blue', height=60, width=400))
                frames[i].grid(row=i, column=0, columnspan=2, pady=pady, sticky=E + W)

            i += 1
            Label(frames[0], text='First Name', font=font1, width=width, bg='red') \
                .grid(row=0, column=0, ipadx=ipadx, ipady=ipady, padx=padx, pady=pady)
            Entry(frames[0], textvariable=var[0], font=font2, width=width*3, bg='green') \
                .grid(row=0, column=1, ipadx=ipadx, ipady=ipady, padx=padx, pady=pady, sticky=E + W)
            Grid.columnconfigure(frames[0], 1, weight=1)

            Label(frames[1], text='Last Name', font=font1, width=width, bg='red') \
                .grid(row=0, column=0, ipadx=ipadx, ipady=ipady, padx=padx, pady=pady)
            Entry(frames[1], textvariable=var[1], font=font2, width=width*3, bg='green') \
                .grid(row=0, column=1, ipadx=ipadx, ipady=ipady, padx=padx, pady=pady, sticky=E + W)
            Grid.columnconfigure(frames[1], 1, weight=1)

            Label(frames[2], text='Budget', font=font1, width=width, bg='red') \
                .grid(row=0, column=0, ipadx=ipadx, ipady=ipady, padx=padx, pady=pady)
            Label(frames[2], textvariable=var[2], font=font2, width=int(width / 3), bg='green') \
                .grid(row=0, column=1, ipadx=ipadx, ipady=ipady, padx=padx, pady=pady, sticky=W)
            top_up_btn = Button(
                frames[2], text='Top Up', font=font2, width=width*2, bg='green', command=lambda: self.combine_funcs(
                    top_up_entry.grid(row=0, column=2, ipadx=ipadx, ipady=ipady, padx=padx, pady=pady),
                    top_up_btn.grid(row=0, column=3, ipadx=ipadx, ipady=ipady, padx=padx, pady=pady, sticky=E + W),
                    top_up_btn.config(command=lambda: self.combine_funcs(
                        var[2].set(float(var[2].get() if var[2].get() != '' else 0) +
                                   float(budget.get() if budget.get() != '' else 0)), budget.set('')))))
            top_up_btn.grid(row=0, column=2, columnspan=2, ipadx=ipadx, ipady=ipady, padx=padx, pady=pady, sticky=E + W)
            Grid.columnconfigure(frames[2], 2, weight=1)
            budget = StringVar()
            top_up_entry = Entry(frames[2], textvariable=budget, font=font2, width=int(width / 3), bg='green')

            discount_frame = Frame(frames[3], bg='purple')
            Label(frames[3], text='Discount', font=font1, width=width, bg='red') \
                .grid(row=0, column=0, ipadx=ipadx, ipady=ipady, padx=padx, pady=pady)
            var[3].set("%")
            opt_menu_1 = OptionMenu(discount_frame, var[3], "%", "£")
            opt_menu_1.config(font=font2, bg='green')
            opt_menu_1.nametowidget(opt_menu_1.menuname).configure(font=font2, bg='green')
            opt_menu_1.grid(row=0, column=0, pady=pady * 2, sticky=N + S)
            discount_amount = Entry(discount_frame, textvariable=var[4], font=font2, width=int(width / 3), bg='green')
            discount_amount.grid(row=0, column=1, pady=pady * 2, sticky=N + S)
            Grid.rowconfigure(discount_frame, 0, weight=1)
            time_period_frame_setter(frames[3], discount_frame)

            spending_limit_frame = Frame(frames[4], bg='purple')
            Label(frames[4], text='Spending Limit', font=font1, width=width, bg='red') \
                .grid(row=0, column=0, ipadx=ipadx, ipady=ipady, padx=padx, pady=pady)
            Grid.columnconfigure(spending_limit_frame, 1, weight=1)
            Label(spending_limit_frame, text='£', font=font2, bg='green') \
                .grid(row=0, column=0, pady=pady * 2, sticky=N + S)
            Entry(spending_limit_frame, textvariable=var[7], font=font2, width=int(width / 3), bg='green')\
                .grid(row=0, column=1, pady=pady * 2, sticky=N + S)
            Label(spending_limit_frame, text='per', font=font2, width=int(width / 3), bg='green')\
                .grid(row=0, column=2, pady=pady * 2, sticky=N + S)
            var[8].set("purchase")
            opt_menu_3 = OptionMenu(spending_limit_frame, var[8], "purchase", "day", "week", "month")
            opt_menu_3.config(font=font2, bg='green')
            opt_menu_3.nametowidget(opt_menu_3.menuname).configure(font=font2, bg='red')
            opt_menu_3.grid(row=0, column=3, pady=pady * 2, sticky=N + S)
            Grid.rowconfigure(spending_limit_frame, 0, weight=1)
            time_period_frame_setter(frames[4], spending_limit_frame)

            sub_zero_frame = Frame(frames[5], bg='purple')
            Label(frames[5], text='Sub-Zero Allowance', font=font1, width=width, bg='red') \
                .grid(row=0, column=0, ipadx=ipadx, ipady=ipady, padx=padx, pady=pady)
            Label(sub_zero_frame, text='£', font=font2, bg='green') \
                .grid(row=0, column=0, pady=pady * 2, sticky=N + S)
            Entry(sub_zero_frame, textvariable=var[9], font=font2, width=int(width / 3), bg='green') \
                .grid(row=0, column=1, ipadx=ipadx, ipady=ipady, pady=pady * 2, sticky=N + S)
            Grid.rowconfigure(sub_zero_frame, 0, weight=1)
            time_period_frame_setter(frames[5], sub_zero_frame)

            Label(frames[6], text='Notes', font=font1, width=width, bg='red') \
                .grid(row=0, column=0, ipadx=ipadx, ipady=ipady, padx=padx, pady=pady)
            Entry(frames[6], textvariable=var[10], font=font2, width=int(width / 3), bg='green') \
                .grid(row=0, column=1, ipadx=ipadx, ipady=ipady, padx=padx, pady=pady, sticky=E + W)
            Grid.columnconfigure(frames[6], 1, weight=1)

        data_valid = BooleanVar()
        if info is not None:
            def edit():  # for the sake of binding the enter key
                self.data_deleter(table, self.get_columns(table)[0], info[0])
                data_valid.set(self.data_appender(table, [item.get() for item in var]))
                self.data_appender(table, [item for item in info[1:-1]]) if not data_valid.get() else caller(page_num)

            delete_btn = Button(center_frame, text="Delete", font=font1, bg="orange", width=width,
                                command=lambda: self.combine_funcs(
                                    self.data_deleter(table, self.get_columns(table)[0], info[0]), caller(page_num)))
            delete_btn.grid(row=i, column=0, ipadx=ipadx, ipady=ipady, padx=padx, pady=pady, sticky=E + W)

            edit_btn = Button(center_frame, text="Edit", font=font1, bg="orange", width=width,
                              command=lambda: edit())
            edit_btn.grid(row=i, column=1, ipadx=ipadx, ipady=ipady, padx=padx, pady=pady, sticky=E + W)

            for j in range(len(var)):
                column_name = self.get_columns(table)[j + 1]

                if column_name in ['f_name', 'l_name']:
                    var[j].set(info[j + 1])
                elif column_name in ['budget', 'discount_2', 'spending_limit_1', 'sub_zero_allowance']:
                    try:
                        var[j].set("£{:.2f}".format(float(info[j + 1])))
                    except ValueError:  # in case of empty string (can't float nothing)
                        var[j].set("£{:.2f}".format(float()))
                elif column_name == 'discount_1':
                    var[j].set(info[j + 1] if info[j + 1] in ['£', '%'] else '%')
                else:
                    var[j].set(info[j + 1])

            self.delete.append(info[0])
        else:
            def add():  # for the sake of binding the enter key
                caller(page_num) if self.data_appender(table, [item.get() for item in var]) else None

            cancel_btn = Button(center_frame, text="Cancel", font=font1, bg="orange", width=width,
                                command=lambda: caller(page_num))
            cancel_btn.grid(row=i, column=0, ipadx=ipadx, ipady=ipady, padx=padx, pady=pady, sticky=E + W)

            add_btn = Button(center_frame, text="Add", font=font1, bg="orange", width=width,
                             command=lambda: add())
            add_btn.grid(row=i, column=1, ipadx=ipadx, ipady=ipady, padx=padx, pady=pady, sticky=W + E)

        for i in range(len(self.get_columns(table)[1:-1]) + 1):
            Grid.rowconfigure(center_frame, i, weight=1)
        Grid.columnconfigure(center_frame, 0, weight=1)
        Grid.columnconfigure(center_frame, 1, weight=1)
        Grid.columnconfigure(center_frame, 2, weight=0)
        Grid.columnconfigure(center_frame, 3, weight=0)

    def get_columns(self, table):
        self.cursor.execute('SELECT * FROM {}'.format(table))
        return [description[0] for description in self.cursor.description]

    def data_deleter(self, table, column_name, item_id):
        self.cursor.execute("""DELETE FROM {} WHERE {} = ?;""".format(table, column_name), (item_id,))
        self.connection.commit()
        
    def data_appender(self, table, *args, silence=False):
        # appends given data into database but first checks for validity including if item is duplicate
        items = self.table_reader(table)
        code, data = self.account_data_validator(args[0], table)

        if code != 0:
            if not silence:
                tkinter.messagebox.showerror("Data Validity Error",
                                             "There is a problem with the entered data.\n\nPlease ensure that no symbol"
                                             "s are used for the name entries and that no symbols nor letters are used "
                                             "for the budget, daily limit and discount entries.\n\nPlease ensure that A"
                                             "LL entries are filled in.")
            return False

        duplicate = False
        for item in items:
            if data[0] == item[1]:
                if table == 'accounts' and data[1] != item[2]:
                    continue
                if not silence:
                    tkinter.messagebox.showerror("Duplicate",
                                                 "Entry already exists!\n\nPlease alter the name to continue.")
                return False

        if not duplicate:
            num_of_vals = str()
            for _ in range(len(self.get_columns(table)) - 1):
                num_of_vals += '?, '
            num_of_vals = num_of_vals[:-2]

            values = list()
            [values.append(val) for val in data], values.append(datetime.datetime.now())

            self.cursor.execute(
                "INSERT INTO {} VALUES (NULL, {});".format(table, num_of_vals), values)
            self.connection.commit()

        return True

    def get_accounts(self):
        self.cursor.execute("""SELECT * FROM accounts ORDER BY l_name, f_name;""")
        return self.cursor.fetchall()

    def csv_reader(self, csv_address, depth=2):  # imports csv and breaks it up into a returned list
        try:
            with open(csv_address, 'r', encoding="UTF-8") as file:
                    file = file.read()
            csv = file.split('\n')
            if depth == 2:
                for i in range(len(csv)):
                    csv[i] = csv[i].split(',')
                if csv[-1][0] == '':
                        csv = csv[:-1]
        except FileNotFoundError:
            csv = ''
        return csv

    def account_data_validator(self, data, table):  # verifies validity of data; returns the input data
        # (or, if possible, amended input data) as well as a code to identify whether the data is valid or if there is
        # an error (and if so, what that error is)

        # ensures the right number of items are in the data array (used for importing)
        size = len(self.get_columns(table)[1:-1])
        if len(data) < 2:
            return False
        while len(data) > size:
            del data[-1]
        while len(data) < size:
            data.append('')

        code = 0

        for i in range(len(data)):
            column_name = self.get_columns(table)[i + 1]

            if column_name in ['f_name', 'l_name']:
                if data[i] == '':
                    code = 1  # missing first / last name
                for char in data[i]:
                    if not (char.lower() in self.letters or char in self.numbers or char in '_- '):
                        code = 2  # invalid char used in name

            if column_name in ['budget', 'discount_2', 'spending_limit_1', 'sub_zero_allowance']:
                if str(data[i]).count('.') > 1:
                    code = 3  # multiple decimal places used
                for symbol in '£$%':  # remove above symbols because numbers are stored without them
                    data[i] = str(data[i]).replace(symbol, '')
                if data[i] == '':  # if just left empty
                    continue
                for char in data[i]:
                    if not (char in self.numbers or char == '.'):
                        code = 4  # only numbers can be used (and optional single decimal place)

            if data[i] == '':
                if column_name == 'discount_1':
                    data[i] = '%'
                if column_name == 'discount_4':
                    data[i] = 'week(s)'
                if column_name == 'spending_limit_2':
                    data[i] = 'purchase'


        return code, data

    def importer(self, csv_address, table):  # imports data from external csv file to a local csv file
        try:  # sort out if user cancels looking for csv address
            csv = self.csv_reader(csv_address)

            for i in range(len(csv)):
                csv[i][0] = csv[i][0].lower().capitalize()
                csv[i][1] = csv[i][1].lower().capitalize()

            for i in range(len(csv)):  # send data for validation
                try:
                    code, csv[i] = self.account_data_validator(csv[i], table)
                except IndexError:
                    pass

            # remove invalid items such as empty or False items
            for _ in range(csv.count('')):
                csv.remove('')
            invalid_accounts = int()
            for _ in range(csv.count(False)):
                csv.remove(False)
                invalid_accounts += 1

            # imports into given account
            success = int()
            for item in csv:
                success += self.data_appender(table, item, silence=True)

            extra_msg = "\n\nThe remaining {} were not imported either because they were duplicates or because the " \
                        "data is not in the appropriate order."
            tkinter.messagebox.showinfo("Import Results",
                                        "Out of all {} found row(s) in the csv {} were successfully imported.{}".format(
                                            len(csv), success, extra_msg.format(len(csv) - success)
                                            if success < len(csv) else ""))

        except TypeError:
            pass

    def page_populator(self, frame, items, page, table, caller):  # populates the given frame with the given items up to
        # a hardcoded limit for any given page
        for widget in frame.winfo_children():
            widget.destroy()

        offset = (page - 1) * self.page_items_width * self.page_items_height
        btn, i = dict(), int()

        for j in range(self.page_items_height):
            Grid.rowconfigure(frame, j, weight=1)
            for k in range(self.page_items_width):
                if j == 0:
                    Grid.columnconfigure(frame, k, weight=1)
                try:
                    btn[i] = Button(frame, text="{} {}".format(items[i+offset][1], items[i+offset][2])
                                                if table == 'accounts' else "{}".format(items[i+offset][1]),
                                    font=("Calibri", "14", "bold"), width=6, height=2,
                                    command=lambda item=items[i+offset]: self.item_form(1, page, table, caller, item)
                                    if caller != self.shop else caller(user=item))
                    btn[i].grid(row=j, column=k, padx=15, pady=5, sticky=E+W)
                except IndexError:
                    break
                i += 1

    def products(self, page_num=1):  # provides the appropriate data for the setup_window_generator to generate the
        # products window (see the generator itself for functionality)

        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.setup_window_generator(page_num, 'products', self.item_form, self.table_reader, self.products)

    def table_reader(self, table, *orders):  # loads all items from given table into a dictionary, however, it first
        # files the list down according to any search terms, sorts them alphabetically according to given columns and
        # then returns them.
        # Function starts by building an SQL search query which must have it's syntax exact and then procedes to execute
        # the query

        sql_command, search, order_by = """SELECT * FROM {};""".format(table), '', ''

        for char in self.search:
            search += char
        try:
            search = search[:-1] if search[-1] == ' ' else search
        except IndexError:
            pass

        for arg in orders:
            if arg is not None:
                order_by += '\"' + arg + '\", '
        order_by = order_by[:-2]

        if search != '':
            sql_command = sql_command[:-1]
            sql_command += ' WHERE '

            for _ in range(search.count(' ') + 1):
                sql_command += '\"{}\" LIKE ? OR '.format('First Name' if table == 'accounts' else 'Product Name')
                sql_command = sql_command + '\"Last Name\" LIKE ? OR ' if table == 'accounts' else sql_command
            sql_command = sql_command[:-4] + ';'

        if order_by != '':
            sql_command = sql_command[:-1]
            sql_command += ' ORDER BY ' + order_by + ';'

        if search != '':
            search_ = ['%' + search.split(' ')[i] + '%' for i in range(search.count(' ') + 1)]
            search = [search_[i//2] for i in range(len(search_)*2)] if table == 'accounts' else search_

            # print('sql_command:', sql_command)
            # print('search', search)

            self.cursor.execute(sql_command, search)
        else:
            self.cursor.execute(sql_command)

        return self.cursor.fetchall()

    def combine_funcs(*funcs):  # this function is used to allow buttons to call multiple functions since they can
        # otherwise only call one; this function is the function called by the button and it can input as the parameters
        # to this function whichever other functions (and however many)
        def combined_func(*args, **kwargs):
            for f in funcs:
                f(*args, **kwargs)
        return combined_func


start = TuckProgram()
