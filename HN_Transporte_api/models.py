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


class Chauffeur(models.Model):
    
    name = models.CharField(max_length=255)  # Adjust max_length as needed
    telephone = models.CharField(max_length=40,blank=True, null=True)  # Adjust length to match your requirements
    statut = models.BooleanField(default=True,)  # Adjust max_length as needed, e.g., "Available", "Busy"
    responsable = models.ForeignKey(User,null=True, blank=True, on_delete=models.CASCADE)
    def __str__(self):
        return self.name
    

class Camion(models.Model):
    # Exemple de modèle Camion (à personnaliser selon vos besoins)
    immatriculation = models.CharField(max_length=100)
    marque = models.CharField(max_length=100)
    volume = models.FloatField()  # Volume transporté
    disponibilite = models.BooleanField(default=True,)  # Adjust max_length as needed, e.g., "Available", "Busy"
    responsable = models.ForeignKey(User,null=True, blank=True, on_delete=models.CASCADE)
    
    
    def __str__(self):
        return f" {self.immatriculation}"
    
class Facture(models.Model):
    date = models.DateTimeField()  # Date de création de la facture
    contrat = models.CharField(max_length=255)  # Contrat lié à la facture
    camion = models.ForeignKey(Camion, on_delete=models.CASCADE)  # Référence au camion
    chauffeur = models.ForeignKey(Chauffeur, on_delete=models.CASCADE)  # Référence au chauffeur
    volume = models.FloatField()  # Volume transporté
    nbre_voyages = models.IntegerField()  # Nombre de voyages effectués
    tarif = models.DecimalField(max_digits=10, decimal_places=2)  # Tarif pour la facture
    created_at = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE,blank=True, null=True)
    responsable = models.ForeignKey(User,null=True, blank=True, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Facture {self.id} - {self.contrat}"
    


class DepenseCamion(models.Model):
    

    camion = models.ForeignKey('Camion', on_delete=models.CASCADE, related_name="depenses")
    date = models.DateField(auto_now_add=True)  # Date de la dépense
    type_depense = models.CharField(
        max_length=50,
        choices=TYPE_DEPENSES,
        default='Autre'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Montant de la dépense
    description = models.TextField(null=True, blank=True)  # Description facultative
    responsable = models.ForeignKey(User,null=True, blank=True, on_delete=models.CASCADE)
    




