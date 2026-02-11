from decimal import Decimal
import arabic_reshaper
from django.shortcuts import get_object_or_404, render

from Gestion_solde.common.custom_viewset import *
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
from rest_framework.decorators import action

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
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime, date
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from bidi.algorithm import get_display
pdfmetrics.registerFont(TTFont('Amiri', 'Amiri-Regular.ttf'))
from reportlab.lib.enums import TA_RIGHT
from reportlab.platypus import Paragraph
# Style pour l'Arabe
arabic_style = ParagraphStyle(
    'Arabic',
    fontName='Amiri',
    fontSize=10,
    alignment=TA_RIGHT,  # Important pour l'alignement droite->gauche
)

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





# ================= ARABIC =================
def reshape_arabic(text):
    if not text:
        return "—"
    reshaped = arabic_reshaper.reshape(str(text))
    bidi_text = get_display(reshaped)
    return bidi_text

# ================= HEADER / FOOTER =================
def add_header_footer(canvas, doc, info):
    canvas.saveState()
    width, height = landscape(A4)

    # ======= SOCIETE =======
    # canvas.setFont("Amiri", 16)
    # canvas.drawString(30, height - 50, "SOCIETE XYZ")

    # canvas.setFont("Amiri", 10)
    # canvas.drawString(30, height - 65, "Adresse: Nouakchott - Mauritanie")
    # canvas.drawString(30, height - 80, "Tel: +222 XX XX XX XX")

    # ======= INFO CLIENT =======
    y = height - 110
    canvas.setFont("Amiri", 12)
    canvas.drawString(30, y, f"Client : {info.get('name', '—')}")
    canvas.drawString(300, y, f"N° Compte : {info.get('account', '000000')}")

    y -= 15
    canvas.setFont("Amiri", 10)
    phone = info.get('phone_number') or "—"
    canvas.drawString(30, y, f"Tel Client  : {phone}")

    y -= 15
    canvas.drawString(30, y, f"Adresse : {info.get('address', '—')}")
    canvas.drawString(300, y, f"Période : {info.get('start', '—')} au {info.get('end', '—')}")

    y -= 15
    canvas.drawString(30, y, f"Solde initial : {info.get('initial', 0.00):.2f} MRU")
    canvas.drawString(300, y, f"Solde actuel : {info.get('current', 0.00):.2f} MRU")

    canvas.line(30, y-10, width-30, y-10)

    # ======= FOOTER =======
    canvas.setFont("Amiri", 9)
    canvas.drawString(30, 30, f"Généré le {datetime.now().strftime('%d-%m-%Y %H:%M')}")
    canvas.drawRightString(width-30, 30, f"Page {canvas.getPageNumber()}")

    canvas.restoreState()



# ================= API =================
class GenerateProfessionalStatement(APIView):

    def post(self, request):
        try:
            start_date = datetime.strptime(request.data.get("start_date"), "%Y-%m-%d")
            end_date = datetime.strptime(request.data.get("end_date"), "%Y-%m-%d")
            client = Client.objects.get(id=request.data.get("client_id"))
        except:
            return Response({"error": "Données invalides"}, status=400)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="releve_{client.name}.pdf"'

        doc = SimpleDocTemplate(
            response,
            pagesize=landscape(A4),
            topMargin=165,
            bottomMargin=50
        )

        elements = []

        # ====== OPERATIONS ======
        operations = Operation.objects.filter(
            client=client,
            date__range=(start_date, end_date)
        ).order_by('date')

        # Calcul solde initial
        total_before = Operation.objects.filter(
            client=client,
            date__lt=start_date
        ).aggregate(total=models.Sum('amount'))['total'] or 0

        initial_balance = total_before
        current_balance = initial_balance

        # ====== TABLE ======
        data = [["Date", "Description", "Débit", "Crédit", "Solde"]]

        total_debit = 0
        total_credit = 0

        for op in operations:
            desc = reshape_arabic(op.description)

            if op.operation_type == 'Dépôt':
                debit = 0
                credit = op.amount
                current_balance += op.amount
                total_credit += op.amount
            else:
                debit = op.amount
                credit = 0
                current_balance -= op.amount
                total_debit += op.amount

            data.append([
                op.date.strftime("%d-%m-%Y"),
                Paragraph(desc, arabic_style),
                f"{debit:.2f}" if debit else "",
                f"{credit:.2f}" if credit else "",
                f"{current_balance:.2f}"
            ])

        # Ligne des totaux
        data.append([
            "Totaux",
            "",
            f"{total_debit:.2f}",
            f"{total_credit:.2f}",
            f"{current_balance:.2f}"
        ])

        table = Table(
            data,
            colWidths=[1.2*inch, 3*inch, 1.2*inch, 1.2*inch, 1.5*inch],
            repeatRows=1
        )

        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1F4E79")),  # header
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Amiri'),
            ('ALIGN', (2,1), (-1,-1), 'RIGHT'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0,1), (-2,-2), [colors.whitesmoke, colors.transparent]),  # lignes normales
            ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#D9E1F2")),  # ligne totaux
            ('FONTNAME', (0,-1), (-1,-1), 'Amiri'),
            ('ALIGN', (2,-1), (-1,-1), 'RIGHT'),
        ]))

        elements.append(table)

        # ====== HEADER INFO ======
        info = {
            "name": client.name,
            "account": getattr(client, "code", "000000"),
            "phone_number": getattr(client, "phone_number", ""),
            "address": getattr(client, "address", ""),
            "start": start_date.strftime("%d-%m-%Y"),
            "end": end_date.strftime("%d-%m-%Y"),
            "initial": initial_balance,
            "current": getattr(client, "balance", ""),
        }

        doc.build(
            elements,
            onFirstPage=partial(add_header_footer, info=info),
            onLaterPages=partial(add_header_footer, info=info)
        )

        return response




