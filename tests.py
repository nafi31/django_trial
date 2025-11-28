from django.test import TestCase

# Create your tests here.
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'analytics_test.settings')
django.setup()

from analytics.models import Country, User, Blog, BlogView
from django.utils import timezone
from datetime import timedelta

def create_test_data():
    # Clear existing data
    BlogView.objects.all().delete()
    Blog.objects.all().delete()
    User.objects.all().delete()
    Country.objects.all().delete()
    
    # Create countries
    usa = Country.objects.create(name="United States")
    uk = Country.objects.create(name="United Kingdom")
    canada = Country.objects.create(name="Canada")
    germany = Country.objects.create(name="Germany")
    
    # Create users
    user1 = User.objects.create(username="john_doe", country=usa)
    user2 = User.objects.create(username="jane_smith", country=uk)
    user3 = User.objects.create(username="bob_wilson", country=canada)
    user4 = User.objects.create(username="alice_brown", country=germany)
    
    # Create blogs
    blog1 = Blog.objects.create(title="Python Programming Guide", author=user1)
    blog2 = Blog.objects.create(title="Django Best Practices", author=user1)
    blog3 = Blog.objects.create(title="React Tutorial", author=user2)
    blog4 = Blog.objects.create(title="Vue.js Fundamentals", author=user3)
    blog5 = Blog.objects.create(title="Data Science with Python", author=user4)
    
    # Create blog views with different dates for time-series testing
    now = timezone.now()
    
    # Blog 1 views (most popular)
    for i in range(50):
        BlogView.objects.create(
            blog=blog1,
            count=1,
            viewed_at=now - timedelta(days=i % 30)
        )
    
    # Blog 2 views
    for i in range(30):
        BlogView.objects.create(
            blog=blog2,
            count=1,
            viewed_at=now - timedelta(days=i % 20)
        )
    
    # Blog 3 views
    for i in range(20):
        BlogView.objects.create(
            blog=blog3,
            count=1,
            viewed_at=now - timedelta(days=i % 15)
        )
    
    # Blog 4 views
    for i in range(15):
        BlogView.objects.create(
            blog=blog4,
            count=1,
            viewed_at=now - timedelta(days=i % 10)
        )
    
    # Blog 5 views
    for i in range(10):
        BlogView.objects.create(
            blog=blog5,
            count=1,
            viewed_at=now - timedelta(days=i % 5)
        )
    
    print("Test data created successfully!")
    print(f"Countries: {Country.objects.count()}")
    print(f"Users: {User.objects.count()}")
    print(f"Blogs: {Blog.objects.count()}")
    print(f"Blog Views: {BlogView.objects.count()}")

if __name__ == "__main__":
    create_test_data()