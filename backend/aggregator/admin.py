from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin
from parler.forms import TranslatableModelForm
from mptt.admin import DraggableMPTTAdmin, TreeRelatedFieldListFilter
from mptt.forms import MPTTAdminForm
from django_admin_inline_paginator.admin import TabularInlinePaginated
from .models import Shop, Category, Product, Price, Promotion, Track


@admin.register(Shop)
class ShopAdmin(TranslatableAdmin):
    list_display = ['title', 'country_flag', 'active', 'category_count', 'product_count', 'promotion_count', 'language_column']
    list_editable = ['active']
    search_fields = ['translations__title']

    def country_flag(self, obj):
        return '🇺🇦' if obj.country == 'UA' else obj.country
    country_flag.short_description = _('Country')


class ProductItemInline(TabularInlinePaginated):
    model = Product
    verbose_name = _('Product')
    verbose_name_plural = _('Products')
    fields = ['id', 'volume', 'product_slug', 'external_id', 'image', 'available', 'promoted']
    per_page = 5
    
    def id(self, obj):
        return obj.__str__()
    id.short_description = _('Name')

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class CategoryAdminForm(MPTTAdminForm, TranslatableModelForm):
    """
    Form for categories, both MPTT + translatable.
    """
    pass


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin, TranslatableAdmin):
    list_display = ['tree_actions', 'indented_title', 'category_slug', 'product_count', 'available', 'shop', 'language_column']
    list_display_links = ['indented_title']
    list_filter = ['shop', 'available', 'date_created']
    list_editable = ['available']
    list_per_page = 20
    search_fields = ['translations__name', 'category_slug']
    inlines = [ProductItemInline]
    mptt_indent_field = 'name'  # be explicit for MPTT
    form = CategoryAdminForm

    # def get_prepopulated_fields(self, request, obj=None):
    #     return {'category_slug': ('name',)}


class DiscountRangeFilter(admin.SimpleListFilter):
    title = _('Discount Range')  # Display name for the filter
    parameter_name = 'discount_range'  # Parameter name used in the URL

    def lookups(self, request, model_admin):
        # Define the filter options
        return (
            ('below_5', _('Below 5%')),
            ('5_to_10', _('5% to 10%')),
            ('10_to_20', _('10% to 20%')),
            ('20_to_40', _('20% to 40%')),
            ('over_40', _('Over 40%')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'below_5':
            return queryset.filter(prices__available=True, prices__percent__lt=5)
        elif self.value() == '5_to_10':
            return queryset.filter(prices__available=True, prices__percent__range=(5, 10))
        elif self.value() == '10_to_20':
            return queryset.filter(prices__available=True, prices__percent__range=(10, 20))
        elif self.value() == '20_to_40':
            return queryset.filter(prices__available=True, prices__percent__range=(20, 40))
        elif self.value() == 'over_40':
            return queryset.filter(prices__available=True, prices__percent__gt=40)


class PriceRangeFilter(admin.SimpleListFilter):
    title = _('Price Range')  # Display name for the filter
    parameter_name = 'price_range'  # Parameter name used in the URL

    def lookups(self, request, model_admin):
        # Define the filter options
        return (
            ('below_100', _('Below 100')),
            ('100_to_200', _('100 to 200')),
            ('200_to_500', _('200 to 500')),
            ('500_to_1000', _('500 to 1000')),
            ('over_1000', _('Over 1000')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'below_100':
            return queryset.filter(prices__available=True, prices__price__lt=100)
        elif self.value() == '100_to_200':
            return queryset.filter(prices__available=True, prices__price__range=(100, 200))
        elif self.value() == '200_to_500':
            return queryset.filter(prices__available=True, prices__price__range=(200, 500))
        elif self.value() == '500_to_1000':
            return queryset.filter(prices__available=True, prices__price__range=(500, 1000))
        elif self.value() == 'over_1000':
            return queryset.filter(prices__available=True, prices__price__gt=1000)


class PriceItemInline(admin.TabularInline):
    model = Price
    verbose_name = _('Price')
    verbose_name_plural = _('Prices')
    extra = 0
    readonly_fields = ['date_created', 'date_updated']


@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    list_display = ['name', 'last_price', 'promotions', 'discount', 'volume', 'available', 'shop', 'external_id']#, 'language_column']
    list_filter = ['shop', 'available', DiscountRangeFilter, PriceRangeFilter, 'prices__promotions', ('category', TreeRelatedFieldListFilter)]
    list_editable = ['available']
    list_per_page = 20
    search_fields = ['external_id', 'product_slug', 'translations__name']
    inlines = [PriceItemInline]

    # def get_queryset(self, request):
    #     queryset = super().get_queryset(request)
    #     # Apply the default filter(s) here
    #     queryset = queryset.filter(available=True)
    #     return queryset

    def promotions(self, obj):
        html = ''
        price = obj.prices.first() # order by DESC
        if not price: return '-'
        for promotion in price.promotions.all():
            html += f'<img src="{promotion.icon_url}" width="20" height="20" title="{promotion.title}" />&nbsp;'
        return format_html(html)
    promotions.short_description = _('Promotions')

    # def get_prepopulated_fields(self, request, obj=None):
    #     return {'product_slug': ('name',)}


@admin.register(Promotion)
class PromotionAdmin(TranslatableAdmin):
    list_display = ['title', 'slug', 'icon', 'product_count', 'available', 'shop', 'language_column']
    list_filter = ['shop', 'available']
    list_editable = ['available']
    list_per_page = 20
    search_fields = ['translations__title', 'slug']

    def icon(self, obj):
        return format_html('<img src="{}" width="20" height="20" />', obj.icon_url)
    icon.short_description = _('Image')

    # def get_prepopulated_fields(self, request, obj=None):
    #     return {'slug': ('title',)}
