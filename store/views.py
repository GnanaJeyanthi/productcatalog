# D:\2312040-wfp\productcatalog_project\store\views.py
from .models import Product, Category, Brand, Order, OrderItem, Review, ProductImage, Wishlist, ReturnRequest, UserActivity, Notification, AbandonedCart
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CheckoutForm, ProductForm
from decimal import Decimal
import razorpay
import json
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Avg
from django.db.models.functions import TruncDate

@staff_member_required
def order_analytics(request):
    """Analytics view for order data with graphs"""
    from django.utils import timezone
    import datetime

    # Get date filters from request
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    # Parse dates or set defaults
    if start_date_str and end_date_str:
        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            # Invalid dates, use defaults
            end_date = timezone.now().date()
            start_date = end_date - timezone.timedelta(days=30)
    else:
        # Default to last 7 days
        end_date = timezone.now().date()
        start_date = end_date - timezone.timedelta(days=7)

    # Filter orders based on date range
    orders_queryset = Order.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)

    # Total orders and revenue
    total_orders = orders_queryset.count()
    total_revenue = orders_queryset.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    # Orders by status
    status_counts = orders_queryset.values('status').annotate(count=Count('status')).order_by('status')

    # Orders over time
    orders_over_time = orders_queryset.annotate(date=TruncDate('created_at'))\
        .values('date')\
        .annotate(count=Count('id'), revenue=Sum('total_amount'))\
        .order_by('date')

    # Revenue over time
    revenue_over_time = json.dumps([[str(item[0]), float(item[1])] for item in orders_over_time.values_list('date', 'revenue')], cls=DjangoJSONEncoder)

    # Orders per day
    orders_per_day = json.dumps([[str(item[0]), item[1]] for item in orders_over_time.values_list('date', 'count')], cls=DjangoJSONEncoder)

    # For 7-day view, use last 7 days from end_date
    seven_days_ago = end_date - timezone.timedelta(days=7)
    orders_over_time_7 = Order.objects.filter(created_at__date__gte=seven_days_ago, created_at__date__lte=end_date)\
        .annotate(date=TruncDate('created_at'))\
        .values('date')\
        .annotate(count=Count('id'), revenue=Sum('total_amount'))\
        .order_by('date')

    # Revenue over time (7 days)
    revenue_over_time_7 = json.dumps([[str(item[0]), float(item[1])] for item in orders_over_time_7.values_list('date', 'revenue')], cls=DjangoJSONEncoder)

    # Orders per day (7 days)
    orders_per_day_7 = json.dumps([[str(item[0]), item[1]] for item in orders_over_time_7.values_list('date', 'count')], cls=DjangoJSONEncoder)

    # For 30-day view, use last 30 days from end_date
    thirty_days_ago = end_date - timezone.timedelta(days=30)
    orders_over_time_30 = Order.objects.filter(created_at__date__gte=thirty_days_ago, created_at__date__lte=end_date)\
        .annotate(date=TruncDate('created_at'))\
        .values('date')\
        .annotate(count=Count('id'), revenue=Sum('total_amount'))\
        .order_by('date')

    # Revenue over time (30 days)
    revenue_over_time_30 = json.dumps([[str(item[0]), float(item[1])] for item in orders_over_time_30.values_list('date', 'revenue')], cls=DjangoJSONEncoder)

    # Orders per day (30 days)
    orders_per_day_30 = json.dumps([[str(item[0]), item[1]] for item in orders_over_time_30.values_list('date', 'count')], cls=DjangoJSONEncoder)

    # Status distribution for pie chart
    status_labels = json.dumps([status['status'].title() for status in status_counts], cls=DjangoJSONEncoder)
    status_data = json.dumps([status['count'] for status in status_counts], cls=DjangoJSONEncoder)

    # Top users by number of orders
    top_users_by_orders = Order.objects.values('user__username')\
        .annotate(order_count=Count('id'))\
        .order_by('-order_count')[:10]

    # Top users by total revenue
    top_users_by_revenue = Order.objects.values('user__username')\
        .annotate(total_revenue=Sum('total_amount'))\
        .order_by('-total_revenue')[:10]

    # Prepare data for charts
    user_order_labels = json.dumps([user['user__username'] for user in top_users_by_orders], cls=DjangoJSONEncoder)
    user_order_data = json.dumps([user['order_count'] for user in top_users_by_orders], cls=DjangoJSONEncoder)

    user_revenue_labels = json.dumps([user['user__username'] for user in top_users_by_revenue], cls=DjangoJSONEncoder)
    user_revenue_data = json.dumps([float(user['total_revenue']) for user in top_users_by_revenue], cls=DjangoJSONEncoder)

    # Low stock products (stock < 10)
    low_stock_products = Product.objects.filter(stock__lt=10).order_by('stock')[:10]

    # Top rated products
    top_rated_products = Product.objects.annotate(avg_rating=Avg('reviews__rating')).filter(avg_rating__isnull=False).order_by('-avg_rating')[:10]

    # Most ordered products
    most_ordered_products = OrderItem.objects.values('product__name').annotate(total_ordered=Sum('quantity')).order_by('-total_ordered')[:10]

    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'status_labels': status_labels,
        'status_data': status_data,
        'orders_per_day': orders_per_day,
        'revenue_over_time': revenue_over_time,
        'orders_per_day_7': orders_per_day_7,
        'revenue_over_time_7': revenue_over_time_7,
        'orders_per_day_30': orders_per_day_30,
        'revenue_over_time_30': revenue_over_time_30,
        'user_order_labels': user_order_labels,
        'user_order_data': user_order_data,
        'user_revenue_labels': user_revenue_labels,
        'user_revenue_data': user_revenue_data,
        'low_stock_products': low_stock_products,
        'top_rated_products': top_rated_products,
        'most_ordered_products': most_ordered_products,
    }

    return render(request, 'store/admin_analytics.html', context)

