#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import url
from functiontest import views

urlpatterns = [
    url(r'^question/', views.question),
]
