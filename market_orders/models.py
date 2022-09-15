from django.db import models
# need to user view_table module to create a view of the table - WIP -django-view-table module
# Or refer: https://stackoverflow.com/a/58790784/5143121


class User(models.Model):
    """User model"""
    name = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Trade(models.Model):
    """Trade model"""
    symbol = models.CharField(max_length=255)
    price = models.FloatField()
    size = models.IntegerField()
    trade_id = models.CharField(max_length=255, unique=True)
    is_buy = models.BooleanField()
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.trade_id


class TopBuyerView(models.Model):
    """TopBuyerView model"""
    user_id = models.IntegerField()
    symbol = models.CharField(max_length=255)
    total_quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user_id
