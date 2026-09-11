from collections import defaultdict
from decimal import Decimal

from reconciliation.models import Location, SystemARecord, SystemBEntry
from .importer import normalize_record_ref


REASONS = {
    "missing_in_b": "Missing in B",
    "orphan_in_b": "Orphan in B",
    "duplicate_in_b": "Duplicate in B",
    "value_mismatch": "Value mismatch",
}


def values_differ(a_value, b_value):
    if a_value is None or b_value is None:
        return a_value != b_value
    return Decimal(a_value) != Decimal(b_value)


def build_disagreements(org_id):
    # Tenant boundary is enforced before comparison output is created.
    location_ids = set(
        Location.objects.filter(org_id=org_id).values_list("location_id", flat=True)
    )

    a_records = list(
        SystemARecord.objects.filter(location_id_raw__in=location_ids)
    )
    b_entries = list(
        SystemBEntry.objects.filter(location_id_raw__in=location_ids)
    )

    a_by_ref = {}
    for record in a_records:
        a_by_ref[normalize_record_ref(record.record_id)] = record

    b_by_ref = defaultdict(list)
    for entry in b_entries:
        b_by_ref[entry.normalized_ref].append(entry)

    result = []

    # A exists, B does not.
    for record in a_records:
        ref = normalize_record_ref(record.record_id)
        if ref not in b_by_ref:
            result.append({
                "record_ref": record.record_id,
                "reason": "missing_in_b",
                "reason_label": REASONS["missing_in_b"],
                "system_a_value": record.total_value,
                "system_b_value": None,
                "system_a_raw_value": record.total_value_raw,
                "system_b_raw_value": None,
                "location_id": record.location_id_raw,
                "org_id": org_id,
                "system_b_entry_id": None,
            })

    # B points to no A record.
    for entry in b_entries:
        if entry.normalized_ref not in a_by_ref:
            result.append({
                "record_ref": entry.record_ref_raw,
                "reason": "orphan_in_b",
                "reason_label": REASONS["orphan_in_b"],
                "system_a_value": None,
                "system_b_value": entry.value,
                "system_a_raw_value": None,
                "system_b_raw_value": entry.value_raw,
                "location_id": entry.location_id_raw,
                "org_id": org_id,
                "system_b_entry_id": entry.entry_id,
            })

    # A reference occurs more than once in B.
    # Return every duplicate B row so the UI shows every problematic entry.
    for ref, entries in b_by_ref.items():
        if ref in a_by_ref and len(entries) > 1:
            record = a_by_ref[ref]
            for entry in entries:
                result.append({
                    "record_ref": record.record_id,
                    "reason": "duplicate_in_b",
                    "reason_label": REASONS["duplicate_in_b"],
                    "system_a_value": record.total_value,
                    "system_b_value": entry.value,
                    "system_a_raw_value": record.total_value_raw,
                    "system_b_raw_value": entry.value_raw,
                    "location_id": record.location_id_raw,
                    "org_id": org_id,
                    "system_b_entry_id": entry.entry_id,
                })

    # Compare values only when there is exactly one B entry.
    # Duplicates have their own, higher-priority disagreement reason.
    for ref, entries in b_by_ref.items():
        if ref not in a_by_ref or len(entries) != 1:
            continue

        record = a_by_ref[ref]
        entry = entries[0]

        if values_differ(record.total_value, entry.value):
            result.append({
                "record_ref": record.record_id,
                "reason": "value_mismatch",
                "reason_label": REASONS["value_mismatch"],
                "system_a_value": record.total_value,
                "system_b_value": entry.value,
                "system_a_raw_value": record.total_value_raw,
                "system_b_raw_value": entry.value_raw,
                "location_id": record.location_id_raw,
                "org_id": org_id,
                "system_b_entry_id": entry.entry_id,
            })

    return result
