from django.db import models
from rh.models import Cluster, Location

NAME_MAX_LENGTH = 200


class WarehouseLocation(models.Model):
    province = models.ForeignKey(
        Location,
        related_name="province",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    district = models.ForeignKey(
        Location,
        related_name="district",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Warehouse Location Plan"
        verbose_name_plural = "Warehouse Locations"


class StockItemsType(models.Model):
    cluster = models.ForeignKey(Cluster, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Stock Type"
        verbose_name_plural = "Stock Types"


class StockUnit(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Stock Unit"
        verbose_name_plural = "Stock Units"


class StockLocationDetails(models.Model):
    PURPOSE_TYPES = [
        ("Prepositioned", "Prepositioned"),
        ("Operational", "Operational"),
    ]
    TARGET_GROUP_TYPES = [
        ("All Population", "All Population"),
        ("Conflict Affected", "Conflict Affected"),
        ("Natural Disaster", "natural-disaster"),
        ("Returnees", "Returnees"),
    ]
    STATUS_TYPES = [
        ("Available", "Available"),
        ("Reserved", "Reserved"),
    ]
    warehouse_location = models.ForeignKey(WarehouseLocation, on_delete=models.CASCADE, null=True, blank=True)
    cluster = models.ForeignKey(Cluster, on_delete=models.SET_NULL, null=True, blank=True)
    stock_purpose = models.CharField(max_length=255, choices=PURPOSE_TYPES, default="", null=True, blank=True)
    targeted_groups = models.CharField(max_length=255, choices=TARGET_GROUP_TYPES, default="", null=True, blank=True)
    stock_type = models.ForeignKey(StockItemsType, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=255, choices=STATUS_TYPES, default="", null=True, blank=True)
    stock_unit = models.ForeignKey(
        StockUnit,
        verbose_name="Units",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    qty_in_stock = models.IntegerField(default=0, verbose_name="Qty in Stock", null=True, blank=True)
    qty_in_pipeline = models.IntegerField(default=0, verbose_name="Qty in Pipeline", null=True, blank=True)
    beneficiary_coverage = models.IntegerField(default=0, blank=True, null=True)
    unit_required = models.IntegerField(default=0, verbose_name="No Unit Required", null=True, blank=True)
    people_to_assisted = models.IntegerField(default=0, verbose_name="No People to be assisted", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.warehouse_location} Stock Details"

    class Meta:
        verbose_name = "Stock Item"
        verbose_name_plural = "Stock Item"


class StockReports(models.Model):
    stock_location_details = models.ManyToManyField(StockLocationDetails)
    STOCK_State = (
        ("todo", "To Do"),
        ("submitted", "Submitted"),
    )
    state = models.CharField(max_length=10, choices=STOCK_State, default="todo")
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    submitted_at = models.DateTimeField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.created_at.strftime("%B, %Y")

    class Meta:
        verbose_name = "Stock Report"
        verbose_name_plural = "Stock Reports"
