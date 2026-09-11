from django.db import models


class Location(models.Model):
    location_id = models.CharField(max_length=50, unique=True)
    org_id = models.CharField(max_length=50, db_index=True)
    location_name = models.CharField(max_length=255)

    class Meta:
        ordering = ["location_id"]

    def __str__(self):
        return f"{self.location_id} ({self.org_id})"


class SystemARecord(models.Model):
    row_number = models.PositiveIntegerField()
    record_id = models.CharField(max_length=100, db_index=True)
    location_id_raw = models.CharField(max_length=100, blank=True)
    event_date_raw = models.CharField(max_length=100, blank=True)
    category_code = models.CharField(max_length=100, blank=True)
    actor_id = models.CharField(max_length=100, blank=True)
    base_value_raw = models.CharField(max_length=100, blank=True)
    adjustment_raw = models.CharField(max_length=100, blank=True)
    total_value_raw = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)

    base_value = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    adjustment = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    total_value = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)

    import_error = models.TextField(blank=True)

    class Meta:
        ordering = ["row_number"]

    def __str__(self):
        return self.record_id


class SystemBEntry(models.Model):
    row_number = models.PositiveIntegerField()
    entry_id = models.CharField(max_length=100)
    record_ref_raw = models.CharField(max_length=100, blank=True)
    normalized_ref = models.CharField(max_length=100, db_index=True)
    location_id_raw = models.CharField(max_length=100, blank=True)
    recorded_on_raw = models.CharField(max_length=100, blank=True)
    value_raw = models.CharField(max_length=100, blank=True)
    label = models.CharField(max_length=255, blank=True)

    value = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)

    import_error = models.TextField(blank=True)

    class Meta:
        ordering = ["row_number"]

    def __str__(self):
        return self.entry_id
