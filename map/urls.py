from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # NDVI data API
    path('api/ndvi/<str:site_id>/', views.ndvi_all_years, name='ndvi-all-years'),
    path('api/ndvi/<str:site_id>/<int:year>/', views.ndvi_data, name='ndvi-data'),
    # Comments API
    path('api/comments/<str:site_id>/<int:year>/', views.CommentList.as_view(), name='comments'),
    # User marks API
    path('api/marks/', views.UserMarkList.as_view(), name='marks'),
    # Auth status
    path('api/auth/status/', views.auth_status, name='auth-status'),
]
