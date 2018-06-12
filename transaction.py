from datetime import datetime


class Transaction:
    """loads provided transaction details into the object with ability to run the functions below on the object
    accordingly"""

    def __init__(self, account, product, quantity, void=False):
        """initialises transaction object with all attributes"""

        self.account = account
        self.product = product
        self.quantity = quantity
        self.date = datetime.now()
        self.void = void

    def record_transaction(self):
        """records the transaction in the database"""

        pass

    def revert_tranasaction(self):
        """reverts the transaction in database by voiding it and then reverting its effects (refunding etc.)"""

        pass
