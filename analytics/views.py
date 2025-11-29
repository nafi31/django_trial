from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import F
from datetime import timedelta
import hashlib
import json
from .models import User, Blog, BlogView
from .services import AnalyticsService
from .serializers import (
    UserSerializer, BlogSerializer, BlogViewSerializer,
    BlogViewsAnalyticsSerializer, TopAnalyticsSerializer, PerformanceAnalyticsSerializer
)
from .filters import BlogFilter, BlogViewFilter

class BaseAnalyticsView(APIView):

    def get_filters_config(self, request):
        """
        Read optional dynamic filters from the request.
        - Primary source: JSON body (supports GET with Content-Type: application/json)
        - Fallback: request.query_params['filters'] for backward compatibility
        """
        filters_config = None
        
        # First, try to get filters from JSON body
        if request.content_type == 'application/json' and request.body:
            try:
                import json
                body_data = json.loads(request.body)
                filters_config = body_data.get("filters")
            except (json.JSONDecodeError, ValueError):
                pass
        
        # Fallback to query params if not found in body
        if filters_config is None:
            filters_config = request.query_params.get("filters")
        
        if not filters_config:
            return None

        # If filters are passed as a JSON string, parse them
        if isinstance(filters_config, str):
            try:
                import json
                return json.loads(filters_config)
            except json.JSONDecodeError:
                return None

        # Already a dict/list
        return filters_config

class BlogViewsAnalyticsView(BaseAnalyticsView):

    def _get_cache_key(self, request):
        """Generate cache key including body parameters."""
        cache_key_parts = [request.path]
        
        if request.query_params:
            cache_key_parts.append(str(sorted(request.query_params.items())))
        
        if request.content_type == 'application/json' and request.body:
            try:
                body_data = json.loads(request.body)
                cache_key_parts.append(json.dumps(body_data, sort_keys=True))
            except (json.JSONDecodeError, ValueError):
                pass
        
        cache_key = hashlib.md5('|'.join(cache_key_parts).encode()).hexdigest()
        return f"analytics:{request.path}:{cache_key}"

    def get(self, request):
        """
        Blog views analytics.

        Supports sending parameters in the **GET body** (JSON) or as query params.
        Recommended (body):
        {
            "object_type": "user",
            "range": "month",
            "filters": { ...optional dynamic filters... }
        }
        """
        # Parse JSON body for GET requests if Content-Type is application/json
        payload = request.query_params.copy()
        if request.content_type == 'application/json' and request.body:
            try:
                import json
                body_data = json.loads(request.body)
                payload.update(body_data)
            except (json.JSONDecodeError, ValueError):
                pass
        
        # Check cache first
        cache_key = self._get_cache_key(request)
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)
        
        serializer = BlogViewsAnalyticsSerializer(data=payload)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        filters_config = self.get_filters_config(request)

        try:
            result = AnalyticsService.get_blog_views_analytics(
                object_type=data['object_type'],
                range_type=data['range'],
                filters_config=filters_config,
            )
            response_data = {'data': result}
            
            # Cache the data (not the Response object) for 5 minutes
            cache.set(cache_key, response_data, 60 * 5)
            return Response(response_data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class TopAnalyticsView(BaseAnalyticsView):

    def _get_cache_key(self, request):
        """Generate cache key including body parameters."""
        cache_key_parts = [request.path]
        
        if request.query_params:
            cache_key_parts.append(str(sorted(request.query_params.items())))
        
        if request.content_type == 'application/json' and request.body:
            try:
                body_data = json.loads(request.body)
                cache_key_parts.append(json.dumps(body_data, sort_keys=True))
            except (json.JSONDecodeError, ValueError):
                pass
        
        cache_key = hashlib.md5('|'.join(cache_key_parts).encode()).hexdigest()
        return f"analytics:{request.path}:{cache_key}"

    def get(self, request):
        """
        Top analytics.

        Supports sending parameters in the **GET body** (JSON) or as query params.
        Recommended (body):
        {
            "top": "blog",
            "time_range": "last_30_days",   # optional
            "filters": { ...optional dynamic filters... }
        }
        """
        # Parse JSON body for GET requests if Content-Type is application/json
        payload = request.query_params.copy()
        if request.content_type == 'application/json' and request.body:
            try:
                import json
                body_data = json.loads(request.body)
                payload.update(body_data)
            except (json.JSONDecodeError, ValueError):
                pass
        
        # Check cache first
        cache_key = self._get_cache_key(request)
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)
        
        serializer = TopAnalyticsSerializer(data=payload)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        filters_config = self.get_filters_config(request)

        try:
            result = AnalyticsService.get_top_analytics(
                top_type=data['top'],
                filters_config=filters_config,
                time_range=data.get('time_range'),
            )
            response_data = {'data': result}
            
            # Cache the data (not the Response object) for 10 minutes
            cache.set(cache_key, response_data, 60 * 10)
            return Response(response_data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class PerformanceAnalyticsView(BaseAnalyticsView):

    def _get_cache_key(self, request):
        """Generate cache key including body parameters."""
        cache_key_parts = [request.path]
        
        if request.query_params:
            cache_key_parts.append(str(sorted(request.query_params.items())))
        
        if request.content_type == 'application/json' and request.body:
            try:
                body_data = json.loads(request.body)
                cache_key_parts.append(json.dumps(body_data, sort_keys=True))
            except (json.JSONDecodeError, ValueError):
                pass
        
        cache_key = hashlib.md5('|'.join(cache_key_parts).encode()).hexdigest()
        return f"analytics:{request.path}:{cache_key}"

    def get(self, request):
        """
        Performance analytics.

        Supports sending parameters in the **GET body** (JSON) or as query params.
        Recommended (body):
        {
            "compare": "month",
            "user_id": 1,                 # optional
            "filters": { ...optional dynamic filters... }
        }
        """
        # Check cache first
        cache_key = self._get_cache_key(request)
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)
        
        # Parse JSON body for GET requests if Content-Type is application/json
        payload = request.query_params.copy()
        if request.content_type == 'application/json' and request.body:
            try:
                body_data = json.loads(request.body)
                payload.update(body_data)
            except (json.JSONDecodeError, ValueError):
                pass
        
        serializer = PerformanceAnalyticsSerializer(data=payload)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        filters_config = self.get_filters_config(request)

        try:
            result = AnalyticsService.get_performance_analytics(
                compare=data['compare'],
                user_id=data.get('user_id'),
                filters_config=filters_config,
            )
            response_data = {'data': result}
            
            # Cache the data (not the Response object) for 2 minutes
            cache.set(cache_key, response_data, 60 * 2)
            return Response(response_data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
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