from tkinter import *
from tkinter import ttk, messagebox, filedialog
from db_interface import *
from OLD import date_picker
from datetime import datetime, timedelta
from math import ceil
from accounts import Account
from products import Product


"""The code below is somewhat of a mess as it was built in a hurry for it's first usage (don't judge me by it!)"""


class GUI:
    def __init__(self):
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

        self.back_btn = Button(top_bar, text="<--", bg=top_bar_btn_bg, font=(self.font_name, 20, "bold"), width=10, height=2)
        self.back_btn.grid(row=0, column=0, sticky=W)

        self.title = StringVar()
        title_lbl = Label(top_bar, textvariable=self.title, font=(self.font_name, 54, "bold"), bg=top_bar_bg)
        title_lbl.grid(row=0, column=1)

        home_btn = Button(top_bar, text="HOME", bg=top_bar_btn_bg, font=(self.font_name, 20, "bold"), width=10, height=2,
                          command=lambda: self.main_menu())
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

        transaction_btn = Button(self.main_frame, text="TRANSACTIONS", bg=bg, font=font, width=18, height=3,
                                 command=lambda: self.transactions())
        transaction_btn.grid(row=0, column=1)

        Grid.columnconfigure(self.main_frame, 0, weight=1), Grid.columnconfigure(self.main_frame, 1, weight=1)
        Grid.rowconfigure(self.main_frame, 0, weight=1)

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

    def accounts1(self):
        self._frame_reset(self.main_frame)
        self.back_btn.config(command=lambda: self.setup())

        accounts = get_accounts()
        self.title.set("Accounts ({0})".format(len(accounts)))

        account_frame = Frame(self.main_frame, bg=self.background_bg)
        account_frame.grid(row=0, column=0, sticky=E + W)

        account_actions_frame = Frame(self.main_frame, bg=self.background_bg)
        account_actions_frame.grid(row=1, column=0, pady=20, sticky=S + E + W)

        Grid.columnconfigure(self.main_frame, 0, weight=1)
        Grid.rowconfigure(self.main_frame, 0, weight=1), Grid.rowconfigure(self.main_frame, 1, weight=0)

        font = (self.font_name, 16, "bold")

        col, row = int(), int()
        Grid.rowconfigure(account_frame, row, weight=1)
        Grid.columnconfigure(account_frame, col, weight=1)

        total_accounts, page, page_limit = len(accounts), self.accounts_page.get(), 35
        total_pages = ceil(total_accounts/page_limit) if total_accounts > 0 else 1
        accounts = accounts[(page - 1) * page_limit:page * page_limit] if total_accounts >= page * page_limit \
            else accounts[(page - 1) * page_limit:]

        for account in accounts:
            Button(account_frame, text=account[1] + " " + account[2], bg="orange", font=font, width=20, height=2,
                   command=lambda account_info=account: self.account(account_info=account_info))\
                .grid(row=row, column=col, pady=20)
            Grid.columnconfigure(account_frame, col, weight=1)
            col += 1
            if col == 5:
                col = 0
                row += 1
                Grid.rowconfigure(account_frame, row, weight=1)

        bg = "salmon"
        initial_dir, title_1 = "%documents%", "Select the File to Import From"
        file_types = ('csv files only', '*.csv')

        import_btn = Button(account_actions_frame, text="IMPORT", font=font, bg=bg, width=12,
                            command=lambda: self.combine_funcs(
                                self.import_items(filedialog.askopenfilename(initialdir=initial_dir, title=title_1,
                                                                             filetypes=[file_types])),
                                self.accounts()))
        import_btn.grid(row=0, column=0)
        add_btn = Button(account_actions_frame, text="ADD", font=font, bg=bg, width=12, command=lambda: self.account())
        add_btn.grid(row=0, column=1)
        previous_btn = Button(account_actions_frame, text="PREVIOUS", font=font, bg=bg, width=12,
                              command=lambda: self.combine_funcs(self.accounts_page.set(page-1), self.accounts())
                              if page > 1 else None)
        previous_btn.grid(row=0, column=2)
        page_lbl = Label(account_actions_frame, text="Page {0} of {1}".format(page, total_pages),
                         font=font, bg=bg, width=12)
        page_lbl.grid(row=0, column=3)
        next_btn = Button(account_actions_frame, text="NEXT", font=font, bg=bg, width=12,
                          command=lambda: self.combine_funcs(self.accounts_page.set(page + 1), self.accounts())
                          if page < total_pages else None)
        next_btn.grid(row=0, column=4)

        [Grid.columnconfigure(account_actions_frame, i, weight=1) for i in range(5)]

    def accounts(self):
        self.page_populator("Accounts")

    def account(self, account_info=None):
        self._frame_reset(self.main_frame)
        self.back_btn.config(command=lambda: self.accounts())
        if account_info is not None:
            self.title.set("Account - {0}".format(" ".join(account_info[1:3])))
        else:
            self.title.set("New Account")

        Grid.columnconfigure(self.main_frame, 0, weight=1)

        if account_info is not None:
            account = Account(account_id=account_info[0])

        font1, font2 = (self.font_name, 18, "bold"), (self.font_name, 18)
        row = int()

        def _create_basic_frame(lbl_txt):
            nonlocal row

            frame = Frame(self.main_frame, bg=self.background_bg)
            frame.grid(row=row, column=0, pady=10, sticky=E + W)
            Grid.rowconfigure(self.main_frame, row, weight=1)
            [Grid.columnconfigure(frame, i, weight=1) for i in range(3)]
            Label(frame, text=lbl_txt, font=font1, width=20, bg=self.background_bg, anchor=E).grid(row=0, column=0, sticky=W)
            centre_frame = Frame(frame, bg=self.background_bg)
            centre_frame.grid(row=0, column=1, sticky=E + W)
            Grid.columnconfigure(frame, 1, weight=100)
            Button(frame, text="See History", font=font2, bg='red', width=15,
                   command=lambda: self.display_history(lbl_txt, account_info[0], self.account, [account_info])
                   ).grid(row=0, column=2, sticky=E)

            row += 1

            return centre_frame

        def top_up():
            try:
                budget_amount.set("£{0:.2f}".format(float(budget_amount.get()[1:]) + float(top_up_amount.get())))
            except ValueError:
                messagebox.showerror("Top Up Error", "Amount must be a valid number.")

        def save_account(result):
            nonlocal account

            if result[0]:  # details are valid
                update_f_name, update_l_name, update_top_ups, update_notes = bool(), bool(), bool(), bool()
                if account_info is not None:  # check if updates are necessary
                    if account_info[1] != f_name.get():
                        update_f_name = True
                    if account_info[2] != l_name.get():
                        update_l_name = True
                    top_up_total = float(budget_amount.get()[1:]) - float(account_info[3])
                    if account_info[3] != budget_amount.get()[1:]:
                        update_top_ups = True
                    if account_info[4] != notes.get():
                        update_notes = True
                else:
                    if budget_amount.get()[1:] != "£0.00":
                        update_top_ups = True
                    top_up_total = float(budget_amount.get()[1:])  # under indented just to avoid IDE error message
                    if notes.get() != "":
                        update_notes = True

                    account = Account()
                    account.add_account(f_name.get(), l_name.get())

                # process save as necessary
                if update_f_name:
                    account.update_details(f_name=f_name.get())
                if update_l_name:
                    account.update_details(l_name=l_name.get())
                if update_top_ups:
                    account.update_details(balance=top_up_total)
                if update_notes:
                    account.update_details(notes=notes.get())

                for discount_ in active_discounts:
                    saved_discounts = [(discount_[1], "%" if discount_[2] == 0 else "£", *discount_[3:]) for discount_
                                       in get_account_conditions(account_id=account_info[0], discount=True)]
                    if discount_ not in saved_discounts:
                        insert_new("accounts_discounts", [account_info[0], discount_[0],
                                                          1 if discount_[1] == "£" else 0, *discount_[2:4], 0,
                                                          datetime.now()])
                for limit_ in active_limits:
                    saved_limits = [(limit_[1:]) for limit_ in get_account_conditions(account_id=account_info[0],
                                                                                      spending_limit=True)]
                    if limit_ not in saved_limits:
                        insert_new("accounts_spending_limit", [account_info[0], *limit_[:4], 0, datetime.now()])
                for allowance_ in active_allowances:
                    saved_allowances = [(allowance_[1:]) for allowance_ in
                                        get_account_conditions(account_id=account_info[0], sub_zero_allowance=True)]
                    if allowance_ not in saved_allowances:
                        insert_new("accounts_sub_zero_allowance", [account_info[0], *allowance_[:3], 0, datetime.now()])

                self.accounts()
            else:
                messagebox.showinfo("Error Saving Item", "Could not save item due to the following error:\n\n{0}"
                                                         "".format(result[1]))

        def validate_details():

            try:
                float(budget_amount.get()[1:])
            except ValueError:
                return False, "Budget must be a valid number"

            if f_name.get() == "" or l_name.get() == "":
                return False, "Name cannot be empty"

            return True, ""

        def display_conditions(conditions, page=1, discount_=False, limit_=False):

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

                Label(from_frame, text="From {}".format(_from), font=font2).grid(row=0, column=0)
                if _from is "":
                    from_hour.set("00"), from_min.set("00")
                    add_datetime_entries(from_frame, from_date, from_hour, from_min)

            def add_until(until, until_frame, length, _for, until_date, until_hour, until_min):
                [widget.destroy() for widget in until_frame.winfo_children()]

                Label(until_frame, text="{}".format(
                    until if until == "Indefinitely" else "For A Duration Of " if until == "time" else "Until"),
                      font=font2).grid(row=0, column=0)
                if until == "time":
                    Entry(until_frame, textvariable=length, font=font2, width=2).grid(row=0, column=1)
                    _for.set("day(s)")
                    _opt_menu = OptionMenu(until_frame, _for, "hour(s)", "day(s)", "week(s)", "month(s)", "year(s)")
                    _opt_menu.config(font=font2)
                    _opt_menu.nametowidget(_opt_menu.menuname).configure(font=font2)
                    _opt_menu.grid(row=0, column=2)
                elif until == "until":
                    until_hour.set("00"), until_min.set("00")
                    add_datetime_entries(until_frame, until_date, until_hour, until_min)

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
                display_conditions(get_discounts() if discount_ else get_limits() if limit_ else get_allowances(),
                                   page=page_, discount_=discount_, limit_=limit_)

            def add_from_():
                self._empty_frame(from_frame)

                Button(from_frame, text="Now", font=font2,
                       command=lambda: self.combine_funcs(
                           add_from(from_frame, "Now", *froms),
                           Button(from_frame, text="Reset", font=font2, command=lambda: add_from_()).grid(row=0,
                                                                                                          column=1)),
                       bg=from_bg).grid(row=0, column=0)
                Button(from_frame, text="Specific Date/Time", font=font2,
                       command=lambda: self.combine_funcs(
                           add_from(from_frame, "", *froms),
                           Button(from_frame, text="Reset", font=font2, command=lambda: add_from_()).grid(row=0,
                                                                                                          column=4)),
                       bg=from_bg).grid(row=0, column=1)

            def add_until_():
                self._empty_frame(until_frame)

                Button(until_frame, text="Indefinitely", font=font2, bg=until_bg,
                       command=lambda: self.combine_funcs(
                           add_until("Indefinitely", until_frame, length, _for, *untils),
                           Button(until_frame, text="Reset", font=font2, command=lambda: add_until_()
                                  ).grid(row=0, column=1))).grid(row=0, column=0)
                Button(until_frame, text="For Given Time", font=font2, bg=until_bg,
                       command=lambda: self.combine_funcs(
                           add_until("time", until_frame, length, _for, *untils),
                           Button(until_frame, text="Reset", font=font2, command=lambda: add_until_()
                                  ).grid(row=0, column=4))).grid(row=0, column=1)
                Button(until_frame, text="Until Given Date", font=font2, bg=until_bg,
                       command=lambda: self.combine_funcs(
                           add_until("until", until_frame, length, _for, *untils),
                           Button(until_frame, text="Reset", font=font2, command=lambda: add_until_()
                                  ).grid(row=0, column=4))).grid(row=0, column=2)

            self._frame_reset(self.main_frame)
            self.back_btn.config(command=lambda: self.account(account_info))

            # titles
            title_width, title_padx, title_pady = 10, 10, 10

            Label(self.main_frame, text="Amount", font=font1, bg=self.background_bg, width=title_width).grid(
                row=0, column=0, padx=title_padx, pady=title_pady, sticky=E + W)

            if discount_ or limit_:
                Label(self.main_frame, text="Per" if limit_ else "Type", font=font1, bg=self.background_bg,
                      width=title_width).grid(row=0, column=1, padx=title_padx, pady=title_pady, sticky=E + W)

            Label(self.main_frame, text="Active From", font=font1, bg=self.background_bg, width=title_width).grid(
                row=0, column=2, padx=title_padx, pady=title_pady, sticky=E + W)
            Label(self.main_frame, text="Active Until", font=font1, bg=self.background_bg, width=title_width).grid(
                row=0, column=3, padx=title_padx, pady=title_pady, sticky=E + W)

            row_ = int(1)

            # list items
            total_conditions, condition_limit = len(conditions), 10
            conditions = conditions[(page - 1) * condition_limit:page * condition_limit] \
                if total_conditions >= page * condition_limit else conditions[(page - 1) * condition_limit:]

            bgs, width, padx, pady, sticky = ["grey60", "grey40"], 10, 0, 2, E + W
            for condition in conditions:
                bg = bgs[conditions.index(condition) % 2]

                Label(self.main_frame, text=condition[0], font=font2, bg=bg, width=width).grid(
                    row=row_, column=0, padx=padx, pady=pady, sticky=sticky)
                if discount_ or limit_:
                    Label(self.main_frame, text=condition[1], font=font2, bg=bg, width=width).grid(
                        row=row_, column=1, padx=padx, pady=pady, sticky=sticky)
                    from_date, until_date = condition[2], condition[3]
                else:
                    from_date, until_date = condition[1], condition[2]
                until_date = "Indefinitely" if until_date == "" or until_date == 0 else until_date
                Label(self.main_frame, text=from_date, font=font2, bg=bg, width=width).grid(
                    row=row_, column=2, padx=padx, pady=pady, sticky=sticky)
                Label(self.main_frame, text=until_date, font=font2, bg=bg, width=width).grid(
                    row=row_, column=3, padx=padx, pady=pady, sticky=sticky)

                Button(self.main_frame, text="DELETE", bg='red2', font=font1, width=width,
                       command=lambda condition_=condition: self.combine_funcs(
                           account.delete_discount(condition_[-1]) if discount_
                           else account.delete_spending_limit(condition_[-1]) if limit_
                           else account.delete_sub_zero_allowance(condition_[-1]),
                           display_conditions(get_discounts() if discount_ else get_limits() if limit_
                                              else get_allowances(), discount_=discount_, limit_=limit_))
                       ).grid(row=row_, column=4, padx=padx, pady=pady, sticky=sticky)

                row_ += 1

            # new item
            item_vars = list()

            from_bg, until_bg = "firebrick1", "SlateBlue1"
            amount = StringVar()
            item_vars.append(amount)
            Entry(self.main_frame, font=font2, textvariable=amount, width=10).grid(row=row_, column=0, padx=100)

            if discount_ or limit_:
                if discount_:
                    discount_type_, discount_drop_down_ = self.create_type_dropdown(self.main_frame)
                    discount_drop_down_.grid(row=row_, column=1, padx=60, sticky=S)
                    item_vars.append(discount_type_)
                else:
                    limit_per_, limit_drop_down_ = self.create_limit_drop_down(self.main_frame)
                    item_vars.append(limit_per_)
                    limit_drop_down_.grid(row=row_, column=1, padx=60, sticky=S)

            from_frame = Frame(self.main_frame)
            from_frame.grid(row=row_, column=2, sticky=S, padx=30)
            froms = [StringVar(), StringVar(), StringVar()]
            add_from_()

            until_frame = Frame(self.main_frame)
            until_frame.grid(row=row_, column=3, sticky=S, padx=30)
            untils = [StringVar(), StringVar(), StringVar()]
            length, _for = StringVar(), StringVar()
            add_until_()

            def get_formmated_dates():
                return [datetime.strptime(date, "%Y-%m-%d %H:%M:%S") if date != "" else date
                        for date in calc_dates([*froms, *untils], length, _for)]

            Button(self.main_frame, text="ADD", bg='orange', font=font1,
                   command=lambda: self.combine_funcs(
                       account.add_discount(float(amount.get()), 1 if discount_type_.get() == "£" else 0,
                                            *get_formmated_dates())
                       if discount_ else
                       account.add_spending_limit(float(amount.get()), limit_per_.get(), *get_formmated_dates())
                       if limit_ else
                       account.add_sub_zero_allowance(float(amount.get()), *get_formmated_dates()), call_yourself())
                   if amount.get() != "" else messagebox.showerror("Null Error", "Amount cannot be left empty")
                   ).grid(row=row_, column=4, sticky=S + E + W)

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

        def get_discounts():
            discounts_ = list()
            for discount in get_account_conditions(account_id=account_info[0], discount=True):

                discounts_.append((discount[1], "%" if discount[2] == 0 else "£", *discount[3:]))
            return discounts_

        def get_limits():
            limits_ = list()
            for limit in get_account_conditions(account_id=account_info[0], spending_limit=True):
                limits_.append((limit[1:]))
            return limits_

        def get_allowances():
            allowances_ = list()
            for allowance in get_account_conditions(account_id=account_info[0], sub_zero_allowance=True):
                allowances_.append((allowance[1:]))
            return allowances_

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
                            command=lambda: self.combine_funcs(top_up(), top_up_amount.set("")))
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
                                     command=lambda: display_conditions(active_allowances))
        active_allowances_btn.grid(row=0, column=0)

        # accounts notes
        notes_frame = _create_basic_frame("Notes")
        notes = StringVar()
        Entry(notes_frame, textvariable=notes, font=(self.font_name, 16)).pack(fill=X)

        actions_frame = Frame(self.main_frame, bg=self.background_bg)
        actions_frame.grid(row=7, column=0, pady=10, sticky=E + W)
        actions_bg = "DarkOrange2"

        Grid.rowconfigure(self.main_frame, 7, weight=1)
        [Grid.columnconfigure(actions_frame, i, weight=1) for i in range(3)]

        actions_cancel_btn = Button(actions_frame, text="Cancel", font=(self.font_name, 20, "bold"), bg=actions_bg,
                                    command=lambda: self.accounts())
        actions_cancel_btn.grid(row=0, column=0, sticky=E + W, padx=(60, 0))

        actions_save_btn = Button(actions_frame, text="Save", font=(self.font_name, 20, "bold"), bg=actions_bg,
                                  command=lambda: save_account(validate_details()))
        actions_save_btn.grid(row=0, column=1, sticky=E + W, padx=60)

        confirm_msg = "Please confirm that you want to delete this account.\n\nPlease click Yes to confirm."
        actions_delete_btn = Button(actions_frame, text="Delete", font=(self.font_name, 20, "bold"), bg=actions_bg,
                                    command=lambda: self.combine_funcs(account.delete_account(), self.accounts())
                                    if messagebox.askyesno("Are you sure?", confirm_msg) else None)
        actions_delete_btn.grid(row=0, column=2, sticky=E + W, padx=(0, 60))

        account_id_lbl = Label(actions_frame, text=account_info[0] if account_info is not None else "",
                               bg=self.background_bg, font=(self.font_name, 12, "bold"))
        account_id_lbl.grid(row=0, column=2, sticky=E, padx=(0, 20))

        if account_info is not None:  # account already exists and thus in editing mode
            f_name.set(account_info[1])
            l_name.set(account_info[2])

            budget_amount.set("£{0:.2f}".format(account_info[3]))

            discounts = get_discounts()
            [active_discounts.append(discount) for discount in discounts]
            active_discounts_btn.config(state=NORMAL, text="{0} Active".format(len(discounts)))

            limits = get_limits()
            [active_limits.append(limit) for limit in limits]
            active_limits_btn.config(state=NORMAL, text="{0} Active".format(len(limits)))

            allowances = get_allowances()
            [active_allowances.append(allowance) for allowance in allowances]
            active_allowances_btn.config(state=NORMAL, text="{0} Active".format(len(allowances)))

            notes.set(account_info[4])

    def products(self):
        self.page_populator("Products")

    def product(self, account_info=None):
        pass

    def display_history(self, field_name, item_id, caller_id, caller_params, page=1):
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

    def page_populator(self, caller):
        self._frame_reset(self.main_frame)
        self.back_btn.config(command=lambda: self.setup())

        call_item = self.accounts if caller == "Accounts" else self.products

        items = get_accounts() if caller == "Accounts" else get_products()

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
            Button(item_frame, text=item[1] + " " + item[2] if caller == "Accounts" else item[1], bg="orange",
                   font=font, width=20, height=2,
                   command=lambda item_info=item: call_item(item_info)).grid(row=row, column=col, pady=20)
            Grid.columnconfigure(item_frame, col, weight=1)
            col += 1
            if col == 5:
                col, row = 0, row + 1
                Grid.rowconfigure(item_frame, row, weight=1)

        bg = "salmon"
        initial_dir, title_1 = "%documents%", "Select the File to Import From"
        file_types = ('csv files only', '*.csv')

        if caller == "Accounts":
            msg = "Accounts can be imported from a csv file where each line is a new account. Each account must have " \
                  "the 3 fields \"First Name\", \"Last Name\" and \"Budget\" delimited by commas."
        else:
            msg = "Products can be imported from a csv file where each line is a new product. Each product must have " \
                  "the 3 fields \"Product Name\", \"Cost Price\" and \"Sale Price\" delimited by commas."
        msg += "\n\nIs the intended CSV file in the correct format?"

        import_btn = Button(item_actions_frame, text="IMPORT", font=font, bg=bg, width=12,
                            command=lambda: self.combine_funcs(
                                self.import_items(filedialog.askopenfilename(initialdir=initial_dir, title=title_1,
                                                                             filetypes=[file_types]), caller=caller),
                                call_item()) if messagebox.askyesno("Import Details", msg) else None)
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

    def transactions(self):
        self._frame_reset(self.main_frame)
        self.back_btn.config(command=lambda: self.main_menu())

    def create_type_dropdown(self, frame, font=("Calibri", 20, "bold")):
        type_ = StringVar()
        type_.set("%")
        drop_down = OptionMenu(frame, type_, "%", "£")
        drop_down.config(font=font, bg=self.background_bg)
        drop_down.nametowidget(drop_down.menuname).configure(font=font, bg=self.background_bg)
        return type_, drop_down

    def create_limit_drop_down(self, frame, font=("Calibri", 20, "bold")):
        limit_ = StringVar()
        limit_.set("day")
        drop_down = OptionMenu(frame, limit_, "transaction", "day", "week", "month", "year")
        drop_down.config(font=font)
        drop_down.nametowidget(drop_down.menuname).configure(font=font)

        return limit_, drop_down

    def _frame_reset(self, frame):
        self._empty_frame(frame)

        [Grid.rowconfigure(frame, i, weight=0) for i in range(20)]
        [Grid.columnconfigure(frame, i, weight=0) for i in range(20)]

    def _empty_frame(self, frame):
        [widget.destroy() for widget in frame.winfo_children()]

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
                        new_item.update_details(balance=float(item[2].strip("£")))
                    else:
                        new_item.add_product(p_name=item[0])
                        new_item.update_details(cost_price=float(item[1].strip("£")),
                                                sale_price=float(item[2].strip("£")))
                    successful += 1
                except:
                    new_item.delete_account() if caller == "Accounts" else new_item.delete_product()
        except FileNotFoundError:
            pass

        messagebox.showinfo("Import Results", "Out of all {0} items found {1} were successful.".format(len(items),
                                                                                                       successful))

    def combine_funcs(*funcs):
        """enables multiple functions to be called serially inline"""

        def combined_func(*args, **kwargs):
            [f(*args, **kwargs) for f in funcs]

        return combined_func


if __name__ == '__main__':
    GUI()
