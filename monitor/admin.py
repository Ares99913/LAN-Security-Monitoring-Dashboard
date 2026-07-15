from django.contrib import admin
from .models import (
    Machine, Alert, BannedIP, SecurityAlert,
    ManagedSwitch, SwitchPort, TraceRoute, TraceHop,
)

# Register your models here.
admin.site.register(Machine)
admin.site.register(Alert)
admin.site.register(BannedIP)
admin.site.register(SecurityAlert)
admin.site.register(ManagedSwitch)
admin.site.register(SwitchPort)
admin.site.register(TraceRoute)
admin.site.register(TraceHop)
