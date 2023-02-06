import django
import os
# django local settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE",'tpro_edge.settings')
django.setup()

from django.db import IntegrityError
import datetime
from mtpo_app.models import Site, Reading
import pandas as pd