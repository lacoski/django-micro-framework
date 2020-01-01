from django.conf.urls import url

from micro_framework.jwt_auth import views as jwt_views

from . import views

urlpatterns = [
    url(r'^token/pair/$', jwt_views.token_obtain_pair, name='token_obtain_pair'),
    url(r'^token/refresh/$', jwt_views.token_refresh, name='token_refresh'),

    url(r'^token/verify/$', jwt_views.token_verify, name='token_verify'),

    url(r'^test-view/$', views.test_view, name='test_view'),
]
