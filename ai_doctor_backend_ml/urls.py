from django.urls import path
from ai_doctor_backend_ml.views import predict_image

urlpatterns = [
    path('predict/', predict_image, name='predict_image'),
]
