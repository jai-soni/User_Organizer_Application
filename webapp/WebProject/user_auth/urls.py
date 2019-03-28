from django.urls import path, re_path

from . import views
import logging
logger = logging.getLogger('__name__')
try:

    urlpatterns = [
        re_path(r'^$', views.signin, name='signin'),
        re_path(r'^user/register/?$', views.registerPage, name='registerPage'),
        re_path(r'^note/?$', views.createOrGetNotes, name='createOrGetNotes'),
        re_path(r'^note/(?P<note_id>[0-9a-z-]+)$', views.noteFromId, name='noteFromId'),
        re_path(r'^note/(?P<note_id>[0-9a-z-]+)/attachments$', views.addAttachmentToNotes, name='addAttachmentToNotes'),
        re_path(r'^note/(?P<note_id>[0-9a-z-]+)/attachments/(?P<attachment_id>[0-9a-z-]+)$', views.updateOrDeleteAttachments, name='updateOrDeleteAttachments'),
        re_path(r'^reset/?$', views.passwordReset, name='passwordReset'),
        re_path(r'^.*/$', views.get404, name='get404')
            ]
except Exception as e:
    logger.debug("Something happened :\n %s", e)

