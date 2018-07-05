from tkinter import *
from tkinter import ttk
from inherit_parent import Inherit
from OLD import date_picker


class GUI:
    def __init__(self):
        root = Tk()

        root.state('zoomed')

        width, height = 1000, 700
        root.minsize(width, height)

        top_bar = Frame(root)
        top_bar.grid(row=0, column=0, sticky=E + W)

        Grid.columnconfigure(root, 0, weight=1)

        back_btn = Button(top_bar, text="<--", bg='blue', font=("Calibri", 20, "bold"), width=10, height=2)
        back_btn.grid(row=0, column=0, sticky=W)

        home_btn = Button(top_bar, text="HOME", bg='blue', font=("Calibri", 20, "bold"), width=10, height=2,
                          command=lambda: self.main_menu())
        home_btn.grid(row=0, column=1, sticky=E)

        Grid.columnconfigure(top_bar, 0, weight=1)
        Grid.columnconfigure(top_bar, 1, weight=1)

        self.main_frame = Frame(root)
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

        self.main_menu()

        root.mainloop()

    def main_menu(self):
        self._frame_reset(self.main_frame)

        setup_btn = Button(self.main_frame, text="SETUP", bg='orange', font=("Calibri", 28, "bold"), width=18, height=3,
                           command=lambda: self.setup())
        setup_btn.grid(row=0, column=0)

        transaction_btn = Button(self.main_frame, text="TRANSACTIONS", bg='orange', font=("Calibri", 28, "bold"),
                                 width=18, height=3, command=lambda: self.transactions())
        transaction_btn.grid(row=0, column=1)

        Grid.columnconfigure(self.main_frame, 0, weight=1), Grid.columnconfigure(self.main_frame, 1, weight=1)
        Grid.rowconfigure(self.main_frame, 0, weight=1)

    def setup(self):
        self._frame_reset(self.main_frame)

        accounts_btn = Button(self.main_frame, text="ACCOUNTS", bg='orange', font=("Calibri", 28, "bold"), width=18,
                              height=3, command=lambda: self.accounts())
        accounts_btn.grid(row=0, column=0)

        products_btn = Button(self.main_frame, text="PRODUCTS", bg='orange', font=("Calibri", 28, "bold"), width=18,
                              height=3, command=lambda: self.products())
        products_btn.grid(row=0, column=1)

        Grid.columnconfigure(self.main_frame, 0, weight=1), Grid.columnconfigure(self.main_frame, 1, weight=1)
        Grid.rowconfigure(self.main_frame, 0, weight=1)

    def accounts(self):
        self._frame_reset(self.main_frame)

        account_frame = Frame(self.main_frame)
        account_frame.grid(row=0, column=0, sticky=E + W)

        account_actions_frame = Frame(self.main_frame)
        account_actions_frame.grid(row=1, column=0, sticky=S + E + W)

        Grid.columnconfigure(self.main_frame, 0, weight=1)
        Grid.rowconfigure(self.main_frame, 0, weight=1), Grid.rowconfigure(self.main_frame, 1, weight=0)

        col, row = int(), int()
        Grid.rowconfigure(account_frame, row, weight=1)
        Grid.columnconfigure(account_frame, col, weight=1)
        for account in self._get_accounts():
            Button(account_frame, text=account[1] + " " + account[2], bg="goldenrod", font=("Calibri", 16, "bold"),
                   width=20, height=2, command=lambda account_info=account: self.account(account_info=account_info))\
                .grid(row=row, column=col, pady=20)
            Grid.columnconfigure(account_frame, col, weight=1)
            col += 1
            if col == 5:
                col = 0
                row += 1
                Grid.rowconfigure(account_frame, row, weight=1)

        import_btn = Button(account_actions_frame, text="IMPORT", font=("Calibri", 16, "bold"), bg="sandy brown",
                            width=12)
        import_btn.grid(row=0, column=0)
        add_btn = Button(account_actions_frame, text="ADD", font=("Calibri", 16, "bold"), bg="sandy brown", width=12)
        add_btn.grid(row=0, column=1)
        previous_btn = Button(account_actions_frame, text="PREVIOUS", font=("Calibri", 16, "bold"), bg="sandy brown",
                              width=12)
        previous_btn.grid(row=0, column=2)
        page_lbl = Label(account_actions_frame, text="Page 1 of 1", font=("Calibri", 16, "bold"), bg="sandy brown",
                         width=12)
        page_lbl.grid(row=0, column=3)
        next_btn = Button(account_actions_frame, text="NEXT", font=("Calibri", 16, "bold"), bg="sandy brown", width=12)
        next_btn.grid(row=0, column=4)

        [Grid.columnconfigure(account_actions_frame, i, weight=1) for i in range(5)]

    def _get_accounts(self, _all=True, f_name=False, l_name=False, top_ups=False, notes=False):
        select = "SELECT accounts.account_ID"
        join = str()
        where = ""

        if f_name or _all:
            select += ", f.name"
            join += "INNER JOIN (SELECT MAX(date) mxdate, account_ID, name from accounts_f_name GROUP BY account_ID) " \
                    "as f ON accounts.account_ID=f.account_ID"

            # where += "WHERE f.date=(SELECT MAX(accounts_f_name.date) FROM accounts_f_name) "

        if l_name or _all:
            select += ", l.name"
            join += " INNER JOIN (SELECT MAX(date) mxdate, account_ID, name from accounts_l_name GROUP BY account_ID)" \
                    " as l ON accounts.account_ID=l.account_ID"

        if top_ups or _all:
            select += ", t.amount"
            join += " INNER JOIN "
            if top_ups:  # get all
                join += "accounts_top_ups"
            else:  # only get last
                join += "(SELECT MAX(date) mxdate, account_ID, amount from accounts_top_ups GROUP BY account_ID)"
            join += "as t ON accounts.account_ID=t.account_ID"

        if notes or _all:
            select += ", n.notes"
            join += " INNER JOIN "
            if notes:  # get all
                join += "accounts_notes"
            else:  # only get last
                join += "(SELECT MAX(date) mxdate, account_ID, notes from accounts_notes GROUP BY account_ID)"
            join += "as n ON accounts.account_ID=n.account_ID"

        sql_command = select + " FROM accounts " + join + where
        return Inherit()._db_execute(sql_command)

    def _get_conditions(self, discount=False):
        select = "SELECT accounts.account_ID"
        join = str()
        where = "WHERE "

        if discount:
            select += ", d.amount, d.type, d.start_date, d.end_date"
            join += "INNER JOIN accounts_discounts as d ON accounts.account_ID=d.account_ID "
            where += "AND d.start_date >= datetime() >= d.end_date " \
                     "AND d.void <> 1 "

    def account(self, account_info):
        self._frame_reset(self.main_frame)

        self.main_frame.config(bg='grey30')
        Grid.columnconfigure(self.main_frame, 0, weight=1)

        font1, font2 = ("Calibri", 20, "bold"), ("Calibri", 20)
        row = int()

        def create_basic_frame(lbl_txt):
            nonlocal row

            frame = Frame(self.main_frame, bg="grey60")
            frame.grid(row=row, column=0, pady=10, sticky=E + W)
            Grid.rowconfigure(self.main_frame, row, weight=1)
            [Grid.columnconfigure(frame, i, weight=1) for i in range(3)]
            Label(frame, text=lbl_txt, font=font1, width=20).grid(row=0, column=0, sticky=W)
            centre_frame = Frame(frame)
            centre_frame.grid(row=0, column=1, sticky=E + W)
            Grid.columnconfigure(frame, 1, weight=100)
            Button(frame, text="See History", font=font2, bg='red', width=15).grid(row=0, column=2, sticky=E)

            row += 1

            return centre_frame

        def _add_condition(frame, level=1):
            from_bg, until_bg = "firebrick1", "SlateBlue1"

            def add_datetime_entries(frame_, date, hour, min_):
                date_picker.Datepicker(frame_, datevar=date, font=font2, entrywidth=10,
                                       entrystyle="EntryStyle.TEntry").grid(row=0, column=1)
                hours = OptionMenu(frame_, hour, *[str("{0:02d}".format(num)) for num in range(0, 24)])
                hours.config(font=font2)
                hours.nametowidget(hours.menuname).configure(font=("Calibri", 16))
                hours.grid(row=0, column=2)
                mins = OptionMenu(frame_, min_, *[str("{0:02d}".format(num)) for num in range(0, 60)])
                mins.config(font=font2)
                mins.nametowidget(hours.menuname).configure(font=("Calibri", 16))
                mins.grid(row=0, column=3)

            def add_from_conditions():
                def add_from(_from):
                    [widget.destroy() for widget in from_frame.winfo_children()]

                    Label(from_frame, text="From {}".format(_from), font=font2).grid(row=0, column=0)
                    if _from is "":
                        date, hour, min_ = StringVar(), StringVar(), StringVar()
                        hour.set("00"), min_.set("00")
                        add_datetime_entries(from_frame, date, hour, min_)

                from_btn.destroy()
                from_frame = Frame(frame)
                from_frame.grid(row=0, column=0, sticky=W)
                Button(from_frame, text="Now", font=font2, command=lambda: add_from("Now"), bg=from_bg
                       ).grid(row=0, column=0)
                Button(from_frame, text="Specific Date/Time", font=font2, command=lambda: add_from(""), bg=from_bg
                       ).grid(row=0, column=1)
                Button(frame, text="Cancel", font=font2, command=lambda: _add_condition(frame)).grid(row=0, column=2)

            def add_until_conditions():
                def add_until(until):
                    [widget.destroy() for widget in until_frame.winfo_children()]

                    Label(until_frame, text="{}".format(
                        until if until == "Indefinitely" else "For A Duration Of " if until == "time" else "Until"),
                          font=font2).grid(row=0, column=0)
                    if until == "time":
                        Entry(until_frame, font=font2, width=2).grid(row=0, column=1)
                        _for = StringVar()
                        _for.set("day(s)")
                        _opt_menu = OptionMenu(until_frame, _for, "hour(s)", "day(s)", "week(s)", "month(s)",
                                               "year(s)")
                        _opt_menu.config(font=font2)
                        _opt_menu.nametowidget(_opt_menu.menuname).configure(font=font2)
                        _opt_menu.grid(row=0, column=2)
                    elif until == "until":
                        date, hour, min_ = StringVar(), StringVar(), StringVar()
                        hour.set("00"), min_.set("00")
                        add_datetime_entries(until_frame, date, hour, min_)

                until_btn.destroy()
                until_frame = Frame(frame)
                until_frame.grid(row=0, column=1, sticky=W)
                Button(until_frame, text="Indefinitely", font=font2, command=lambda: add_until("Indefinitely"),
                       bg=until_bg).grid(row=0, column=0)
                Button(until_frame, text="For Given Time", font=font2, command=lambda: add_until("time"), bg=until_bg
                       ).grid(row=0, column=1)
                Button(until_frame, text="Until Given Date", font=font2, command=lambda: add_until("until"), bg=until_bg
                       ).grid(row=0, column=2)
                Button(frame, text="Cancel", font=font2, command=lambda: _add_condition(frame)).grid(row=0, column=2)

            if level == 0:
                self.empty_frame(frame)
                Button(frame, text="Add Time Condition", font=font2,
                       command=lambda: _add_condition(frame)).grid(row=0, column=0)
            else:
                self.empty_frame(frame)
                from_btn = Button(frame, text="From", font=font2, bg=from_bg,
                                  command=lambda: add_from_conditions())
                from_btn.grid(row=0, column=0)
                until_btn = Button(frame, text="Until", font=font2, bg=until_bg,
                                   command=lambda: add_until_conditions())
                until_btn.grid(row=0, column=1, padx=30)
                cancel = Button(frame, text="Cancel", font=font2, command=lambda: _add_condition(frame, level=0))
                cancel.grid(row=0, column=2)

        def top_up():
            try:
                budget_amount.set("£{0:.2f}".format(float(budget_amount.get()[1:]) + float(top_up_amount.get())))
            except ValueError:
                print("gotcha! can't use", top_up_amount.get(), "\nMust be floatable ;-)")

        f_name_frame = create_basic_frame("First Name")
        f_name = StringVar()
        Entry(f_name_frame, textvariable=f_name, font=font2).grid(row=0, column=0, sticky=W)

        l_name_frame = create_basic_frame("Last Name")
        l_name = StringVar()
        Entry(l_name_frame, textvariable=l_name, font=font2).grid(row=0, column=0, sticky=W)

        budget_frame = create_basic_frame("Budget")
        budget_amount = StringVar()
        budget_amount.set("£0.00")
        budget_amount_label = Label(budget_frame, textvariable=budget_amount, font=font1)
        budget_amount_label.grid(row=0, column=0, sticky=W)
        top_up_amount = StringVar()
        top_up_amount.set("")
        top_up_entry = Entry(budget_frame, textvariable=top_up_amount, font=font2, width=6)
        top_up_entry.grid(row=0, column=1, sticky=W, padx=20)
        top_up_btn = Button(budget_frame, text="Top Up", bg='green', font=font2, command=lambda: top_up())
        top_up_btn.grid(row=0, column=2, sticky=W)

        discount_frame = create_basic_frame("Discount")
        _type = StringVar()
        _type.set("%")
        opt_menu = OptionMenu(discount_frame, _type, "%", "£")
        opt_menu.config(font=("Calibri", 20, "bold"))
        opt_menu.nametowidget(opt_menu.menuname).configure(font=("Calibri", 20, "bold"))
        opt_menu.grid(row=0, column=0, sticky=W)
        discount_amount = DoubleVar()
        discount_amount.set("0.00")
        discount_entry = Entry(discount_frame, font=("Calibri", 20), textvariable=discount_amount, width=6)
        discount_entry.grid(row=0, column=1, sticky=W, padx=10)
        discount_condition_frame = Frame(discount_frame)
        discount_condition_frame.grid(row=0, column=2, sticky=W)
        _add_condition(discount_condition_frame, 0)

        spending_limit_frame = create_basic_frame("Spending Limit")
        spending_limit_amount = DoubleVar()
        spending_limit_amount.set("0.00")
        spending_limit_entry = Entry(spending_limit_frame, font=("Calibri", 20), textvariable=spending_limit_amount,
                                     width=6)
        spending_limit_entry.grid(row=0, column=0, sticky=W, padx=(0, 30))
        spending_limit_condition_frame = Frame(spending_limit_frame)
        spending_limit_condition_frame.grid(row=0, column=1)
        _add_condition(spending_limit_condition_frame, 0)

        sub_zero_allowance_frame = create_basic_frame("Sub Zero Allowance")
        sub_zero_allowance_amount = DoubleVar()
        sub_zero_allowance_amount.set("0.00")
        sub_zero_allowance_entry = Entry(sub_zero_allowance_frame, font=("Calibri", 20), width=6,
                                         textvariable=sub_zero_allowance_amount)
        sub_zero_allowance_entry.grid(row=0, column=0, sticky=W, padx=(0, 30))
        sub_zero_allowance_condition_frame = Frame(sub_zero_allowance_frame)
        sub_zero_allowance_condition_frame.grid(row=0, column=1)
        _add_condition(sub_zero_allowance_condition_frame, 0)

        notes_frame = create_basic_frame("Notes")
        notes = StringVar()
        Entry(notes_frame, textvariable=notes, font=("Calibri", 16)).pack(fill=X)

        actions_frame = Frame(self.main_frame)
        actions_frame.grid(row=7, column=0, pady=10, sticky=E + W)
        Grid.rowconfigure(self.main_frame, 7, weight=1)
        [Grid.columnconfigure(actions_frame, i, weight=1) for i in range(3)]
        actions_cancel_btn = Button(actions_frame, text="Cancel", font=("Calibri", 20, "bold"), bg='orange')
        actions_cancel_btn.grid(row=0, column=0, sticky=E + W, padx=(60, 0))
        actions_save_btn = Button(actions_frame, text="Save", font=("Calibri", 20, "bold"), bg='orange')
        actions_save_btn.grid(row=0, column=1, sticky=E + W, padx=60)
        actions_delete_btn = Button(actions_frame, text="Delete", font=("Calibri", 20, "bold"), bg='orange')
        actions_delete_btn.grid(row=0, column=2, sticky=E + W, padx=(0, 60))

    def products(self):
        self._frame_reset(self.main_frame)

    def transactions(self):
        self._frame_reset(self.main_frame)

    def _frame_reset(self, frame):
        self.empty_frame(frame)

        [Grid.rowconfigure(frame, i, weight=0) for i in range(20)]
        [Grid.columnconfigure(frame, i, weight=0) for i in range(20)]

    def empty_frame(self, frame):
        [widget.destroy() for widget in frame.winfo_children()]

    def combine_funcs(*funcs):
        """enables multiple functions to be called serially inline"""

        def combined_func(*args, **kwargs):
            [f(*args, **kwargs) for f in funcs]

        return combined_func


if __name__ == '__main__':
    GUI()
