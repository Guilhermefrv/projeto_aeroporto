from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('skybridgeapp.urls')),
]

handler404 = 'skybridgeapp.views.erro_404'
handler500 = 'skybridgeapp.views.erro_500'
