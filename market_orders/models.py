from django.db import models


class User2(models.Model):
    """User model"""

    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Trade2(models.Model):
    """Trade model"""

    trade_id = models.AutoField(primary_key=True)
    symbol = models.CharField(max_length=255)
    bid_price = models.FloatField()
    order_quantity = models.IntegerField()
    trade_type = models.CharField(max_length=255, unique=False, null=True, blank=True)
    trade_time = models.DateTimeField(auto_now_add=True, blank=True)
    user_id = models.ForeignKey(User2, on_delete=models.CASCADE)

    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.trade_id
