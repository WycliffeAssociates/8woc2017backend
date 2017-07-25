# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Language, Book, User, Take, Comment, Project, Chapter, Chunk

# Register your models here.
admin.site.register(Project)
admin.site.register(Chapter)
admin.site.register(Chunk)
admin.site.register(Language)
admin.site.register(Book)
admin.site.register(User)
admin.site.register(Take)
admin.site.register(Comment)