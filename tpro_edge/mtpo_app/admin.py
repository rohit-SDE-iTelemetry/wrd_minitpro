from django.contrib import admin
from mtpo_app.models import *

tables = [
    Site,
    Reading,
    epan_sites,
]

for table in tables:
    admin.site.register(table)