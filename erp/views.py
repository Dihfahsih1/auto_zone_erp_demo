from django.shortcuts import render
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from django.utils.translation import gettext as _
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from erp.forms import DispatchForm,DeliveryNoteForm
from .models import DeliveryNote, Dispatch, Estimate
import json
from django.db.models import Q

from django.views.decorators.http import require_http_methods

@require_http_methods(["PATCH"])
def mark_delivered(request, dispatch_id):
    try:
        dispatch = Dispatch.objects.get(pk=dispatch_id)
        dispatch.mark_as_delivered()
        return JsonResponse({
            'status': 'success',
            'message': 'Dispatch marked as delivered'
        })
    except Dispatch.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Dispatch not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)
    

def dashboard(request):
    context = {
        'page_title': 'Dashboard',
        'active_page': 'dashboard',
    }
    return render(request, 'index.html', context)


def dispatch_view(request):
    """
    Simplified dispatch view that handles:
    - GET: Show empty form
    - POST: Save form data to database
    - PATCH (AJAX): Mark dispatch as delivered
    """
    
    if request.method == 'GET':
        # Show empty form
        form = DispatchForm()
        return render(request, 'dispatch_form.html', {'form': form})
        
    elif request.method == 'POST':
        # Save form data
        form = DispatchForm(request.POST)
        if form.is_valid():
            dispatch = form.save()
            messages.success(request, _("Dispatch saved successfully!"))
            return redirect('mark_dispatch_delivered')  # Redirect to same page to clear form
        else:
            # Show form with errors
            return render(request, 'dispatch_form.html', {'form': form})
    
    elif request.method == 'PATCH' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # AJAX endpoint for marking as delivered
        try:
            data = json.loads(request.body)
            dispatch_id = data.get('dispatch_id')
            if not dispatch_id:
                return HttpResponseBadRequest(_("Missing dispatch ID"))
            
            dispatch = Dispatch.objects.get(pk=dispatch_id)
            dispatch.mark_as_delivered()
            return JsonResponse({
                'status': 'success',
                'message': _("Marked as delivered"),
                'is_delivered': True
            })
            
        except Dispatch.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': _("Dispatch not found")
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': _(f"Error: {str(e)}")
            }, status=400)
    
    return HttpResponseBadRequest(_("Invalid request"))


def dispatch_list_view(request):
    """
    Display all submitted dispatches in a table format
    """
    dispatches = Dispatch.objects.all().order_by('-dispatch_time')
    
    context = {
        'dispatches': dispatches,
        'table_headers': [
            _("Estimate ID"),
            _("Proforma ID"),
            _("Transport Cost"),
            _("Vehicle"),
            _("Driver"),
            _("Contact"),
            _("Dispatch Time"),
            _("Status"),
            _("Actions")
        ]
    }
    return render(request, 'dispatch_list.html', context)

def upload_delivery_note(request):
    if request.method == 'POST':
        form = DeliveryNoteForm(request.POST, request.FILES)
        if form.is_valid():
            # Auto-set sales agent to current user if not provided
            delivery_note = form.save(commit=False)
            if not delivery_note.sales_agent:
                delivery_note.sales_agent = request.user.get_full_name() or request.user.username
            delivery_note.save()
            
            messages.success(request, 'Delivery note uploaded successfully!')
            return redirect('delivery_note_list')
    else:
        form = DeliveryNoteForm()
    
    return render(request, 'upload_note.html', {'form': form})

def delivery_note_list(request):
    # Get search query if exists
    search_query = request.GET.get('search', '')
    
    # Base queryset - sales agents see only their uploads, admins see all
    if request.user.is_staff:
        notes = DeliveryNote.objects.all()
    else:
        agent_name = request.user.get_full_name() or request.user.username
        notes = DeliveryNote.objects.filter(
            Q(sales_agent__iexact=agent_name) |
            Q(sales_agent__icontains=agent_name)
        )
    
    # Apply search filter if query exists
    if search_query:
        notes = notes.filter(
            Q(estimate_number__icontains=search_query) |
            Q(customer_name__icontains=search_query) |
            Q(destination__icontains=search_query)
        )
    
    # Order by upload date (newest first)
    notes = notes.order_by('-upload_date')
    
    context = {
        'delivery_notes': notes,
        'search_query': search_query,
        'is_admin': request.user.is_staff,
    }
    return render(request, 'delivery_note_list.html', context)