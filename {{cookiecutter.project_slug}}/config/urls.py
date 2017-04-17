from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.utils.translation import ugettext as _
from rest_framework_swagger.views import get_swagger_view

# customizing admin class
admin.site.site_header = _('{{cookiecutter.project_name}} admin panel')

schema_view = get_swagger_view(title='Application API')

urlpatterns = [
    url(r'^admin-panel/', admin.site.urls),
    url(r'^api/swagger/$', schema_view),
    url(r'^api/', include('{{cookiecutter.project_slug}}.users.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    static_urls = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    debug_urls = [url(r'^__debug__/', include(debug_toolbar.urls))]
    urlpatterns += static_urls + debug_urls