def product_list(request):
    products = Product.objects.filter(stock__gt=0).select_related('category', 'brand').prefetch_related('images', 'reviews')
    categories = Category.objects.all()
    brands = Brand.objects.all()

    selected_category_slug = request.GET.get('category')
    selected_brand_slug = request.GET.get('brand')
    search_query = request.GET.get('q')
    sort_by = request.GET.get('sort')

    if selected_category_slug:
        products = products.filter(category__slug=selected_category_slug)

    if selected_brand_slug:
        products = products.filter(brand__slug=selected_brand_slug)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name_asc':
        products = products.order_by('name')
    elif sort_by == 'name_desc':
        products = products.order_by('-name')
    else:
        products = products.order_by('-created_at')

    # Check if user is college student for discounts
    user_is_college_student = False
    discount_categories = ['Laptop', 'Computer', 'Tablet', 'Smartphone', 'Accessories']  # Categories eligible for discount

    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            if profile.profile_completed and profile.is_college_student:
                user_is_college_student = True
        except:
            pass

    # Add average rating, review count, and discount info to each product
    for product in products:
        reviews = product.reviews.all()
        if reviews:
            product.average_rating = round(sum(review.rating for review in reviews) / len(reviews), 1)
            product.review_count = len(reviews)
        else:
            product.average_rating = 0
            product.review_count = 0

        # Apply discount for college students on eligible categories
        product.original_price = product.price
        product.discounted_price = None
        product.discount_percentage = None

        if user_is_college_student and product.category and product.category.name in discount_categories:
            discount_amount = product.price * Decimal('0.10')  # 10% discount
            product.discounted_price = product.price - discount_amount
            product.discount_percentage = 10

    context = {
        'products': products,
        'categories': categories,
        'brands': brands,
        'selected_category_slug': selected_category_slug,
        'selected_brand_slug': selected_brand_slug,
        'search_query': search_query,
        'sort_by': sort_by,
        'user_is_college_student': user_is_college_student,
        'discount_categories': discount_categories,
    }

    return render(request, 'store/product_list.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, stock__gt=0)
    product_images = product.images.all()
    
    context = {
        'product': product,
        'product_images': product_images,
    }
    return render(request, 'store/product_detail.html', context)

@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get(settings.CART_SESSION_ID, {})

    product_id_str = str(product_id)
    quantity = int(request.POST.get('quantity', 1))

    if product_id_str in cart:
        cart[product_id_str]['quantity'] += quantity
    else:
        cart[product_id_str] = {'quantity': quantity, 'price': str(product.price)}

    request.session[settings.CART_SESSION_ID] = cart
    request.session.modified = True

    # Tracking abandoned cart for logged in users
    if request.user.is_authenticated:
        abandoned_item, created = AbandonedCart.objects.get_or_create(
            user=request.user,
            product=product,
            is_converted=False
        )
        if not created:
            abandoned_item.quantity += quantity
            abandoned_item.save()
        else:
            abandoned_item.quantity = quantity
            abandoned_item.save()

    messages.success(request, f'{product.name} added to cart!')
    return redirect(request.POST.get('next', 'product_list'))

def cart_detail(request):
    return render(request, 'store/cart_detail.html')

@require_POST
def remove_from_cart(request, product_id):
    cart = request.session.get(settings.CART_SESSION_ID, {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]
        request.session[settings.CART_SESSION_ID] = cart
        request.session.modified = True
        messages.success(request, 'Item removed from cart!')

    return redirect('cart_detail')

@login_required
def checkout(request):
    cart = request.session.get(settings.CART_SESSION_ID, {})
    
    if not cart:
        messages.warning(request, 'Your cart is empty!')
        return redirect('product_list')
    
    # Get cart items
    product_ids = cart.keys()
    products = Product.objects.filter(id__in=product_ids)
    
    cart_items = []
    cart_total = Decimal('0.00')
    
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
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total_amount = cart_total
            
            # Handle Razorpay
            if order.payment_method == 'razorpay':
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                
                # Create Razorpay order
                razorpay_order = client.order.create({
                    'amount': int(cart_total * 100),  # Amount in paise
                    'currency': 'INR',
                    'payment_capture': 1
                })
                
                order.razorpay_order_id = razorpay_order['id']
                order.save()
                
                # Create order items
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        product_name=item['product'].name,
                        price=item['product'].price,
                        quantity=item['quantity']
                    )
                
                # Store order ID in session for payment verification
                request.session['pending_order_id'] = order.id
                
                context = {
                    'order': order,
                    'razorpay_order_id': razorpay_order['id'],
                    'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                    'amount': int(cart_total * 100),
                    'cart_total': cart_total,
                }
                return render(request, 'store/razorpay_payment.html', context)
            
            # Handle COD
            else:
                order.payment_completed = True
                order.save()
                
                # Create order items
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        product_name=item['product'].name,
                        price=item['product'].price,
                        quantity=item['quantity']
                    )
                    
                    # Reduce stock
                    product = item['product']
                    product.stock -= item['quantity']
                    product.save()
                
                # Clear cart
                request.session[settings.CART_SESSION_ID] = {}
                request.session.modified = True

                # Mark abandoned carts as converted
                AbandonedCart.objects.filter(user=request.user, is_converted=False).update(is_converted=True)
                
                messages.success(request, 'Order placed successfully!')
                return redirect('order_success', order_id=order.id)
    else:
        # Pre-fill form with user data
        initial_data = {
            'full_name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
        }
        form = CheckoutForm(initial=initial_data)
    
    context = {
        'form': form,
        'cart_items': cart_items,
        'cart_total': cart_total,
    }
    return render(request, 'store/checkout.html', context)

