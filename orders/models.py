from django.db import models
from django.contrib.auth.models import User

# Create your models here.
from django.db import models

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_email = models.EmailField()

    def __str__(self):
        return self.name


class Product(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=100)
    price_per_unit = models.FloatField()

    def __str__(self):
        return f"{self.name} ({self.supplier.name})"
    
    
STATUS_CHOICES = [
    ('Placed', 'Placed'),
    ('Shipped', 'Shipped'),
    ('Delivered', 'Delivered'),
]

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True, blank=True)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=50, choices=[
        ('Placed', 'Placed'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered')
    ])
    reference_image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} from {self.supplier.name}"
