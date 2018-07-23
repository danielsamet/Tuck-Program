from tkinter import *
from tkinter import ttk, messagebox, filedialog
from db_interface import *
import date_picker
from datetime import datetime, timedelta
from math import ceil
from accounts import Account
from products import Product
from transaction import Transaction
import db_interface
import inherit_parent
import ctypes.wintypes

"""The code below is somewhat of a mess as it was built in a hurry for it's first usage (don't judge me by it!)"""


class GUI:
    def __init__(self):
        CSIDL_PERSONAL = 5  # My Documents
        SHGFP_TYPE_CURRENT = 0  # Get current, not default value

        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)

        path = buf.value

        db_interface.path, inherit_parent.path = path, path

        prep_db()

        root = Tk()

        root.state('zoomed')

        width, height = 1000, 700
        root.minsize(width, height)

        self.background_bg = "grey50"
        top_bar_bg = self.background_bg
        top_bar_btn_bg = "DarkOrange2"
        main_frame_bg = self.background_bg
        self.font_name = "Calibri"

        top_bar = Frame(root, bg=top_bar_bg)
        top_bar.grid(row=0, column=0, sticky=E + W)

        Grid.columnconfigure(root, 0, weight=1)

        self.back_btn = Button(top_bar, text="<--", bg=top_bar_btn_bg, font=(self.font_name, 20, "bold"), width=10,
                               height=2)
        self.back_btn.grid(row=0, column=0, sticky=W)

        self.title = StringVar()
        title_lbl = Label(top_bar, textvariable=self.title, font=(self.font_name, 54, "bold"), bg=top_bar_bg)
        title_lbl.grid(row=0, column=1)

        home_btn = Button(top_bar, text="HOME", bg=top_bar_btn_bg, font=(self.font_name, 20, "bold"), width=10,
                          height=2, command=lambda: self.main_menu())
        home_btn.grid(row=0, column=2, sticky=E)

        Grid.columnconfigure(top_bar, 0, weight=1), Grid.columnconfigure(top_bar, 1, weight=2)
        Grid.columnconfigure(top_bar, 2, weight=1)

        self.main_frame = Frame(root, bg=main_frame_bg)
        self.main_frame.grid(row=1, column=0, sticky=N + E + W + S)

        Grid.rowconfigure(root, 0, weight=0), Grid.rowconfigure(root, 1, weight=1)

        estyle = ttk.Style()  # style is for the setting of date_picker entry bg
        estyle.element_create("plain.field", "from", "clam")
        estyle.layout("EntryStyle.TEntry",
                      [('Entry.plain.field',
                        {'children': [('Entry.background', {'children': [('Entry.padding',
                                                                          {'children': [('Entry.textarea',
                                                                                         {'sticky': 'nswe'})],
                                                                           'sticky': 'nswe'})],
                                                            'sticky': 'nswe'})],
                         'border': '2', 'sticky': 'nswe'})])
        estyle.configure("EntryStyle.TEntry",
                         fieldbackground="grey85")

        self.items_page = IntVar()
        self.items_page.set(1)

        self.transactions_page = IntVar()
        self.transactions_page.set(1)

        self.main_menu()

        root.mainloop()

    def main_menu(self):
        self._frame_reset(self.main_frame)
        self.back_btn.config(command=None)
        self.title.set("Tuck Shop")

        font, bg = (self.font_name, 28, "bold"), "DarkOrange2"
        setup_btn = Button(self.main_frame, text="SETUP", bg=bg, font=font, width=18, height=3,
                           command=lambda: self.setup())
        setup_btn.grid(row=0, column=0)

        transaction_btn = Button(self.main_frame, text="SHOP", bg=bg, font=font, width=18, height=3,
                                 command=lambda: self.transactions())
        transaction_btn.grid(row=0, column=1)

        transaction_btn = Button(self.main_frame, text="TRACK", bg=bg, font=font, width=18, height=3,
                                 command=lambda: self.track())
        transaction_btn.grid(row=0, column=2)

        Grid.columnconfigure(self.main_frame, 0, weight=1), Grid.columnconfigure(self.main_frame, 1, weight=1)
        Grid.columnconfigure(self.main_frame, 2, weight=1)

        Grid.rowconfigure(self.main_frame, 0, weight=1)

        Label(self.main_frame, text="By Daniel Samet", font=("Calibri", 13, "bold"), bg=self.background_bg).grid(
            row=1, column=0, sticky=W)
        Button(self.main_frame, text="EXPORT", font=("Calibri", 13, "bold"), bg="orange",
               command=lambda: self.export()).grid(row=1, column=1, ipadx=10, pady=5)
        Label(self.main_frame, text="V1.0", font=("Calibri", 13), bg=self.background_bg).grid(row=1, column=2, sticky=E)

    def setup(self):
        self._frame_reset(self.main_frame)
        self.back_btn.config(command=lambda: self.main_menu())
        self.title.set("Tuck Shop")

        font, bg = (self.font_name, 28, "bold"), "DarkOrange2"

        accounts_btn = Button(self.main_frame, text="ACCOUNTS", bg=bg, font=font, width=18, height=3,
                              command=lambda: self.accounts())
        accounts_btn.grid(row=0, column=0)

        products_btn = Button(self.main_frame, text="PRODUCTS", bg=bg, font=font, width=18, height=3,
                              command=lambda: self.products())
        products_btn.grid(row=0, column=1)

        Grid.columnconfigure(self.main_frame, 0, weight=1), Grid.columnconfigure(self.main_frame, 1, weight=1)
        Grid.rowconfigure(self.main_frame, 0, weight=1)

        self.items_page.set(1)

    def accounts(self):
        self.page_populator("Accounts")

    def account(self, account_info=None):
        self.item_populator(self.accounts, "Account", item_info=account_info)

    def products(self):
        self.page_populator("Products")

    def product(self, product_info=None):
        self.item_populator(self.products, "Product", item_info=product_info)

    def item_populator(self, caller, caller_name, item_info):

        self._frame_reset(self.main_frame)
        self.back_btn.config(command=lambda: caller())

        account = True if caller_name == "Account" else False

        if item_info is not None:
            name = " ".join(item_info[1:3]) if account else item_info[1]
            self.title.set("{0}s - {1}".format(caller_name, name))
        else:
            self.title.set("New {0}".format(caller_name))

        Grid.columnconfigure(self.main_frame, 0, weight=1)

        if item_info is not None:
            item = Account(account_id=item_info[0]) if account else Product(product_id=item_info[0])

        font1, font2 = (self.font_name, 18, "bold"), (self.font_name, 18)
        row = int()

        def _create_basic_frame(lbl_txt):
            nonlocal row

            frame = Frame(self.main_frame, bg=self.background_bg)
            frame.grid(row=row, column=0, pady=10, sticky=E + W)
            Grid.rowconfigure(self.main_frame, row, weight=1)
            [Grid.columnconfigure(frame, i, weight=1) for i in range(3)]
            Label(frame, text=lbl_txt, font=font1, width=20, bg=self.background_bg, anchor=E).grid(row=0, column=0,
                                                                                                   sticky=W)
            centre_frame = Frame(frame, bg=self.background_bg)
            centre_frame.grid(row=0, column=1, sticky=E + W)
            Grid.columnconfigure(frame, 1, weight=100)
            if item_info is not None:
                Button(frame, text="See History", font=font2, bg='red', width=15,
                       command=lambda: self.display_history(lbl_txt, item_info[0], self.item_populator, caller,
                                                            caller_name, item_info)).grid(row=0, column=2, sticky=E)

            row += 1

            return centre_frame

        def top_up(save=True):
            try:
                budget_amount.set("£{0:.2f}".format(float(budget_amount.get()[1:]) + float(top_up_amount.get())))
                if save:
                    item.top_up(amount=float(top_up_amount.get()))
                    item_info[3] = float(budget_amount.get().strip("£"))
                    messagebox.showinfo("Note", "Note that this topping up has auto saved the quantity!")
            except ValueError:
                messagebox.showerror("Top Up Error", "Amount must be a valid number.")

        def add_quantity(to_update, amount, save=True):
            try:
                to_update.set("{0}".format(int(to_update.get()) + int(amount.get())))
                if save:
                    item.top_up(amount=int(amount.get()))
                    item_info[5] = int(to_update.get())
                    messagebox.showinfo("Note", "Note that this topping up has auto saved the quantity!")
            except ValueError:
                messagebox.showerror("Top Up Error", "Amount must be a valid number.")
            amount.set("")

        def update_amount(to_update, amount):
            try:
                to_update.set("£{0:.2f}".format(float(amount.get().strip("£"))))
            except ValueError:
                messagebox.showerror("Update Error", "Amount must be a valid number.")
            amount.set("")

        def save_account(result):
            nonlocal item

            if result[0]:  # details are valid
                update_f_name, update_l_name, update_top_ups, update_notes = bool(), bool(), bool(), bool()
                if item_info is not None:  # update or new
                    if item_info[1] != f_name.get():
                        update_f_name = True
                    if item_info[2] != l_name.get():
                        update_l_name = True
                    top_up_total = float(budget_amount.get().strip("£")) - float(item_info[3])
                    if float(item_info[3]) != float(budget_amount.get().strip("£")):
                        update_top_ups = True
                    if item_info[4] != notes.get():
                        update_notes = True
                else:
                    if budget_amount.get()[1:] != "£0.00":
                        update_top_ups = True
                    top_up_total = float(budget_amount.get()[1:])
                    if notes.get() != "":
                        update_notes = True

                    item = Account()
                    item.add_account(f_name.get(), l_name.get())

                # process save as necessary
                if update_f_name:
                    item.update_details(f_name=f_name.get())
                if update_l_name:
                    item.update_details(l_name=l_name.get())
                if update_top_ups:
                    item.top_up(amount=top_up_total)
                if update_notes:
                    item.update_details(notes=notes.get())

                for discount_ in active_discounts:
                    saved_discounts = [(discount_[1], "%" if discount_[2] == 0 else "£", discount_[3], discount_[4],
                                        discount_[5], discount_[6]) for discount_
                                       in get_account_conditions(account_id=item_info[0], discount=True)]
                    if discount_ not in saved_discounts:
                        insert_new("accounts_discounts", [item_info[0], discount_[0],
                                                          1 if discount_[1] == "£" else 0, discount_[2], discount_[3], 0,
                                                          datetime.now()])
                for limit_ in active_limits:
                    saved_limits = [(limit_[1:]) for limit_ in get_account_conditions(account_id=item_info[0],
                                                                                      spending_limit=True)]
                    if limit_ not in saved_limits:
                        insert_new("accounts_spending_limit", [item_info[0], limit_[0], limit_[1], limit_[2], limit_[3],
                                                               0, datetime.now()])
                for allowance_ in active_allowances:
                    saved_allowances = [(allowance_[1:]) for allowance_ in
                                        get_account_conditions(account_id=item_info[0], sub_zero_allowance=True)]
                    if allowance_ not in saved_allowances:
                        insert_new("accounts_sub_zero_allowance", [item_info[0], allowance_[0], allowance_[1],
                                                                   allowance_[2], 0, datetime.now()])

                self.accounts()
            else:
                messagebox.showinfo("Error Saving Item", "Could not save item due to the following error:\n\n{0}"
                                                         "".format(result[1]))

        def validate_account():

            try:
                float(budget_amount.get()[1:])
            except ValueError:
                return False, "Budget must be a valid number"

            if f_name.get() == "" or l_name.get() == "":
                return False, "Name cannot be empty"

            return True, ""

        def save_product():
            nonlocal item

            result = validate_product()

            top_up_total = float()

            if result[0]:  # details are valid
                update_name, update_supplier, update_cost_price, update_sale_price, update_quantity, update_notes = \
                    bool(), bool(), bool(), bool(), bool(), bool()
                if item_info is not None:  # update
                    if item_info[1] != p_name.get():
                        update_name = True
                    if item_info[2] != supplier.get() and not (item_info[2] is None and supplier.get() == ""):
                        update_supplier = True
                    if item_info[3] != cost_amount.get():
                        update_cost_price = True
                    if item_info[4] != price_amount.get():
                        update_sale_price = True
                    top_up_total = int(quantity_amount.get()) - int(item_info[5])
                    if int(item_info[5]) != int(quantity_amount.get()):
                        update_quantity = True
                    if item_info[6] != notes.get():
                        update_notes = True
                else:  # new
                    if supplier.get() != "":
                        update_supplier = True
                    update_cost_price = True
                    if price_amount.get() != "£0.00":
                        update_sale_price = True
                    update_quantity = True
                    top_up_total = int(quantity_amount.get())  # under indented just to avoid IDE error message
                    if notes.get() != "":
                        update_notes = True

                    item = Product()
                    item.add_product(p_name=p_name.get())

                # process save as necessary
                if update_name:
                    item.update_details(name=p_name.get())
                if update_supplier:
                    item.update_details(supplier=supplier.get())
                if update_cost_price:
                    item.update_details(cost_price=float(cost_amount.get().strip("£")))
                if update_sale_price:
                    item.update_details(sale_price=float(price_amount.get().strip("£")))
                if update_quantity:
                    item.top_up(amount=int(top_up_total))
                if update_notes:
                    item.update_details(notes=notes.get())

                for discount_ in active_discounts:
                    saved_discounts = [(discount_[1], "%" if discount_[2] == 0 else "£", discount_[3], discount_[4],
                                        discount_[5], discount_[6]) for discount_
                                       in get_product_conditions(product_id=item_info[0], discount=True)]
                    if discount_ not in saved_discounts:
                        insert_new("products_discount", [item_info[0], discount_[0],
                                                         1 if discount_[1] == "£" else 0, discount_[2], discount_[3], 0,
                                                         datetime.now()])

                for limit_ in active_limits:
                    saved_limits = [(limit_[1:]) for limit_ in get_product_conditions(product_id=item_info[0],
                                                                                      purchase_limit=True)]
                    if limit_ not in saved_limits:
                        insert_new("products_spending_limit", [item_info[0], limit_[0], limit_[1], limit_[2], limit_[3],
                                                               0, datetime.now()])

                for offer_ in active_offers:
                    saved_offers = [(offer_[1:]) for offer_ in get_product_conditions(product_id=item_info[0],
                                                                                      offer=True)]
                    if offer_ not in saved_offers:
                        insert_new("products_offers", [item_info[0], offer_[0], offer_[1], offer_[2], offer_[3],
                                                       offer_[4], 0, datetime.now()])

                self.products()
            else:
                messagebox.showinfo("Error Saving Item", "Could not save item due to the following error:\n\n{0}"
                                                         "".format(result[1]))

        def validate_product():
            def update_error(name):
                return False, "Please update the {0} before clicking save (alternatively, simply clear the entry" \
                              "".format(name)

            if amount_to_update_c.get() != "":
                return update_error("cost price")
            elif price_amount.get() == "£0.00":
                return False, "Sale Amount cannot be 0. Please update with a positive value."
            elif amount_to_update_p.get() != "":
                return update_error("sale price")
            elif amount_to_update_q.get() != "":
                return update_error("quantity")

            return True, ""

        def display_conditions(conditions, page=1, discount_=False, limit_=False, allowance_=False,
                               p_discount=False, p_limit=False, p_offer=False):

            def add_datetime_entries(frame_, date, hour, min_):
                date_picker.Datepicker(frame_, datevar=date, font=font2, entrywidth=10,
                                       entrystyle="EntryStyle.TEntry").grid(row=0, column=1)
                hours = OptionMenu(frame_, hour, *[str("{0:02d}".format(num)) for num in range(0, 24)])
                hours.config(font=font2)
                hours.nametowidget(hours.menuname).configure(font=(self.font_name, 16))
                hours.grid(row=0, column=2)
                mins = OptionMenu(frame_, min_, *[str("{0:02d}".format(num)) for num in range(0, 60)])
                mins.config(font=font2)
                mins.nametowidget(hours.menuname).configure(font=(self.font_name, 16))
                mins.grid(row=0, column=3)

            def add_from(from_frame, _from, from_date, from_hour, from_min):
                [widget.destroy() for widget in from_frame.winfo_children()]

                Label(from_frame, text="From {}".format(_from), font=font2, bg=self.background_bg).grid(row=0, column=0)
                if _from is "":
                    from_hour.set("00"), from_min.set("00")
                    add_datetime_entries(from_frame, from_date, from_hour, from_min)

            def add_until(until, until_frame, length, _for, until_date, until_hour, until_min):
                [widget.destroy() for widget in until_frame.winfo_children()]

                Label(until_frame, bg=self.background_bg, text="{}".format(
                    until if until == "Indefinitely" else "For A Duration Of " if until == "time" else "Until"),
                      font=font2).grid(row=0, column=0)
                if until == "time":
                    Entry(until_frame, textvariable=length, font=font2, width=2).grid(row=0, column=1, padx=10)
                    _for.set("day(s)")
                    _opt_menu = OptionMenu(until_frame, _for, "hour(s)", "day(s)", "week(s)", "month(s)", "year(s)")
                    _opt_menu.config(font=font2)
                    _opt_menu.nametowidget(_opt_menu.menuname).configure(font=font2)
                    _opt_menu.grid(row=0, column=2)
                elif until == "until":
                    until_hour.set("00"), until_min.set("00")
                    add_datetime_entries(until_frame, until_date, until_hour, until_min)

            def add_from_():
                self._empty_frame(from_frame)

                Button(from_frame, text="Now", font=font2,
                       command=lambda: self.combine_funcs(
                           add_from(from_frame, "Now", *froms),
                           Button(from_frame, text="Reset", font=font2, bg='red', command=lambda: add_from_()
                                  ).grid(row=0, column=1)),
                       bg=from_bg).grid(row=0, column=0)
                Button(from_frame, text="Specific Date/Time", font=font2,
                       command=lambda: self.combine_funcs(
                           add_from(from_frame, "", *froms),
                           Button(from_frame, text="Reset", font=font2, bg='red', command=lambda: add_from_()
                                  ).grid(row=0, column=4)),
                       bg=from_bg).grid(row=0, column=1)

            def add_until_():
                self._empty_frame(until_frame)

                Button(until_frame, text="Indefinitely", font=font2, bg=until_bg,
                       command=lambda: self.combine_funcs(
                           add_until("Indefinitely", until_frame, length, _for, *untils),
                           Button(until_frame, text="Reset", bg='red', font=font2, command=lambda: add_until_()
                                  ).grid(row=0, column=1))).grid(row=0, column=0)
                Button(until_frame, text="For Given Time", font=font2, bg=until_bg,
                       command=lambda: self.combine_funcs(
                           add_until("time", until_frame, length, _for, *untils),
                           Button(until_frame, text="Reset", bg='red', font=font2, command=lambda: add_until_()
                                  ).grid(row=0, column=4))).grid(row=0, column=1)
                Button(until_frame, text="Until Given Date", font=font2, bg=until_bg,
                       command=lambda: self.combine_funcs(
                           add_until("until", until_frame, length, _for, *untils),
                           Button(until_frame, text="Reset", font=font2, bg='red', command=lambda: add_until_()
                                  ).grid(row=0, column=4))).grid(row=0, column=2)

            def calc_dates(dates, length, _for):

                from_date = dates[0].get() + " {0}:{1}:00".format(dates[1].get(), dates[2].get()) \
                    if dates[0].get() != "" else str(datetime.now())[:19]

                if dates[3].get() == "":
                    if length.get() != "":
                        fors = {"hour(s)": timedelta(hours=1), "day(s)": timedelta(days=1),
                                "week(s)": timedelta(weeks=1), "month(s)": timedelta(weeks=4),
                                "year(s)": timedelta(weeks=52)}
                        period = int(length.get()) * fors[_for.get()]
                        until_date = str(datetime.strptime(from_date, "%Y-%m-%d %H:%M:%S") + period)
                    else:
                        until_date = ""
                else:
                    until_date = dates[3].get() + " {0}:{1}:00".format(dates[4].get(), dates[5].get())

                return from_date, until_date

            def call_yourself(page_=page):
                display_conditions(get_discounts() if discount_ else get_limits() if limit_ else get_allowances()
                                   if allowance_ else get_p_discounts() if p_discount else get_p_limits() if p_limit
                                   else get_p_offers(),
                                   page=page_, discount_=discount_, limit_=limit_, allowance_=allowance_,
                                   p_discount=p_discount, p_limit=p_limit, p_offer=p_offer)

            def get_formmated_dates():
                return [datetime.strptime(date, "%Y-%m-%d %H:%M:%S") if date != "" else date
                        for date in calc_dates((froms[0], froms[1], froms[2], untils[0], untils[1], untils[2]), length,
                                               _for)]

            if item_info is not None:

                self._frame_reset(self.main_frame)
                self.back_btn.config(command=lambda: self.item_populator(caller, caller_name, item_info))

                # titles
                title_width, title_padx, title_pady = 10, 10, 10

                if p_offer:
                    title_padx = 0
                    Label(self.main_frame, text="Buy X", font=font1, bg=self.background_bg, width=title_width
                          ).grid(row=0, column=0, padx=title_padx, pady=title_pady, sticky=E + W)
                    Label(self.main_frame, text="Get Y", font=font1, bg=self.background_bg, width=title_width
                          ).grid(row=0, column=1, padx=title_padx, pady=title_pady, sticky=E + W)
                    Label(self.main_frame, text="Z Off", font=font1, bg=self.background_bg, width=title_width
                          ).grid(row=0, column=2, padx=title_padx, pady=title_pady, sticky=E + W)
                    Label(self.main_frame, text="Type", font=font1, bg=self.background_bg, width=title_width
                          ).grid(row=0, column=3, padx=title_padx, pady=title_pady, sticky=E + W)
                    col = 4
                else:
                    Label(self.main_frame, text="Amount (£)" if p_limit or limit_ or allowance_ else "Amount",
                          font=font1, bg=self.background_bg, width=title_width).grid(row=0, column=0, padx=title_padx,
                                                                                     pady=title_pady)
                    col = 1

                    if discount_ or limit_ or p_discount or p_limit:
                        Label(self.main_frame, text="Per" if limit_ or p_limit else "Type", font=font1,
                              bg=self.background_bg, width=title_width).grid(row=0, column=1, padx=title_padx,
                                                                             pady=title_pady, sticky=E + W)
                        col = 2

                Label(self.main_frame, text="Active From", font=font1, bg=self.background_bg, width=title_width).grid(
                    row=0, column=col, padx=title_padx, pady=title_pady, sticky=E + W)
                Label(self.main_frame, text="Active Until", font=font1, bg=self.background_bg, width=title_width).grid(
                    row=0, column=col+1, padx=title_padx, pady=title_pady, sticky=E + W)

                [Grid.columnconfigure(self.main_frame, i, weight=1) for i in range(col + 2)]

                row_ = int(1)

                # list items
                total_conditions, condition_limit = len(conditions), 10
                conditions = conditions[(page - 1) * condition_limit:page * condition_limit] \
                    if total_conditions >= page * condition_limit else conditions[(page - 1) * condition_limit:]

                bgs, width, padx, pady, sticky = ["grey60", "grey40"], 9, 0, 2, E + W
                for condition in conditions:
                    bg = bgs[conditions.index(condition) % 2]

                    Label(self.main_frame, text=condition[0], font=font2, bg=bg, width=width).grid(
                        row=row_, column=0, padx=padx, pady=pady, sticky=sticky)
                    if discount_ or limit_ or p_discount or p_limit:
                        Label(self.main_frame, text=condition[1], font=font2, bg=bg, width=width).grid(
                            row=row_, column=1, padx=padx, pady=pady, sticky=sticky)
                        from_date, until_date = condition[2], condition[3]
                    elif p_offer:
                        Label(self.main_frame, text=condition[1], font=font2, bg=bg, width=width).grid(
                            row=row_, column=1, padx=padx, pady=pady, sticky=sticky)
                        Label(self.main_frame, text=condition[2], font=font2, bg=bg, width=width).grid(
                            row=row_, column=2, padx=padx, pady=pady, sticky=sticky)
                        Label(self.main_frame, text="%" if condition[3] == 0 else "£", font=font2, bg=bg,
                              width=width).grid(row=row_, column=3, padx=padx, pady=pady, sticky=sticky)
                        from_date, until_date = condition[4], condition[5]
                    else:
                        from_date, until_date = condition[1], condition[2]
                    until_date = "Indefinitely" if until_date == "" or until_date == 0 else until_date
                    Label(self.main_frame, text=from_date, font=font2, bg=bg, width=width).grid(
                        row=row_, column=col, padx=padx, ipadx=padx, pady=pady, sticky=sticky)
                    Label(self.main_frame, text=until_date, font=font2, bg=bg, width=width).grid(
                        row=row_, column=col + 1, padx=padx, pady=pady, sticky=sticky)

                    Button(self.main_frame, text="DELETE", bg='red2', font=font1, width=width,
                           command=lambda condition_=condition: self.combine_funcs(
                               item.delete_discount(condition_[-1]) if discount_ or p_discount
                               else item.delete_spending_limit(condition_[-1]) if limit_
                               else item.delete_sub_zero_allowance(condition_[-1]) if allowance_
                               else item.delete_purchase_limit(condition_[-1]) if p_limit
                               else item.delete_offer(condition_[-1]),
                               display_conditions(get_discounts() if discount_
                                                  else get_limits() if limit_
                                                  else get_allowances() if allowance_
                                                  else get_p_discounts() if p_discount
                                                  else get_p_limits() if p_limit
                                                  else get_p_offers(),
                                                  discount_=discount_, limit_=limit_, allowance_=allowance_,
                                                  p_discount=p_discount, p_limit=p_limit, p_offer=p_offer))
                           ).grid(row=row_, column=col + 2, padx=padx, pady=pady, sticky=sticky)

                    row_ += 1

                # new item
                item_vars = list()

                from_bg, until_bg = "firebrick1", "SlateBlue1"
                if p_offer:
                    width, padx = 5, 0

                    buy_get_off = list()
                    [buy_get_off.append(StringVar()) for _ in range(3)]
                    Entry(self.main_frame, font=font2, textvariable=buy_get_off[0], width=width).grid(
                        row=row_, column=0, padx=padx)
                    Entry(self.main_frame, font=font2, textvariable=buy_get_off[1], width=width).grid(
                        row=row_, column=1, padx=padx)
                    Entry(self.main_frame, font=font2, textvariable=buy_get_off[2], width=width).grid(
                        row=row_, column=2, padx=padx)

                    offer_type, offer_drop_down_ = self.create_type_dropdown(self.main_frame)
                    offer_drop_down_.grid(row=row_, column=3, padx=0, sticky=S)

                    item_vars.append(buy_get_off[0]), item_vars.append(buy_get_off[1]), item_vars.append(buy_get_off[2])
                    item_vars.append(offer_type)

                else:
                    amount = StringVar()
                    item_vars.append(amount)
                    Entry(self.main_frame, font=font2, textvariable=amount, width=10).grid(row=row_, column=0, padx=50)

                    if discount_ or limit_ or p_discount or p_limit:
                        if discount_ or p_discount:
                            discount_type_, discount_drop_down_ = self.create_type_dropdown(self.main_frame)
                            discount_drop_down_.grid(row=row_, column=1, padx=60, sticky=S)
                            item_vars.append(discount_type_)
                        else:
                            limit_per_, limit_drop_down_ = self.create_limit_drop_down(self.main_frame)
                            item_vars.append(limit_per_)
                            limit_drop_down_.grid(row=row_, column=1, padx=60, sticky=S)

                from_frame = Frame(self.main_frame, bg=self.background_bg)
                from_frame.grid(row=row_, column=col, sticky=S, padx=30)
                froms = [StringVar(), StringVar(), StringVar()]
                add_from_()

                until_frame = Frame(self.main_frame, bg=self.background_bg)
                until_frame.grid(row=row_, column=col+1, sticky=S, padx=30)
                untils = [StringVar(), StringVar(), StringVar()]
                length, _for = StringVar(), StringVar()
                add_until_()

                def check_fields_validity():
                    if not p_offer and (amount.get() == "" or not amount.get().isdigit()):
                        return True
                    if p_offer:
                        for item_ in buy_get_off:
                            if item_.get() == "" or not item_.get().replace('.', '', 1).isdigit() \
                                    or str(item_.get()) == "0":
                                return True

                    return False

                amount = StringVar() if "amount" not in locals() else amount
                too_many_msg = "Unfortunately, only one per item is supported at this time."

                Button(self.main_frame, text="ADD", bg='orange', font=font1, width=7,
                       command=lambda: self.combine_funcs(
                           item.add_discount(float(amount.get()), 1 if discount_type_.get() == "£" else 0,
                                             *get_formmated_dates())
                           if discount_ or p_discount else
                           item.add_spending_limit(float(amount.get()), limit_per_.get(), *get_formmated_dates())
                           if limit_ else
                           (item.add_sub_zero_allowance(float(amount.get()), *get_formmated_dates())
                            if len(conditions) == 0 else messagebox.showinfo("Too Many Allowances", too_many_msg))
                           if allowance_ else
                           item.add_purchase_limit(float(amount.get()), limit_per_.get(), *get_formmated_dates())
                           if p_limit else
                           item.add_offer(buy_get_off[0].get(), buy_get_off[1].get(), buy_get_off[2].get(),
                                          1 if offer_type.get() == "£" else 0, *get_formmated_dates())
                           if len(conditions) == 0 else messagebox.showinfo("Too Many Offers", too_many_msg),
                           call_yourself())
                       if not check_fields_validity()
                       else messagebox.showerror("Null Error",
                                                 "Ensure all fields are filled out with appropriate data.")
                       ).grid(row=row_, column=col + 2, sticky=S + E + W)

                page_scrolling_frame = Frame(self.main_frame, bg=self.background_bg)
                page_scrolling_frame.grid(row=row_ + 1, column=0, sticky=S, columnspan=5)
                Grid.rowconfigure(self.main_frame, row_ + 1, weight=1)

                total_pages = ceil(total_conditions/condition_limit) if total_conditions > 0 else 1
                bg = "sandy brown"

                if total_pages > 1:
                    Button(page_scrolling_frame, text="Previous", font=font2, bg=bg,
                           command=lambda: call_yourself(page-1) if page > 1 else None).grid(row=0, column=0)
                    Button(page_scrolling_frame, text="Next", font=font2, bg=bg,
                           command=lambda: call_yourself(page+1) if page < total_pages else None).grid(row=0, column=2)

                Label(page_scrolling_frame, text="Page {0} of {1}".format(page, total_pages), bg=self.background_bg,
                      font=font2).grid(row=0, column=1, padx=20)
            else:
                messagebox.showinfo("Adding Conditions", "In order to add a condition item you must first save the "
                                                         "account.")

        def get_discounts():
            discounts_ = list()

            for discount in get_account_conditions(account_id=item_info[0], discount=True):
                discounts_.append((discount[1], "%" if discount[2] == 0 else "£", discount[3], discount[4], discount[5],
                                   discount[6]))

            return discounts_

        def get_limits():
            limits_ = list()

            for limit in get_account_conditions(account_id=item_info[0], spending_limit=True):
                limits_.append((limit[1:]))

            return limits_

        def get_allowances():
            allowances_ = list()

            for allowance in get_account_conditions(account_id=item_info[0], sub_zero_allowance=True):
                allowances_.append((allowance[1:]))

            return allowances_

        def get_p_discounts():
            discounts_ = list()

            for discount in get_product_conditions(product_id=item_info[0], discount=True):
                discounts_.append((discount[1], "%" if str(discount[2]) == "0" else "£", discount[3], discount[4],
                                   discount[5], discount[6]))

            return discounts_

        def get_p_limits():
            limits_ = list()

            for limit in get_product_conditions(product_id=item_info[0], purchase_limit=True):
                limits_.append((limit[1:]))

            return limits_

        def get_p_offers():
            offers = list()

            for offer in get_product_conditions(product_id=item_info[0], offer=True):
                offers.append((offer[1:]))

            return offers

        if account:
            # account first name
            f_name_frame = _create_basic_frame("First Name")
            f_name = StringVar()
            Entry(f_name_frame, textvariable=f_name, font=font2).grid(row=0, column=0, sticky=W)

            # account last name
            l_name_frame = _create_basic_frame("Last Name")
            l_name = StringVar()
            Entry(l_name_frame, textvariable=l_name, font=font2).grid(row=0, column=0, sticky=W)

            # account budget and top up
            budget_frame = _create_basic_frame("Budget")
            budget_amount = StringVar()
            budget_amount.set("£0.00")
            budget_amount_label = Label(budget_frame, textvariable=budget_amount, font=font1, bg=self.background_bg)
            budget_amount_label.grid(row=0, column=0, sticky=W)
            top_up_amount = StringVar()
            top_up_amount.set("")
            top_up_entry = Entry(budget_frame, textvariable=top_up_amount, font=font2, width=6)
            top_up_entry.grid(row=0, column=1, sticky=W, padx=20)
            top_up_btn = Button(budget_frame, text="Top Up", bg='green', font=font2,
                                command=lambda: self.combine_funcs(top_up(save=False if item_info is None else True),
                                                                   top_up_amount.set("")))
            top_up_btn.grid(row=0, column=2, sticky=W)

            # account discounts
            active_discounts = list()
            active_discounts_btn = Button(_create_basic_frame("Discount"))
            active_discounts_btn.config(text="None Active", state=NORMAL, font=font1,
                                        command=lambda: display_conditions(active_discounts, discount_=True))
            active_discounts_btn.grid(row=0, column=0)

            # account spending limit
            active_limits = list()
            active_limits_btn = Button(_create_basic_frame("Spending Limit"))
            active_limits_btn.config(text="None Active", state=NORMAL, font=font1,
                                     command=lambda: display_conditions(active_limits, limit_=True))
            active_limits_btn.grid(row=0, column=0)

            # account sub zero allowances
            active_allowances = list()
            active_allowances_btn = Button(_create_basic_frame("Sub Zero Allowances"))
            active_allowances_btn.config(text="None Active", state=NORMAL, font=font1,
                                         command=lambda: display_conditions(active_allowances, allowance_=True))
            active_allowances_btn.grid(row=0, column=0)

            # accounts notes
            notes_frame = _create_basic_frame("Notes")
            notes = StringVar()
            Entry(notes_frame, textvariable=notes, font=(self.font_name, 16)).pack(fill=X)

            if item_info is not None:  # account already exists and thus in editing mode
                f_name.set(item_info[1])
                l_name.set(item_info[2])

                budget_amount.set("£{0:.2f}".format(item_info[3]))

                discounts = get_discounts()
                [active_discounts.append(discount) for discount in discounts]
                active_discounts_btn.config(state=NORMAL, text="{0} Active".format(len(discounts)))

                limits = get_limits()
                [active_limits.append(limit) for limit in limits]
                active_limits_btn.config(state=NORMAL, text="{0} Active".format(len(limits)))

                allowances = get_allowances()
                [active_allowances.append(allowance) for allowance in allowances]
                active_allowances_btn.config(state=NORMAL, text="{0} Active".format(len(allowances)))

                notes.set(item_info[4])

        else:
            # product Name
            p_name_frame = _create_basic_frame("Product Name")
            p_name = StringVar()
            Entry(p_name_frame, textvariable=p_name, font=font2).grid(row=0, column=0, sticky=W)

            # Product Supplier
            supplier_frame = _create_basic_frame("Supplier")
            supplier = StringVar()
            Entry(supplier_frame, textvariable=supplier, font=font2).grid(row=0, column=0, sticky=W)

            # Product Cost Price
            cost_frame = _create_basic_frame("Cost Price")
            cost_amount = StringVar()
            cost_amount.set("£0.00")
            cost_amount_label = Label(cost_frame, textvariable=cost_amount, font=font1, bg=self.background_bg)
            cost_amount_label.grid(row=0, column=0, sticky=W)
            amount_to_update_c = StringVar()
            amount_to_update_c.set("")
            update_entry = Entry(cost_frame, textvariable=amount_to_update_c, font=font2, width=6)
            update_entry.grid(row=0, column=1, sticky=W, padx=20)
            update_btn = Button(cost_frame, text="Update", bg='green', font=font2,
                                command=lambda: update_amount(cost_amount, amount_to_update_c))
            update_btn.grid(row=0, column=2, sticky=W)

            # Product Sale Price
            price_frame = _create_basic_frame("Sale Price")
            price_amount = StringVar()
            price_amount.set("£0.00")
            price_amount_label = Label(price_frame, textvariable=price_amount, font=font1, bg=self.background_bg)
            price_amount_label.grid(row=0, column=0, sticky=W)
            amount_to_update_p = StringVar()
            amount_to_update_p.set("")
            update_entry = Entry(price_frame, textvariable=amount_to_update_p, font=font2, width=6)
            update_entry.grid(row=0, column=1, sticky=W, padx=20)
            update_btn = Button(price_frame, text="Update", bg='green', font=font2,
                                command=lambda: update_amount(price_amount, amount_to_update_p))
            update_btn.grid(row=0, column=2, sticky=W)

            # Product Quantity
            quantity_frame = _create_basic_frame("Quantity")
            quantity_amount = StringVar()
            quantity_amount.set("0")
            quantity_amount_label = Label(quantity_frame, textvariable=quantity_amount, font=font1,
                                          bg=self.background_bg)
            quantity_amount_label.grid(row=0, column=0, sticky=W)
            amount_to_update_q = StringVar()
            amount_to_update_q.set("")
            update_entry = Entry(quantity_frame, textvariable=amount_to_update_q, font=font2, width=6)
            update_entry.grid(row=0, column=1, sticky=W, padx=20)
            update_btn = Button(quantity_frame, text="Update", bg='green', font=font2,
                                command=lambda: add_quantity(quantity_amount, amount_to_update_q,
                                                             save=False if item_info is None else True))
            update_btn.grid(row=0, column=2, sticky=W)

            # Product Purchase Limit
            active_limits = list()
            active_limits_btn = Button(_create_basic_frame("Purchase Limit"))
            active_limits_btn.config(text="None Active", state=NORMAL, font=font1,
                                     command=lambda: display_conditions(active_limits, p_limit=True))
            active_limits_btn.grid(row=0, column=0)

            # Product Discount
            active_discounts = list()
            active_discounts_btn = Button(_create_basic_frame("Discounts"))
            active_discounts_btn.config(text="None Active", state=NORMAL, font=font1,
                                        command=lambda: display_conditions(active_discounts, p_discount=True))
            active_discounts_btn.grid(row=0, column=0)

            # Product Offer
            active_offers = list()
            active_offers_btn = Button(_create_basic_frame("Offers"))
            active_offers_btn.config(text="None Active", state=NORMAL, font=font1,
                                     command=lambda: display_conditions(active_offers, p_offer=True))
            active_offers_btn.grid(row=0, column=0)

            # Product Notes
            notes_frame = _create_basic_frame("Product Notes")
            notes = StringVar()
            Entry(notes_frame, textvariable=notes, font=(self.font_name, 16)).pack(fill=X)

            if item_info is not None:  # account already exists and thus in editing mode
                p_name.set(item_info[1])

                supplier.set(item_info[2]) if item_info[2] is not None else None

                cost_amount.set("£{0:.2f}".format(item_info[3] if item_info[3] is not None else 0))
                price_amount.set("£{0:.2f}".format(item_info[4] if item_info[4] is not None else 0))

                quantity_amount.set(item_info[5])

                discounts = get_p_discounts()
                [active_discounts.append(discount) for discount in discounts]
                active_discounts_btn.config(state=NORMAL, text="{0} Active".format(len(discounts)))

                limits = get_p_limits()
                [active_limits.append(limit) for limit in limits]
                active_limits_btn.config(state=NORMAL, text="{0} Active".format(len(limits)))

                offers = get_p_offers()
                [active_offers.append(offer) for offer in offers]
                active_offers_btn.config(state=NORMAL, text="{0} Active".format(len(offers)))

                notes.set(item_info[6] if item_info[6] is not None else "")

        actions_frame = Frame(self.main_frame, bg=self.background_bg)
        actions_frame.grid(row=7 if account else 9, column=0, pady=10, sticky=E + W)
        actions_bg = "DarkOrange2"

        Grid.rowconfigure(self.main_frame, 7, weight=1)
        [Grid.columnconfigure(actions_frame, i, weight=1) for i in range(3)]

        actions_cancel_btn = Button(actions_frame, text="Cancel", font=(self.font_name, 20, "bold"), bg=actions_bg,
                                    command=lambda: caller())
        actions_cancel_btn.grid(row=0, column=0, sticky=E + W, padx=(60, 0))

        actions_save_btn = Button(actions_frame, text="Save", font=(self.font_name, 20, "bold"), bg=actions_bg,
                                  command=lambda: save_account(validate_account()) if account
                                  else save_product())
        actions_save_btn.grid(row=0, column=1, sticky=E + W, padx=60)

        confirm_msg = "Please confirm that you want to delete this {0}.\n\nPlease click Yes to confirm." \
                      "".format(caller_name)
        actions_delete_btn = Button(actions_frame, text="Delete", font=(self.font_name, 20, "bold"), bg=actions_bg,
                                    command=lambda: self.combine_funcs(item.delete_account() if account
                                                                       else item.delete_product(), caller())
                                    if messagebox.askyesno("Are you sure?", confirm_msg) else None)
        actions_delete_btn.grid(row=0, column=2, sticky=E + W, padx=(0, 60))

        item_id_lbl = Label(actions_frame, text=item_info[0] if item_info is not None else "",
                            bg=self.background_bg, font=(self.font_name, 12, "bold"))
        item_id_lbl.grid(row=0, column=2, sticky=E, padx=(0, 20))

    def display_history(self, field_name, item_id, caller_id, *caller_params, page=1):
        """display history resets main frame to shown the history for any given account or product field"""

        def call_yourself(page_):
            self.display_history(field_name, item_id, caller_id, caller_params, page=page_)

        self.back_btn.config(command=lambda: caller_id(*caller_params))

        # interface_address stores layout data and access for all account and product fields in the form:
        # [access to data, *[field name to display, display width, position found in "access to data"]]
        interface_address = {
            "First Name": [lambda: get_item_history("accounts_f_name", "account_id", item_id), ["First Name", 10, 1]],
            "Last Name": [lambda: get_item_history("accounts_l_name", "account_id", item_id), ["Last Name", 10, 1]],
            "Budget": [lambda: get_item_history("accounts_top_ups", "account_id", item_id), ["Topped Up", 10, 1]],
            "Discount": [lambda: get_item_history("accounts_discounts", "account_id", item_id), ["Type", 4, 2],
                         ["Amount", 10, 1], ["Start Date", 20, 3], ["End Date", 20, 4], ["Void", 10, -2]],
            "Spending Limit": [lambda: get_item_history("accounts_spending_limit", "account_id", item_id),
                               ["Amount", 10, 1], ["Per", 10, 2], ["Start Date", 20, 3], ["End Date", 20, 4],
                               ["Void", 10, -2]],
            "Sub Zero Allowances": [lambda: get_item_history("accounts_sub_zero_allowance", "account_id", item_id),
                                       ["Amount", 10, 1], ["Start Date", 20, 2], ["End Date", 20, 3], ["Void", 10, -2]],
            "Notes": [lambda: get_item_history("accounts_notes", "account_id", item_id), ["Notes", 30, 1]],

            "Product Name": [lambda: get_item_history("products_name", "product_id", item_id), ["Product Name", 20, 1]],
            "Supplier": [lambda: get_item_history("products_supplier", "product_id", item_id), ["Supplier", 20, 1]],
            "Cost Price": [lambda: get_item_history("products_cost_price", "product_id", item_id), ["Cost Price", 20, 1]],
            "Sale Price": [lambda: get_item_history("products_sale_price", "product_id", item_id), ["Sale Price", 20, 1]],
            "Quantity": [lambda: get_item_history("products_quantity_top_ups", "product_id", item_id), ["Quantity", 20, 1]],
            "Purchase Limit": [lambda: get_item_history("products_purchase_limit", "product_id", item_id),
                               ["Amount", 10, 1], ["Per", 10, 2], ["Start Date", 20, 3], ["End Date", 20, 4],
                               ["Void", 10, -2]],
            "Discounts": [lambda: get_item_history("products_discounts", "product_id", item_id),
                          ["Amount", 10, 1], ["Type", 10, 2], ["Start Date", 20, 3], ["End Date", 20, 4],
                          ["Void", 10, -2]],
            "Offers": [lambda: get_item_history("products_offers", "product_id", item_id),
                       ["Buy X", 10, 1], ["Get Y", 10, 1], ["Z Off", 10, 1], ["Type", 10, 2], ["Start Date", 20, 3],
                       ["End Date", 20, 4], ["Void", 10, -2]],
            "Product Notes": [lambda: get_item_history("products_notes", "product_id", item_id), ["Notes", 30, 1]],
        }

        [interface_address[key].append(["Date Added", 20, -1]) for key in interface_address.keys()]

        self._frame_reset(self.main_frame)

        font1, font2 = (self.font_name, 20, "bold"), (self.font_name, 18)

        fields_info = interface_address[field_name][1:]

        # titles
        [Label(self.main_frame, text=field_info[0], width=field_info[1], font=font1, bg=self.background_bg).grid(
            row=0, column=fields_info.index(field_info), pady=15) for field_info in fields_info]

        [Grid.columnconfigure(self.main_frame, i, weight=1) for i in range(len(fields_info))]

        # items
        bgs = ["grey70", "grey60"]
        item_history = interface_address[field_name][0]()
        total_items, page_limit = len(item_history), 15
        item_history = item_history[(page - 1) * page_limit:page * page_limit] \
            if total_items >= page * page_limit else item_history[(page - 1) * page_limit:]
        row = int()

        for item in item_history:
            row = item_history.index(item) + 1
            bg = bgs[item_history.index(item) % 2]

            for field_info in fields_info:
                value = item[field_info[2]]
                if field_info[0] == "Type":
                    text = "£" if value == 1 else "%"
                elif field_info[0] == "Void":
                    text = "True" if value == 1 else "False"
                elif field_info[0] == "End Date":
                    text = "Indefinitely" if value == "" else value
                else:
                    text = item[field_info[2]]

                Label(self.main_frame, text=text, font=font2, bg=bg).grid(row=row, column=fields_info.index(field_info),
                                                                          sticky=E + W)

        page_scrolling_frame = Frame(self.main_frame, bg=self.background_bg)
        page_scrolling_frame.grid(row=row + 1, column=0, sticky=S, columnspan=len(fields_info))
        Grid.rowconfigure(self.main_frame, row + 1, weight=1)

        total_pages = ceil(total_items / page_limit) if total_items > 0 else 1
        bg = "sandy brown"

        if total_pages > 1:
            Button(page_scrolling_frame, text="Previous", font=font2, bg=bg, width=10,
                   command=lambda: call_yourself(page - 1) if page > 1 else None).grid(row=0, column=0)
            Button(page_scrolling_frame, text="Next", font=font2, bg=bg, width=10,
                   command=lambda: call_yourself(page + 1) if page < total_pages else None).grid(row=0, column=2)

        Label(page_scrolling_frame, text="Page {0} of {1}".format(page, total_pages), bg=self.background_bg,
              font=font2).grid(row=0, column=1, padx=20)

    def page_populator(self, caller, select_user=False, account_track=False, product_track=False):
        self._frame_reset(self.main_frame)
        self.back_btn.config(command=lambda: self.setup() if not select_user else self.transactions()
                             if not (account_track or product_track) else self.track())

        call_item = self.account if caller == "Accounts" else self.product if caller == "Products" \
            else self.transactions

        items = get_accounts() if caller in ["Accounts", "Transactions"] else get_products()

        self.title.set("{0} ({1})".format(caller, len(items)))

        item_frame = Frame(self.main_frame, bg=self.background_bg)
        item_frame.grid(row=0, column=0, sticky=E + W)

        item_actions_frame = Frame(self.main_frame, bg=self.background_bg)
        item_actions_frame.grid(row=1, column=0, pady=20, sticky=S + E + W)

        Grid.columnconfigure(self.main_frame, 0, weight=1)
        Grid.rowconfigure(self.main_frame, 0, weight=1), Grid.rowconfigure(self.main_frame, 1, weight=0)

        font = (self.font_name, 16, "bold")

        col, row = int(), int()
        Grid.rowconfigure(item_frame, row, weight=1), Grid.columnconfigure(item_frame, col, weight=1)

        total_items, page, page_limit = len(items), self.items_page.get(), 35
        total_pages = ceil(total_items/page_limit) if total_items > 0 else 1

        items = items[(page - 1) * page_limit:page * page_limit] if total_items >= page * page_limit \
            else items[(page - 1) * page_limit:]

        for item in items:
            Button(item_frame, text=item[1] + " " + item[2] if caller in ["Accounts", "Transactions"] else item[1],
                   bg="orange", font=font, width=20, height=2,
                   command=lambda item_info=list(item): call_item(item_info) if not select_user
                   else self.transactions(item_info) if not (account_track or product_track)
                   else self.product_stats(item_info) if product_track
                   else self.account_purchase_history(item_info)).grid(row=row, column=col, pady=20)
            Grid.columnconfigure(item_frame, col, weight=1)
            col += 1
            if col == 5:
                col, row = 0, row + 1
                Grid.rowconfigure(item_frame, row, weight=1)

        if len(items) == 0:
            Label(item_frame, text="No Items!", font=("Calibri", 36, "bold"), bg=self.background_bg).pack()

        if not select_user:
            bg = "salmon"
            initial_dir, title_1 = "%documents%", "Select the File to Import From"
            file_types = ('csv files only', '*.csv')

            if caller == "Accounts":
                msg = "Accounts can be imported from a csv file where each line is a new account. Each account must " \
                      "have the 3 fields \"First Name\", \"Last Name\" and \"Budget\" delimited by commas."
            else:
                msg = "Products can be imported from a csv file where each line is a new product. Each product must have " \
                      "the 3 fields \"Product Name\", \"Cost Price\" and \"Sale Price\" delimited by commas."
            msg += "\n\nIs the intended CSV file in the correct format?"

            import_btn = Button(item_actions_frame, text="IMPORT", font=font, bg=bg, width=12,
                                command=lambda: self.combine_funcs(
                                    self.import_items(filedialog.askopenfilename(
                                        initialdir=initial_dir, title=title_1, filetypes=[file_types]), caller=caller),
                                    self.page_populator(caller)) if messagebox.askyesno("Import Details", msg)
                                else None)
            import_btn.grid(row=0, column=0)
            add_btn = Button(item_actions_frame, text="ADD", font=font, bg=bg, width=12, command=lambda: call_item())
            add_btn.grid(row=0, column=1)
            previous_btn = Button(item_actions_frame, text="PREVIOUS", font=font, bg=bg, width=12,
                                  command=lambda: self.combine_funcs(self.items_page.set(page-1),
                                                                     self.page_populator(caller))
                                  if page > 1 else None)
            previous_btn.grid(row=0, column=2)
            page_lbl = Label(item_actions_frame, text="Page {0} of {1}".format(page, total_pages),
                             font=font, bg=bg, width=12)
            page_lbl.grid(row=0, column=3)
            next_btn = Button(item_actions_frame, text="NEXT", font=font, bg=bg, width=12,
                              command=lambda: self.combine_funcs(self.items_page.set(page + 1),
                                                                 self.page_populator(caller))
                              if page < total_pages else None)
            next_btn.grid(row=0, column=4)

            [Grid.columnconfigure(item_actions_frame, i, weight=1) for i in range(5)]

    def transactions(self, item_info=None):

        def add_transaction(product):
            if product in transactions.keys():
                quantity = transactions[product] + 1
            else:
                quantity = 1

            transactions[product] = quantity

            [widget.destroy() for widget in transactions_individual.winfo_children()]

            flag = False
            for item in transactions.items():
                quantity = item[1]
                position = list(transactions.keys()).index(item[0])

                if not add(quantity, item[0], position):
                    flag = True
            if flag:
                remove_transaction(product)

        def add(quantity, product, position):

            cost = product[4] if product[4] is not None else 0

            text = "{0:02d}".format(quantity) + " x " + str(product[1]) + " @ " + "£{0:.2f} = £{1:.2f}".format(
                cost, quantity * cost)

            try:  # product discount
                p_discounts = get_product_conditions(product_id=product[0], discount=True)
                p_discount = float()
                for item in p_discounts:
                    if item[2] == "0":
                        p_discount += item[1]
            except IndexError:
                p_discount = float()

            d_condition = "{0:.2f}% off = £{1:.2f}".format(p_discount,
                                                           quantity * cost - p_discount / 100 * quantity * cost) \
                if p_discount != float() else None

            try:  # product offers
                p_offers = get_product_conditions(product_id=product[0], offer=True)

                buy_x, get_y, z_off = p_offers[0][1:4]
                divider = buy_x + get_y
                cost = product[4]

                if quantity >= divider:

                    no_to_apply = int(quantity / divider)  # total to be discounted
                    discount_cost = no_to_apply * (cost - (get_y * cost * z_off / 100))  # discounted items cost
                    remaining_cost = (quantity - no_to_apply) * cost  # rest of items cost

                    o_condition = "Buy {0} Get {1} {2}% off = £{3:.2f}".format(buy_x, get_y, z_off,
                                                                               discount_cost + remaining_cost)
                    if d_condition is not None:
                        if float(discount_cost + remaining_cost) > float(d_condition[d_condition.rfind("£")+1:]):
                            raise IndexError()
                else:
                    raise IndexError()
            except (IndexError, UnboundLocalError):
                o_condition = None

            transaction_f = Frame(transactions_individual)
            transaction_f.grid(row=position, column=0)

            Label(transaction_f, text=text, font=font2, width=30, anchor=W).grid(row=0, column=0, sticky=W)
            if o_condition is not None:
                Label(transaction_f, text=o_condition, font=font2, width=30, anchor=E).grid(row=2, column=0)
            elif d_condition is not None:
                Label(transaction_f, text=d_condition, font=font2, width=30, anchor=E).grid(row=1, column=0)

            total_ = float()
            for frame_ in transactions_individual.winfo_children():  # calc total
                txt = frame_.winfo_children()[-1].cget("text")
                total_ += float(txt[txt.rfind("£") + 1:]) - float(txt[txt.rfind("£") + 1:]) * (discount / 100)

            try:
                p_limit = get_product_conditions(product[0], purchase_limit=True)[0][0]
            except IndexError:
                p_limit = -1

            if total_ > limit > 0:
                messagebox.showerror("Spending Limit Reached", "You have reached the spending limit for this account "
                                                               "and therefore cannot add this item.")
                return False
            elif balance - total_ + allowance < 0:
                messagebox.showerror("Insufficient Funds", "Your account does not have enough funds for this item to be"
                                                           " added.")
            elif quantity > p_limit > -1:
                messagebox.showerror("Product Purchase Limit", "There is a purchase limit on this item. Unfortunately, "
                                                               "you cannot increase this items quantity any further.")

            else:
                total.set("£{:.2f}".format(total_))  # look for neater solution for the remove loop
                new_balance.set("£{0:.2f}".format(item_info[3] - total_))

                return True

        def remove_transaction(product):
            if product in transactions.keys():
                quantity = transactions[product] - 1
                position = list(transactions.keys()).index(product)

                if quantity == 0:
                    del transactions[product]
                    [widget.destroy() for widget in transactions_individual.winfo_children()]
                    for item in transactions.items():
                        quantity = item[1]
                        position = list(transactions.keys()).index(item[0])

                        add(quantity, item[0], position)

                    if len(transactions.items()) == 0:  # when removing all items from transactions list
                        total.set("£0.00")
                        new_balance.set("£{:.2f}".format(balance))
                else:
                    transactions[product] = quantity

                    [widget.destroy() for widget in transactions_individual.winfo_children()
                     if product[1] in widget.winfo_children()[0].cget("text")]

                    add(quantity, product, position)

        self._frame_reset(self.main_frame)
        back_msg = "You will lose any data from this transaction and have to start again.\n\nAre you sure you want to" \
                   " continue?"
        self.back_btn.config(command=lambda: self.main_menu() if item_info is None else self.main_menu()
                             if messagebox.askyesno("Confirm", back_msg) else None)
        self.title.set("Transactions{0}".format(" - {0} {1}".format(*item_info[1:3]) if item_info is not None else ""))

        product_frame = Frame(self.main_frame, bg=self.background_bg)
        product_frame.grid(row=0, column=0, sticky=N + E + S + W)

        transactions_frame = Frame(self.main_frame, bg=self.background_bg)
        transactions_frame.grid(row=0, column=1, rowspan=2, sticky=N + S)

        actions_frame = Frame(self.main_frame, bg=self.background_bg)
        actions_frame.grid(row=1, column=0, sticky=E + W)

        Grid.rowconfigure(self.main_frame, 0, weight=1), Grid.columnconfigure(self.main_frame, 0, weight=1)

        font1, font2 = (self.font_name, 19, "bold"), (self.font_name, 16)
        font3, font4 = (self.font_name, 14, "bold"), (self.font_name, 14)

        column_limit = 5

        page_actions_frame = Frame(actions_frame, bg=self.background_bg)
        page_actions_frame.grid(row=0, column=1, sticky=E)

        curr_page = StringVar()

        back_btn = Button(page_actions_frame, text="Previous Page", font=font1)
        back_btn.grid(row=0, column=0, padx=10)
        Label(page_actions_frame, textvariable=curr_page, font=font1, bg=self.background_bg).grid(
            row=0, column=1, padx=10)
        forward_btn = Button(page_actions_frame, text="Next Page", font=font1)
        forward_btn.grid(row=0, column=2, padx=10)

        products = get_products()

        total_products, page_limit = len(products), 30
        total_pages = ceil(total_products / page_limit) if total_products > 0 else 1

        def product_populator(page=1):
            row, col = int(), int()

            self._frame_reset(product_frame)

            curr_page.set("{0} of {1}".format(page, total_pages))
            back_btn.config(command=lambda: product_populator(page-1) if page > 1 else None)
            forward_btn.config(command=lambda: product_populator(page+1) if page < total_pages else None)

            products_ = products[(page - 1) * page_limit:page * page_limit] if total_products >= page * page_limit \
                else products[(page - 1) * page_limit:]

            for product in products_:
                frame = Frame(product_frame, bg='LightSkyBlue3')
                frame.grid(row=row, column=col, padx=10, pady=(14, 0), sticky=E + W)

                Label(frame, text=product[1], font=font1, width=13, bg='LightSkyBlue3').grid(row=0, column=0,
                                                                                             sticky=E + W)
                Label(frame, text="£{0:.2f}".format(product[4] if product[4] is not None else 0), font=font2,
                      bg='LightSkyBlue3').grid(row=1, column=0, sticky=E + W)

                def no_user():
                    messagebox.showerror("Must Select User", "Please select a user before adding items!")

                Button(frame, text="+", font=font2, width=3, bg="orange",
                       command=lambda item=product: add_transaction(item)
                       if item_info is not None else no_user()).grid(row=0, column=1)
                Button(frame, text="-", font=font2, width=3, bg="orange",
                       command=lambda item=product: remove_transaction(item)
                       if item_info is not None else no_user()).grid(row=1, column=1)

                Grid.columnconfigure(frame, 0, weight=1)

                col += 1

                if col == column_limit:
                    row += 1
                    col = 0

        product_populator()
        transactions_individual = Frame(transactions_frame, bg='white')
        transactions_individual.grid(row=0, column=0, sticky=N + E + S + W)

        transactions = dict()

        user_frame = Frame(transactions_frame, bg=self.background_bg)
        user_frame.grid(row=1, column=0, pady=10, padx=10, sticky=E + W + S)

        if item_info is None:
            Button(user_frame, text="Select User", font=font1, bg='orange',
                   command=lambda: self.page_populator("Transactions", select_user=True)).grid(row=0, column=0,
                                                                                               sticky=E + W, padx=4)
        else:
            Label(user_frame, text="Account Discount", font=font3, bg=self.background_bg).grid(row=0, column=0,
                                                                                               sticky=W)
            Label(user_frame, text="Account Spending Limit", font=font3, bg=self.background_bg).grid(row=1, column=0,
                                                                                                     sticky=W)
            Label(user_frame, text="Account Sub Zero Allowance", font=font3, bg=self.background_bg).grid(row=2,
                                                                                                         column=0,
                                                                                                         sticky=W)

            try:
                discounts = get_account_conditions(account_id=item_info[0], discount=True)
                discount = float()
                for item in discounts:
                    if item[2] == 0:
                        discount += item[1]
            except IndexError:
                discount = float()

            try:
                limits = get_account_conditions(account_id=item_info[0], spending_limit=True)
                limit = float()
                for item in limits:
                    limit += item[1]
            except IndexError:
                limit = float()
            try:
                allowances = get_account_conditions(account_id=item_info[0], sub_zero_allowance=True)
                allowance = float()
                for item in allowances:
                    allowance += item[1]
            except IndexError:
                allowance = float()

            Label(user_frame, text="{0:.2f}%".format(discount), font=font4, bg=self.background_bg).grid(row=0, column=1,
                                                                                                        sticky=E)
            Label(user_frame, text="£{0:.2f}".format(limit), font=font4, bg=self.background_bg).grid(row=1, column=1,
                                                                                                     sticky=E)
            Label(user_frame, text="£{0:.2f}".format(allowance), font=font4, bg=self.background_bg).grid(row=2,
                                                                                                         column=1,
                                                                                                         sticky=E)

        Grid.columnconfigure(user_frame, 0, weight=1)

        total_frame = Frame(transactions_frame)
        total_frame.grid(row=3, column=0, pady=10, padx=10, sticky=E + W + S)
        Grid.columnconfigure(total_frame, 1, weight=1)

        Label(total_frame, text="Account Balance:", font=font3).grid(row=0, column=0, sticky=W)
        balance = item_info[3] if item_info is not None else 0
        Label(total_frame, text="£{0:.2f}".format(balance), font=font4).grid(row=0, column=1, sticky=E)

        total = StringVar()
        total.set("£0.00")

        Label(total_frame, text="Total:", font=font1).grid(row=1, column=0, sticky=W, pady=10)
        Label(total_frame, textvariable=total, font=font1).grid(row=1, column=1, sticky=E)

        Label(total_frame, text="New Balance:", font=font3).grid(row=2, column=0, sticky=W)
        new_balance = StringVar()
        new_balance.set("£{0:.2f}".format(balance))
        Label(total_frame, textvariable=new_balance, font=font4).grid(row=2, column=1, sticky=E)

        Button(transactions_frame, text="Purchase", font=font1, width=23, bg="green2",
               command=lambda: self.combine_funcs(
                   Transaction().record_transaction(Account(item_info[0]),
                                                    *[[Product(product[0]), quantity] for product, quantity
                                                      in transactions.items()]),
                   messagebox.showinfo("Successful", "Transaction was successful!"),
                   self.transactions()))\
            .grid(row=5, column=0, pady=10, padx=10, sticky=E + W + S)

        Grid.rowconfigure(transactions_frame, 0, weight=1)

        msg = "This will reset the current transaction and deselect the current user.\n\nAre you sure you want to " \
              "continue?"
        Button(actions_frame, text="Cancel", font=font1, bg="DarkOrange2",
               command=lambda: self.transactions() if messagebox.askyesno("Cancel", msg) else None).grid(row=0,
                                                                                                         column=0)

        Grid.columnconfigure(actions_frame, 1, weight=1)

    def track(self):
        self._frame_reset(self.main_frame)
        self.back_btn.config(command=lambda: self.main_menu())
        self.title.set("Track")

        font, bg = ("Calibri", 22, "bold"), "orange"
        Button(self.main_frame, text="Account Purchase History", font=font, bg=bg, width=25, height=2,
               command=lambda: self.page_populator("Accounts", select_user=True, account_track=True)).grid(row=0,
                                                                                                           column=0)

        Button(self.main_frame, text="Product Stats", font=font, bg=bg, width=25, height=2,
               command=lambda: self.page_populator("Products", select_user=True, product_track=True)).grid(row=0,
                                                                                                           column=1)

        Button(self.main_frame, text="Overall Stats", font=font, bg=bg, width=25, height=2,
               command=lambda: stats()).grid(row=0, column=2)

        Grid.rowconfigure(self.main_frame, 0, weight=1)
        Grid.columnconfigure(self.main_frame, 0, weight=1)
        Grid.columnconfigure(self.main_frame, 1, weight=1)
        Grid.columnconfigure(self.main_frame, 2, weight=1)

        def stats():
            self._frame_reset(self.main_frame)
            self.back_btn.config(command=lambda: self.track())
            self.title.set("Track - Stats")

            # calc stats
            budget = sum(sum(top_up[1] for top_up in get_item_history("accounts_top_ups", "account_id", account[0]))
                         for account in get_accounts())

            income = sum(transaction[2] for transaction in get_transactions())

            expense = \
                sum(get_item_history("products_cost_price", "product_id", product[0])[-1][1] *
                    sum(top_up[1] for top_up in get_item_history("products_quantity_top_ups", "product_id", product[0]))
                    for product in get_products())
            # issue with the above calculation is that it does not take into account the price for different quantities
            # (assuming they had changed)

            profit = income - expense

            # present them
            font1, font2 = ("Calibri", 18, "bold"), ("Calibri", 18)

            frame = Frame(self.main_frame, bg=self.background_bg)
            frame.grid(row=0, column=0)

            Label(frame, text="Total Accounts Budget:", font=font1, bg=self.background_bg).grid(row=0, column=0,
                                                                                                sticky=W)
            Label(frame, text="Total Income:", font=font1, bg=self.background_bg).grid(row=1, column=0, sticky=W)
            Label(frame, text="Total Expenses:", font=font1, bg=self.background_bg).grid(row=2, column=0, sticky=W)
            Label(frame, text="Total Profit:", font=font1, bg=self.background_bg).grid(row=3, column=0, sticky=W)

            Label(frame, text="£{0:.2f}".format(budget), font=font1, bg=self.background_bg).grid(row=0, column=1,
                                                                                                 padx=(100, 0))
            Label(frame, text="£{0:.2f}".format(income), font=font1, bg=self.background_bg).grid(row=1, column=1,
                                                                                                 padx=(100, 0))
            Label(frame, text="£{0:.2f}".format(expense), font=font1, bg=self.background_bg).grid(row=2, column=1,
                                                                                                  padx=(100, 0))
            Label(frame, text="£{0:.2f}".format(profit), font=font1, bg=self.background_bg).grid(row=3, column=1,
                                                                                                 padx=(100, 0))

            Grid.rowconfigure(self.main_frame, 0, weight=1), Grid.columnconfigure(self.main_frame, 0, weight=1)

    def product_stats(self, product):
        self._frame_reset(self.main_frame)
        self.back_btn.config(command=lambda: self.track())
        self.title.set("Purchase History - {}".format(product[1]))

        starting_qty = sum(top_up[1] for top_up in get_item_history("products_quantity_top_ups", "product_id",
                                                                    product[0]))
        current_qty = product[5]
        cost = product[3]
        sale = product[4]
        profit = sale - cost
        ttl_cost = starting_qty * cost
        ttl_income = (starting_qty - current_qty) * sale
        ttl_profit = ttl_income - ttl_cost

        font1, font2 = ("Calibri", 18, "bold"), ("Calibri", 18)

        frame = Frame(self.main_frame, bg=self.background_bg)
        frame.grid(row=0, column=0)

        Label(frame, text="Starting Qty:", font=font1, bg=self.background_bg).grid(row=0, column=0, sticky=W)
        Label(frame, text="Current Qty:", font=font1, bg=self.background_bg).grid(row=1, column=0, sticky=W)
        Label(frame, text="Cost per Item:", font=font1, bg=self.background_bg).grid(row=2, column=0, sticky=W)
        Label(frame, text="Sale Price:", font=font1, bg=self.background_bg).grid(row=3, column=0, sticky=W)
        Label(frame, text="Profit per Item:", font=font1, bg=self.background_bg).grid(row=4, column=0, sticky=W)
        Label(frame, text="Total Cost:", font=font1, bg=self.background_bg).grid(row=5, column=0, sticky=W)
        Label(frame, text="Total Income:", font=font1, bg=self.background_bg).grid(row=6, column=0, sticky=W)
        Label(frame, text="Total Profit:", font=font1, bg=self.background_bg).grid(row=7, column=0, sticky=W)

        Label(frame, text=starting_qty, font=font1, bg=self.background_bg).grid(row=0, column=1, padx=(100, 0))
        Label(frame, text=current_qty, font=font1, bg=self.background_bg).grid(row=1, column=1, padx=(100, 0))
        Label(frame, text="£{0:.2f}".format(cost), font=font1, bg=self.background_bg).grid(row=2, column=1,
                                                                                           padx=(100, 0))
        Label(frame, text="£{0:.2f}".format(sale), font=font1, bg=self.background_bg).grid(row=3, column=1,
                                                                                           padx=(100, 0))
        Label(frame, text="£{0:.2f}".format(profit), font=font1, bg=self.background_bg).grid(row=4, column=1,
                                                                                             padx=(100, 0))
        Label(frame, text="£{0:.2f}".format(ttl_cost), font=font1, bg=self.background_bg).grid(row=5, column=1,
                                                                                               padx=(100, 0))
        Label(frame, text="£{0:.2f}".format(ttl_income), font=font1, bg=self.background_bg).grid(row=6, column=1,
                                                                                                 padx=(100, 0))
        Label(frame, text="£{0:.2f}".format(ttl_profit), font=font1, bg=self.background_bg).grid(row=7, column=1,
                                                                                                 padx=(100, 0))

        Grid.rowconfigure(self.main_frame, 0, weight=1), Grid.columnconfigure(self.main_frame, 0, weight=1)

    def account_purchase_history(self, account, page=1):
        self._frame_reset(self.main_frame)
        self.back_btn.config(command=lambda: self.track())
        self.title.set("Account History - {0} {1}".format(account[1], account[2]))

        starting_budget = sum(top_up[1] for top_up in get_item_history("accounts_top_ups", "account_id", account[0]))

        current_budget = account[3]

        ttl_spent = starting_budget - current_budget

        font1, font2 = ("Calibri", 24, "bold"), ("Calibri", 24)
        font3, font4 = ("Calibri", 18, "bold"), ("Calibri", 18)

        frame = Frame(self.main_frame, bg=self.background_bg)
        frame.grid(row=0, column=0, sticky=N + E + W, pady=40)

        Label(frame, text="Starting Budget:", font=font1, bg=self.background_bg, relief=RAISED).grid(row=0, column=0,
                                                                                                     ipadx=10)
        Label(frame, text="Current Budget:", font=font1, bg=self.background_bg, relief=RAISED).grid(row=0, column=2,
                                                                                                    ipadx=10)
        Label(frame, text="Total Money Spent:", font=font1, bg=self.background_bg, relief=RAISED).grid(row=0, column=4,
                                                                                                       ipadx=10)

        Label(frame, text="£{0:.2f}".format(starting_budget), font=font2, bg=self.background_bg).grid(row=0, column=1,
                                                                                                      sticky=W)
        Label(frame, text="£{0:.2f}".format(current_budget), font=font2, bg=self.background_bg).grid(row=0, column=3,
                                                                                                     sticky=W)
        Label(frame, text="£{0:.2f}".format(ttl_spent), font=font2, bg=self.background_bg).grid(row=0, column=5,
                                                                                                sticky=W)

        Grid.rowconfigure(self.main_frame, 0, weight=0), Grid.rowconfigure(self.main_frame, 1, weight=1)
        Grid.columnconfigure(self.main_frame, 0, weight=1)
        [Grid.columnconfigure(frame, i, weight=1) for i in range(6)]

        transaction_frame = Frame(self.main_frame, bg=self.background_bg)
        transaction_frame.grid(row=1, column=0, sticky=N + S + E + W)

        Label(transaction_frame, text="Transaction Code", font=font3, bg=self.background_bg).grid(row=0, column=0)
        Label(transaction_frame, text="Transaction Amount", font=font3, bg=self.background_bg).grid(row=0, column=1)
        Label(transaction_frame, text="Transaction Date", font=font3, bg=self.background_bg).grid(row=0, column=2)
        Label(transaction_frame, text="Action", font=font3, bg=self.background_bg).grid(row=0, column=3)

        [Grid.columnconfigure(transaction_frame, i, weight=1) for i in range(4)]

        transactions = get_transactions(account[0])

        page_limit, total_items = 9, len(transactions)
        total_pages = ceil(total_items / page_limit) if total_items > 0 else 1

        transactions = transactions[(page - 1) * page_limit:page * page_limit]  if total_items >= page * page_limit \
            else transactions[(page - 1) * page_limit:]

        for transaction in transactions:
            row = transactions.index(transaction) + 1

            date = datetime.strptime(transaction[3], "%Y-%m-%d %H:%M:%S.%f").replace(microsecond=0)

            Label(transaction_frame, text=transaction[0], font=font4, bg=self.background_bg).grid(row=row, column=0)
            Label(transaction_frame, text="£{0:.2f}".format(transaction[2]), font=font4, bg=self.background_bg).grid(
                row=row, column=1)
            Label(transaction_frame, text=date, font=font4, bg=self.background_bg).grid(row=row, column=2)
            temp_frame = Frame(transaction_frame, bg=self.background_bg)
            temp_frame.grid(row=row, column=3)
            Button(temp_frame, text="See Details", font=font4, bg="orange", width=15,
                   command=lambda item=transaction: transaction_products(item)).grid(row=0, column=0)
            Button(temp_frame, text="Undo", font=font4, bg="red2", width=15,
                   command=lambda item=transaction: self.combine_funcs(Transaction().revert_transaction(item[0]),
                                                                       self.account_purchase_history(
                                                                           [account[0], account[1], account[2],
                                                                            account[3] + transaction[2], account[4]]))
                   ).grid(row=0, column=1)

        page_frame = Frame(self.main_frame, bg=self.background_bg)
        page_frame.grid(row=2, column=0, pady=15)

        Button(page_frame, text="Previous Page", font=font3, bg="orange", width=15,
               command=lambda: self.account_purchase_history(account, page=page-1) if page > 1 else None
               ).grid(row=0, column=0)
        Label(page_frame, text="{0} of {1}".format(page, total_pages), font=font4, bg=self.background_bg).grid(
            row=0, column=1, padx=25)
        Button(page_frame, text="Next Page", font=font3, bg="orange", width=15,
               command=lambda: self.account_purchase_history(account, page=page+1) if page < total_pages else None
               ).grid(row=0, column=2)

        def transaction_products(transaction_, page_=1):
            self._frame_reset(self.main_frame)
            self.back_btn.config(command=lambda: self.account_purchase_history(account=account))
            self.title.set("Transaction Products")

            top_frame = Frame(self.main_frame, bg=self.background_bg)
            top_frame.grid(row=0, column=0, pady=40)
            Grid.columnconfigure(self.main_frame, 0, weight=1)

            Label(top_frame, text="Transaction Total:", font=font1, bg=self.background_bg, relief=RAISED
                  ).grid(row=0, column=0, ipadx=10)
            Label(top_frame, text="£{0:.2f}".format(transaction_[2]), font=font2, bg=self.background_bg).grid(
                row=0, column=1, padx=20)

            main_frame = Frame(self.main_frame, bg=self.background_bg)
            main_frame.grid(row=1, column=0, sticky=N + S + E + W)

            Grid.rowconfigure(self.main_frame, 1, weight=1)

            Label(main_frame, text="Product Name", font=font3, bg=self.background_bg).grid(row=0, column=0)
            Label(main_frame, text="Product Price", font=font3, bg=self.background_bg).grid(row=0, column=1)
            Label(main_frame, text="Quantity", font=font3, bg=self.background_bg).grid(row=0, column=2)
            Label(main_frame, text="Total Cost", font=font3, bg=self.background_bg).grid(row=0, column=3)

            [Grid.columnconfigure(main_frame, i, weight=1) for i in range(4)]

            details = get_transactions_details(transaction_[0])

            page_limit_, total_items_ = 8, len(details)
            total_pages_ = ceil(total_items_ / page_limit_) if total_items_ > 0 else 1

            details = details[(page_ - 1) * page_limit_:page_ * page_limit_] if total_items_ >= page_ * page_limit_ \
                else details[(page_ - 1) * page_limit_:]

            for item in details:
                product = get_products(product_id=item[1])[0]
                row = details.index(item) + 1

                Label(main_frame, text=product[1], font=font4, bg=self.background_bg).grid(row=row, column=0)
                Label(main_frame, text="£{0:.2f}".format(product[4]), font=font4, bg=self.background_bg).grid(row=row,
                                                                                                              column=1)
                Label(main_frame, text=item[2], font=font4, bg=self.background_bg).grid(row=row, column=2)
                Label(main_frame, text="£{0:.2f}".format(product[4] * item[2]), font=font4, bg=self.background_bg
                      ).grid(row=row, column=3)

            note = "Note: the price of individual items listed here will not include any discounts or offers"
            Label(self.main_frame, text=note, font=font4, bg=self.background_bg).grid(row=2, column=0, columnspan=3,
                                                                                      pady=10, sticky=S)

            page_frame_ = Frame(self.main_frame, bg=self.background_bg)
            page_frame_.grid(row=3, column=0, pady=15)

            Button(page_frame_, text="Previous Page", font=font3, bg="orange", width=15,
                   command=lambda: transaction_products(transaction_, page_=page-1) if page > 1 else None
                   ).grid(row=0, column=0)
            Label(page_frame_, text="{0} of {1}".format(page_, total_pages_), font=font4, bg=self.background_bg
                  ).grid(row=0, column=1, padx=25)
            Button(page_frame_, text="Next Page", font=font3, bg="orange", width=15,
                   command=lambda: transaction_products(transaction_, page_=page+1) if page < total_pages else None
                   ).grid(row=0, column=2)

    def create_type_dropdown(self, frame, font=("Calibri", 20, "bold")):
        type_ = StringVar()
        type_.set("%")
        drop_down = OptionMenu(frame, type_, "%", "£")
        drop_down.config(font=font, state=DISABLED)
        drop_down.nametowidget(drop_down.menuname).configure(font=font, bg=self.background_bg, fg="black")
        return type_, drop_down

    def create_limit_drop_down(self, frame, font=("Calibri", 20, "bold")):
        limit_ = StringVar()
        limit_.set("transaction")
        drop_down = OptionMenu(frame, limit_, "transaction", "day", "week", "month", "year")
        drop_down.config(state=DISABLED, font=font)
        drop_down.nametowidget(drop_down.menuname).configure(font=font)

        return limit_, drop_down

    def import_items(self, csv_address, caller):
        successful, items = int(), list()

        try:
            with open(csv_address, 'r', encoding="UTF-8") as file:
                    file = file.read()

            csv = file.split('\n')

            for item in csv:
                temp = item.split(",")
                if temp != [""]:
                    if caller == "Accounts":
                        if len(temp) >= 3:
                            items.append(temp)
                    else:
                        if len(temp) >= 1:
                            items.append(temp)

            for item in items:
                new_item = Account() if caller == "Accounts" else Product()
                try:
                    if caller == "Accounts":
                        new_item.add_account(f_name=item[0], l_name=item[1])
                        new_item.top_up(amount=float(item[2].strip("£")))
                    else:
                        new_item.add_product(p_name=item[0])
                        new_item.update_details(cost_price=float(item[1].strip("£")),
                                                sale_price=float(item[2].strip("£")))
                        try:
                            new_item.top_up(amount=int(item[3]))
                        except IndexError:
                            pass
                    successful += 1
                except:
                    new_item.delete_account() if caller == "Accounts" else new_item.delete_product()
        except FileNotFoundError:
            pass

        messagebox.showinfo("Import Results", "Out of all {0} items found {1} were successful.".format(len(items),
                                                                                                       successful))

    def export(self):
        path = filedialog.asksaveasfilename(filetypes=(("CSV Files", "*.csv"),), parent=self.main_frame,
                                            title="Export database to CSV")

        export(path)

    def _frame_reset(self, frame):
        self._empty_frame(frame)

        [Grid.rowconfigure(frame, i, weight=0) for i in range(20)]
        [Grid.columnconfigure(frame, i, weight=0) for i in range(20)]

    def _empty_frame(self, frame):
        [widget.destroy() for widget in frame.winfo_children()]

    def combine_funcs(*funcs):
        """enables multiple functions to be called serially inline"""

        def combined_func(*args, **kwargs):
            [f(*args, **kwargs) for f in funcs]

        return combined_func


if __name__ == '__main__':
    GUI()
