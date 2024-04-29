import graphene
from django.conf import settings
from django_filters import CharFilter, FilterSet
from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from backend.graphene import DjangoParlerObjectType
from parler.models import TranslatableModel
from parler.utils import get_active_language_choices
from django.db.models import Q, F, Count, Min, Max, BooleanField, Case, When, Value
from django.contrib.auth.models import AnonymousUser
from graphql_jwt.decorators import login_required
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity, TrigramDistance
import redis

from .models import Shop, Category, Promotion, Product, Price, Track


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
    is_tracked = graphene.Boolean()

    def resolve_image(root, info, **kwargs):
        if root.shop.id == settings.SILPO_ID:
            return settings.SILPO_IMAGES_URL + root.image
        if root.shop.id == settings.ROZETKA_ID:
            return root.image
        if root.shop.id == settings.TAVRIA_ID:
            return root.image
        if root.shop.id == settings.MAUDAU_ID:
            return settings.MAUDAU_IMAGES_URL + root.image
        if root.shop.id == settings.METRO_ID:
            return root.image


    def resolve_url(root, info, **kwargs):
        if root.shop.id == settings.SILPO_ID:
            return root.shop.url + 'product/' + root.product_slug
        if root.shop.id == settings.ROZETKA_ID:
            return root.shop.url + 'product/p' + root.external_id
        if root.shop.id == settings.TAVRIA_ID:
            return root.shop.url + 'product/' + root.product_slug
        if root.shop.id == settings.MAUDAU_ID:
            return root.shop.url + 'product/' + root.product_slug
        if root.shop.id == settings.METRO_ID:
            return root.shop.api + 'shop/pv/' + root.external_id

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
    new_products = graphene.List(
        ShopProductNode,
        language=graphene.String(),
        description="Get new shop products"
    )
    track_products = DjangoFilterConnectionField(
        ShopProductNode,
        language=graphene.String(),
        description="Get my products"
    )
    similar_products = DjangoFilterConnectionField(
        ShopProductNode,
        product=graphene.ID(required=True, description="Product ID"),
        language=graphene.String(),
        description="Get similar products"
    )
    history_products = graphene.List(
        ShopProductNode,
        language=graphene.String(),
        description="Get user history products"
    )
    search_products = DjangoFilterConnectionField(
        ShopProductNode,
        query=graphene.String(required=True),
        language=graphene.String(),
        description="Get search products"
    )
 
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
        if not isinstance(info.context.user, AnonymousUser):
            queryset = queryset.annotate(
                is_tracked=Case(
                    When(Q(track__user=info.context.user) & Q(track__active=True), then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                )
            )
        # print(queryset)
        return queryset
    
    def resolve_category(root, info, slug, language=None):
        if issubclass(Category, TranslatableModel):
            return Category.objects.active_translations(language, category_slug=slug).get()
        else:
            return Category.objects.get(category_slug=slug)

    def resolve_product(root, info, slug, language=None, **kwargs):
        # if issubclass(Product, TranslatableModel):
        #     product = Product.objects.active_translations(language, product_slug=slug).get()
        #     product.set_current_language(language)
        # else:
        product = Product.objects.prefetch_related('prices').get(product_slug=slug)
        if info.context.user.is_anonymous:
            return product
        else:
            user_history_product_key = f'user_{info.context.user.id}_history_products'
            redis_instance = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
            history_products_slugs = redis_instance.lrange(user_history_product_key, 0, 20)
            history_products_slugs = [slug.decode('utf-8') for slug in history_products_slugs]
            if slug not in history_products_slugs:
                if len(history_products_slugs) < 20:
                    redis_instance.lpush(user_history_product_key, slug)
                else:
                    redis_instance.rpop(f'user_{info.context.user.id}_history_products')
                    redis_instance.lpush(user_history_product_key, slug)
            else:
                redis_instance.lrem(user_history_product_key, 0, slug)
                redis_instance.lpush(user_history_product_key, slug)
            return product

    @login_required
    def resolve_history_products(root, info, language=None, **kwargs):
        redis_instance = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
        product_slugs = redis_instance.lrange(f'user_{info.context.user.id}_history_products', 0, 20)
        product_slugs = [slug.decode('utf-8') for slug in product_slugs]
        history_products = []
        for product_slug in product_slugs:
            history_products.append(Product.objects.get(product_slug=product_slug))
        return history_products

    def resolve_new_products(root, info, language=None, **kwargs):
        shops = Shop.objects.all()
        all_products = []
        for shop in shops:
            shop_products = shop.products.filter(available=True, prices__available=True).order_by('-date_created')[:20 / shops.count()]
            all_products.extend(shop_products)
        return all_products[:20]
    
    def resolve_search_products(root, info, query, language=None, **kwargs):
        products = Product.objects.annotate(
            similarity=TrigramSimilarity('translations__name', query),
        ).filter(
            similarity__gte=0
        ).order_by('-similarity').distinct()
        return products
    
    @login_required
    def resolve_track_products(root, info, language=None, **kwargs):
        return Product.objects.filter(id__in=info.context.user.tracks.filter(active=True).values_list('product', flat=True))
    
    def resolve_similar_products(root, info, product=None, language=None, **kwargs):
        product = graphene.Node.get_node_from_global_id(info, product)
        similar_products = Product.objects.annotate(
            similarity=TrigramSimilarity('translations__name', product.name),
        ).filter(
            similarity__gte=0.395
        ).order_by('-similarity').distinct()
        return similar_products[:12]


class TrackProduct(graphene.Mutation):
    class Arguments:
        product = graphene.ID(required=True, description='Product ID')

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(root, info, product):
        ok = True
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("Authentication credentials were not provided")
        product_instance = graphene.Node.get_node_from_global_id(info, product)
        track, created = Track.objects.get_or_create(user=user, product=product_instance)
        track.active = True
        track.save()
        return TrackProduct(ok=ok)


class UntrackProduct(graphene.Mutation):
    class Arguments:
        product = graphene.ID(required=True, description='Product ID')

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(root, info, product):
        ok = True
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("Authentication credentials were not provided")
        product_instance = graphene.Node.get_node_from_global_id(info, product)
        track = Track.objects.get(user=user, product=product_instance)
        track.active = False
        track.save()
        return UntrackProduct(ok=ok)


class Mutation(ObjectType):
   track_product = TrackProduct.Field(description="Track product")
   untrack_product = UntrackProduct.Field(description="Untrack product")
