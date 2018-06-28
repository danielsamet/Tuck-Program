import datetime
import uuid

from django.db import models
from django.utils import timezone


class ItemCondition(models.Model):
    amount = models.FloatField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    void = models.BooleanField(default=False)
    date = models.DateTimeField(primary_key=True, auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        return "{0} from {1} till {2}".format(self.amount, self.start_date, self.end_date)


class Discount(ItemCondition):
    type_ = models.SmallIntegerField(verbose_name="type", default=0, choices=((0, "%"), (1, "£")))

    class Meta:
        abstract = True


class Limit(ItemCondition):
    per = models.SmallIntegerField(default="transaction", choices=("transaction", "day", "week", "month", "year"))

    class Meta:
        abstract = True


class Item(models.Model):
    item_id = vars()
    date_added = models.DateTimeField(primary_key=True, auto_now_add=True)
    void = models.BooleanField(default=False)

    def __str__(self):
        return self.item_id

    class Meta:
        abstract = True


class Note(models.Model):
    note = models.TextField()

    def __str__(self):
        return self.note

    class Meta:
        abstract = True


class Account(Item):
    item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="account id")
    balance = models.FloatField(default=0)


class AccountItem(models.Model):
    account_id = models.ForeignKey(Account, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class AccountName(AccountItem):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class AccountFName(AccountName):
    pass


class AccountLName(AccountName):
    pass


class AccountTopUp(AccountItem):
    amount = models.FloatField()

    def __str__(self):
        return self.amount


class AccountItemCondition(ItemCondition):
    account_id = models.ForeignKey(Account, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class AccountDiscount(AccountItemCondition, Discount):
    pass


class AccountSpendingLimit(AccountItemCondition, Limit):
    pass


class AccountSubZeroAllowance(AccountItemCondition):
    pass


class AccountNote(Note, AccountItem):
    pass


class Product(Item):
    item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="product id")


class ProductItem(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class ProductName(ProductItem):
    name = models.CharField()

    def __str__(self):
        return self.name


class ProductSupplier(ProductItem):
    name = models.CharField(max_length=30)
    email_address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class ProductPrice(ProductItem):
    amount = models.FloatField()

    def __str__(self):
        return self.amount

    class Meta:
        abstract = True


class ProductCostPrice(ProductPrice):
    pass


class ProductSalePrice(ProductPrice):
    pass


class ProductQuantityTopUp(ProductItem):
    amount = models.FloatField()

    def __str__(self):
        return self.amount


class ProductItemCondition(ItemCondition):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class ProductDiscount(ProductItemCondition, Discount):
    pass


class ProductPurchaseLimit(ProductItemCondition, Limit):
    pass


class ProductOffer(ProductItemCondition, Discount):
    amount = None

    buy_x = models.IntegerField()
    get_y = models.IntegerField()
    z_off = models.FloatField()

    def __str__(self):
        return "buy {0} get {1} {2}{3} off from {4} till {5}".format(self.buy_x, self.get_y,
                                                                     self.type_ if self.type_ != "%" else self.z_off,
                                                                     self.type_ if self.type_ == "%" else self.z_off,
                                                                     self.start_date, self.end_date)


class ProductNote(Note, ProductItem):
    pass


class Transaction(Item):
    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="account id")
    amount = models.FloatField()

    def __str__(self):
        return self.transaction_id


class TransactionProduct(models.Model):
    transaction_id = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        unique_together = ('transaction_id', 'product_id', 'quantity')
