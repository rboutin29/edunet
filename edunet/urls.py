"""edunet_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from . import views

app_name = 'edunet'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('help/', views.HelpView.as_view(), name='help'),
    path('help/technical-report', views.pdf_view, name='tech_report'),
    path('contributors', views.ContributorView.as_view(), name='contributors'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('search/', views.SearchResultsView.as_view(), name='search_results'),
    path('departments/', views.DepartmentListView.as_view(), name='departments'),
    path('<slug:department_slug>/', views.course_list, name='course_list'),
    path('<slug:department_slug>/<slug:course_slug>/', views.course_detail, name='course_detail'),
    path('<slug:department_slug>/<slug:course_slug>/tree-form/', views.tk_form, name='tk_form'),
    path('<slug:department_slug>/<slug:course_slug>/<int:transcript_num>-tree/', views.tk_view, name='tk_view'), # pylint: disable=line-too-long
    path('<slug:department_slug>/<slug:course_slug>/<int:transcript_num>-puzzle/', views.pz_view, name='pz_view'), # pylint: disable=line-too-long
]
