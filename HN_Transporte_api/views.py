from django.shortcuts import get_object_or_404, render

from HN_Transporte.common.custom_viewset import *
from .models import *
from .serializers import *
from datetime import datetime
from rest_framework import  filters , generics
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
import requests
from functools import partial


from .serializers import ClientSerializer

from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Spacer
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from django.http import HttpResponse
from rest_framework.views import APIView
from reportlab.pdfgen import canvas
from rest_framework.views import APIView

from django.db.models import Case, When, Value, IntegerField,Sum,Count
from rest_framework.viewsets import ViewSet

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from .models import Facture
from .serializers import FactureSerializer
from datetime import datetime, date


class ClientViewSet(RetrieveUpdateCreateListViewSet):
    queryset =  Client.objects.all()
    # pagination_class = None
    serializer_class =  ClientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name','phone_number','code' ]

    def perform_create(self, serializer):
        serializer.save(responsable = self.request.user)



# class CompteViewSet(RetrieveUpdateCreateListViewSet):
#     queryset = Compte.objects.all()
#     serializer_class = CompteSerializer

class OperationViewSet(RetrieveUpdateCreateListViewSet):
    queryset = Operation.objects.all()
    serializer_class = OperationSerializer



    def perform_create(self, serializer):
        serializer.save(responsable = self.request.user)




class ClientOperationsView(generics.GenericAPIView):
    serializer_class = OperationSerializer

    def get_queryset(self):
        client_id = self.kwargs['client_id']
        type = self.request.query_params.get('type')
        
        
        # Parse dates if provided, otherwise use a default queryset
        try:
           
                return Operation.objects.filter(client_id=client_id,operation_type=type).order_by('-created_at')[:10]
        except ValueError:
            # Return an empty queryset if date parsing fails
            return Operation.objects.none()

    def get(self, request, client_id):
        try:
            operations = self.get_queryset()
            serializer = self.get_serializer(operations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)



class ChauffeurViewSet(RetrieveUpdateCreateListViewSet):
    queryset = Chauffeur.objects.all()
    serializer_class = ChauffeurSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'telephone', 'statut']  # Ajoutez ici les champs sur lesquels vous souhaitez effectuer une recherche

    def perform_create(self, serializer):
        serializer.save(responsable=self.request.user) 

class CamionViewSet(RetrieveUpdateCreateListViewSet):
    queryset = Camion.objects.all().order_by('immatriculation')  # Ajoutez un champ de tri ici
    serializer_class = CamionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['immatriculation', 'volume']  # Ajoutez ici les champs sur lesquels vous souhaitez effectuer une recherche

    def perform_create(self, serializer):
        serializer.save(responsable=self.request.user)
        
        
         # Remplacez ou supprimez cette ligne si `responsable` n'est pas un champ du modèle Chauffeur
class FactureViewSet(RetrieveUpdateCreateListViewSet):
    queryset = Facture.objects.all()
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ['contrat','volume', ]
    # search_fields = ['societe',]
    # serializer_class = DayCategorySerializer

    def perform_create(self, serializer):
        serializer.save(responsable = self.request.user)
    def get_serializer_class(self):
        if self.action in ["list",]:
            return FactureGetSerializer
        return FactureSerializer

class DepenseCamionViewSet(RetrieveUpdateCreateListViewSet):
    queryset = DepenseCamion.objects.all()
    pagination_class = None
    filter_backends = [filters.SearchFilter]
   
    serializer_class = DepenseCamionSerializer

    def perform_create(self, serializer):
        serializer.save(responsable = self.request.user)
   

