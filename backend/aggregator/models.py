from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields
from mptt.models import MPTTModel, TreeForeignKey
from users.models import User
from star_ratings.models import Rating
from .managers import CategoryManager

class Shop(TranslatableModel):
    translations = TranslatedFields(
        title = models.CharField(max_length=255, blank=True, verbose_name=_('Title')),
        description = models.TextField(blank=True, verbose_name=_('Description'))
    )
    image = models.ImageField(upload_to='shops/images', blank=True, verbose_name=_('Image'))
    url = models.URLField(blank=True, verbose_name=_('URL'))
    api = models.URLField(blank=True, verbose_name=_('API'))
    country = models.CharField(max_length=2, blank=True, verbose_name=_('Country'))
    active = models.BooleanField(default=True, verbose_name=_('Active'))
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    ratings = GenericRelation(Rating, related_query_name='shops')

    class Meta:
        verbose_name = _('Shop')
        verbose_name_plural = _('Shops')
        ordering = ['date_created']
        indexes = [
            models.Index(fields=['date_created']),
        ]

    def __str__(self):
        return self.safe_translation_getter("title", super().__str__())

    def category_count(self):
        """Return a count of all the categories in this shop."""
        return self.categories.filter(available=True).count()
    category_count.short_description = _('Categories')

    def product_count(self):
        """Return a count of all the products in this shop."""
        return self.products.filter(available=True).count()
    product_count.short_description = _('Products')

    def promotion_count(self):
        """Return a count of all the promotions in this shop."""
        return self.promotions.filter(available=True).count()
    promotion_count.short_description = _('Promotions')


class Promotion(TranslatableModel):
    shop = models.ForeignKey(Shop,
                             related_name='promotions',
                             on_delete=models.CASCADE,
                             verbose_name=_('Shop'))
    slug = models.SlugField(max_length=255, blank=True, verbose_name=_('Slug'))
    icon_url = models.URLField(blank=True, verbose_name=_('Icon URL'))
    translations = TranslatedFields(
        title = models.CharField(max_length=255, blank=True, verbose_name=_('Title')),
        description = models.TextField(blank=True, verbose_name=_('Description'))
    )
    available = models.BooleanField(default=True, verbose_name=_('Available'))
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Promotion')
        verbose_name_plural = _('Promotions')
        ordering = ['-date_created']
        indexes = [
            models.Index(fields=['-date_created']),
        ]

    def __str__(self):
        return self.safe_translation_getter("title", super().__str__())

    def product_count(self):
        """Return a count of all the products in this promotion."""
        return Price.objects.filter(promotions=self, product__available=True, available=True).values_list('product', flat=True).count()
    product_count.short_description = _('Products')


class Category(MPTTModel, TranslatableModel):
    shop = models.ForeignKey(Shop,
                             related_name='categories',
                             on_delete=models.CASCADE,
                             verbose_name=_('Shop'))
    parent = TreeForeignKey('self',
                            null=True,
                            blank=True,
                            related_name='children',
                            on_delete=models.CASCADE,
                            verbose_name=_('Parent'))
    translations = TranslatedFields(
        name = models.CharField(max_length=255, verbose_name=_('Name'))
    )
    category_slug = models.SlugField(max_length=255, blank=True, verbose_name=_('Category slug'))
    available = models.BooleanField(default=True, verbose_name=_('Available'))
    date_created = models.DateTimeField(auto_now_add=True)

    objects = CategoryManager()

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['-date_created']
        indexes = [
            models.Index(fields=['-date_created']),
        ]

    def __str__(self):
        return self.safe_translation_getter("name", super().__str__())

    def product_count(self):
        """Return a count of all the products in this category."""
        return self.products.count()
    product_count.short_description = _('Products')


class Product(TranslatableModel):
    shop = models.ForeignKey(Shop,
                             related_name='products',
                             on_delete=models.CASCADE,
                             verbose_name=_('Shop'))
    category = models.ForeignKey(Category,
                                 null=True,
                                 related_name='products',
                                 on_delete=models.CASCADE,
                                 verbose_name=_('Category'))
    translations = TranslatedFields(
        name = models.CharField(max_length=255, verbose_name=_('Name')),
        brand = models.CharField(max_length=255, blank=True, verbose_name=_('Brand')),
        description = models.TextField(blank=True, verbose_name=_('Description'))
    )
    product_slug = models.SlugField(max_length=255, blank=True, verbose_name=_('Product slug'))
    category_slug = models.SlugField(max_length=255, blank=True, verbose_name=_('Category slug'))
    external_id = models.CharField(max_length=255, blank=True, verbose_name=_('External ID'))
    image = models.TextField(blank=True, verbose_name=_('Image'))
    volume = models.CharField(max_length=16, blank=True, verbose_name=_('Volume'))
    alcohol = models.CharField(max_length=16, blank=True, verbose_name=_('Alcohol'))
    available = models.BooleanField(default=True, verbose_name=_('Available'))
    promoted = models.BooleanField(default=False, verbose_name=_('Promoted'))
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['-date_created']
        indexes = [
            models.Index(fields=['-date_created']),
            models.Index(fields=['external_id']),
        ]

    def __str__(self):
        return self.safe_translation_getter("name", super().__str__())

    def last_price(self):
        last = self.prices.first() # order by DESC
        return last.price if last else 0
    last_price.short_description = _('Price')

    def discount(self):
        last = self.prices.first() # order by DESC
        return f'{round(last.percent) if last else 0}%'
    discount.short_description = _('Discount')


class Price(models.Model):
    product = models.ForeignKey(Product,
                                related_name='prices',
                                on_delete=models.CASCADE,
                                verbose_name=_('Product'))
    price = models.DecimalField(max_digits=10,
                                decimal_places=2,
                                default=0.00,
                                verbose_name=_('Price'))
    currency = models.CharField(max_length=3,
                                blank=True,
                                null=True,
                                verbose_name=_('Currency'))
    discount = models.DecimalField(max_digits=10,
                                   decimal_places=2,
                                   default=0.00,
                                   verbose_name=_('Discount'))
    percent = models.DecimalField(max_digits=5,
                                  decimal_places=2,
                                  default=0.00,
                                  verbose_name=_('Percent'))
    available = models.BooleanField(default=True, verbose_name=_('Available'))
    promotions = models.ManyToManyField(Promotion, verbose_name=_('Promotions'))
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Price')
        verbose_name_plural = _('Prices')
        ordering = ['-date_created']
        indexes = [
            models.Index(fields=['-date_created']),
            models.Index(fields=['-date_updated']),
        ]

    def __str__(self):
        return f'#{self.id} {_("Product")}: {self.product.name} = {self.price}'


class Track(models.Model):
    user = models.ForeignKey(User,
                             related_name='tracks',
                             on_delete=models.PROTECT,
                             verbose_name=_('User'))
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE,
                                verbose_name=_('Product'))
    active = models.BooleanField(default=True, verbose_name=_('Active'))
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Track')
        verbose_name_plural = _('Tracks')
        ordering = ['-date_updated']
        indexes = [
            models.Index(fields=['-date_updated']),
        ]
