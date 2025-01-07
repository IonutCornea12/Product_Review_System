from django.urls import path
from App_Product_Review.views import (
    custom_logout_view, product_detail, delete_review, custom_login_view, custom_register_view, edit_product,
    add_product, explore_products, delete_product, view_all_user_profiles, reset_password)

urlpatterns = [
    path('accounts/logout/', custom_logout_view, name='logout'),
    path('accounts/login/', custom_login_view, name='login'),
    path("accounts/reset-password/", reset_password, name="reset_password"),
    path('accounts/register/', custom_register_view, name='register'),
    path('add_product/', add_product, name='add_product'),
    path('explore_products/', explore_products, name='explore_products'),
    path('delete_product/<int:product_id>/', delete_product, name='delete_product'),
    path('edit_product/<int:product_id>/', edit_product, name='edit_product'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('delete_review/<int:review_id>/', delete_review, name='delete_review'),
    path('admin/user-profiles/', view_all_user_profiles, name='view_all_user_profiles'),

]