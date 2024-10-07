import os
import numpy as np
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from keras.models import load_model
from keras.preprocessing import image
from django.core.files.storage import default_storage
from keras.src.applications.vgg19 import preprocess_input

# Load the model once when the server starts
model_ecg = load_model('./model_vgg19.h5')
model_mri = load_model('./mri_ml.h5')
model_xray = load_model('./xray_chest.h5')

IMAGE_SIZE = (224, 224)


@csrf_exempt
def predict_image_ecg(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)

    if 'file' not in request.FILES:
        return JsonResponse({"error": "No file provided"}, status=400)

    file = request.FILES['file']

    # Save the file to a temporary location
    file_path = default_storage.save(file.name, file)

    try:
        # Preprocess the image
        img = image.load_img(file_path, target_size=IMAGE_SIZE)
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0

        # Make predictions
        predictions = model_ecg.predict(img_array)
        predicted_class = np.argmax(predictions)
        confidence = np.max(predictions) * 100

        # Class descriptions
        class_labels = {
            0: "Слияние стимуляционного и нормального ритма (Fusion of paced and normal beat)",
            1: "Слияние желудочкового и нормального ритма (Fusion of ventricular and normal beat)",
            2: "Нормальный ритм (Normal beat)",
            3: "Неопределенный или неизвестный тип (Unclassified beat)",
            4: "Наджелудочковая экстрасистола (Supraventricular premature beat)",
            5: "Преждевременная желудочковая экстрасистола (Ventricular premature contraction)"
        }

        # Get the description of the predicted class
        predicted_class_description = class_labels.get(predicted_class, "Unknown")

        # Clean up the file after processing
        if default_storage.exists(file_path):
            default_storage.delete(file_path)

        # Respond with the predicted class and confidence score
        return JsonResponse({
            "predicted_class": int(predicted_class),
            "predicted_class_description": predicted_class_description,
            "confidence": f"{confidence:.2f}%"
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def predict_image_mri(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)

    if 'file' not in request.FILES:
        return JsonResponse({"error": "No file provided"}, status=400)

    file = request.FILES['file']

    # Save the file to a temporary location
    file_path = default_storage.save(file.name, file)

    try:
        # Preprocess the image
        img = image.load_img(file_path, target_size=(224, 224))  # Adjust target_size to 224x224
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)  # Apply preprocessing used for your model

        # Define class labels
        class_labels = ['glioma', 'meningioma', 'pituitary', 'no tumor']

        # Make predictions
        predictions = model_mri.predict(img_array)
        predictions_percent = predictions[0] * 100  # Convert to percentage

        # Get the predicted class and confidence
        predicted_class = class_labels[np.argmax(predictions)]
        confidence = np.max(predictions_percent)

        # Clean up the file after processing
        if default_storage.exists(file_path):
            default_storage.delete(file_path)

        # Prepare a response with all class probabilities and the predicted class
        class_confidences = {label: round(float(predictions_percent[i]), 2) for i, label in
                             enumerate(class_labels)}  # Ensure float conversion

        # Respond with predicted class, confidence score, and all class probabilities
        return JsonResponse({
            "predicted_class": predicted_class,
            "confidence": round(float(confidence), 2),
            "class_confidences": class_confidences  # Include probabilities for all classes
        })

    except Exception as e:
        # Clean up the file in case of an error
        if default_storage.exists(file_path):
            default_storage.delete(file_path)
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def predict_image_xray(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)

    if 'file' not in request.FILES:
        return JsonResponse({"error": "No file provided"}, status=400)

    file = request.FILES['file']

    # Save the file to a temporary location
    file_path = default_storage.save(file.name, file)

    try:
        # Preprocess the image (resize and apply model-specific preprocessing)
        img = image.load_img(file_path, target_size=(224, 224))  # VGG19 requires 224x224
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)  # Preprocess image for VGG19 model

        # Define class labels for X-ray predictions
        class_labels = ['COVID-19', 'Normal', 'Pneumonia']

        # Make predictions
        predictions = model_xray.predict(img_array)
        predictions_percent = predictions[0] * 100  # Convert to percentage

        # Get the predicted class and confidence score
        predicted_class = class_labels[np.argmax(predictions)]
        confidence = np.max(predictions_percent)

        # Clean up the file after processing
        if default_storage.exists(file_path):
            default_storage.delete(file_path)

        # Prepare a response with all class probabilities and the predicted class
        class_confidences = {label: round(float(predictions_percent[i]), 2) for i, label in enumerate(class_labels)}

        # Respond with predicted class, confidence score, and all class probabilities
        return JsonResponse({
            "predicted_class": predicted_class,
            "confidence": round(float(confidence), 2),
            "class_confidences": class_confidences  # Include probabilities for all classes
        })

    except Exception as e:
        # Clean up the file in case of an error
        if default_storage.exists(file_path):
            default_storage.delete(file_path)
        return JsonResponse({"error": str(e)}, status=500)