@csrf_exempt
@require_POST
def verify_payment(request):
    if request.method == 'POST':
        try:
            data = request.POST

            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

            # Verify signature
            params_dict = {
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature': data['razorpay_signature']
            }

            client.utility.verify_payment_signature(params_dict)

            # Get order
            order_id = request.session.get('pending_order_id')
            order = Order.objects.get(id=order_id)

            # Update order
            order.razorpay_payment_id = data['razorpay_payment_id']
            order.razorpay_signature = data['razorpay_signature']
            order.payment_completed = True
            order.save()

            # Reduce stock for order items
            for item in order.items.all():
                if item.product:
                    item.product.stock -= item.quantity
                    item.product.save()

            # Clear cart
            request.session[settings.CART_SESSION_ID] = {}
            del request.session['pending_order_id']
            request.session.modified = True

            # Mark abandoned carts as converted
            AbandonedCart.objects.filter(user=order.user, is_converted=False).update(is_converted=True)

            return JsonResponse({'status': 'success', 'order_id': order.id})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {'order': order}
    return render(request, 'store/order_success.html', context)

@login_required
def my_orders(request):
    if request.user.is_staff:
        # Staff users see all orders except their own
        orders = Order.objects.exclude(user=request.user).prefetch_related('items__product', 'user').order_by('-created_at')

        # Analytics data for staff
        total_orders = Order.objects.count()
        total_revenue = Order.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

        # Orders by status
        status_counts = Order.objects.values('status').annotate(count=Count('status')).order_by('status')

        # Orders over time (last 30 days)
        from django.utils import timezone
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        orders_over_time = Order.objects.filter(created_at__gte=thirty_days_ago)\
            .annotate(date=TruncDate('created_at'))\
            .values('date')\
            .annotate(count=Count('id'), revenue=Sum('total_amount'))\
            .order_by('date')

        # Revenue over time
        revenue_over_time = json.dumps(list(orders_over_time.values_list('date', 'revenue')), cls=DjangoJSONEncoder)

        # Orders per day
        orders_per_day = json.dumps(list(orders_over_time.values_list('date', 'count')), cls=DjangoJSONEncoder)

        # Status distribution for pie chart
        status_labels = json.dumps([status['status'].title() for status in status_counts], cls=DjangoJSONEncoder)
        status_data = json.dumps([status['count'] for status in status_counts], cls=DjangoJSONEncoder)

        # Top users by number of orders
        top_users_by_orders = Order.objects.values('user__username')\
            .annotate(order_count=Count('id'))\
            .order_by('-order_count')[:10]

        # Top users by total revenue
        top_users_by_revenue = Order.objects.values('user__username')\
            .annotate(total_revenue=Sum('total_amount'))\
            .order_by('-total_revenue')[:10]

        # Prepare data for charts
        user_order_labels = json.dumps([user['user__username'] for user in top_users_by_orders], cls=DjangoJSONEncoder)
        user_order_data = json.dumps([user['order_count'] for user in top_users_by_orders], cls=DjangoJSONEncoder)

        user_revenue_labels = json.dumps([user['user__username'] for user in top_users_by_revenue], cls=DjangoJSONEncoder)
        user_revenue_data = json.dumps([float(user['total_revenue']) for user in top_users_by_revenue], cls=DjangoJSONEncoder)

        # Low stock products (stock < 10)
        low_stock_products = Product.objects.filter(stock__lt=10).order_by('stock')[:10]

        # Top rated products
        top_rated_products = Product.objects.annotate(avg_rating=Avg('reviews__rating')).filter(avg_rating__isnull=False).order_by('-avg_rating')[:10]

        # Most ordered products
        most_ordered_products = OrderItem.objects.values('product__name').annotate(total_ordered=Sum('quantity')).order_by('-total_ordered')[:10]

        context = {
            'orders': orders,
            'show_analytics': True,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'status_labels': status_labels,
            'status_data': status_data,
            'orders_per_day': orders_per_day,
            'revenue_over_time': revenue_over_time,
            'user_order_labels': user_order_labels,
            'user_order_data': user_order_data,
            'user_revenue_labels': user_revenue_labels,
            'user_revenue_data': user_revenue_data,
            'low_stock_products': low_stock_products,
            'top_rated_products': top_rated_products,
            'most_ordered_products': most_ordered_products,
        }
    else:
        # Regular users see only their orders
        orders = Order.objects.filter(user=request.user).prefetch_related('items__product')

        # Add review status and rating to each order item
        for order in orders:
            for item in order.items.all():
                if item.product:
                    item.has_review = Review.objects.filter(
                        user=request.user,
                        product=item.product,
                        order=order
                    ).exists()
                    # Add average rating and review count
                    reviews = item.product.reviews.all()
                    if reviews:
                        item.average_rating = round(sum(review.rating for review in reviews) / len(reviews), 1)
                        item.review_count = len(reviews)
                    else:
                        item.average_rating = 0
                        item.review_count = 0

        context = {'orders': orders, 'show_analytics': False}

    return render(request, 'store/my_orders.html', context)

