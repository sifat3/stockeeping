from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add_product/', views.add_product, name='add_product'),
    path('view_inventory/', views.view_inventory, name='view_inventory'),
    path('purchase/', views.purchase_product, name='purchase_product'),
    path('sell/', views.sell_product, name='sell_product'),
    # path('invoice_pdf/<str:type>/<int:product_id>/<str:quantity>/<str:quantity>/', views.generate_pdf, name='invoice'),

    path('daily_profit/', views.daily_profit, name='daily_profit'),
    path('weekly_profit/', views.weekly_profit, name='weekly_profit'),
    path('monthly_profit/', views.monthly_profit, name='monthly_profit'),

    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),

    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
]
