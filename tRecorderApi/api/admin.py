# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Language, Book, Take, \
    Comment, Project, Chapter, Chunk, \
    Anthology, Version, Mode

# Register your models here.
admin.site.register(Project)
admin.site.register(Chapter)
admin.site.register(Chunk)
admin.site.register(Language)
admin.site.register(Book)
admin.site.register(Take)
admin.site.register(Comment)
admin.site.register(Anthology)
admin.site.register(Version)
admin.site.register(Mode)
