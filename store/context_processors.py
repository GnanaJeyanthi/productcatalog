# D:\2312040-wfp\productcatalog_project\store\context_processors.py
from .models import Product
from django.conf import settings
from decimal import Decimal

def cart(request):
    """
    A context processor to make the cart available on all pages.
    """
    cart = request.session.get(settings.CART_SESSION_ID, {})
    cart_items = []
    cart_total = Decimal('0.00')
    cart_item_count = 0
    
    product_ids = cart.keys()
    products = Product.objects.filter(id__in=product_ids)
    
    for product in products:
        product_id_str = str(product.id)
        if product_id_str not in cart:
            continue
            
        quantity = cart[product_id_str]['quantity']
        total_price = product.price * quantity
        
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total_price': total_price,
        })
        cart_total += total_price
        cart_item_count += quantity

    return {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'cart_item_count': cart_item_count,
    }
