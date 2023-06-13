from django.contrib import admin
from .models import (
    User,
    Participant,  
    C0, 
    T1_L, 
    T1_R,  
    Tracker2, 
    T2,  
    Treatment,
    C0_L,
    C0_R,
)
from django.contrib.sessions.models import Session

# Added by Ranjeet
class TreatmentAdmin(admin.ModelAdmin):
    change_list_template = "survey/sessionNode.html"
    list_display = ('treatmentNodeName','isActive')

# Register your models here.
admin.site.register(User)
admin.site.register(Participant)
admin.site.register(Session)
admin.site.register(C0)
admin.site.register(T1_L)
admin.site.register(T1_R)
admin.site.register(Tracker2)
admin.site.register(T2)
# Added by Ranjeet
admin.site.register(Treatment,TreatmentAdmin)
admin.site.register(C0_R)
admin.site.register(C0_L)

