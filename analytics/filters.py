from django.db.models import Q
from django_filters import rest_framework as filters
from django_filters import NumberFilter, DateTimeFilter
from .models import Blog, BlogView

class DynamicFilter:
   
    
    @staticmethod
    def build_q_object(filters_config):
       
        if not filters_config:
            return Q()
        
        return DynamicFilter._parse_filter(filters_config)
    
    @staticmethod
    def _parse_filter(filter_config):
        if 'and' in filter_config:
            q_objects = [DynamicFilter._parse_filter(f) for f in filter_config['and']]
            return DynamicFilter._combine_q_objects(q_objects, 'and')
        elif 'or' in filter_config:
            q_objects = [DynamicFilter._parse_filter(f) for f in filter_config['or']]
            return DynamicFilter._combine_q_objects(q_objects, 'or')
        elif 'not' in filter_config:
            return ~DynamicFilter._parse_filter(filter_config['not'])
        elif 'eq' in filter_config:
            return DynamicFilter._build_equality_q(filter_config['eq'])
        else:
            return Q()
    
    @staticmethod
    def _combine_q_objects(q_objects, operator):
        if not q_objects:
            return Q()
        
        combined = q_objects[0]
        for q_obj in q_objects[1:]:
            if operator == 'and':
                combined &= q_obj
            else:
                combined |= q_obj
        return combined
    
    @staticmethod
    def _build_equality_q(eq_config):
        q_obj = Q()
        for field, value in eq_config.items():
            q_obj &= Q(**{field: value})
        return q_obj

class BlogFilter(filters.FilterSet):
    author = NumberFilter(field_name='author', lookup_expr='exact')
    created_at = DateTimeFilter(field_name='created_at', lookup_expr='exact')
    created_at__gte = DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at__lte = DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Blog
        fields = ['author', 'created_at']

class BlogViewFilter(filters.FilterSet):
    class Meta:
        model = BlogView
        fields = ['blog', 'viewed_at']