from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from reconciliation.services.importer import import_all


class Command(BaseCommand):
    help = "Import locations.csv, system_a.csv and system_b.csv from a data directory."

    def add_arguments(self, parser):
        parser.add_argument(
            "--data-dir",
            default=str(Path(__file__).resolve().parents[4] / "data"),
            help="Directory containing locations.csv, system_a.csv and system_b.csv",
        )

    def handle(self, *args, **options):
        data_dir = Path(options["data_dir"])

        required = ["locations.csv", "system_a.csv", "system_b.csv"]
        missing = [name for name in required if not (data_dir / name).exists()]
        if missing:
            raise CommandError(
                f"Missing CSV files in {data_dir}: {', '.join(missing)}"
            )

        counts = import_all(data_dir)

        self.stdout.write(self.style.SUCCESS("Import completed successfully."))
        for name, count in counts.items():
            self.stdout.write(f"  {name}: {count} rows")
