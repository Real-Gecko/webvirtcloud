import sass
import os

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings

from appsettings.models import AppSettings
from logs.views import addlogmsg



@login_required
def appsettings(request):
    """
    :param request:
    :return:
    """
    error_messages = []

    
    show_inst_bottom_bar = AppSettings.objects.get(key="VIEW_INSTANCE_DETAIL_BOTTOM_BAR")
    bootstrap_theme = AppSettings.objects.get(key="BOOTSTRAP_THEME") 
    sass_dir = AppSettings.objects.get(key="SASS_DIR") 

    themes_list = os.listdir(sass_dir.value + "/wvc-theme")

    if request.method == 'POST':        
        if 'BOOTSTRAP_THEME' in request.POST:
            theme = request.POST.get("BOOTSTRAP_THEME", "")
            scss_var = f"@import '{sass_dir.value}/wvc-theme/{theme}/variables';"
            scss_bootswatch = f"@import '{sass_dir.value}/wvc-theme/{theme}/bootswatch';"       
            scss_boot = f"@import '{sass_dir.value}/bootstrap-overrides.scss';"

            try:              
                with open(sass_dir.value + "/wvc-main.scss", "w") as main:
                    main.write(scss_var + "\n" + scss_boot + "\n" + scss_bootswatch)
                
                css_compressed = sass.compile(string=scss_var + "\n"+ scss_boot + "\n" + scss_bootswatch, output_style='compressed')
                with open("static/" + "css/wvc-main.min.css", "w") as css:
                    css.write(css_compressed)    

                bootstrap_theme.value = theme
                bootstrap_theme.save()

                msg = _(f"Theme changed. Now: {theme}")
                messages.success(request, msg)
            except Exception as err:
                msg = err
                error_messages.append(msg)
            
            addlogmsg(request.user.username, "", msg)
            return HttpResponseRedirect(request.get_full_path())

        if 'SASS_DIR' in request.POST:
            try:
                sass_dir.value = request.POST.get("SASS_DIR", "")
                sass_dir.save()

                msg = _(f"SASS directory path is changed. Now: {sass_dir.value}")
                messages.success(request, msg)
            except Exception as err:
                msg = err
                error_messages.append(msg)
            
            addlogmsg(request.user.username, "", msg)
            return HttpResponseRedirect(request.get_full_path())

        if 'VIEW_INSTANCE_DETAIL_BOTTOM_BAR' in request.POST:
            try:
                show_inst_bottom_bar.value = request.POST.get("VIEW_INSTANCE_DETAIL_BOTTOM_BAR", "")
                show_inst_bottom_bar.save()

                msg = _(f"Show bottom bar setting is changed. Now: {show_inst_bottom_bar.value}")
                messages.success(request, msg)
            except Exception as err:
                msg = err
                error_messages.append(msg)
            
            addlogmsg(request.user.username, "", msg)
            return HttpResponseRedirect(request.get_full_path())

    return render(request, 'appsettings.html', locals())
