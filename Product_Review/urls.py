from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from App_Product_Review.views import (custom_login_view,home_view)


urlpatterns = [
    path('', custom_login_view, name='login'),
    path('', include('App_Product_Review.urls')),
    path('home/', home_view, name='home'),
    path('admin/', admin.site.urls),

]