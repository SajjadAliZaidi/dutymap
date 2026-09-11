from django.contrib import admin
from .branding import BUILT_BY
from .models import Trip

admin.site.site_header = f"DutyMap Administration — built by {BUILT_BY['name']}"
admin.site.site_title = "DutyMap Admin"
admin.site.index_title = "Trip Planning Console"

admin.site.register(Trip)
