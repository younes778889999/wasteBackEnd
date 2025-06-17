from django.contrib import admin
from . import models
# Register your models here.
class TruckAdmin(admin.ModelAdmin):
    list_display=['id','Truck_model','Availability']
    list_editable = ['Availability']
class EmployeeAdmin(admin.ModelAdmin):
    list_select_related=['user']
class TripAdmin(admin.ModelAdmin):
    list_display = ['id','truck','Landfill','Start_Date','Duration_min','Distance_km','Fuel_Spent_Liter','container_set','Deviated','initial_truck_latitude', 'initial_truck_longitude']
admin.site.register(models.Truck,TruckAdmin)
admin.site.register(models.Worker)
admin.site.register(models.Driver)
admin.site.register(models.Employee)
admin.site.register(models.Waste_Container)
admin.site.register(models.Landfill)
admin.site.register(models.Trip)
admin.site.register(models.Complaints)
admin.site.register(models.Location)
admin.site.register(models.User)
admin.site.register(models.HistoryTrip)