@login_required
def add_review(request, order_id, product_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    product = get_object_or_404(Product, id=product_id)

    # Check if user has purchased this product in this order
    order_item = order.items.filter(product=product).first()
    if not order_item:
        messages.error(request, 'You can only review products you have purchased.')
        return redirect('my_orders')

    # Check if review already exists
    existing_review = Review.objects.filter(user=request.user, product=product, order=order).first()
    if existing_review:
        messages.warning(request, 'You have already reviewed this product.')
        return redirect('my_orders')

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()

        if not rating or not rating.isdigit() or int(rating) < 1 or int(rating) > 5:
            messages.error(request, 'Please provide a valid rating (1-5 stars).')
            return redirect('add_review', order_id=order_id, product_id=product_id)

        Review.objects.create(
            user=request.user,
            product=product,
            order=order,
            rating=int(rating),
            comment=comment if comment else None
        )

        messages.success(request, 'Thank you for your review!')
        return redirect('my_orders')

    context = {
        'order': order,
        'product': product,
        'order_item': order_item,
    }
    return render(request, 'store/add_review.html', context)

@login_required
def request_return(request, order_id):
    """Handle return request for an order"""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Check if order is eligible for return (within time limits based on category)
    from django.utils import timezone
    days_since_order = (timezone.now().date() - order.created_at.date()).days

    # Check if any product in the order has no return policy
    has_no_return_products = any(
        item.product.category.name.lower() == 'laptops'
        for item in order.items.all() if item.product
    )

    if has_no_return_products:
        messages.error(request, 'This order contains products with no return policy.')
        return redirect('my_orders')

    # Check return eligibility based on category
    max_return_days = 7  # Default
    for item in order.items.all():
        if item.product and item.product.category.name.lower() in ['mobile phones', 'smartphones']:
            max_return_days = 3
            break

    if days_since_order > max_return_days:
        messages.error(request, f'Return period has expired. Returns are accepted within {max_return_days} days.')
        return redirect('my_orders')

    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        if not reason:
            messages.error(request, 'Please provide a reason for the return.')
            return redirect('request_return', order_id=order_id)

        # Create return request
        ReturnRequest.objects.create(
            order=order,
            reason=reason
        )

        # Update order status to 'return_requested'
        order.status = 'return_requested'
        order.save()

        messages.success(request, 'Return request submitted successfully. We will process it within 2-3 business days.')
        return redirect('my_orders')

    context = {
        'order': order,
        'days_since_order': days_since_order,
        'max_return_days': max_return_days,
    }
    return render(request, 'store/request_return.html', context)

@staff_member_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            # Handle multiple images
            images = request.FILES.getlist('images')
            for i, image in enumerate(images):
                ProductImage.objects.create(
                    product=product,
                    image=image,
                    order=i
                )
            messages.success(request, f'Product "{product.name}" added successfully!')
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'store/add_product.html', {'form': form})

