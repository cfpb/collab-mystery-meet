from django.contrib import admin
from mystery.models import Interest

class InterestAdmin(admin.ModelAdmin):
    list_display = ('owner', 'is_active', 'match_name', 'for_lunch',
                    'for_coffee', 'video_chat', 'location_list', 'dept_list',
                    'created', 'updated')
    search_fields = ['owner__username', 'is_active', 'match__owner__username',
                     'locations__name', 'departments__title']

    def match_name(self, obj):
        if obj.match:
            return obj.match.owner
        else:
            return None
    match_name.short_description = 'Match'

    def location_list(self, obj):
        return ", ".join([location.name for location in obj.locations.all()])
    location_list.short_description = 'Locations'

    def dept_list(self, obj):
        return ", ".join([dept.title for dept in obj.departments.all()])
    location_list.short_description = 'Departments'

admin.site.register(Interest, InterestAdmin)
