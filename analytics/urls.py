from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BlogViewsAnalyticsView,
    TopAnalyticsView,
    PerformanceAnalyticsView,
    UserViewSet,
    BlogViewSet,
    BlogViewViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'blogs', BlogViewSet)
router.register(r'blog-views', BlogViewViewSet)

urlpatterns = [
    path('analytics/blog-views/', BlogViewsAnalyticsView.as_view(), name='blog-views-analytics'),
    path('analytics/top/', TopAnalyticsView.as_view(), name='top-analytics'),
    path('analytics/performance/', PerformanceAnalyticsView.as_view(), name='performance-analytics'),
    path('', include(router.urls)),
]