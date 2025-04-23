# dispatch/forms.py
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Dispatch,DeliveryNote, Estimate

from .models import Customer,Employee,Department,UserRole
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
 

class EmployeeRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)
    department = forms.ModelChoiceField(queryset=Department.objects.all())
    role = forms.ModelChoiceField(queryset=UserRole.objects.all(), required=False)

    class Meta:
        model = Employee
        fields = ('username', 'email', 'password1', 'password2', 
                 'first_name', 'last_name', 'phone', 'department', 'role')

class EmployeeLoginForm(AuthenticationForm):
    class Meta:
        model = Employee
        fields = ('username', 'password')

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'
        widgets = {
            'location': forms.TextInput(attrs={'id': 'location-input', 'placeholder': 'Auto-detect or type location'}),
            'prepared_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

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

class EstimateForm(forms.ModelForm):
    class Meta:
        model = Estimate
        fields = ['bk_estimate_id', 'customer', 'sales_agent', 'status']
        widgets = {
            'bk_estimate_id': forms.TextInput(attrs={'readonly': True}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'customer': forms.TextInput(attrs={'class': 'form-control'}),
            'sales_agent': forms.TextInput(attrs={'readonly': True, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bk_estimate_id'].required = False
        self.fields['sales_agent'].required = False

class EstimateUploadForm(forms.Form):
    excel_file = forms.FileField(
        label='Excel File',
        help_text='Upload an Excel file with estimates. Required columns: bk_estimate_id, customer',
        widget=forms.FileInput(attrs={
            'accept': '.xlsx, .xls',
            'class': 'form-control'
        })
    )
    
    def clean_excel_file(self):
        file = self.cleaned_data['excel_file']
        if not file.name.endswith(('.xlsx', '.xls')):
            raise forms.ValidationError("Only Excel files are allowed")
        return file
    
class DispatchVerificationForm(forms.ModelForm):
    class Meta:
        model = Dispatch
        fields = ['vehicle_number', 'driver_name', 'driver_contact', 'cancellation_reason']
        widgets = {
            'vehicle_number': forms.TextInput(attrs={'class': 'form-control'}),
            'driver_name': forms.TextInput(attrs={'class': 'form-control'}),
            'driver_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'cancellation_reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter reason for cancellation if applicable'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cancellation_reason'].required = False