from django.core.management.base import BaseCommand, CommandError

from dashboard.models import RentFile, CustomUserModel, SubDistrict


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
        rent_files_to_update = RentFile.objects.filter(created_by__isnull=True)
        self.stdout.write(
            f"Found {rent_files_to_update.count()} RentFile objects with empty created_by field"
        )
        if options['dry_run']:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        updated_count = 0
        error_count = 0
        for rent_file in rent_files_to_update:
            if rent_file.sub_district:
                sub_district_id = rent_file.sub_district.id
                if sub_district_id in sub_district_to_user_mapping:
                    user_id = sub_district_to_user_mapping[sub_district_id]
                    try:
                        user = CustomUserModel.objects.get(id=user_id)
                        if not options['dry_run']:
                            rent_file.created_by = user
                            rent_file.save()
                        updated_count += 1
                        self.stdout.write(
                            f"{'[DRY RUN] Would update' if options['dry_run'] else 'Updated'} "
                            f"RentFile {rent_file.id} (sub_district: {rent_file.sub_district.name}) "
                            f"-> User {user.username}"
                        )
                    except CustomUserModel.DoesNotExist:
                        error_count += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f"User with ID {user_id} not found for RentFile {rent_file.id}"
                            )
                        )
                else:
                    error_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"No mapping found for sub_district ID {sub_district_id} "
                            f"in RentFile {rent_file.id}"
                        )
                    )
            else:
                error_count += 1
                self.stdout.write(
                    self.style.WARNING(f"RentFile {rent_file.id} has no sub_district assigned")
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
                    f"Successfully updated {updated_count} RentFile objects, "
                    f"{error_count} errors/warnings"
                )
            )


