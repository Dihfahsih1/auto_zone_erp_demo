from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from auditlog.models import AuditlogHistoryField
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

# ----------------------------
# 1. Core Entities
# ----------------------------
class Department(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Department Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))

    class Meta:
        ordering = ['name']
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")

    def __str__(self):
        return self.name


class Employee(AbstractUser):
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        verbose_name=_("Department"),
        related_name='employees'
    )
    phone = models.CharField(
        max_length=20,
        verbose_name=_("Phone Number"),
        blank=True
    )
    
    # Add these to resolve the clash
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to.'),
        related_name='employee_set',  # Changed from default
        related_query_name='employee'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='employee_set',  # Changed from default
        related_query_name='employee'
    )

    class Meta:
        verbose_name = _("Employee")
        verbose_name_plural = _("Employees")

class Customer(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Customer Name"))
    contact = models.CharField(max_length=100, verbose_name=_("Contact Information"))
    email = models.EmailField(blank=True, verbose_name=_("Email Address"))
    address = models.TextField(blank=True, verbose_name=_("Physical Address"))

    class Meta:
        ordering = ['name']
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")

    def __str__(self):
        return f"{self.name} - {self.contact}"


class SparePart(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Part Name"))
    sku = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("SKU"),
        help_text=_("Matching BK system SKU")
    )
    current_stock = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Current Stock"),
        validators=[MinValueValidator(0)]
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Unit Price"),
        validators=[MinValueValidator(0)]
    )

    class Meta:
        ordering = ['name']
        verbose_name = _("Spare Part")
        verbose_name_plural = _("Spare Parts")

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def get_absolute_url(self):
        return reverse('sparepart-detail', kwargs={'pk': self.pk})


# ----------------------------
# 2. Estimate Lifecycle
# ----------------------------
class Estimate(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', _('Draft (Sales)')
        SUBMITTED = 'submitted', _('Submitted to CRM')
        VERIFIED = 'verified', _('Verified')
        DISPATCHED = 'dispatched', _('Dispatched')
        DELIVERED = 'delivered', _('Delivered (Signed)')
    
    bk_estimate_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("BK Estimate ID"),
        help_text=_("Reference ID from Bookkeeping System")
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        verbose_name=_("Customer"),
        related_name='estimates'
    )
    sales_agent = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        limit_choices_to={'department__name': 'Sales'},
        verbose_name=_("Sales Agent"),
        related_name='sales_estimates'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name=_("Status")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Last Updated"))
    history = AuditlogHistoryField()

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Estimate")
        verbose_name_plural = _("Estimates")
        permissions = [
            ("change_estimate_status", "Can modify estimate status"),
            ("view_all_estimates", "Can view all estimates"),
        ]

    def __str__(self):
        return f"Estimate #{self.bk_estimate_id} - {self.customer.name} ({self.get_status_display()})"

    def get_absolute_url(self):
        return reverse('estimate-detail', kwargs={'pk': self.pk})

    def total_value(self):
        return sum(item.line_total() for item in self.items.all())

    def mark_as_verified(self, verified_by):
        self.status = self.Status.VERIFIED
        self.save()
        Verification.objects.create(
            estimate=self,
            verified_by=verified_by
        )
        return True


class EstimateItem(models.Model):
    estimate = models.ForeignKey(
        Estimate,
        on_delete=models.CASCADE,
        verbose_name=_("Estimate"),
        related_name='items'
    )
    part = models.ForeignKey(
        SparePart,
        on_delete=models.PROTECT,
        verbose_name=_("Spare Part")
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Quantity"),
        validators=[MinValueValidator(1)]
    )
    negotiated_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Negotiated Price"),
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = _("Estimate Item")
        verbose_name_plural = _("Estimate Items")
        unique_together = ['estimate', 'part']

    def __str__(self):
        return f"{self.part.name} x {self.quantity}"

    def line_total(self):
        return self.quantity * self.negotiated_price


