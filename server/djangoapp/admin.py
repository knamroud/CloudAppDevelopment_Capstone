from django.contrib import admin
from .models import CarMake, CarModel

class CarModelInline(admin.StackedInline):
    model = CarModel

class CarModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'dealerId', 'type', 'year']
    search_fields = ['name', 'type']

class CarMakeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']
    inlines = [CarModelInline]

admin.site.register(CarMake, CarMakeAdmin)
admin.site.register(CarModel, CarModelAdmin)