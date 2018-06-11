class Account:
    def __init__(self, account):
        """initialises account object with all attributes"""

        if type(account) != "list" and len(account) != 9:
            raise RuntimeError("Parameter must be a list with 9 items")

        self.account_id = account[0]
        self.f_name = account[1]
        self.l_name = account[2]
        self.budget = account[3]
        self.discount = account[4]
        self.spending_limit = account[5]
        self.sub_zero_allowance = account[6]
        self.notes = account[7]
        self.date_created = account[8]

    def add_account(self, f_name, l_name, budget=0, discount=0, spending_limit=0, sub_zero_allowance=0, notes=""):
        """adds an account to database"""

        pass

    def delete_account(self, account_id):
        """deletes an account from database using account_id"""

        pass

    def import_accounts(self, csv_address):
        """imports accounts from a given csv address"""

        pass
