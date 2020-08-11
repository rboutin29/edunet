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
    path('admin-help/', views.AdminHelpView.as_view(), name='admin_help'),
    path('student-help/', views.StudentHelpView.as_view(), name='student_help'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('search/', views.SearchResultsView.as_view(), name='search_results'),
    path('departments/', views.DepartmentListView.as_view(), name='departments'),
    path('<slug:department_slug>/', views.course_list, name='course_list'),
    path('<slug:department_slug>/<slug:course_slug>/', views.course_detail, name='course_detail'),
    path('<slug:department_slug>/<slug:course_slug>/course-processor', views.course_processor, name='course_processor'), # pylint: disable=line-too-long
    path('<slug:department_slug>/<slug:course_slug>/form/', views.tk_form, name='tk_form'),
    path('<slug:department_slug>/<slug:course_slug>/<int:transcript_num>/', views.tk_view, name='tk_view'), # pylint: disable=line-too-long,
]
