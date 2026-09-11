from decimal import Decimal

from django.test import TestCase

from reconciliation.models import Location, SystemARecord, SystemBEntry
from reconciliation.services.comparator import build_disagreements


class ComparatorTests(TestCase):
    def setUp(self):
        Location.objects.create(
            location_id="LOC-101",
            org_id="ORG-A",
            location_name="Location 101",
        )

    def add_a(self, record_id, value, location_id="LOC-101"):
        return SystemARecord.objects.create(
            row_number=1,
            record_id=record_id,
            location_id_raw=location_id,
            total_value_raw=str(value) if value is not None else "",
            total_value=Decimal(str(value)) if value is not None else None,
        )

    def add_b(self, ref, value, entry_id, location_id="LOC-101"):
        from reconciliation.services.importer import normalize_record_ref
        return SystemBEntry.objects.create(
            row_number=2,
            entry_id=entry_id,
            record_ref_raw=ref,
            normalized_ref=normalize_record_ref(ref),
            location_id_raw=location_id,
            value_raw=str(value) if value is not None else "",
            value=Decimal(str(value)) if value is not None else None,
        )

    def test_missing_in_b(self):
        self.add_a("REC-1001", "100.00")
        rows = build_disagreements("ORG-A")
        self.assertEqual([r["reason"] for r in rows], ["missing_in_b"])

    def test_orphan_in_b(self):
        self.add_b("REC-9999", "100.00", "ENT-1")
        rows = build_disagreements("ORG-A")
        self.assertEqual([r["reason"] for r in rows], ["orphan_in_b"])

    def test_duplicate_in_b(self):
        self.add_a("REC-1001", "100.00")
        self.add_b("REC-1001", "100.00", "ENT-1")
        self.add_b("rec1001", "100.00", "ENT-2")
        rows = build_disagreements("ORG-A")
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(r["reason"] == "duplicate_in_b" for r in rows))

    def test_value_mismatch(self):
        self.add_a("REC-1001", "100.00")
        self.add_b("REC-1001", "120.00", "ENT-1")
        rows = build_disagreements("ORG-A")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["reason"], "value_mismatch")
        self.assertEqual(rows[0]["system_a_value"], Decimal("100.00"))
        self.assertEqual(rows[0]["system_b_value"], Decimal("120.00"))

    def test_tenant_isolation(self):
        Location.objects.create(
            location_id="LOC-201",
            org_id="ORG-B",
            location_name="Location 201",
        )
        self.add_a("REC-A", "100.00", "LOC-101")
        self.add_a("REC-B", "200.00", "LOC-201")

        rows = build_disagreements("ORG-A")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["record_ref"], "REC-A")
