import graphene
from django.conf import settings
from django_filters import CharFilter, FilterSet
from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from backend.graphene import DjangoParlerObjectType
from parler.models import TranslatableModel
from parler.utils import get_active_language_choices
from django.db.models import Q, F, Count, Min, Max

from .models import Shop, Category, Promotion, Product, Price


class ShopNode(DjangoParlerObjectType):
    class Meta:
        model = Shop
        interfaces = (relay.Node, )


class ShopCategoryFilter(FilterSet):
    class Meta:
        model = Category
        fields = []


class ShopCategoryNode(DjangoParlerObjectType):
    count_products = graphene.Int()

    def resolve_count_products(root, info, **kwargs):
        childs = list(Category.objects.filter(parent=root).values_list('id', flat=True))
        childs.append(root.id)
        queryset = Product.objects.filter(category__in=childs, available=True, prices__available=True)
        if info.variable_values['filters']:
            # print(info.variable_values['filters'])
            price = info.variable_values['filters'].price
            # print(price)
            queryset = queryset.filter(prices__price__range=(price.min, price.max), prices__available=True)
        return queryset.count()


    class Meta:
        model = Category
        filterset_class = ShopCategoryFilter
        interfaces = (relay.Node, )


class ShopPromotionNode(DjangoParlerObjectType):
    class Meta:
        model = Promotion
        interfaces = (relay.Node, )


class FilterWithCountNode(ObjectType):
    value = graphene.String()
    count = graphene.Int()


class ListNode(ObjectType):
    param = graphene.String()
    values = graphene.List(FilterWithCountNode)
    class Meta:
        interfaces = (relay.Node, )


class RangeNode(ObjectType):
    param = graphene.String()
    min = graphene.Float()
    max = graphene.Float()
    class Meta:
        interfaces = (relay.Node, )


class FilterBaseNode(graphene.Union):
    class Meta:
        types = (ListNode, RangeNode)


class ShopFilterNode(ObjectType):
    filters = graphene.List(FilterBaseNode)

    def resolve_filters(root, info):
        filters = []
        min_value = root.aggregate(min_value=Min('prices__price')).get('min_value')
        max_value = root.aggregate(max_value=Max('prices__price')).get('max_value')
        filters.append(RangeNode(param='price', min=int(min_value), max=int(max_value)))
        
        volumes = root.values('volume').annotate(value=F('volume'), count=Count('id')).order_by('-count')
        filters.append(ListNode(param='volume', values=volumes))

        brands = root.values('translations__brand').annotate(value=F('translations__brand'), count=Count('id')).order_by('-count')
        filters.append(ListNode(param='brand', values=brands))

        products = root.values_list('id', flat=True)
        promos = Promotion.objects.filter(shop=root.first().shop, available=True).annotate(value=F('translations__title'))
        for promo in promos:
            prices = Price.objects.filter(product__in=products, promotions=promo.id, available=True)
            promo.count = prices.count()
        filters.append(ListNode(param='promo', values=sorted(promos, key=lambda x: x.count, reverse=True)))

        return filters
    
    class Meta:
        exclude = []
        interfaces = (relay.Node, )


class PriceFilterInput(graphene.InputObjectType):
    min = graphene.Float(required=True, description="Min price")
    max = graphene.Float(required=True, description="Max price")


class ShopFilterInput(graphene.InputObjectType):
    price = graphene.InputField(PriceFilterInput, description='Price filter')
    volume = graphene.List(graphene.String)
    brand = graphene.List(graphene.String)
    promo = graphene.List(graphene.String)


class ProductPriceNode(DjangoObjectType):
    old_price = graphene.String()

    def resolve_old_price(root, info, **kwargs):
        return root.price + root.discount

    class Meta:
        model = Price
        exclude = []
        interfaces = (relay.Node, )


class ShopProductFilter(FilterSet):
    class Meta:
        model = Product
        fields = []


class ShopProductNode(DjangoParlerObjectType):
    category_id = graphene.String(source='category_id')
    url = graphene.String()
    price = graphene.Field(ProductPriceNode)

    def resolve_image(root, info, **kwargs):
        if root.shop.id == settings.SILPO_ID:
            return settings.SILPO_IMAGES_URL + root.image
        if root.shop.id == settings.ROZETKA_ID:
            return root.image
        if root.shop.id == settings.TAVRIA_ID:
            return root.image

    def resolve_url(root, info, **kwargs):
        if root.shop.id == settings.SILPO_ID:
            return root.shop.url + 'product/' + root.product_slug
        if root.shop.id == settings.ROZETKA_ID:
            return root.shop.url + 'product/p' + root.product_slug
        if root.shop.id == settings.TAVRIA_ID:
            return root.shop.url + 'product/' + root.product_slug

    def resolve_price(root, info, **kwargs):
        return root.prices.first()

    class Meta:
        model = Product
        filterset_class = ShopProductFilter
        interfaces = (relay.Node, )


