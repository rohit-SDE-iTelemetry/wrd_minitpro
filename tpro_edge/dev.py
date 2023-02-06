import django
import os
# django local settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE",'tpro_edge.settings')
django.setup()

from django.db import IntegrityError
import datetime
from mtpo_app.models import Site, Reading
import pandas as pd
file_loc = "/home/rohit/Desktop/dev/tpro_edge/aaxipro_site_202302061431_nhp_wrdcg_sites.csv"

df = pd.read_csv(file_loc)
# df = pd.read_excel(file_loc)

Data_reverse_row_1 = df.iloc[::]
print(Data_reverse_row_1)


for dfssss in Data_reverse_row_1.values:
    site_name = dfssss[0]
    site_prefix = dfssss[1]
    site_city = dfssss[5]
    site_address = dfssss[2]
    site_longitude = dfssss[3]
    site_latitude = dfssss[4]

    siteObj = Site(name = dfssss[0],
                    prefix = dfssss[1],
                    city = dfssss[5],
                    address = dfssss[2],
                    longitude = dfssss[3],
                    latitude = dfssss[4])
    siteObj.save()

#     from dateutil import parser
#     s= parser.parse(str(dfssss[0]))
#     date=datetime.datetime.strftime(s, "%Y-%m-%d %H:%M")
# #
#     try:
#         # remove from DB
#         readingObj = Reading2022N.objects.get(site=siteObj,timestamp=date)
#         if(readingObj):
#             readingObj.delete()
#             print('reading deleted')
#             reading_Obj = Reading2022N.objects.create(site=siteObj, timestamp=date, reading=datastr)
#             print('reading saved1')

#     except Exception as err:
#         print('error >> ',err)
#         reading_Obj = Reading2022N.objects.create(site=siteObj, timestamp=date, reading=datastr)
#         print('reading saved2')

