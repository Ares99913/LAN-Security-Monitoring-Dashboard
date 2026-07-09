from django.urls import path
from . import views

urlpatterns = [
    path('',                              views.dashboard_view),
    path('api/login/',                    views.login_api),
    path('api/heartbeat/',                views.heartbeat),
    path('api/alert/',                    views.receive_alert),
    path('api/dashboard/',                views.get_dashboard_data),
    path('api/banned-ips/',               views.get_banned_ips),
    path('api/unban/<str:ip>/',           views.unban_ip),
    path('api/alerts/mark-read/',         views.mark_alerts_read),
    path('api/switch/',                   views.get_switch_data),
    path('api/traceroute/',               views.get_traceroute_data),       
    path('api/traceroute/run/<str:ip>/',  views.run_traceroute_now),        
]
