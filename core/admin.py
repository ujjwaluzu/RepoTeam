from django.contrib import admin
from .models import Team, Membership, Project, Issue,Comment 
# Register your models here.
admin.site.register(Team)
admin.site.register(Membership)
admin.site.register(Project)
admin.site.register(Issue)
admin.site.register(Comment)