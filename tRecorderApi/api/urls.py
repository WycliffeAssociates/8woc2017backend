from django.conf.urls import url
from rest_framework import routers
import api.views as views

router = routers.DefaultRouter()
router.register(r'api/languages', views.LanguageViewSet)
router.register(r'api/anthologies', views.AnthologyViewSet)
router.register(r'api/versions', views.VersionViewSet)
router.register(r'api/books', views.BookViewSet)
router.register(r'api/modes', views.ModeViewSet)
router.register(r'api/projects', views.ProjectViewSet)
router.register(r'api/chapters', views.ChapterViewSet)
router.register(r'api/chunks', views.ChunkViewSet)
router.register(r'api/takes', views.TakeViewSet)
router.register(r'api/comments', views.CommentViewSet)
router.register(r'api/transfer', views.TransferViewSet)
router.register(r'api/export', views.ExportViewSet)
router.register(r'api/tr', views.TrViewSet)
router.register(r'api/exclude_files', views.ExcludeFilesViewSet)
router.register(r'api/profiles', views.UserViewSet)
router.register(r'api/tasks', views.TaskViewSet, base_name='tasks')

urlpatterns = [
    url(r'^(?!api).*$', views.frontend.FrontendAppView.as_view()),
    url(r'^api/$', views.index, name='index'),
    url(r'^api/cleanup_orphans/$', views.clean_orphans.CleanupOrphansView.as_view()),
    url(r'^api/upload/(?P<filename>[^/]+)$',
        views.file_upload.FileUploadView.as_view()),
    url(r'^api/resumable_upload/(?P<filename>[^/]+)/$',
        views.resumable_upload.ResumableFileUploadView.as_view()),
    url(r'^api/login/$',
        views.user.LoginUserView.as_view()),
    # url(r'^source/(?P<filename>[^/]+)$', views.UploadSourceFileView.as_view()),
    # url(r'^exclude_files/$', views.ExcludeFilesView.as_view()),
]

urlpatterns += router.urls