# ----------------------------
# 3. Verification & Stores
# ----------------------------
class Verification(models.Model):
    estimate = models.OneToOneField(
        Estimate,
        on_delete=models.CASCADE,
        verbose_name=_("Estimate"),
        related_name='verification'
    )
    verified_by = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        limit_choices_to={'department__name': 'Verification'},
        verbose_name=_("Verified By")
    )
    notes = models.TextField(blank=True, verbose_name=_("Verification Notes"))
    verification_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Verification Date"))

    class Meta:
        verbose_name = _("Verification")
        verbose_name_plural = _("Verifications")
        ordering = ['-verification_date']

    def __str__(self):
        return f"Verification for Estimate #{self.estimate.bk_estimate_id}"


# ----------------------------
# 4. Dispatch Automation
# ----------------------------
class Dispatch(models.Model):
    estimate = models.OneToOneField(
        Estimate,
        on_delete=models.CASCADE,
        verbose_name=_("Estimate"),
        related_name='dispatch'
    )
    bk_proforma_id = models.CharField(
        max_length=20,
        verbose_name=_("BK Proforma ID"),
        help_text=_("Reference ID from Bookkeeping System")
    )
    transport_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Transport Cost"),
        validators=[MinValueValidator(0)]
    )
    vehicle_number = models.CharField(max_length=20, verbose_name=_("Vehicle Number"))
    driver_name = models.CharField(max_length=100, verbose_name=_("Driver Name"))
    driver_contact = models.CharField(max_length=20, verbose_name=_("Driver Contact"))
    dispatch_time = models.DateTimeField(auto_now_add=True, verbose_name=_("Dispatch Time"))
    is_delivered = models.BooleanField(default=False, verbose_name=_("Delivery Status"))

    class Meta:
        verbose_name = _("Dispatch")
        verbose_name_plural = _("Dispatches")
        ordering = ['-dispatch_time']

    def __str__(self):
        return f"Dispatch for Estimate #{self.estimate.bk_estimate_id}"

    def mark_as_delivered(self):
        self.is_delivered = True
        self.save()
        self.estimate.status = Estimate.Status.DELIVERED
        self.estimate.save()
        return True


class DeliveryConfirmation(models.Model):
    estimate = models.OneToOneField(
        Estimate,
        on_delete=models.CASCADE,
        verbose_name=_("Estimate"),
        related_name='delivery_confirmation'
    )
    signed_document = models.FileField(
        upload_to='delivery_proofs/%Y/%m/%d/',
        verbose_name=_("Signed Delivery Note")
    )
    uploaded_by = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        limit_choices_to={'department__name': 'Sales'},
        verbose_name=_("Uploaded By")
    )
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name=_("Upload Time"))

    class Meta:
        verbose_name = _("Delivery Confirmation")
        verbose_name_plural = _("Delivery Confirmations")
        ordering = ['-upload_time']

    def __str__(self):
        return f"Delivery proof for Estimate #{self.estimate.bk_estimate_id}"


# ----------------------------
# 5. Reconciliation
# ----------------------------
class StoresReconciliation(models.Model):
    estimate = models.OneToOneField(
        Estimate,
        on_delete=models.CASCADE,
        verbose_name=_("Estimate"),
        related_name='reconciliation'
    )
    reconciled_by = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        limit_choices_to={'department__name': 'Stores'},
        verbose_name=_("Reconciled By")
    )
    discrepancies = models.TextField(blank=True, verbose_name=_("Discrepancy Notes"))
    reconciliation_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Reconciliation Date"))

    class Meta:
        verbose_name = _("Stores Reconciliation")
        verbose_name_plural = _("Stores Reconciliations")
        ordering = ['-reconciliation_date']

    def __str__(self):
        return f"Reconciliation for Estimate #{self.estimate.bk_estimate_id}"


# ----------------------------
# 6. Notifications
# ----------------------------
class Notification(models.Model):
    estimate = models.ForeignKey(
        Estimate,
        on_delete=models.CASCADE,
        verbose_name=_("Estimate"),
        related_name='notifications'
    )
    message = models.CharField(max_length=200, verbose_name=_("Notification Message"))
    recipient = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        verbose_name=_("Recipient"),
        related_name='notifications'
    )
    is_read = models.BooleanField(default=False, verbose_name=_("Read Status"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")

    def __str__(self):
        return f"Notification for {self.recipient}: {self.message[:50]}"

    def mark_as_read(self):
        self.is_read = True
        self.save()
        return True