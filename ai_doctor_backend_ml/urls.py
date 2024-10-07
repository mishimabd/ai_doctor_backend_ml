from django.urls import path
from ai_doctor_backend_ml.views import predict_image_ecg, predict_image_mri, predict_image_xray

urlpatterns = [
    path('predict/ecg', predict_image_ecg),
    path('predict/mri', predict_image_mri),
    path('predict/xray', predict_image_xray),
]
