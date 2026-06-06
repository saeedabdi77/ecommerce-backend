from django.contrib import admin
from django.utils.html import format_html
from .models import ProductType, Product, ProductImage, Category


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
    autocomplete_fields = []
    fields = ('serial', 'purchase_price', 'state')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'homepage_show', 'order')
    list_filter = ('homepage_show',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'sell_price', 'main_price', 'stock', 'active')
    list_editable = ('sell_price', 'main_price', 'active')
    list_filter = ('category', 'active')
    search_fields = ('name', 'slug')
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline, ProductInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_type', 'state', 'purchase_price')
    list_filter = ('state', 'product_type')
    search_fields = ('serial',)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product_type', 'is_thumbnail', 'order')
    list_filter = ('is_thumbnail',)
