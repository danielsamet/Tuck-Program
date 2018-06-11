from datetime import datetime


class Account:
    def __init__(self,  f_name, l_name, account_id=None, budget=0, spending_limit=None, discount=None,
                 sub_zero_allowance=None, notes="", date_created=None):
        """initialises account object with all attributes"""

        self.account_id = account_id if account_id is not None else self._get_new_id()
        self.f_name = f_name
        self.l_name = l_name
        self.budget = budget
        self.spending_limit = spending_limit
        self.discount = discount
        self.sub_zero_allowance = sub_zero_allowance
        self.notes = notes
        self.date_created = date_created if date_created is not None else datetime.now()

    def add_account(self):
        """adds account to database"""

        pass

    def delete_account(self):
        """deletes account from database using account_id"""

        pass

    def update_account(self):
        """updates account in database with any new data"""
        # note: cannot just run the delete and add functions as the database could have related records for the account,
        # e.g. discounts

        pass

    def _get_new_id(self):
        """gets last used id and adds 1 for a new unique id"""

        pass

    def add_discount(self, amount, type_):
        """adds discount to database for the account to be applied to all purchases by account"""

        pass

    def delete_discount(self):
        """deletes discount from database for the account"""

        pass

    def add_spending_limit(self):
        """adds spending limit to database for the account"""

        pass

    def delete_spending_limit(self):
        """deletes spending limit from database for the account"""

        pass

    def add_sub_zero_allowance(self):
        """adds sub-zero allowance to database for the account"""

        pass

    def delete_sub_zero_allowance(self):
        """deletes sub-zero allowance from database for the account"""

        pass

