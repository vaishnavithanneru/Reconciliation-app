from decimal import Decimal, InvalidOperation

from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Location
from .services.comparator import REASONS, build_disagreements


class OrganizationsView(APIView):
    def get(self, request):
        orgs = list(
            Location.objects.values_list("org_id", flat=True).distinct().order_by("org_id")
        )
        return Response({"organizations": orgs})


class DisagreementsView(APIView):
    def get(self, request):
        org_id = (request.query_params.get("org_id") or "").strip()
        reason = (request.query_params.get("reason") or "all").strip()
        sort = (request.query_params.get("sort") or "value_desc").strip()

        if not org_id:
            return Response(
                {"detail": "org_id is required. Tenant context cannot be omitted."},
                status=400,
            )

        valid_orgs = set(
            Location.objects.values_list("org_id", flat=True).distinct()
        )
        if org_id not in valid_orgs:
            return Response({"detail": "Unknown organization."}, status=404)

        rows = build_disagreements(org_id)

        if reason != "all":
            if reason not in REASONS:
                return Response({"detail": "Invalid reason filter."}, status=400)
            rows = [row for row in rows if row["reason"] == reason]

        if sort == "value_asc":
            rows.sort(key=lambda x: self.sort_value(x), reverse=False)
        elif sort == "value_desc":
            rows.sort(key=lambda x: self.sort_value(x), reverse=True)
        elif sort == "record":
            rows.sort(key=lambda x: x["record_ref"].lower())
        else:
            return Response({"detail": "Invalid sort option."}, status=400)

        return Response({
            "org_id": org_id,
            "count": len(rows),
            "results": rows,
        })

    @staticmethod
    def sort_value(row):
        values = [row.get("system_a_value"), row.get("system_b_value")]
        parsed = [v for v in values if v is not None]
        if not parsed:
            return Decimal("-999999999999999999")
        return max(parsed)
