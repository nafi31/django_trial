# Clone and setup
git clone <repository-url>
cd analytics_test

# Install dependencies
pip install Django==4.2.7 djangorestframework==3.14.0 django-filter==23.3

# Setup database
python manage.py makemigrations
python manage.py migrate

# Create test data
python create_test_data.py

# Run server
python manage.py runserver


# Blog Views Analytics

```Endpoint: GET /api/analytics/blog-views/

Parameters:

object_type (required): country or user

range (required): week, month, or year

filters (optional): JSON filter configuration


example request : GET http://127.0.0.1:8000/api/analytics/blog-views/?object_type=country&range=month 

```

# Top Analytics
```Endpoint: GET /api/analytics/top/

Parameters:

top (required): user, country, or blog

time_range (optional): Custom time range

filters (optional): JSON filter configuration

Example Request:


GET http://127.0.0.1:8000/api/analytics/top/?top=blog
``` 
# Performance Analytics
```Endpoint: GET /api/analytics/performance/

Parameters:

compare (required): day, week, month, or year

user_id (optional): Filter by specific user

filters (optional): JSON filter configuration

Example Request:
GET http://127.0.0.1:8000/api/analytics/performance/?compare=month

```

 # Dynamic Filtering Examples
### Filter by Country:
Example Request:
```GET /api/analytics/blog-views/?object_type=user&range=month&filters={"eq":{"blog__author__country__name":"United States"}}```

### Filter by User and Content:
Example Request:
```GET /api/analytics/top/?top=blog&filters={"and":[{"eq":{"blog__author__username":"john_doe"}},{"eq":{"blog__title__icontains":"Python"}}]}```
### Exclude Specific Content:
Example Request:
```GET /api/analytics/performance/?compare=week&filters={"not":{"eq":{"blog__title__icontains":"React"}}}```
