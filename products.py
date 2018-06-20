from datetime import datetime
from inherit_parent import Inherit


class Product(Inherit):
    """loads provided product details into the object with ability to run the functions below on the object
    accordingly"""

    def __init__(self, product_id=None):
        """initialises product object with all attributes"""

        self.item_id = []
        self.item_id.append("product_id")

        self.product_id = product_id
        self.item_id.append(self.product_id)

        if product_id is not None:
            if not self._check_item_exists("SELECT * FROM products WHERE product_id = {0}".format(product_id)):
                raise ValueError("Product is either set to None or does not exist in database")

            product = self._db_execute("SELECT * FROM products WHERE product_id = {0}".format(product_id))[0]
            p_name = self._get_last_by_date("products_name")
            supplier = self._get_last_by_date("products_supplier")
            cost_price = self._get_last_by_date("products_cost_price")
            sale_price = self._get_last_by_date("products_sale_price")

            purchase_limit = self._get_active_item_condition(
                "SELECT * FROM products_purchase_limit WHERE product_id = {0}".format(product_id), 3)
            discount = self._get_active_item_condition(
                "SELECT * FROM products_discount WHERE product_id = {0}".format(product_id), 3)
            offers = self._get_active_item_condition(
                "SELECT * FROM products_offers WHERE product_id = {0}".format(product_id), 4)
        else:
            product = [int(), int(), str(), datetime.now(), False]
            p_name, supplier, cost_price, sale_price = str(), str(), int(), int()
            purchase_limit, discount, offers = [], [], []

        self.name = p_name
        self.supplier = supplier
        self.cost_price = cost_price
        self.selling_price = sale_price
        self.quantity = product[1]

        self.purchase_limit = purchase_limit
        self.discount = discount
        self.offers = offers

        self.notes = product[2]
        self.date_created = product[3]
        self.void = product[4]

    def add_product(self, p_name, notes=""):
        """adds product to database"""

        if self.product_id is not None:
            raise ValueError("cannot add a product that already exists! (if product is new then ensure to leave "
                             "product_id empty else if product is simply void then just update the void attrib and run"
                             " update_product)")

        self._db_execute("INSERT INTO products VALUES (NULL, ?, ?, ?)",
                         (p_name, datetime.now(), 0))

        self.product_id, self.name, self.notes = self._get_last_id("products"), p_name, notes

        self.item_id.pop(), self.item_id.append(self.product_id)

        self._db_execute("INSERT INTO products_name VALUES (?, ?, ?)", (self.product_id, p_name, datetime.now()))
        if notes != "":
            self._db_execute("INSERT INTO products_notes VALUES (?, ?, ?)", (self.product_id, notes, datetime.now()))

    def delete_product(self):
        """deletes product from database using product_id"""

        if not self._check_item_exists("SELECT * FROM products WHERE product_id = {0}".format(self.product_id)):
            raise ValueError("Product is either set to None or does not exist in database")

        self._db_execute("UPDATE products SET void = 1 WHERE product_id = {0}".format(self.product_id))
        self.void = False

    def add_discount(self, amount, type_, start_date, end_date, void=False):
        """adds new discount to database for the product"""

        Inherit._add_discount(self, "products", amount, type_, start_date, end_date, void)

    def delete_discount(self, date):
        """deletes discount from database for the product"""

        self._run_condition_delete_commands("products_discounts", date=date)

    def add_purchase_limit(self, amount, per, start_date, end_date, void=False):
        """adds spending limit to database for the product"""

        Inherit._add_limit(self, "products_purchase_limit", amount, per, start_date, end_date, void)

    def delete_purchase_limit(self, date):
        """deletes spending limit from database for the product"""

        self._run_condition_delete_commands("products_spending_limit", date=date)

    def add_offer(self, buy_x, get_y, z_off, type_, start_date, end_date, void=False):
        """adds offer to database for the product"""

        start_date, end_date = self._check_param_validity(int(), start_date, end_date, void)
        if not isinstance(buy_x, int):
            raise ValueError("buy_x parameter must be an int object")
        if not isinstance(get_y, int):
            raise ValueError("get_y parameter must be an int object")
        if not (isinstance(z_off, int) or isinstance(z_off, float)):
            raise ValueError("z_off parameter must be an instance of one of the following: [int, float]")
        self._check_type_param(type_)

        get_items = \
            "SELECT * FROM products_offers WHERE product_id = {0} AND buy_x = {1} AND get_y = {2} AND z_off = {3} AND" \
            " type = {4} AND start_date = \"{5}\" AND end_date = \"{6}\"".format(self.product_id, buy_x, get_y, z_off,
                                                                                 type_, start_date, end_date)
        update_void = \
            "UPDATE products_offers SET void = 0 WHERE product_id = {0} AND buy_x = {1} AND get_y = {2} AND z_off = " \
            "{3} AND type = {4} AND start_date = \"{5}\" AND end_date = \"{6}\"".format(
                self.product_id, buy_x, get_y, z_off, type_, start_date, end_date)
        add_new = "INSERT INTO products_offers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", \
                  (self.product_id, buy_x, get_y, z_off, type_, start_date, end_date, 1 if void else 0, datetime.now())

        self._run_condition_insert_commands(get_items, void, update_void, add_new, "sub zero allowance")

    def delete_offer(self, date):
        """deletes offer from database for the product"""

        self._run_condition_delete_commands("products_offers", date=date)

    def update_details(self, **details):
        """updates details passed (raises an error if an unknown detail is passed)"""

        if len(details) == 0:
            raise KeyError("update_details requires at least one argument")
        if not self._check_item_exists("SELECT * FROM products WHERE product_id = {0}".format(self.product_id)):
            raise ValueError("Product is either set to None or does not exist in database")

        for key, value in details.items():
            if key == "name":
                self._update_item("products_name", value, str)
                self.name = value
            elif key == "supplier":
                self._update_item("products_supplier", value, str)
                self.supplier = value
            elif key == "cost_price":
                self._update_item("products_cost_price", value, int, float)
                self.cost_price = value
            elif key == "sale_price":
                self._update_item("products_sale_price", value, int, float)
                self.selling_price = value
            elif key == "quantity":
                self._update_item("products_quantity_top_ups", value, int)
                new_quantity = self.quantity + value
                self._db_execute("UPDATE products SET quantity = {0} WHERE product_id = {1}".format(new_quantity,
                                                                                                    self.product_id))
                self.quantity = new_quantity
            elif key == "notes":
                self._update_item("products_notes", value, str)
                self.notes = value
            else:
                raise KeyError("{0} is not a valid detail name. "
                               "Ensure detail name is in [f_name, l_name, balance, notes].".format(key))

    def _check_item_exists(self, cmd, product_check=True):
        """internal use only - overriding parent class to include a check for account_id being None None"""

        if product_check:
            if self.product_id is None:
                return False

        return super()._check_item_exists(cmd)


if __name__ == "__main__":
    def _date(date_time):
        return datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")

    def _date2(date_time):  # with microsecond
        return datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S.%f")

    couch = Product()
    couch.add_product("Sour Sticks")
    couch.update_details(supplier="Lord")
    couch.update_details(name="Sour Chews")
    couch.update_details(cost_price=20.00)
    couch.update_details(sale_price=35.00)
    couch.update_details(quantity=250)
    couch.update_details(notes="Yo, testing the new products object. Kl eh?")
    print(couch.item_id)
    couch.add_discount(100, 1, _date('2018-06-10 14:38:30'), _date('2018-06-30 14:38:30'))
    # couch.delete_discount("2018-06-19 14:50:21.371553")
    couch.add_purchase_limit(20, "week", _date('2018-06-10 14:38:30'), _date('2018-06-24 14:38:30'))
    # couch.delete_spending_limit(20, "week", date('2018-06-18 14:38:30'), date('2018-06-18 14:38:30'))
    couch.add_offer(3, 1, 50, 1, _date('2018-06-11 14:38:30'), _date('2018-06-27 14:38:30'))
    # couch.delete_sub_zero_allowance(5, date('2018-06-18 14:38:30'), date('2018-06-18 14:38:30'))
