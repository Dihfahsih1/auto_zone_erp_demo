import json
from django import forms
from django.contrib import admin
from .models import Department,Region,SalesPerson, Employee, Customer, SparePart, Estimate, EstimateItem, Verification, Dispatch, DeliveryNote, StoresReconciliation, UserRole

from django.utils.html import format_html
from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
from django.templatetags.static import static
from .utils.delivery_ocr import extract_delivery_data

# Model Admin Classes
@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description','districts')
    search_fields = ('name',)

@admin.register(SalesPerson)
class SalesPersonAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'department', 'phone')
    list_filter = ('department', 'is_staff')
    search_fields = ('username', 'email', 'phone')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Department', {'fields': ('department',)}),
    )

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('owner_name','district')
    search_fields = ('owner_name','district')
    list_per_page = 20


@admin.register(SparePart)
class SparePartAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'current_stock', 'unit_price')
    list_filter = ('current_stock',)
    search_fields = ('name', 'sku')
    ordering = ('name',)

class EstimateItemInline(admin.TabularInline):
    model = EstimateItem
    extra = 1
    fields = ('part', 'quantity', 'negotiated_price', 'line_total')
    readonly_fields = ('line_total',)
    
    def line_total(self, instance):
        return instance.line_total()
    line_total.short_description = 'Total'

@admin.register(Estimate)
class EstimateAdmin(admin.ModelAdmin):
    list_display = ('bk_estimate_id', 'customer', 'sales_agent', 'status', 'created_at', 'total_value')
    list_filter = ('status', 'created_at')
    search_fields = ('bk_estimate_id', 'customer__name')
    inlines = [EstimateItemInline]
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')

    actions = ['mark_as_verified']

    def mark_as_verified(self, request, queryset):
        queryset.update(status='verified')
    mark_as_verified.short_description = "Mark selected as verified"
    
    def total_value(self, obj):
        return sum(item.line_total() for item in obj.items.all())
    total_value.short_description = 'Total Value'

# @admin.register(Verification)
# class VerificationAdmin(admin.ModelAdmin):
#     list_display = ('estimate', 'verified_by', 'verification_date', 'is_approved')
#     list_filter = ('verification_date', 'is_approved')
#     raw_id_fields = ('estimate',)

@admin.register(Dispatch)
class DispatchAdmin(admin.ModelAdmin):
    list_display = ('estimate', 'vehicle_number', 'driver_name', 'dispatch_time')
    search_fields = ('vehicle_number', 'driver_name')

@admin.register(DeliveryNote)
class DeliveryNoteAdmin(admin.ModelAdmin):
    list_display = ('estimate_no', 'customer_name', 'customer_contact', 'salesperson')
    
    search_fields = ('estimate_no', 'customer_name', 'salesperson') 

   
@admin.register(StoresReconciliation)
class StoresReconciliationAdmin(admin.ModelAdmin):
    list_display = ('estimate', 'reconciled_by', 'reconciliation_date')
    readonly_fields = ('reconciliation_date',)