@login_required
def wishlist_view(request):
    """View user's wishlist"""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product__category', 'product__brand').prefetch_related('product__images')
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'store/wishlist.html', context)

@login_required
@require_POST
def add_to_wishlist(request, product_id):
    """Add product to user's wishlist"""
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    if created:
        messages.success(request, f'{product.name} added to your wishlist!')
    else:
        messages.info(request, f'{product.name} is already in your wishlist.')

    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)
    else:
        return redirect('product_detail', product_id=product_id)

@login_required
@require_POST
def remove_from_wishlist(request, product_id):
    """Remove product from user's wishlist"""
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.filter(user=request.user, product=product).delete()
    messages.success(request, f'{product.name} removed from your wishlist!')
    return redirect('wishlist')

@login_required
def compare_products(request):
    """Compare selected products from user's wishlist"""
    if request.method == 'POST':
        product_ids = request.POST.getlist('product_ids')

        if not product_ids:
            messages.warning(request, 'Please select at least two products to compare.')
            return redirect('wishlist')

        # Ensure products are in user's wishlist
        wishlist_products = Wishlist.objects.filter(
            user=request.user,
            product_id__in=product_ids
        ).select_related('product__category', 'product__brand').prefetch_related('product__images')

        if len(wishlist_products) != len(product_ids):
            messages.error(request, 'Some selected products are not in your wishlist.')
            return redirect('wishlist')

        products = [item.product for item in wishlist_products]

        # Prepare comparison data
        comparison_data = []
        fields = ['name', 'brand', 'price', 'stock', 'category', 'description']

        for field in fields:
            row = {'field': field.replace('_', ' ').title(), 'values': []}
            for product in products:
                value = getattr(product, field)
                if field == 'brand':
                    value = value.name if value else 'No Brand'
                elif field == 'category':
                    value = value.name if value else 'Uncategorized'
                elif field == 'price':
                    value = f'₹{value}'
                elif field == 'stock':
                    value = f'{value} in stock' if value > 0 else 'Out of stock'
                row['values'].append(value)
            comparison_data.append(row)

        # Handle specs separately (JSON field)
        specs_row = {'field': 'Specifications', 'values': []}
        for product in products:
            specs = product.specs or {}
            if specs:
                specs_list = [f"{k}: {v}" for k, v in specs.items()]
                specs_row['values'].append('<br>'.join(specs_list))
            else:
                specs_row['values'].append('No specifications available')
        comparison_data.append(specs_row)

        context = {
            'products': products,
            'comparison_data': comparison_data,
        }
        return render(request, 'store/compare.html', context)
    else:
        return redirect('wishlist')

