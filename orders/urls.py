from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('ajax/load-products/', views.load_products, name='ajax_load_products'),
    path('orders/', views.order_list, name='order_list'),
    path('place_order/', views.place_order, name='place_order'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('edit-image/<int:order_id>/', views.edit_reference_image, name='edit_reference_image'),
    path('delete-order/<int:order_id>/', views.delete_order, name='delete_order'),
    path('order_cost_summary/<int:order_id>/', views.order_cost_view, name='order_cost_summary'),
]
