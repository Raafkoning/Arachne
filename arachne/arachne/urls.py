from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from istos import views as istos

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', istos.scrape, name='scrape'),
    path('sec_scrape/<int:id>/<path:url>/', istos.sec_scrape, name='sec_scrape'),
    path('update/<path:url>/', istos.update, name='update'),
    path('delete/<int:id>/<str:type>/', istos.delete, name='delete'),
    path('clear/', istos.clear, name='clear'),
    path('<int:id>/', istos.items, name='items'),
    path('settings/', istos.settings, name='settings'),
    path('loading/<str:type>/', istos.loading, name='loading'),
    path('error/', istos.error, name='error'),

]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
