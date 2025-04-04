# dispatch/forms.py
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Dispatch,DeliveryNote

class DispatchForm(forms.ModelForm):
    class Meta:
        model = Dispatch
        fields = [
            'estimate',
            'bk_proforma_id',
            'transport_cost',
            'vehicle_number',
            'driver_name',
            'driver_contact'
        ]
        widgets = {
            'transport_cost': forms.NumberInput(attrs={'step': '0.01'}),
        }
        labels = {
            'bk_proforma_id': _('BK Proforma ID'),
            'transport_cost': _('Transport Cost'),
            'vehicle_number': _('Vehicle Number'),
            'driver_name': _('Driver Name'),
            'driver_contact': _('Driver Contact'),
        }


class DeliveryNoteForm(forms.ModelForm):
    class Meta:
        model = DeliveryNote
        fields = [
            'estimate_number',
            'customer_name',
            'destination',
            'customer_remarks',
            'sales_agent',
            'signed_document'
        ]
        widgets = {
            'customer_remarks': forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'signed_document': 'Upload scanned copy or photo of signed delivery note (PDF, JPG, PNG)',
        }