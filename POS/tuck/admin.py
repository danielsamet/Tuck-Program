from django.contrib import admin

from .models import Account, Product, AccountFName, AccountLName, AccountDiscount, AccountSpendingLimit, AccountSubZeroAllowance, ProductDiscount, \
    ProductPurchaseLimit, ProductOffer


class AccountDiscountInline(admin.TabularInline):
    model = AccountDiscount
    classes = ['collapse']
    extra = 0

    fieldsets = [
        (None, {'fields': ['_type']}),
        (None, {'fields': ['amount']}),
        (None, {'fields': ['start_date']}),
        (None, {'fields': ['end_date']}),
    ]


class AccountSpendingLimitInline(admin.TabularInline):
    model = AccountSpendingLimit
    classes = ['collapse']
    extra = 0

    fieldsets = [
        (None, {'fields': ['per']}),
        (None, {'fields': ['amount']}),
        (None, {'fields': ['start_date']}),
        (None, {'fields': ['end_date']}),
    ]


class AccountSubZeroAllowanceInline(admin.TabularInline):
    model = AccountSubZeroAllowance
    classes = ['collapse']
    extra = 0

    fieldsets = [
        (None, {'fields': ['amount']}),
        (None, {'fields': ['start_date']}),
        (None, {'fields': ['end_date']}),
    ]


class AccountFNameInline(admin.TabularInline):
    model = AccountFName
    classes = ['collapse']
    extra = 0

    fieldsets = [
        (None, {'fields': ['amount']}),
        (None, {'fields': ['start_date']}),
        (None, {'fields': ['end_date']}),
    ]


class AccountAdmin(admin.ModelAdmin):
    readonly_fields = ('item_id', 'date_added')
    fieldsets = [
        (None, {'fields': ['item_id', 'balance', 'date_added']}),
    ]

    # exclude = ('void',)

    inlines = [AccountDiscountInline, AccountSpendingLimitInline, AccountSubZeroAllowanceInline]


class AccountDiscountAdmin(admin.ModelAdmin):
    readonly_fields = ('void', 'date')
    fieldsets = [
        (None, {'fields': ['_type', 'amount', 'start_date', 'end_date', 'void', 'date']}),
    ]


class AccountSpendingLimitAdmin(admin.ModelAdmin):
    readonly_fields = ('void', 'date')
    fieldsets = [
        (None, {'fields': ['amount', 'per', 'start_date', 'end_date', 'void', 'date']}),
    ]


class AccountSubZeroAllowanceAdmin(admin.ModelAdmin):
    readonly_fields = ('void', 'date')
    fieldsets = [
        ("Product", {"fields": ["product_id"]}),
        (None, {'fields': ['amount', 'start_date', 'end_date', 'void', 'date']}),
    ]


class ProductDiscountInline(admin.TabularInline):
    model = ProductDiscount
    classes = ['collapse']
    extra = 0

    fieldsets = [
        (None, {'fields': ['_type']}),
        (None, {'fields': ['amount']}),
        (None, {'fields': ['start_date']}),
        (None, {'fields': ['end_date']}),
    ]


class ProductPurchaseLimitInline(admin.TabularInline):
    model = ProductPurchaseLimit
    classes = ['collapse']
    extra = 0

    fieldsets = [
        (None, {'fields': ['per']}),
        (None, {'fields': ['amount']}),
        (None, {'fields': ['start_date']}),
        (None, {'fields': ['end_date']}),
    ]


class ProductOfferInline(admin.TabularInline):
    model = ProductOffer
    classes = ['collapse']
    extra = 0

    fieldsets = [
        (None, {'fields': ['buy_x']}),
        (None, {'fields': ['get_y']}),
        (None, {'fields': ['_type']}),
        (None, {'fields': ['z_off']}),
        (None, {'fields': ['start_date']}),
        (None, {'fields': ['end_date']}),
    ]


class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ('item_id', 'date_added')
    fieldsets = [
        (None, {'fields': ['item_id', 'date_added']}),
    ]

    # exclude = ('void',)

    inlines = [ProductOfferInline, ProductDiscountInline, ProductPurchaseLimitInline]


class ProductDiscountAdmin(admin.ModelAdmin):
    readonly_fields = ('void', 'date')
    fieldsets = [
        (None, {'fields': ['_type', 'amount', 'start_date', 'end_date', 'void', 'date']}),
    ]


class ProductOfferAdmin(admin.ModelAdmin):
    readonly_fields = ('void', 'date')
    fieldsets = [
        ("Product", {"fields": ["product_id"]}),
        (None, {'fields': ['buy_x', 'get_y', '_type', 'z_off', 'start_date', 'end_date', 'void', 'date']}),
    ]


class ProductPurchaseLimitAdmin(admin.ModelAdmin):
    readonly_fields = ('void', 'date')
    fieldsets = [
        (None, {'fields': ['_type', 'amount', 'start_date', 'end_date', 'void', 'date']}),
    ]


admin.site.register(Account, AccountAdmin)
admin.site.register(Product, ProductAdmin)

admin.site.register(AccountDiscount, AccountDiscountAdmin)
admin.site.register(AccountSpendingLimit, AccountSpendingLimitAdmin)
admin.site.register(AccountSubZeroAllowance, AccountSubZeroAllowanceAdmin)
admin.site.register(ProductDiscount, ProductDiscountAdmin)
admin.site.register(ProductPurchaseLimit, ProductPurchaseLimitAdmin)
admin.site.register(ProductOffer, ProductOfferAdmin)
