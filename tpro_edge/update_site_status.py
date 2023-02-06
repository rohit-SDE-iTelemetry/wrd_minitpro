import django
import os
# django local settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE",'tpro_edge.settings')
django.setup()

from mtpo_app.models import Site
import datetime


def update_site_status():
    sites_obj = Site.objects.all().order_by('name')
    for site in sites_obj:
        ts_now = datetime.datetime.now()
        if(site.last_reading_at != None):
            last_reading_ts = site.last_reading_at
            duration = ts_now - last_reading_ts 
            duration_in_s = duration.total_seconds() 
            hours = divmod(duration_in_s, 3600)[0] 
            if(int(hours) >= int(4) and int(hours) < int(48)):
                site.status = 'Delay' 
            elif(int(hours) >= int(48)):
                site.status = 'Offline'
            else:
                site.status = 'Live'
            site.save()


if __name__ == "__main__":
    print('site status update started')
    update_site_status()
    print('site status update end')