def about_us(request):
    context = {
        'title': 'About Us - Product Catalog'
    }
    return render(request, 'store/about_us.html', context)
# --- AI & Personalization API Endpoints ---

@csrf_exempt
def track_activity(request):
    """API endpoint to track user interactions"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            action_type = data.get('action_type') # 'view', 'click', 'time_spent'
            duration = data.get('duration', 0)
            
            product = Product.objects.get(id=product_id)
            user = request.user if request.user.is_authenticated else None
            
            UserActivity.objects.create(
                user=user,
                product=product,
                action_type=action_type,
                duration=duration
            )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

def get_recommendations(request):
    """AI Recommendation API based on user activity"""
    user = request.user
    recommendations = []
    
    if user.is_authenticated:
        # 1. Recommended Based on Recently Viewed
        recent_views = UserActivity.objects.filter(user=user, action_type='view').order_by('-timestamp')[:5]
        viewed_product_ids = [activity.product.id for activity in recent_views]
        
        # Suggest from same categories as recently viewed
        categories = Category.objects.filter(products__id__in=viewed_product_ids).distinct()
        recommended = Product.objects.filter(category__in=categories).exclude(id__in=viewed_product_ids).order_by('?')[:4]
        
        # 2. Trending Products (Most viewed by everyone in last 7 days)
        from django.utils import timezone
        last_week = timezone.now() - timezone.timedelta(days=7)
        trending_ids = UserActivity.objects.filter(timestamp__gte=last_week, action_type='view')\
            .values('product')\
            .annotate(view_count=Count('product'))\
            .order_by('-view_count')[:4]
        
        trending_products = Product.objects.filter(id__in=[t['product'] for t in trending_ids])
        
        # Format results
        def format_product(p):
            return {
                'id': p.id,
                'name': p.name,
                'price': float(p.price),
                'image': p.get_primary_image(),
                'url': f'/product/{p.id}/'
            }

        response_data = {
            'personalized': [format_product(p) for p in recommended],
            'trending': [format_product(p) for p in trending_products]
        }
        return JsonResponse(response_data)
    else:
        # For anonymous users, just return trending
        trending_ids = UserActivity.objects.filter(action_type='view')\
            .values('product')\
            .annotate(view_count=Count('product'))\
            .order_by('-view_count')[:8]
        trending_products = Product.objects.filter(id__in=[t['product'] for t in trending_ids])
        
        return JsonResponse({
            'personalized': [],
            'trending': [{
                'id': p.id, 'name': p.name, 'price': float(p.price), 
                'image': p.get_primary_image(), 'url': f'/product/{p.id}/'
            } for p in trending_products]
        })

@csrf_exempt
def chatbot_query(request):
    """Rule-based Chatbot for Product Assistance"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query', '').lower()
            
            # Simple rule-based filtering
            products = Product.objects.all()
            
            # Handle "under [price]"
            import re
            price_match = re.search(r'under\s+(\d+)', query)
            if price_match:
                max_price = int(price_match.group(1))
                products = products.filter(price__lte=max_price)
                
            # Handle searching for categories (shoes, electronics, etc)
            categories = Category.objects.all()
            for cat in categories:
                if cat.name.lower() in query:
                    products = products.filter(category=cat)
            
            # General keyword search if no category matched
            if products.count() == Product.objects.count() and not price_match:
                 products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
            
            results = products[:5]
            
            response_text = f"Beep boop! Retail Genie found {products.count()} items for you."
            if products.count() == 0:
                response_text = "I couldn't find exactly what you're looking for, but check these out!"
                results = Product.objects.order_by('?')[:3]

            return JsonResponse({
                'message': response_text,
                'products': [{
                    'id': p.id, 'name': p.name, 'price': float(p.price),
                    'image': p.get_primary_image(), 'url': f'/product/{p.id}/'
                } for p in results]
            })
        except Exception as e:
            return JsonResponse({'message': 'Oops, something went wrong!', 'error': str(e)}, status=400)
    return JsonResponse({'message': 'Please send a POST request.'}, status=405)