class ClientByCodeAPIView(APIView):
    def get(self, request, client_code, *args, **kwargs):
        try:
            # Get the client by client_code
            client = Client.objects.get(code=client_code)
        except Client.DoesNotExist:
            return Response({"error": "Client not found"}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the client data
        serializer = ClientSerializer(client)

        # Return the client data in the response
        return Response(serializer.data, status=status.HTTP_200_OK)














def add_table_header(canvas, doc, header):
    """Ajoute l'en-tête du tableau sur chaque page."""
    canvas.saveState()
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(30, doc.bottomMargin + 15, header)
    canvas.restoreState()

def add_header_footer(canvas, doc, info_client):
    """Ajoute un en-tête et un pied de page pour chaque page."""
    canvas.saveState()

    # Dimensions de la page
    width, height = landscape(A4)

    # En-tête
    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawString(30, height - 50, "Société HN TRANSPORTE")
    canvas.drawString(250, height - 50, f"Relevé du Compte  {info_client['client_name']}")
    canvas.setFont("Helvetica", 10)
    canvas.drawString(30, height - 65, f"Client : {info_client['client_name']}")
    canvas.drawString(250, height - 65, f"Période : {info_client['date_start']} à {info_client['date_end']}")
    canvas.drawString(30, height - 85, f"Solde Actuel : {info_client['current_balance']} MRO")

    # Ligne séparatrice (en-tête)
    canvas.line(30, height - 100, width - 30, height - 100)

    # Pied de page
    page_number = f"Page {canvas.getPageNumber()}"
    canvas.setFont("Helvetica", 9)
    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
    canvas.drawString(30, 30, f"Date de génération : {formatted_date}")
    canvas.drawRightString(width - 30, 30, page_number)

    canvas.restoreState()

class GenerateAccountStatement(APIView):
    def post(self, request):
        # Simuler des données pour le test
        start_date = "2024-01-01"
        end_date = "2024-12-31"
        client_id = 1
        client = Client.objects.get(id=client_id)
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="facture_{formatted_date}.pdf"'

        # Configurer le document PDF
        doc = SimpleDocTemplate(
            response,
            pagesize=landscape(A4),
            topMargin=100,
            bottomMargin=50,
        )
        elements = []

        # Simuler les données d'opérations
        grouped_operation_data = self.get_grouped_operations(start_date, end_date,client_id)
        current_balance = client.balance

        # Ajouter les informations récapitulatives
        elements.append(Spacer(1, 20))
        summary_data = [
            ["Date de début:", start_date.strftime('%Y-%m-%d')],
            ["Date de fin:", end_date.strftime('%Y-%m-%d')],
            ["Solde actuel:", f"{current_balance} UM"],
        ]
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 20))

        # Ajouter les données d'opérations avec des tableaux
        for operation_type, operations in grouped_operation_data.items():
            elements.append(Paragraph(f"Type d'Opération : {operation_type}", getSampleStyleSheet()['Heading3']))
            table_data = [["Client", "Operation Type", "Amount", "Date"]]
            totals = {"amount": 0}

            for operation in operations:
                table_data.append([
                    operation["client_name"],
                    operation["operation_type"],
                    f"{operation['amount']:.2f}",
                    operation["created_at"]
                ])
                totals["amount"] += float(operation["amount"])

            table_data.append(["TOTAL", "", f"{totals['amount']:.2f}", ""])
            table = Table(table_data, colWidths=[2 * inch, 2 * inch, 1.5 * inch, 1.2 * inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.black),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 20))

        # Construire le document
        client_info = {
            "client_name": client.name,
            "date_start": start_date.strftime('%Y-%m-%d'),
            "date_end": end_date.strftime('%Y-%m-%d'),
            "current_balance": current_balance
        }
        doc.build(elements, 
                  onFirstPage=partial(add_header_footer, info_client=client_info),
                  onLaterPages=partial(add_header_footer, info_client=client_info))
        return response


    



