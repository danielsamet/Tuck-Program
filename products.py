from datetime import datetime


class Product:
    def __init__(self, p_name, product_id=None, supplier="N/A", cost_price=0, sale_price=0, quantity=0,
                 purchase_limit=None, discount=None, offer=None, notes="", date_created=None, void=False):
        """initialises product object with all attributes"""

        self.product_id = product_id if product_id is not None else self._get_new_id()
        self.name = p_name
        self.supplier = supplier
        self.cost_price = cost_price
        self.sale_price = sale_price
        self.quantity = quantity
        self.purchase_limit = purchase_limit
        self.discount = discount
        self.offer = offer
        self.notes = notes
        self.date_created = date_created if date_created is not None else datetime.now()
        self.void = void

    def add_product(self):
        """adds product to database"""

        pass

    def delete_product(self):
        """deletes product from database using product_id"""

        if self._get_new_id() == self.product_id:
            raise ValueError("product not in database (thus it cannot be deleted)")

        pass

    def update_product(self):
        """updates product in database with any new data"""
        # note: cannot just run the delete and add functions as the database could have related records for the product,
        # e.g. discounts

        if self._get_new_id() == self.product_id:
            raise ValueError("product not in database (thus it cannot be updated)")

        pass

    def _get_new_id(self):
        """gets last used id and adds 1 for a new unique id"""

        pass

    def update_cost_price(self):
        """updates cost of product in database"""

        pass

    def update_sale_price(self):
        """updates price of product in database"""

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

