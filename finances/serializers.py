from rest_framework import serializers
from .models import Currency, Category, Tag, Transaction


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'code', 'symbol', 'name', 'rate_to_base']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'type', 'icon', 'color']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color']


class TransactionSerializer(serializers.ModelSerializer):
    currency_detail = CurrencySerializer(source='currency', read_only=True)
    category_detail = CategorySerializer(source='category', read_only=True)
    tags_detail = TagSerializer(source='tags', many=True, read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'type', 'amount', 'currency', 'currency_detail',
            'category', 'category_detail',
            'tags', 'tags_detail', 'custom_tags',
            'date', 'note', 'receipt', 'is_recurring',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