class GenerateAccountStatement(APIView):
    def post(self, request):
        # Extract and validate the JSON payload
        try:
            start_date = request.data.get("start_date")
            end_date = request.data.get("end_date")
            client_id = request.data.get("client_id")

            # start_date= "2024-01-01"
            # end_date ="2024-12-31"
            # client_id = 1
             # Récupérer le client
            client = Client.objects.get(id=client_id)
            if not start_date or not end_date:
                return Response({"error": "Both start_date and end_date are required."}, status=400)
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)
        

        now = datetime.now()
        
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
        
        # Créer la réponse HTTP avec le type de contenu PDF
        response = HttpResponse(content_type='application/pdf')
        
        # Ajouter l'en-tête de disposition du fichier avec un nom dynamique
        response['Content-Disposition'] = f'attachment; filename="facture_{client.name+formatted_date}.pdf"'

        # response = HttpResponse(content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename="grouped_report.pdf"'

        # Create the PDF document
        doc = SimpleDocTemplate(
            response,
            pagesize=landscape(A4),
            topMargin=100,  # Reserve space for the header
            bottomMargin=50,  # Reserve space for the footer
        )

        elements = []

       
        grouped_operation_data = self.get_grouped_operations(start_date, end_date,client_id)

         # Calculer le solde actuel
        current_balance = client.balance


           
        #     # Ajouter le titre
        # elements.append(Paragraph(f"Relevé du Compte : {client.name}", styles['Title']))
        elements.append(Spacer(1, 20))

        # Ajouter les informations récapitulatives
        summary_data = [
            ["Date de début:", start_date.strftime('%Y-%m-%d') if start_date else "N/A"],
            ["Date de fin:", end_date.strftime('%Y-%m-%d') if end_date else "N/A"],
            ["Solde actuel:", f"{current_balance} UM"],
    ]
        
        # Add operation data to PDF
        for operation_type, operations in grouped_operation_data.items():
           
            elements.append(Spacer(0, 12))
            elements.append(Table([[f"Operation Type: {operation_type}"]], style=[
                  ('BACKGROUND', (0, 0), (-1, 0), colors.black),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
            ]))
            elements.append(Spacer(0, 8))

            table_data = [["Operation", "Amount", "Date",
                           "Paiement","Facteur Number","Description","Date Creation"]]
            totals = {"amount": 0}

            for operation in operations :
                table_data.append([
                    # operation["client_name"],
                    operation["operation_type"],
                    f"{operation['amount']:.2f}",
                    operation["date"],
                    operation["payment_type"],
                    operation["facteur_number"],
                operation["description"],
                
                    operation["created_at"]
                ])
                totals["amount"] += float(operation["amount"])

            # Add totals row
            table_data.append(["TOTAL",  f"{totals['amount']:.2f}", ""])

            table = Table(table_data, colWidths=[2 * inch, 2 * inch, 1.5 * inch, 1.2 * inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.black),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
            ]))
            elements.append(table)
            elements.append(Spacer(0, 24))

        client_info = {
        "client_name": client.name,
        "date_start": start_date.strftime('%Y-%m-%d') if start_date else "N/A",
        "date_end": end_date.strftime('%Y-%m-%d') if end_date else "N/A",
        "current_balance": current_balance
    }

        # Build the document with header and footer
        doc.build(elements, onFirstPage=partial(add_header_footer, info_client=client_info), 
          onLaterPages=partial(add_header_footer, info_client=client_info))

        return response
    


    

       

    def get_grouped_operations(self, start_date, end_date,client_id):
       
        # operation_types = ['FA', 'ACM', 'ADM']
        operations = Operation.objects.filter(
            date__range=(start_date, end_date),
            client_id=client_id  # Assuming you have the client ID available
             
        ).values(
            'operation_type',
            'amount',
            'date',
            'payment_type',
            'facteur_number',
            'description',
            'created_at',
            'client__name'
        ).order_by('operation_type','date')

        grouped_operations = {}
        for operation in operations:
            operation_type = operation["operation_type"]
            if operation_type not in grouped_operations:
                grouped_operations[operation_type] = []
            grouped_operations[operation_type].append({
                "operation_type": operation_type,
                "amount": operation["amount"],
                "date": operation["date"].strftime("%d-%m-%Y"),
                "created_at": operation["created_at"].strftime("%d-%m-%Y"),
                "client_name": operation["client__name"],
                'facteur_number':operation["facteur_number"],
                'description':operation["description"],
                'payment_type':operation["payment_type"],
                
            })

        return grouped_operations
    


class ChauffeurActiveViewSet(viewsets.ViewSet):
    """
    API endpoint that returns all chauffeurs with statut = True.
    """
    def list(self, request):
        # Filtrer les chauffeurs dont le statut est True
        active_chauffeurs = Chauffeur.objects.filter(statut=True)
        serializer = ChauffeurSerializer(active_chauffeurs, many=True)
        return Response(serializer.data)


class CamionActiveViewSet(viewsets.ViewSet):
    """
    API endpoint that returns all chauffeurs with statut = True.
    """
    def list(self, request):
        # Filtrer les chauffeurs dont le statut est True
        active_camions = Camion.objects.filter(disponibilite=True)
        serializer = CamionSerializer(active_camions, many=True)
        return Response(serializer.data)




