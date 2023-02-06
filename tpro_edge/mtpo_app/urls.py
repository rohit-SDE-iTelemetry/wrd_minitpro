from django.urls import path

# Routers provide an easy way of automatically determining the URL conf.
from mtpo_app.views import *

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.


app_name = 'dashboard'
urlpatterns = [
    path('', Dashboard.as_view(), name='dashboard'),
    path('', RefreshDB.as_view(), name='refresh-db'),
    path('', Reports.as_view(), name='report'),
    path('', update_chart_n_table),
]