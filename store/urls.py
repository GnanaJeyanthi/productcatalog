# D:\2312040-wfp\productcatalog_project\store\urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

    # Cart URLs
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Checkout URLs
    path('checkout/', views.checkout, name='checkout'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('add-review/<int:order_id>/<int:product_id>/', views.add_review, name='add_review'),
    path('request-return/<int:order_id>/', views.request_return, name='request_return'),

    # Admin URLs
    path('add-product/', views.add_product, name='add_product'),

    # Wishlist URLs
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('add-to-wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('compare-products/', views.compare_products, name='compare_products'),

    path('about-us/', views.about_us, name='about_us'),
    path('admin/analytics/', views.order_analytics, name='order_analytics'),
    
    # --- AI & Personalization API endpoints ---
    path('api/track/', views.track_activity, name='track_activity'),
    path('api/recommendations/', views.get_recommendations, name='get_recommendations'),
    path('api/chatbot/', views.chatbot_query, name='chatbot_query'),
    path('api/notifications/', views.get_notifications, name='get_notifications'),
    path('api/notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('api/analytics/', views.get_analytics_json, name='api_analytics_json'),
    path('admin/ai-analytics/', views.ai_analytics_dashboard, name='ai_analytics'),
]