class FactureMonthViewSet(ViewSet):
    queryset = Facture.objects.all()  # Définir le queryset par défaut
    serializer_class = FactureGetSerializer  # Définir le sérialiseur
    pagination_class = None


    def list(self, request, client_id):
        now = datetime.now()
        current_month = now.month
        current_year = now.year

        factures = Facture.objects.filter(
            client_id=client_id,
            date__year=current_year,
            date__month=current_month,
        )

        serializer = self.serializer_class(factures, many=True)
        return Response({
            "factures": serializer.data,
            "facture_number": f"{current_month}/{current_year}",
            "date": datetime.now().strftime('%d-%m-%Y'),
        }, status=status.HTTP_200_OK)
    
    


class FactureChercheByMonthViewSet(APIView):
    """
    Endpoint pour rechercher les factures d'un client par mois et année.
    """
    serializer_class = FactureGetSerializer

    def post(self, request, client_id):
        """
        Recherche des factures pour un client donné.
        """
        requested_month = request.data.get('month')
        requested_year = request.data.get('year')

        # Validation : mois et année requis
        if not requested_month or not requested_year:
            return Response({"error": "Month et Year sont obligatoires."}, status=status.HTTP_400_BAD_REQUEST)

        # Validation des entrées : vérifier que ce sont des entiers
        try:
            requested_month = int(requested_month)
            requested_year = int(requested_year)
        except ValueError:
            return Response({"error": "Month et Year doivent être des entiers."}, status=status.HTTP_400_BAD_REQUEST)

        # Vérification de la plage des valeurs pour le mois
        if requested_month < 1 or requested_month > 12:
            return Response({"error": "Month doit être entre 1 et 12."}, status=status.HTTP_400_BAD_REQUEST)
        # Obtenir le dernier jour du mois
        _, last_day = calendar.monthrange(requested_year, requested_month)
        last_date_of_month = datetime(requested_year, requested_month, last_day)
        # Filtrage des factures
        factures = Facture.objects.filter(
            client_id=client_id,
            date__year=requested_year,
            date__month=requested_month
        )

        # Sérialisation des factures
        serializer = self.serializer_class(factures, many=True)

        # Retour de la réponse
        return Response({
            "factures": serializer.data,
            "facture_number": f"{requested_month}/{requested_year}",
            "date" :last_date_of_month.strftime('%d-%m-%Y'),
        })

class VoyageSummaryWithFacturesView(APIView):
    def post(self, request):
        # Get data from the request body
        data = request.data
        camion_id = data.get('camion_id')  # ID of the camion
        
        # Validate camion_id
        if not camion_id:
            return Response({"error": "camion_id is required."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Get start_date and end_date from the request body
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        # If dates are not provided, default to the first day of the current month to today
        if not start_date:
            start_date = date.today().replace(day=1)  # First day of the current month
        else:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

        if not end_date:
            end_date = date.today()  # Today's date
        else:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()


        # Filter Factures within the date range for the specified camion
        factures = Facture.objects.filter(
            camion_id=camion_id,
            date__range=[start_date, end_date]
        )


        # Filter Factures within the date range for the specified camion
        depences = DepenseCamion.objects.filter(
            camion_id=camion_id,
            date__range=[start_date, end_date]
        )

         # Aggregate the total voyages, volume, and tarif
        totals_depences = depences.aggregate(
            
            total_depences=Sum('amount')
        )

        # Aggregate the total voyages, volume, and tarif
        totals = factures.aggregate(
            total_voyages=Sum('nbre_voyages'),
            total_volume=Sum('volume'),
            total_tarif=Sum('tarif')
        )
        
        total_voyages = totals['total_voyages'] or 0
        total_volume = totals['total_volume'] or 0
        total_tarif = totals['total_tarif'] or 0
        total_depences = totals_depences['total_depences']  or 0

        # Serialize the factures
        serializer = FactureGetSerializer(factures, many=True)
        depencesserializer = DepenseCamionSerializer(depences, many=True)

        return Response({
            "camion_id": camion_id,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "total_voyages": total_voyages,
            "total_volume": total_volume,
            "total_tarif": total_tarif,
            "total_depences":total_depences,
            "factures": serializer.data,  # Include the detailed factures,
            "depences": depencesserializer.data
        })



    
