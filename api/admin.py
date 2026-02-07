
from django.apps import apps
from django.contrib import admin

def register_all_models():
    for model in apps.get_models():
        # Check if the model is not already registered
        if not admin.site.is_registered(model):
            admin.site.register(model)

# Call the function to register all models
register_all_models()