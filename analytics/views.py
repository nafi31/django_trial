from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import F
from datetime import timedelta
from .models import User, Blog, BlogView
from .services import AnalyticsService
from .serializers import (
    UserSerializer, BlogSerializer, BlogViewSerializer,
    BlogViewsAnalyticsSerializer, TopAnalyticsSerializer, PerformanceAnalyticsSerializer
)
from .filters import BlogFilter, BlogViewFilter

class BaseAnalyticsView(APIView):
 
    
    def get_filters_config(self, request):
     
        filters_config = request.query_params.get('filters')
        if filters_config:
            try:
                import json
                return json.loads(filters_config)
            except json.JSONDecodeError:
                return None
        return None

class BlogViewsAnalyticsView(BaseAnalyticsView):

    
    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    def get(self, request):
        serializer = BlogViewsAnalyticsSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        filters_config = self.get_filters_config(request)
        
        try:
            result = AnalyticsService.get_blog_views_analytics(
                object_type=data['object_type'],
                range_type=data['range'],
                filters_config=filters_config
            )
            return Response({'data': result})
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TopAnalyticsView(BaseAnalyticsView):

    
    @method_decorator(cache_page(60 * 10))  # Cache for 10 minutes
    def get(self, request):
        serializer = TopAnalyticsSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        filters_config = self.get_filters_config(request)
        
        try:
            result = AnalyticsService.get_top_analytics(
                top_type=data['top'],
                filters_config=filters_config,
                time_range=data.get('time_range')
            )
            return Response({'data': result})
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PerformanceAnalyticsView(BaseAnalyticsView):

    
    @method_decorator(cache_page(60 * 2))  # Cache for 2 minutes
    def get(self, request):
        serializer = PerformanceAnalyticsSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        filters_config = self.get_filters_config(request)
        
        try:
            result = AnalyticsService.get_performance_analytics(
                compare=data['compare'],
                user_id=data.get('user_id'),
                filters_config=filters_config
            )
            return Response({'data': result})
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.select_related('country').all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['country']

class BlogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Blog.objects.select_related('author', 'author__country').all()
    serializer_class = BlogSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = BlogFilter
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a blog and automatically increment its view count.
        """
        instance = self.get_object()
        
        # Automatically record the view when blog is opened
        self._record_view(instance)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def _record_view(self, blog):
        """
        Record a view for a blog. Gets or creates a single BlogView record per blog 
        and increments the count every time this method is called (every API call).
        """
        now = timezone.now()
        
        try:
            # Get or create a single BlogView record for this blog
            blog_view, created = BlogView.objects.get_or_create(
                blog=blog,
                defaults={'count': 1, 'viewed_at': now}
            )
            
            if not created:
                # Always increment the count on every API call
                BlogView.objects.filter(id=blog_view.id).update(
                    count=F('count') + 1,
                    viewed_at=now
                )
        except Exception as e:
            # Fallback: try to increment if record exists, otherwise create
            try:
                BlogView.objects.filter(blog=blog).update(
                    count=F('count') + 1,
                    viewed_at=now
                )
            except:
                BlogView.objects.create(blog=blog, count=1, viewed_at=now)
    
    @action(detail=True, methods=['post'])
    def record_view(self, request, pk=None):
        """
        Manually record a view for a blog (optional endpoint if needed).
        Views are now automatically tracked on GET requests to retrieve a blog.
        """
        blog = self.get_object()
        self._record_view(blog)
        
        return Response(
            {
                'message': 'View recorded successfully',
                'blog_id': blog.id
            },
            status=status.HTTP_200_OK
        )

class BlogViewViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BlogView.objects.select_related('blog', 'blog__author').all()
    serializer_class = BlogViewSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = BlogViewFilter