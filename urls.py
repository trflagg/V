from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()
#from Vgame.views import *
#from Vsite.views import *
#from Vedit.views import *

urlpatterns = patterns('',
    # Example:
    # (r'^V/', include('V.foo.urls')),

    # Uncomment this for admin:
    (r'^admin/(.*)', admin.site.root),
    
    ### Accounts views
    url(r'^accounts/login/$', 'V.Vsite.views.accounts_login', name="accounts_login"),
    url(r'^accounts/new/$', 'V.Vsite.views.accounts_new', name="accounts_new"),

    ### Game views
    url(r'^v/$', 'V.Vgame.views.index', name="game_index"),
    url(r'^v/new/$', 'V.Vgame.views.avatar_new', name="avatar_new"),


    ## In-Game views
    url(r'^v/map/$', 'V.Vgame.views.base_game_map', name="base_game_map"),
    url(r'^v/map/map/$', 'V.Vgame.views.game_map', name="game_map"),
    url(r'^v/map/messages/$', 'V.Vgame.views.messages', name="messages"),
    url(r'^v/map/info/(?P<mappableType>.+)/(?P<id>\d+)/$', 'V.Vgame.views.mappable_info', name="mappable_info"),
    url(r'^v/map/character/$', 'V.Vgame.views.self_avatar_info', name="self_avatar_info"),
    url(r'^v/map/equipment/$', 'V.Vgame.views.self_avatar_equipment', name="self_avatar_equipment"),
    #url(r'^v/map/ability/(?P<mappableType>.+)/(?P<id>\d+)/$', 'V.Vgame.views.ability_list', name="ability_list"),
    url(r'^v/map/ability/', 'V.Vgame.views.perform_ability', name="perform_ability"),
     
    #Editor
    url(r'^edit/map/$', 'V.Vedit.views.mapEdit', name="map_edit"),
    url(r'^edit/map/(?P<x>\d{1})/(?P<y>\d{1})/$', 'V.Vedit.views.mapEdit', name="map_edit"),
    
    
)

