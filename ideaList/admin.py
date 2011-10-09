from django.contrib import admin
from ideaList.models import List,Item,Subscription

class ItemInline(admin.TabularInline):
    model = Item
    extra = 3
class ListAdmin(admin.ModelAdmin):
    list_display = ('name', 'owners_first_name', 'n_items')
    search_fields = ['name']
    inlines = [ItemInline]
    def owners_first_name(self, obj):
        return obj.owner.first_name
    owners_first_name.short_description = "Owner"
admin.site.register(List, ListAdmin)

class ItemAdmin(admin.ModelAdmin):
    list_display = ('list', 'text', 'priority', 'last_changed')
    list_filter = ('list', 'priority', 'last_changed')
admin.site.register(Item, ItemAdmin)

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('list', 'user')
    list_filter = ('list', 'user')
admin.site.register(Subscription, SubscriptionAdmin)
