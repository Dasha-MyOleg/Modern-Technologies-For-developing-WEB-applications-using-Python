from django.urls import path
from . import views
from .views import manage_users_view, delete_user_view


urlpatterns = [
    path('', views.home, name='home'),
]

urlpatterns = [
    path("", views.index_view, name="index"),
    path("part1/", views.part1_view, name="part1"),
    path("part2/", views.part2_view, name="part2"),
    path("part3/", views.part3_view, name="part3"),
    path("login", views.login_view, name="login"),
    path("register", views.register_view, name="register"),
    path("logout", views.logout_view, name="logout"),
    path('manage_users', views.manage_users_view, name='manage_users'),
    path("delete_user/<int:user_id>", views.delete_user_view, name="delete_user"),
    path("about", views.about_view, name="about"),
    path("support", views.support_view, name="support"),
    path("feedbacks", views.feedbacks_view, name="feedbacks"),
    path("delete-feedback", views.delete_feedback_view, name="delete_feedback"),
    path("create_form", views.create_figure_form, name="create_form"),
    path("create", views.create_figure_view, name="create_figure"),
    path("edit/<int:figure_id>", views.edit_figure_form, name="edit_figure_form"),
    path("update/<int:figure_id>", views.update_figure_view, name="update_figure"),
    path("delete/<int:figure_id>", views.delete_figure_view, name="delete_figure"),
    path("toggle_owned/<int:figure_id>", views.toggle_owned, name="toggle_owned"),

]