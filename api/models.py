from django.db import models


from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser , Group, Permission

# Create your models here.
import datetime

phone_regex = RegexValidator(
    regex=r'^\+222[2-4]\d{7}$',
    message="Le numéro de téléphone doit être saisi au format : +222 40999999."
)
GENDERS = (
    ('M', 'M'),
    ('F', 'F'),    
)


CAMION_TYPES = (
    ('Disponible', 'Disponible'),
    ('Occupé', 'Occupé'),    
)



OPERATION_TYPES = [
    ('Dépôt', 'Dépôt'),
    ('Débit', 'Débit'),  # Retrait pour les retraits d'argent
    # ('Transfer', 'Transfert'),  # Transfert d'argent entre comptes
    # ('Payment', 'Paiement'),    # Paiement pour les services
    ('other', 'Autre'),         # Option pour d'autres types d'opérations
]


TYPE_DEPENSES = (
        ('Carburant', 'Carburant'),
        ('Entretien', 'Entretien'),
        ('Réparation', 'Réparation'),
        ('Autre', 'Autre'),
    )



PAYMENT_TYPES = [
               # Retrait pour les retraits d'argent
    ('Paiement Espèce', 'Paiement Espèce'),  # Paiement en espèces
    ('Paiement Digital', 'Paiement Digital'),  # Paiement numérique/digital
    ('other', 'Autre'),             # Option pour d'autres types d'opérations
]





class User(AbstractUser):
    phone = models.CharField('phone',unique=True,validators=[phone_regex], max_length=8, null=True, blank=True)
    watsapp = models.CharField('watsapp',unique=True,validators=[phone_regex], max_length=8, null=True, blank=True)

class Client(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    responsable = models.ForeignKey(User,null=True, blank=True, on_delete=models.CASCADE)


   

    def __str__(self):
        return f"{self.name} "





class Operation(models.Model):
   

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='operations',blank=True, null=True)
    operation_type = models.CharField(max_length=20, choices=OPERATION_TYPES)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES,blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    responsable = models.ForeignKey(User,null=True, blank=True, related_name='UserEmployees', on_delete=models.CASCADE)
    date = models.DateField(verbose_name="Operation Date")  # New field added
    facteur_number = models.CharField(max_length=50, null=True, blank=True)  # New field
    def __str__(self):
        return f"{self.operation_type} of {self.amount} on {self.date}"


