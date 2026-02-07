from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api import views
from django.urls import path, include
from .views import   ClientByCodeAPIView, ClientOperationsView,  ClientViewSet, GenerateAccountStatement, OperationViewSet
router = DefaultRouter()

# router.register(r'willayas', views.WillayaView)




router = DefaultRouter()
router.register(r'clients', ClientViewSet)

router.register(r'operations', OperationViewSet)


# router.register(r'salaries', SalaireChauffeurViewSet, basename='salaries')

# router.register(r'pointage-summary', PointageSummaryViewSet, basename='pointage-summary')


urlpatterns = [  
    path('', include(router.urls),),
     path('client-operations/<int:client_id>/', ClientOperationsView.as_view(), name='client-operations'),
    
      
     path('client/<str:client_code>/', ClientByCodeAPIView.as_view(), name='client-by-code'),
    
     path('account-statement/', GenerateAccountStatement.as_view(), name='account_statement'),
   
]

# http://127.0.0.1:8000/api/availability/today/?service=1
# http://127.0.0.1:8000/api/availability/future/?medecin=2
# http://127.0.0.1:8000/api/service/medecins/?service=1