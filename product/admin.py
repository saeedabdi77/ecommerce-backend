from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.db.models import Count
from .models import (
    Category, Brand, Attribute, AttributeValue,
    ProductType, ProductAttribute, ProductImage,
    Product, Tag, Review, Wishlist, ProductCollection
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('preview', 'image', 'is_thumbnail', 'order')
    readonly_fields = ('preview',)

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:90px;height:90px;object-fit:cover;border-radius:6px;" />', obj.image.url)
        return '-'
    preview.short_description = 'پیش نمایش'


class ProductInline(admin.TabularInline):
    model = Product
    extra = 1
    fields = ('serial', 'purchase_price', 'state')
    show_change_link = True


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1
    autocomplete_fields = ['attribute_value']
    fields = ('attribute_value', 'extra_price')
    verbose_name = 'ویژگی'
    verbose_name_plural = 'ویژگی‌ها'


class AttributeValueInline(admin.TabularInline):
    model = AttributeValue
    extra = 1
    fields = ('value', 'slug')
    prepopulated_fields = {'slug': ('value',)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'homepage_show', 'order', 'product_count')
    list_filter = ('homepage_show', 'parent')
    search_fields = ('name', 'slug', 'seo_keywords')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')
    list_editable = ('homepage_show', 'order')
    fieldsets = (
        ('اطلاعات پایه', {
            'fields': ('name', 'slug', 'parent', 'order')
        }),
        ('تصاویر', {
            'fields': ('image', 'icon'),
            'classes': ('collapse',)
        }),
        ('نمایش در سایت', {
            'fields': ('homepage_show',)
        }),
        ('سئو', {
            'fields': ('seo_description', 'seo_keywords'),
            'classes': ('collapse',)
        }),
    )

    def product_count(self, obj):
        count = ProductType.objects.filter(category=obj).count()
        url = reverse('admin:product_producttype_changelist') + f'?category__id__exact={obj.id}'
        return format_html('<a href="{}">{}</a>', url, count)
    product_count.short_description = 'تعداد محصولات'


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'logo_preview', 'is_active', 'product_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active',)
    fieldsets = (
        ('اطلاعات برند', {
            'fields': ('name', 'slug', 'logo', 'is_active')
        }),
    )

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="width:50px;height:50px;object-fit:contain;" />', obj.logo.url)
        return '-'
    logo_preview.short_description = 'لوگو'

    def product_count(self, obj):
        count = ProductType.objects.filter(brand=obj).count()
        url = reverse('admin:product_producttype_changelist') + f'?brand__id__exact={obj.id}'
        return format_html('<a href="{}">{}</a>', url, count)
    product_count.short_description = 'تعداد محصولات'


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'values_count')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [AttributeValueInline]

    def values_count(self, obj):
        return obj.values.count()
    values_count.short_description = 'تعداد مقادیر'


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ('value', 'attribute', 'slug')
    list_filter = ('attribute',)
    search_fields = ('value', 'slug')
    prepopulated_fields = {'slug': ('value',)}
    autocomplete_fields = ['attribute']


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'sell_price', 'main_price', 'stock', 'active', 'has_discount')
    list_editable = ('sell_price', 'main_price', 'active')
    list_filter = ('category', 'brand', 'active', 'tags')
    search_fields = ('name', 'slug', 'description', 'seo_keywords')
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ['category', 'brand', 'tags']
    inlines = [ProductImageInline, ProductInline, ProductAttributeInline]
    filter_horizontal = ('tags',)
    fieldsets = (
        ('اطلاعات پایه', {
            'fields': ('category', 'brand', 'name', 'slug', 'description', 'active')
        }),
        ('قیمت', {
            'fields': ('main_price', 'sell_price'),
            'description': 'TODO: Add discount system later'
        }),
        ('وزن و ابعاد', {
            'fields': ('weight', 'dimensions'),
            'classes': ('collapse',)
        }),
        ('برچسب‌ها', {
            'fields': ('tags',),
            'classes': ('collapse',)
        }),
        ('سئو', {
            'fields': ('seo_title', 'seo_description', 'seo_keywords'),
            'classes': ('collapse',)
        }),
    )
    actions = ['activate_products', 'deactivate_products']

    def has_discount(self, obj):
        # TODO: Check if product has active discounts
        return False
    has_discount.boolean = True
    has_discount.short_description = 'تخفیف دارد'

    def activate_products(self, request, queryset):
        queryset.update(active=True)
    activate_products.short_description = 'فعال کردن محصولات انتخاب شده'

    def deactivate_products(self, request, queryset):
        queryset.update(active=False)
    deactivate_products.short_description = 'غیرفعال کردن محصولات انتخاب شده'


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ('product_type', 'attribute_value', 'extra_price')
    list_filter = ('attribute_value__attribute',)
    search_fields = ('product_type__name', 'attribute_value__value')
    autocomplete_fields = ['product_type', 'attribute_value']
    list_editable = ('extra_price',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_type', 'state', 'purchase_price', 'serial')
    list_filter = ('state', 'product_type')
    search_fields = ('serial', 'product_type__name')
    list_editable = ('state', 'purchase_price')
    autocomplete_fields = ['product_type']
    fieldsets = (
        ('اطلاعات محصول', {
            'fields': ('product_type', 'serial', 'state')
        }),
        ('قیمت و انبار', {
            'fields': ('purchase_price',)
        }),
        ('تاریخ در دسترس', {
            'fields': ('available_from', 'available_to'),
            'classes': ('collapse',)
        }),
    )
    actions = ['mark_in_warehouse', 'mark_sold', 'mark_reserved']

    def mark_in_warehouse(self, request, queryset):
        queryset.update(state='in_warehouse')
    mark_in_warehouse.short_description = 'تغییر وضعیت به "در انبار"'

    def mark_sold(self, request, queryset):
        queryset.update(state='sold')
    mark_sold.short_description = 'تغییر وضعیت به "فروخته شده"'

    def mark_reserved(self, request, queryset):
        queryset.update(state='reserved')
    mark_reserved.short_description = 'تغییر وضعیت به "رزرو شده"'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product_type', 'thumbnail_preview', 'is_thumbnail', 'order')
    list_filter = ('is_thumbnail', 'product_type')
    search_fields = ('product_type__name',)
    list_editable = ('is_thumbnail', 'order')
    autocomplete_fields = ['product_type']
    fields = ('product_type', 'image', 'is_thumbnail', 'order')
    readonly_fields = ('thumbnail_preview',)

    def thumbnail_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:120px;height:120px;object-fit:cover;border-radius:6px;" />', obj.image.url)
        return '-'
    thumbnail_preview.short_description = 'پیش نمایش'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'product_count')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

    def product_count(self, obj):
        return obj.product_types.count()
    product_count.short_description = 'تعداد محصولات'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product_type', 'rating', 'is_verified', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_verified', 'is_approved', 'created_at')
    search_fields = ('user__username', 'product_type__name', 'title', 'comment')
    list_editable = ('is_approved',)
    actions = ['approve_reviews', 'unapprove_reviews', 'mark_verified']
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('اطلاعات نظر', {
            'fields': ('product_type', 'user', 'rating', 'title', 'comment')
        }),
        ('وضعیت', {
            'fields': ('is_verified', 'is_approved')
        }),
        ('تاریخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = 'تایید و انتشار نظرات انتخاب شده'

    def unapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
    unapprove_reviews.short_description = 'عدم تایید نظرات انتخاب شده'

    def mark_verified(self, request, queryset):
        queryset.update(is_verified=True)
    mark_verified.short_description = 'تایید خرید (Verified)'


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product_type', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'product_type__name')
    autocomplete_fields = ['user', 'product_type']
    readonly_fields = ('created_at',)


@admin.register(ProductCollection)
class ProductCollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code_name', 'product_count', 'is_active', 'order', 'created_at')
    list_editable = ('is_active', 'order')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code_name', 'description', 'seo_title', 'seo_description')
    prepopulated_fields = {'code_name': ('name',)}
    filter_horizontal = ('product_types',)
    fieldsets = (
        ('اطلاعات پایه', {
            'fields': ('name', 'code_name', 'description', 'is_active', 'order')
        }),
        ('تصاویر', {
            'fields': ('image',),
            'classes': ('collapse',)
        }),
        ('محصولات', {
            'fields': ('product_types',),
            'description': 'محصولات موجود در این مجموعه'
        }),
        ('سئو', {
            'fields': ('seo_title', 'seo_description'),
            'classes': ('collapse',)
        }),
    )
    actions = ['activate_collections', 'deactivate_collections']

    def product_count(self, obj):
        return obj.product_types.count()
    product_count.short_description = 'تعداد محصولات'

    def activate_collections(self, request, queryset):
        queryset.update(is_active=True)
    activate_collections.short_description = 'فعال کردن مجموعه‌های انتخاب شده'

    def deactivate_collections(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_collections.short_description = 'غیرفعال کردن مجموعه‌های انتخاب شده'
