# models.py
import datetime
from datetime import datetime
from django.contrib.auth.models import User
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255,default='Unknown')
    brand = models.CharField(max_length=255,default='Unknown')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # Just use auto_now_add
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='static/product_images', null=True, blank=True)

    def __str__(self):
        return self.name

class Review(models.Model):
        product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
        user = models.ForeignKey(User, on_delete=models.CASCADE)
        description = models.TextField()
        rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # 1 to 5 stars
        created_at = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return f"Review by {self.user.username} for {self.product.name}"