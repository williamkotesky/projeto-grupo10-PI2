from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html"
        ),
        name="login",
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    path("atendimento/", views.atendimento, name="atendimento"),

    path(
        "ordem/nova/<int:moto_id>/",
        views.criar_ordem,
        name="criar_ordem",
    ),
    
    path(
        "ordem/criada/<int:ordem_id>/",
        views.ordem_criada,
        name="ordem_criada",
    ),

    path(
        "moto/nova/<int:cliente_id>/",
        views.criar_moto,
        name="criar_moto",
    ),

    path(
        "fipe/marcas/",
        views.fipe_marcas,
        name="fipe_marcas",
    ),
    
    path(
        "fipe/marcas/<str:brand_id>/modelos/",
        views.fipe_modelos,
        name="fipe_modelos",
    ),
    
    path(
        "fipe/marcas/<str:brand_id>/modelos/<str:model_id>/anos/",
        views.fipe_anos,
        name="fipe_anos",
    ),
    
    path(
        "fipe/marcas/<str:brand_id>/modelos/<str:model_id>/anos/<str:year_id>/",
        views.fipe_preco,
        name="fipe_preco",
    ),

    path(
        "clientes/novo/",
        views.criar_cliente,
        name="criar_cliente",
    ),


]