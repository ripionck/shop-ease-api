import django_filters
from django.db.models import Q
from django.core.exceptions import ValidationError
from .models import Product, Category


class ProductFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        method='custom_search', help_text="Search by name, brand, or category.")
    category = django_filters.ModelMultipleChoiceFilter(
        field_name='category__id',
        queryset=Category.objects.all(),
        to_field_name='id',
        help_text="Filter by category IDs."
    )
    min_price = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte',
        help_text="Minimum price.",
        error_messages={'invalid': 'Invalid minimum price value.'}
    )
    max_price = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte',
        help_text="Maximum price.",
        error_messages={'invalid': 'Invalid maximum price value.'}
    )
    rating = django_filters.CharFilter(
        method='filter_rating',
        help_text="Comma-separated list of ratings to filter by."
    )
    sort = django_filters.ChoiceFilter(
        method='filter_by_sort',
        choices=[
            ('price-low-high', 'Price Low to High'),
            ('price-high-low', 'Price High to Low'),
            ('rating', 'Rating'),
            ('featured', 'Featured'),
        ],
        help_text="Sort results."
    )

    class Meta:
        model = Product
        fields = []

    def custom_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(brand__icontains=value) |
            Q(category__name__icontains=value)
        ).distinct()

    def filter_rating(self, queryset, name, value):
        try:
            ratings = [int(r.strip())
                       for r in value.split(',') if r.strip().isdigit()]
            if not ratings:
                raise ValueError
            return queryset.filter(rating__in=ratings)
        except (ValueError, TypeError):
            raise ValidationError("Invalid rating value.")

    def filter_by_sort(self, queryset, name, value):
        if value == 'price-low-high':
            return queryset.order_by('price')
        elif value == 'price-high-low':
            return queryset.order_by('-price')
        elif value == 'rating':
            return queryset.order_by('-rating')
        elif value == 'featured':
            return queryset.order_by('-created_at')
        return queryset
