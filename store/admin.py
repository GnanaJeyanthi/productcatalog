# D:\2312040-wfp\productcatalog_project\store\admin.py
from django.contrib import admin
from django.db import models
from django.forms import Textarea
from django.urls import reverse
from django.utils.html import format_html
from .models import Category, Product, Brand, ProductImage, Order, OrderItem, Wishlist, ReturnRequest

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ('image', 'alt_text', 'order')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'price', 'stock', 'created_at')
    list_filter = ('category', 'brand', 'created_at')
    search_fields = ('name', 'description')
    inlines = [ProductImageInline]

    fieldsets = (
        ('🧾 Basic Information', {
            'fields': ('name', 'description', 'category', 'brand'),
        }),
        ('⚙️ Specifications', {
            'fields': ('specs',),
        }),
        ('💰 Pricing & Stock', {
            'fields': ('price', 'stock'),
        }),
    )

    # Use formfield_overrides instead of a custom form
    formfield_overrides = {
        models.JSONField: {
            'widget': Textarea(attrs={
                'rows': 5,
                'cols': 60,
                'placeholder': '{"RAM": "8GB", "Storage": "256GB"}'
            })
        },
    }

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'price', 'quantity')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'total_amount', 'payment_method', 'status', 'payment_completed', 'created_at')
    list_filter = ('status', 'payment_method', 'payment_completed', 'created_at')
    search_fields = ('full_name', 'email', 'phone', 'id')
    readonly_fields = ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled', 'mark_as_return_approved', 'mark_as_return_rejected']

    fieldsets = (
        ('Customer Information', {
            'fields': ('user', 'full_name', 'email', 'phone')
        }),
        ('Shipping Address', {
            'fields': ('address', 'city', 'state', 'pincode')
        }),
        ('Order Details', {
            'fields': ('total_amount', 'payment_method', 'status', 'payment_completed')
        }),
        ('Payment Information', {
            'fields': ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def mark_as_processing(self, request, queryset):
        queryset.update(status='processing')
        self.message_user(request, f"{queryset.count()} order(s) marked as processing.")
    mark_as_processing.short_description = "Mark selected orders as Processing"

    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')
        self.message_user(request, f"{queryset.count()} order(s) marked as shipped.")
    mark_as_shipped.short_description = "Mark selected orders as Shipped"

    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
        self.message_user(request, f"{queryset.count()} order(s) marked as delivered.")
    mark_as_delivered.short_description = "Mark selected orders as Delivered"

    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, f"{queryset.count()} order(s) marked as cancelled.")
    mark_as_cancelled.short_description = "Mark selected orders as Cancelled"

    def mark_as_return_approved(self, request, queryset):
        queryset.update(status='return_approved')
        self.message_user(request, f"{queryset.count()} order(s) marked as return approved.")
    mark_as_return_approved.short_description = "Mark selected orders as Return Approved"

    def mark_as_return_rejected(self, request, queryset):
        queryset.update(status='return_rejected')
        self.message_user(request, f"{queryset.count()} order(s) marked as return rejected.")
    mark_as_return_rejected.short_description = "Mark selected orders as Return Rejected"

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'product__name')
    readonly_fields = ('added_at',)

# Custom admin site to add analytics link
class CustomAdminSite(admin.AdminSite):
    site_header = "Product Catalog Administration"
    site_title = "Product Catalog Admin"
    index_title = "Welcome to Product Catalog Admin"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('analytics/', self.admin_view(order_analytics_view), name='order_analytics'),
        ]
        return custom_urls + urls

def order_analytics_view(request):
    from .views import order_analytics
    return order_analytics(request)

# Create custom admin site instance
admin_site = CustomAdminSite(name='custom_admin')

@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ('order', 'reason', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('order__id', 'reason')
    readonly_fields = ('created_at',)

# Register models with custom admin site
admin_site.register(Category, CategoryAdmin)
admin_site.register(Brand, BrandAdmin)
admin_site.register(Product, ProductAdmin)
admin_site.register(Order, OrderAdmin)
admin_site.register(Wishlist, WishlistAdmin)
admin_site.register(ReturnRequest, ReturnRequestAdmin)




