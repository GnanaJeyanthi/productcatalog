# TODO: Add Order Analytics with Graphs in Admin Page

## Steps to Complete

1. **Create Analytics View in store/views.py**
   - Add a new view function `order_analytics` that aggregates order data (e.g., orders per day, total revenue, status distribution).
   - Use Django ORM to query Order model for data like total orders, revenue, orders by status, orders over time.
   - Prepare data in JSON format suitable for Chart.js.

2. **Add URL for Analytics in store/urls.py**
   - Add a new URL pattern for the analytics view, e.g., `path('admin/analytics/', order_analytics, name='order_analytics')`.
   - Ensure it's accessible only to staff members using `@staff_member_required`.

3. **Create Analytics Template in store/templates/store/admin_analytics.html**
   - Create a new HTML template that extends the admin base template.
   - Include Chart.js library.
   - Add canvas elements for different graphs (e.g., line chart for orders over time, bar chart for revenue, pie chart for order status).
   - Use JavaScript to render the charts with data passed from the view.

4. **Modify Admin Site in store/admin.py**
   - Add a custom admin site or modify the existing one to include a link to the analytics page.
   - Override the admin index template or add a custom menu item to link to `/admin/analytics/`.

5. **Test the Analytics Page**
   - Run the server and access the admin analytics page.
   - Verify that graphs display correctly with sample data.
   - Ensure the page is only accessible to staff users.

6. **Update Admin Change Form Template if Needed**
   - If required, modify `templates/admin/change_form.html` to include any custom styling or links, but likely not necessary for this feature.

## Dependent Files
- store/views.py: Add analytics view.
- store/urls.py: Add URL pattern.
- store/templates/store/admin_analytics.html: New template for graphs.
- store/admin.py: Add link to analytics in admin interface.

## Followup Steps
- Install Chart.js if not already included (via CDN in template).
- Ensure data is accurate and handle edge cases (e.g., no orders).
- Optimize queries for performance if dealing with large datasets.
