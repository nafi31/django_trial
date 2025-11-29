from django.db.models import Count, Sum, Q, F, Window
from django.db.models.functions import Trunc, Lag
from django.utils import timezone
from datetime import timedelta
from .models import Blog, BlogView, User, Country
from .filters import DynamicFilter

class AnalyticsService:
 
    @staticmethod
    def get_blog_views_analytics(object_type, range_type, filters_config=None):
     
        base_qs = BlogView.objects.select_related(
            'blog', 'blog__author', 'blog__author__country'
        )
        
        if filters_config:
            q_object = DynamicFilter.build_q_object(filters_config)
            base_qs = base_qs.filter(q_object)
        
      
        date_trunc = AnalyticsService._get_date_trunc(range_type)
        start_date = AnalyticsService._get_range_start_date(range_type)
        base_qs = base_qs.filter(viewed_at__gte=start_date)
        
     
        if object_type == 'country':
            group_field = 'blog__author__country__name'
        else:  
            group_field = 'blog__author__username'
        
 
        analytics_data = (
            base_qs
            .annotate(period=Trunc('viewed_at', date_trunc))
            .values('period', group_field)
            .annotate(
                number_of_blogs=Count('blog_id', distinct=True),
                total_views=Sum('count')
            )
            .order_by('period', group_field)
        )
        
        return [
            {
                'x': item[group_field],
                'y': item['number_of_blogs'],
                'z': item['total_views']
            }
            for item in analytics_data
        ]
    
    @staticmethod
    def get_top_analytics(top_type, filters_config=None, time_range=None):
     
        base_qs = BlogView.objects.all()
        
        if filters_config:
            q_object = DynamicFilter.build_q_object(filters_config)
            base_qs = base_qs.filter(q_object)
        
        if time_range:
            start_date = AnalyticsService._parse_time_range(time_range)
            base_qs = base_qs.filter(viewed_at__gte=start_date)
        
        if top_type == 'blog':
            return AnalyticsService._get_top_blogs(base_qs)
        elif top_type == 'user':
            return AnalyticsService._get_top_users(base_qs)
        elif top_type == 'country':
            return AnalyticsService._get_top_countries(base_qs)
    
    @staticmethod
    def _get_top_blogs(queryset):
  
        return list(
            queryset
            .select_related('blog', 'blog__author')
            .filter(blog__isnull=False)  # Ensure blog exists
            .values('blog_id', 'blog__title', 'blog__author__username')
            .annotate(
                x=F('blog__title'),
                y=F('blog_id'),  # y represents blog ID for top blogs
                z=Sum('count')
            )
            .order_by('-z')[:10]
        )
    
    @staticmethod
    def _get_top_users(queryset):

        return list(
            queryset
            .select_related('blog__author')
            .values('blog__author__username')
            .annotate(
                x=F('blog__author__username'),
                y=Count('blog_id', distinct=True),
                z=Sum('count')
            )
            .order_by('-z')[:10]
        )
    
    @staticmethod
    def _get_top_countries(queryset):
       
        return list(
            queryset
            .select_related('blog__author__country')
            .values('blog__author__country__name')
            .annotate(
                x=F('blog__author__country__name'),
                y=Count('blog_id', distinct=True),
                z=Sum('count')
            )
            .order_by('-z')[:10]
        )
    
    @staticmethod
    def get_performance_analytics(compare, user_id=None, filters_config=None):
     
        base_qs = BlogView.objects.select_related('blog')
        
        if user_id:
            base_qs = base_qs.filter(blog__author_id=user_id)
        
        if filters_config:
            q_object = DynamicFilter.build_q_object(filters_config)
            base_qs = base_qs.filter(q_object)
        
        date_trunc = AnalyticsService._get_date_trunc(compare)
        
   
        performance_data = (
            base_qs
            .annotate(period=Trunc('viewed_at', date_trunc))
            .values('period')
            .annotate(
                number_of_blogs=Count('blog_id', distinct=True),
                views=Sum('count'),
            )
            .annotate(
                previous_views=Window(
                    expression=Lag('views'),
                    partition_by=[],
                    order_by=F('period').asc(),
                )
            )
            .order_by('period')
        )
        
     
        blog_qs = Blog.objects.all()
        if user_id:
            blog_qs = blog_qs.filter(author_id=user_id)
        
        blogs_by_period = (
            blog_qs
            .annotate(period=Trunc('created_at', date_trunc))
            .values('period')
            .annotate(
                blogs_created=Count('id')
            )
            .order_by('period')
        )
        
       
        blogs_dict = {item['period']: item['blogs_created'] for item in blogs_by_period}
        
        
        result = []
        for item in performance_data:
            period = item['period']
            blogs_created = blogs_dict.get(period, 0)
            current_views = item['views'] or 0
            previous_views = item['previous_views'] or 0
            
            if previous_views > 0:
                growth_pct = ((current_views - previous_views) / previous_views) * 100
            else:
                growth_pct = 100.0 if current_views > 0 else 0.0

       
            if date_trunc == 'month':
                period_label_base = period.strftime('%B %Y')
            elif date_trunc == 'week':
                period_label_base = period.strftime('%b %d, %Y')
            elif date_trunc == 'day':
                period_label_base = period.strftime('%B %d, %Y')
            elif date_trunc == 'year':
                period_label_base = period.strftime('%Y')
            else:
                period_label_base = period.strftime('%B %d, %Y')

            period_label = f"{period_label_base} ({blogs_created} blogs)"

            result.append({
                'x': period_label,
                'y': current_views,
                'z': round(growth_pct, 2)
            })
        
        return result
    
    @staticmethod
    def _get_date_trunc(range_type):
        trunc_map = {
            'day': 'day',
            'week': 'week',
            'month': 'month',
            'year': 'year'
        }
        return trunc_map.get(range_type, 'day')
    
    @staticmethod
    def _get_range_start_date(range_type):
        now = timezone.now()
        range_map = {
            'day': now - timedelta(days=1),
            'week': now - timedelta(days=7),
            'month': now - timedelta(days=30),
            'year': now - timedelta(days=365),
        }
        return range_map.get(range_type, now - timedelta(days=7))
    
    @staticmethod
    def _parse_time_range(time_range):
        """
        Parse time range string and return the start date.
        Supports: 'last_7_days', 'last_30_days', 'last_90_days', 'last_year', etc.
        """
        now = timezone.now()
        
        if not time_range:
            return now - timedelta(days=30)
        
        time_range_lower = time_range.lower().strip()
        
      
        if 'last_7_days' in time_range_lower or '7_days' in time_range_lower:
            return now - timedelta(days=7)
        elif 'last_30_days' in time_range_lower or '30_days' in time_range_lower:
            return now - timedelta(days=30)
        elif 'last_90_days' in time_range_lower or '90_days' in time_range_lower:
            return now - timedelta(days=90)
        elif 'last_year' in time_range_lower or '365_days' in time_range_lower:
            return now - timedelta(days=365)
        elif 'last_week' in time_range_lower:
            return now - timedelta(days=7)
        elif 'last_month' in time_range_lower:
            return now - timedelta(days=30)
        else:
        
            return now - timedelta(days=30)