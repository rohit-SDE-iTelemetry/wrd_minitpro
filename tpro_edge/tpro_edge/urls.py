from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from tpro_edge import settings

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', include('mtpo_app.urls',
                                    namespace='dashboard')),

              ] + static(settings.STATIC_URL,
                         document_root=settings.STATIC_ROOT)