class Query(ObjectType):
    shops = graphene.List(
        ShopNode,
        country=graphene.String(required=True, description="Country code"),
        language=graphene.String(),
        description="Get all shops"
    )
    shop_categories = graphene.List(
        ShopCategoryNode,
        shop=graphene.ID(required=True, description="Shop ID"),
        parent=graphene.String(),
        filters=graphene.Argument(ShopFilterInput),
        slug=graphene.String(),
        language=graphene.String(),
        description="Get shop categories"
    )
    shop_filters = graphene.Field(
        ShopFilterNode,
        shop=graphene.ID(required=True, description="Shop ID"),
        category=graphene.String(),
        language=graphene.String(),
        description="Get shop filters product"
    )
    shop_products = DjangoFilterConnectionField(
        ShopProductNode,
        shop=graphene.ID(required=True, description="Shop ID"),
        category=graphene.String(),
        filters=graphene.Argument(ShopFilterInput),
        sort_by=graphene.String(),
        sort_direction=graphene.String(),
        slug=graphene.String(),
        language=graphene.String(),
        description="Get shop products"
    )
    category = graphene.Field(ShopCategoryNode, slug=graphene.String(), language=graphene.String())
    product = graphene.Field(ShopProductNode, slug=graphene.String(required=True), language=graphene.String())

 
    def resolve_shops(root, info, country=None, language=None):
        if issubclass(Shop, TranslatableModel):
            shops = Shop.objects.active_translations(language).all()
            # shops.set_current_language(language)
        else:
            shops = Shop.objects.all()
        if country == None:
            country = 'UA'
        shops = shops.filter(country=country)
        return shops.prefetch_related('products').order_by('id')

    def resolve_shop_categories(root, info, shop=None, parent=None, filters=None, slug=None, language=None):
        shop = graphene.Node.get_node_from_global_id(info, shop)
        queryset = Category.objects.filter(shop=shop, available=True)
        if parent:
            parent = graphene.Node.get_node_from_global_id(info, parent)
            queryset = queryset.filter(parent=parent)
        else:
            queryset = queryset.filter(parent__isnull=True)
        queryset = queryset.order_by('date_created')
        # print(queryset)
        return queryset

    def resolve_shop_filters(root, info, shop=None, category=None, language=None):
        shop = graphene.Node.get_node_from_global_id(info, shop)
        products = Product.objects.filter(shop=shop, available=True, prices__available=True)
        if category != None:
            category = Category.objects.get(category_slug=category, available=True)
            categories = list(Category.objects.filter(parent=category).values_list('id', flat=True))
            categories.append(category.id)
            products = products.filter(category__in=categories)
        return products

    def resolve_shop_products(root, info, shop=None, category=None, filters=None, sort_by=None, sort_direction=None, slug=None, language=None, **kwargs):
        if sort_by == None:
            sort_by ='percent'
        if sort_direction == None:
            sort_direction = 'desc'
        shop = graphene.Node.get_node_from_global_id(info, shop)
        orderBy = '-' if sort_direction == 'desc' else ''
        if sort_by == 'name':
            orderBy += 'translations__name'
        if sort_by == 'price':
            orderBy += 'prices__price'
        if sort_by == 'percent':
            orderBy += 'prices__percent'
        queryset = Product.objects.filter(shop=shop, available=True, prices__available=True)
        if category:
            root_category = Category.objects.get(category_slug=category)
            childs = list(Category.objects.filter(parent=root_category).values_list('id', flat=True))
            childs.append(root_category.id)
            # print(childs)
            queryset = queryset.filter(category__in=childs)
        if filters.price:
            queryset = queryset.filter(prices__price__range=(filters.price.min, filters.price.max), prices__available=True)
        if filters.volume:
            queryset = queryset.filter(volume__in=filters.volume, prices__available=True)
        if filters.brand:
            queryset = queryset.filter(translations__brand__in=filters.brand, prices__available=True)
        if filters.promo:
            prices = Price.objects.filter(promotions__translations__title__in=filters.promo, available=True).values_list('id', flat=True)
            queryset = queryset.filter(prices__in=prices, prices__available=True)
        queryset = queryset.order_by(orderBy)
        if slug:
            languages = get_active_language_choices()
            languages.append('uk')
            # queryset = queryset.filter(
            #     Q(
            #         translations__language_code__in=languages,
            #         translations__name__icontains=slug
            #     ) | Q(
            #         translations__language_code__in=languages,
            #         translations__slug__icontains=slug
            #     )
            # ).distinct()
        # print(queryset)
        return queryset
    
    def resolve_category(root, info, slug, language=None):
        if issubclass(Category, TranslatableModel):
            return Category.objects.active_translations(language, category_slug=slug).get()
        else:
            return Category.objects.get(category_slug=slug)

    def resolve_product(root, info, slug, language=None):
        if issubclass(Product, TranslatableModel):
            product = Product.objects.active_translations(language, product_slug=slug).get()
            product.set_current_language(language)
        else:
            product = Product.objects.get(product_slug=slug)
        return product


class Mutation(ObjectType):
    pass
