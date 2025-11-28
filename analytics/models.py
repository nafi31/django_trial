from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=128, unique=True, db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'analytics_country'

class User(models.Model):
    username = models.CharField(max_length=150, unique=True, db_index=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="users", db_index=True)

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'analytics_user'

class Blog(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blogs", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'analytics_blog'
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['author', 'created_at']),
        ]

class BlogView(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="views", db_index=True)
    viewed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    count = models.PositiveIntegerField(default=1, db_index=True)

    def __str__(self):
        return f"{self.blog.title} - {self.viewed_at}"

    class Meta:
        db_table = 'analytics_blogview'
        indexes = [
            models.Index(fields=['viewed_at']),
            models.Index(fields=['blog', 'viewed_at']),
            models.Index(fields=['count']),
        ]