def get_notifications(request):
    """Get unread notifications for user"""
    if not request.user.is_authenticated:
        return JsonResponse({'notifications': []})
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    
    # Check for abandoned carts and create notification if none exists recently
    abandoned = AbandonedCart.objects.filter(user=request.user, is_converted=False).first()
    if abandoned:
        # Create a "Bag waiting" notification if user doesn't have one
        if not Notification.objects.filter(user=request.user, title__contains="Bag waiting").exists():
            Notification.objects.create(
                user=request.user,
                title="Bag waiting for you! 🛍️",
                message=f"You left {abandoned.product.name} in your cart. Get it before it's gone!"
            )
            # Re-fetch
            notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    
    # Initial welcome notification if no notifications exist at all
    if not Notification.objects.filter(user=request.user).exists():
        Notification.objects.create(
            user=request.user,
            title="Welcome to Retail Genie! 🧞",
            message="We've upgraded your shopping experience with AI features. Happy browsing!"
        )
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')

    return JsonResponse({
        'notifications': [{
            'id': n.id, 'title': n.title, 'message': n.message, 'created_at': n.created_at
        } for n in notifications]
    })

@csrf_exempt
@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success'})

@staff_member_required
def ai_analytics_dashboard(request):
    """AI-powered Analytics Dashboard"""
    # Most viewed products
    most_viewed = Product.objects.annotate(view_count=Count('useractivity', filter=Q(useractivity__action_type='view'))).order_by('-view_count')[:10]
    
    # Most clicked categories
    most_clicked_cats = Category.objects.annotate(click_count=Count('products__useractivity', filter=Q(products__useractivity__action_type='click'))).order_by('-click_count')
    
    # Abandoned cart count
    abandoned_count = AbandonedCart.objects.filter(is_converted=False).count()
    conversion_rate = 0
    total_abandoned = AbandonedCart.objects.count()
    if total_abandoned > 0:
        conversion_rate = (AbandonedCart.objects.filter(is_converted=True).count() / total_abandoned) * 100

    context = {
        'most_viewed': most_viewed,
        'most_clicked_cats': most_clicked_cats,
        'abandoned_count': abandoned_count,
        'conversion_rate': round(conversion_rate, 2),
        'total_users': User.objects.count(),
        'recent_activities': UserActivity.objects.select_related('user', 'product').order_by('-timestamp')[:20]
    }
    return render(request, 'store/ai_analytics.html', context)

@staff_member_required
def get_analytics_json(request):
    """JSON API for analytics data"""
    most_viewed = Product.objects.annotate(view_count=Count('useractivity', filter=Q(useractivity__action_type='view'))).order_by('-view_count')[:5]
    data = {
        'most_viewed': [{'name': p.name, 'views': p.view_count} for p in most_viewed],
        'total_users': User.objects.count(),
        'abandoned_count': AbandonedCart.objects.filter(is_converted=False).count()
    }
    return JsonResponse(data)
