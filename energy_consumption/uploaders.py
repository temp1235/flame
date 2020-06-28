from django.db import transaction

from typing import Iterable, Tuple

from energy_consumption.models import Building, Meter, MeterReading

@transaction.atomic
def upload_buildings(rows: Iterable[Tuple]) -> None:
    for row in rows:
        building_id = row[0]
        building_name = row[1]
        if building_id:
            Building.objects.update_or_create(
                id=building_id,
                name=building_name,
            )

@transaction.atomic
def upload_meters(rows: Iterable[Tuple]) -> None:
    for row in rows:
        building = Building.objects.get(id=row[0])
        meter_id = row[1]
        fuel = Meter.fuel_from_label(row[2])
        unit = Meter.unit_from_label(row[3])
        if meter_id:
            Meter.objects.update_or_create(
                id=meter_id,
                building=building,
                fuel=fuel,
                unit=unit,
            )

@transaction.atomic
def upload_meter_readings(rows: Iterable[Tuple]) -> None:
    meter_readings = [
        MeterReading(value=row[0], meter_id=row[1], date_time=row[2])
        for row in rows
    ]
    MeterReading.objects.all().delete()
    MeterReading.objects.bulk_create(meter_readings)
