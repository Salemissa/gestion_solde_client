import calendar
from rest_framework import serializers
from HN_Transporte_api.models import *
from django.db import transaction


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
      
        model = Client
        fields = '__all__'



class ChauffeurSerializer(serializers.ModelSerializer):

    class Meta:
      
        model = Chauffeur
        fields = '__all__'

class CamionSerializer(serializers.ModelSerializer):

    class Meta:
      
        model = Camion
        fields = '__all__'

class FactureSerializer(serializers.ModelSerializer):

    class Meta:
      
        model = Facture
        fields = '__all__'

class FactureGetSerializer(serializers.ModelSerializer):
    camion=CamionSerializer() 
    chauffeur=ChauffeurSerializer() 
    client=ClientSerializer() 
    class Meta:
        model = Facture
        fields = '__all__'

# class CompteSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Compte
#         fields = '__all__'

class OperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = '__all__'

    def create(self, validated_data):
        operation_type = validated_data['operation_type']
        amount = validated_data['amount']
        client = validated_data['client']

        # Debugging: Print client balance before updating
        print(f"Client {client.id} initial balance: {client.balance}")

        # Using a transaction to ensure atomicity
        with transaction.atomic():
            
            # Adjust balance based on operation type
            if operation_type in ['Débit',]:  # Subtract for specified operation types
                client.balance -= amount
                print(f"Balance after subtraction: {client.balance}")
            else:  # Add for other types (e.g., Deposit)
                client.balance += amount
                print(f"Balance after addition: {client.balance}")

            # Save the client's updated balance
            client.save()
            # print(f"Client {client.id} saved with new balance: {client.balance}")

            # Create and return the new operation
            operation = Operation.objects.create(**validated_data)

        # Return the operation instance along with client id
        return operation
