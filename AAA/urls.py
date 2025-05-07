
from django.contrib import admin
from django.urls import path , include

urlpatterns = [

     path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
]
