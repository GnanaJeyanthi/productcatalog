# TODO: Phase 1 - Core Enhancements Implementation

## 1. Wishlist System
- [x] Add Wishlist model to store/models.py (user-product many-to-many with timestamp)
- [x] Create wishlist views in store/views.py (add/remove/view)
- [x] Add wishlist URLs to store/urls.py
- [x] Create wishlist.html template
- [x] Update product_detail.html with add-to-wishlist button
- [x] Add wishlist link to base.html navbar

## 2. Advanced Search & Filters
- [x] Modify product_list view in store/views.py to handle filters (price range, brand, category, rating, availability)
- [x] Add sorting options (price, rating, newest, name) to product_list view
- [x] Update product_list.html with filter sidebar and sorting dropdown
- [x] Add advanced search form to product_list.html

## 3. Product Recommendations
- [ ] Add "Similar Products" logic based on category/brand in product_detail view
- [ ] Add "Customers Also Viewed" tracking and display in product_detail view
- [ ] Update product_detail.html to show recommendations section

## 4. Recently Viewed Products
- [x] Add RecentlyViewed model to store/models.py or use session-based tracking
- [ ] Track product views in product_detail view
- [ ] Display recently viewed on product pages and homepage
- [ ] Add recently viewed template component

## 5. Database and Admin Updates
- [x] Run migrations for new models
- [x] Update store/admin.py to register new models
- [x] Test all features thoroughly
- [x] Ensure mobile responsiveness

## 6. Enhanced Analytics Dashboard
- [x] Add low stock products analytics
- [x] Add top rated products analytics
- [x] Add most ordered products analytics
- [x] Update admin_analytics.html template with new sections
- [x] Update order_analytics view with additional data
- [x] Update my_orders.html template with additional analytics sections
- [x] Update my_orders view with additional analytics data
