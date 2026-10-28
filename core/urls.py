from django.contrib import admin
from django.urls import path, include
from . import views
from . import api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.overview, name='overview'),
    path('metas/', views.goals, name='goals'),
    path('metas/checklist/<int:item_id>/toggle/', views.toggle_checklist_item, name='toggle_checklist_item'),
    path('metas/checklist/<int:item_id>/excluir/', views.delete_checklist_item, name='delete_checklist_item'),
    path('configuracoes/', views.settings_view, name='settings'),
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
