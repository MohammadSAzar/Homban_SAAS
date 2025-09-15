from django.core.management.base import BaseCommand, CommandError

from dashboard.models import SaleFile, CustomUserModel, SubDistrict


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without making changes to see what would be updated',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting created_by field update...'))

        # Replacement Logic
        sub_district_to_user_mapping = {
            1: 3,
            2: 8,
            3: 10,
            4: 14,
            5: 12,
        }

        # Get all SaleFile objects where created_by is null
        sale_files_to_update = SaleFile.objects.filter(created_by__isnull=True)
        self.stdout.write(
            f"Found {sale_files_to_update.count()} SaleFile objects with empty created_by field"
        )
        if options['dry_run']:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        updated_count = 0
        error_count = 0
        for sale_file in sale_files_to_update:
            if sale_file.sub_district:
                sub_district_id = sale_file.sub_district.id
                if sub_district_id in sub_district_to_user_mapping:
                    user_id = sub_district_to_user_mapping[sub_district_id]
                    try:
                        user = CustomUserModel.objects.get(id=user_id)
                        if not options['dry_run']:
                            sale_file.created_by = user
                            sale_file.save()
                        updated_count += 1
                        self.stdout.write(
                            f"{'[DRY RUN] Would update' if options['dry_run'] else 'Updated'} "
                            f"SaleFile {sale_file.id} (sub_district: {sale_file.sub_district.name}) "
                            f"-> User {user.username}"
                        )
                    except CustomUserModel.DoesNotExist:
                        error_count += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f"User with ID {user_id} not found for SaleFile {sale_file.id}"
                            )
                        )
                else:
                    error_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"No mapping found for sub_district ID {sub_district_id} "
                            f"in SaleFile {sale_file.id}"
                        )
                    )
            else:
                error_count += 1
                self.stdout.write(
                    self.style.WARNING(f"SaleFile {sale_file.id} has no sub_district assigned")
                )

        if options['dry_run']:
            self.stdout.write(
                self.style.SUCCESS(
                    f"DRY RUN COMPLETE: Would update {updated_count} objects, "
                    f"{error_count} errors/warnings"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully updated {updated_count} SaleFile objects, "
                    f"{error_count} errors/warnings"
                )
            )


