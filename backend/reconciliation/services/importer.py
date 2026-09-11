import csv
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

from reconciliation.models import Location, SystemARecord, SystemBEntry


def clean(value):
    if value is None:
        return ""
    return str(value).strip()


def normalize_record_ref(value):
    # Normalizes formatting such as REC-1034, rec1034 and REC - 1034.
    # We deliberately do not invent a REC prefix for a digits-only reference.
    return re.sub(r"[^a-zA-Z0-9]", "", clean(value)).lower()


def parse_decimal(value):
    raw = clean(value)
    if not raw:
        return None
    try:
        # Accept common thousands separators, including 1,25,400.00.
        compact = raw.replace(",", "").replace(" ", "")
        return Decimal(compact)
    except (InvalidOperation, ValueError):
        return None


def import_locations(csv_path):
    count = 0
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            Location.objects.update_or_create(
                location_id=clean(row.get("location_id")),
                defaults={
                    "org_id": clean(row.get("org_id")),
                    "location_name": clean(row.get("location_name")),
                },
            )
            count += 1
    return count


def import_system_a(csv_path):
    count = 0
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        for row_number, row in enumerate(csv.DictReader(f), start=2):
            base_raw = clean(row.get("base_value"))
            adjustment_raw = clean(row.get("adjustment"))
            total_raw = clean(row.get("total_value"))

            errors = []
            if base_raw and parse_decimal(base_raw) is None:
                errors.append(f"invalid base_value={base_raw!r}")
            if adjustment_raw and parse_decimal(adjustment_raw) is None:
                errors.append(f"invalid adjustment={adjustment_raw!r}")
            if total_raw and parse_decimal(total_raw) is None:
                errors.append(f"invalid total_value={total_raw!r}")

            SystemARecord.objects.update_or_create(
                row_number=row_number,
                defaults={
                    "record_id": clean(row.get("record_id")),
                    "location_id_raw": clean(row.get("location_id")),
                    "event_date_raw": clean(row.get("event_date")),
                    "category_code": clean(row.get("category_code")),
                    "actor_id": clean(row.get("actor_id")),
                    "base_value_raw": base_raw,
                    "adjustment_raw": adjustment_raw,
                    "total_value_raw": total_raw,
                    "state": clean(row.get("state")),
                    "base_value": parse_decimal(base_raw),
                    "adjustment": parse_decimal(adjustment_raw),
                    "total_value": parse_decimal(total_raw),
                    "import_error": "; ".join(errors),
                },
            )
            count += 1
    return count


def import_system_b(csv_path):
    count = 0
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        for row_number, row in enumerate(csv.DictReader(f), start=2):
            record_ref = clean(row.get("record_ref"))
            value_raw = clean(row.get("value"))

            errors = []
            if value_raw and parse_decimal(value_raw) is None:
                errors.append(f"invalid value={value_raw!r}")

            SystemBEntry.objects.update_or_create(
                row_number=row_number,
                defaults={
                    "entry_id": clean(row.get("entry_id")),
                    "record_ref_raw": record_ref,
                    "normalized_ref": normalize_record_ref(record_ref),
                    "location_id_raw": clean(row.get("location_id")),
                    "recorded_on_raw": clean(row.get("recorded_on")),
                    "value_raw": value_raw,
                    "label": clean(row.get("label")),
                    "value": parse_decimal(value_raw),
                    "import_error": "; ".join(errors),
                },
            )
            count += 1
    return count


def import_all(data_dir):
    data_dir = Path(data_dir)

    # Clear only imported application data. Raw rows are recreated from CSV,
    # so no dirty row disappears during a re-import.
    SystemBEntry.objects.all().delete()
    SystemARecord.objects.all().delete()
    Location.objects.all().delete()

    locations = import_locations(data_dir / "locations.csv")
    system_a = import_system_a(data_dir / "system_a.csv")
    system_b = import_system_b(data_dir / "system_b.csv")

    return {
        "locations": locations,
        "system_a": system_a,
        "system_b": system_b,
    }
