# Create your models here.
# from django.contrib.postgres.fields import HStoreField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
import uuid

# Create your models here.
class Site(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True,
                            max_length=120)
    industry = models.CharField(max_length=50, verbose_name='Industry', default='NHP')
    name = models.CharField(max_length=100, verbose_name='Station Name')
    category = models.CharField(max_length=10, verbose_name='Category',
                                default='')
    prefix = models.CharField(max_length=64, verbose_name='prefix',
                              unique=True)
    status = models.CharField(max_length=8,
                              default='Offline',
                              choices=(
                                  ('Live', 'Live'),
                                  ('Delay', 'Delay'),
                                  ('Offline', 'Offline')
                              )
                              )
    state = models.CharField(max_length=128, verbose_name='state', default='Chattisgarh')
    city = models.CharField(max_length=128, verbose_name='city')
    address = models.TextField(default=None, null=True, blank=True)
    longitude = models.DecimalField(decimal_places=15, max_digits=20,
                                    null=True)
    latitude = models.DecimalField(decimal_places=15, max_digits=20,
                                   null=True)
    last_reading = models.TextField(default='[]')
    last_reading_at = models.DateTimeField(null=True, blank=True)
    last_file_at = models.DateTimeField(null=True, blank=True)
    parameters = models.TextField(default='[]')
    interval = models.CharField(default=60, max_length=20)

    def __str__(self):
        return self.name


class Reading(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True,
                            max_length=120)
    site = models.ForeignKey(Site, null=True, related_name='%(class)s_id',
                             on_delete=models.CASCADE, db_index=True)
    reading = models.TextField(default='[]')
    timestamp = models.DateTimeField(null=False, blank=False)
    last_file_at = models.DateTimeField(null=False, blank=False)

    class Meta:
        unique_together = (('reading', 'site', 'timestamp'),)

    def __str__(self):
        return "%s: %s" % (self.site, self.reading)


class epan_sites(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True,
                            max_length=120)
    site = models.OneToOneField(Site, null=True, on_delete=models.CASCADE)
    previous_value = models.CharField(default=60, max_length=20)
    timestamp = models.DateTimeField(null=False, blank=False)

    def __str__(self):
        return "%s: %s" % (self.site, self.previous_value)


