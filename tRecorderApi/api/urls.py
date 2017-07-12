from django.conf.urls import url, include
from . import views
from rest_framework import routers
from api import views

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
    #url(r'^view_Project/$', views.viewAllProjects.as_view()),
    #url(r'^get_source/$', views.SourceFileView.as_view()),
    url(r'^zipFiles/$', views.ProjectZipFiles.as_view()),
    url(r'^all_project/$', views.viewAllProjects.as_view()),
    url(r'^get_chapters/$', views.projectChapterInfo.as_view())
]

urlpatterns += router.urls
