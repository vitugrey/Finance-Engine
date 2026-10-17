from django.contrib import admin
from django.urls import path, include
from . import views
from . import api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.overview, name='overview'),
    path('metas/', views.goals, name='goals'),
    path('investimentos/', include('investments.urls')),
    path('carteira/', include('budget.urls')),

    # ============ Endpoints da API REST ============ #
    path('api/', api.api_status, name='api_status'),
    path('api/resumo/', api.api_summary, name='api_summary'),
    path('api/investimentos/', api.api_investments, name='api_investments'),
    path('api/proventos/', api.api_dividends, name='api_dividends'),
    path('api/orcamento/', api.api_budget, name='api_budget'),
    path('api/metas/', api.api_goals, name='api_goals'),
]
