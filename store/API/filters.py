from rest_framework import filters


class CustomerPurchaseFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        if not request.user.is_superuser:
            return queryset.filter(customer=request.user)
        return queryset


class PurchaseProductPriceFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        product_price = request.query_params.get('product_price', 'No params')
        if product_price.isdigit():
            return queryset.filter(product__price__gte=product_price)
        return queryset


class CustomerProductFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        product_title = request.query_params.get('product_title')
        if product_title:
            return queryset.filter(purchases__product__title__icontains=product_title)
        return queryset


class CustomerReturnsFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        if not request.user.is_superuser:
            return queryset.filter(purchase__customer=request.user)
        return queryset
