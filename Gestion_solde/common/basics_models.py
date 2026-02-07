from django.db import models
class DocType(models.Model):
    nom = models.CharField(max_length=40, unique=True, null=False)
    # is_Active = models.BooleanField("active", default=True) 
    def __str__(self):
        return  self.nom
class Doc(models.Model):
    nom = models.CharField(max_length=100)
    def __str__(self):
        return  self.nom