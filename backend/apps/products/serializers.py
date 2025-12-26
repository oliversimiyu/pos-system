from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Product
        fields = ('id', 'name', 'category', 'category_name', 'barcode', 'sku', 
                  'price', 'cost_price', 'tax', 'stock', 'low_stock_threshold',
                  'description', 'image', 'is_active', 'is_low_stock', 'total_price',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating products"""
    
    class Meta:
        model = Product
        fields = ('name', 'category', 'barcode', 'sku', 'price', 'cost_price', 
                  'tax', 'stock', 'low_stock_threshold', 'description', 'image', 'is_active')
    
    def validate_barcode(self, value):
        """Ensure barcode is unique"""
        instance = self.instance
        if instance:
            if Product.objects.exclude(pk=instance.pk).filter(barcode=value).exists():
                raise serializers.ValidationError("Product with this barcode already exists.")
        else:
            if Product.objects.filter(barcode=value).exists():
                raise serializers.ValidationError("Product with this barcode already exists.")
        return value
