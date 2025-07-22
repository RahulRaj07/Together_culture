from django.contrib import admin
from .models import Member, Interest
from django.contrib.auth.admin import UserAdmin

class MemberAdmin(UserAdmin):
    model = Member
    list_display = ['username', 'email', 'is_admin', 'is_approved']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone_number', 'location', 'interests', 'is_admin', 'is_approved')}),
    )

admin.site.register(Member, MemberAdmin)
admin.site.register(Interest)
