from datetime import datetime


class Product:
    def __init__(self, p_name, product_id=None, cost=0, price=0, quantity=0, purchase_limit=None, discount=None,
                 offer=None, notes="", date_created=None):
        """initialises product object with all attributes"""

        self.product_id = product_id if product_id is not None else self._get_new_id()
        self.name = p_name
        self.cost = cost
        self.price = price
        self.quantity = quantity
        self.purchase_limit = purchase_limit
        self.discount = discount
        self.offer = offer
        self.notes = notes
        self.date_created = date_created if date_created is not None else datetime.now()

    def add_product(self):
        """adds product to database"""

        pass

    def delete_product(self):
        """deletes product from database using product_id"""

        if self._get_new_id() == self.product_id:
            raise ValueError("product not in database (thus it cannot be deleted)")

        pass

    def _get_new_id(self):
        """gets last used id and adds 1 for a new unique id"""

        pass

    def update_product(self):
        """updates product in database with any new data"""
        # note: cannot just run the delete and add functions as the database could have related records for the product,
        # e.g. discounts

        if self._get_new_id() == self.product_id:
            raise ValueError("product not in database (thus it cannot be updated)")

        pass

    def add_discount(self, amount, type_):
        """adds discount to database for the product to be applied to all purchases of the product"""

        pass

    def delete_discount(self):
        """deletes discount from database for the product"""

        pass

    def add_purchase_limit(self):
        """adds spending limit to database for the product"""

        pass

    def delete_purchase_limit(self):
        """deletes spending limit from database for the product"""

        pass

    def add_offer(self, buy_x, get_y=None, z_off=None):
        """adds offer to database for the product"""

        if get_y is not None and z_off is not None:
            raise ValueError("Cannot use both get_y and z_off for the same offer")

        pass

    def delete_offeer(self):
        """deletes offer from database for the product"""

        pass

