from api import views
from django.conf.urls import url
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'languages', views.LanguageViewSet)
router.register(r'books', views.BookViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'takes', views.TakeViewSet)
router.register(r'comments', views.CommentViewSet)

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^upload/(?P<filename>[^/]+)$', views.FileUploadView.as_view()),
    url(r'^stream/(?P<filepath>.*)$', views.FileStreamView.as_view()),
    url(r'^get_project/$', views.ProjectView.as_view()),
    url(r'^get_source/$', views.SourceFileView.as_view()),
    url(r'^zipFiles/$', views.ProjectZipFilesView.as_view()),
    url(r'^exclude_files/$', views.ExcludeFilesView.as_view()),
    url(r'^all_project/$', views.AllProjectsView.as_view()),
    url(r'^get_chapters/$', views.ProjectChapterInfoView.as_view()),
    url(r'^get_versions/$', views.getVersionsView.as_view())
]

urlpatterns += router.urls
