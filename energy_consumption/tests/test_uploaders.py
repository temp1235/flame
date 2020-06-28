import datetime
from django.test import TestCase
from django.core.exceptions import ValidationError
from energy_consumption.models import Building, Meter, MeterReading
from energy_consumption.uploaders import upload_buildings, upload_meters, upload_meter_readings

class TestUploadBuildings(TestCase):
    def test_upload_creates_building_objects(self):
        rows = [(1, 'building 1'), (200, '')]

        upload_buildings(rows)

        for row in rows:
            Building.objects.get(id=row[0], name=row[1])

    def test_bad_upload_creates_nothing(self):
        rows = [(1, 'building 1'), ('Wrong format', 'building 2')]

        self.assertRaises(ValueError, upload_buildings, rows)

        self.assertEqual(0, len(Building.objects.all()))


class TestUploadMeters(TestCase):
    def setUp(self):
        self.building = Building.objects.create(id=1, name='building 1')

    def test_upload_creates_meter_objects(self):
        rows = [
            (self.building.id, 1, 'Water', 'm3'),
            (self.building.id, 2, 'Electricity', 'kWh'),
            (self.building.id, 3, 'Natural Gas', 'kWh'),
        ]

        upload_meters(rows)

        Meter.objects.get(
            building_id=self.building.id, id=1, fuel=Meter.WATER, unit=Meter.CUBIC_METRES,
        )
        Meter.objects.get(
            building_id=self.building.id, id=2, fuel=Meter.ELECTRICITY, unit=Meter.KILOWATT_HOURS,
        )
        Meter.objects.get(
            building_id=self.building.id, id=3, fuel=Meter.NATURAL_GAS, unit=Meter.KILOWATT_HOURS,
        )

    def test_building_not_found_creates_nothing(self):
        rows = [
            (self.building.id, 1, 'Water', 'm3'),
            (2, 2, 'Electricity', 'kWh'),
        ]

        self.assertRaises(Building.DoesNotExist, upload_meters, rows)

        self.assertEqual(0, len(Meter.objects.all()))

    def test_wrong_fuel_creates_nothing(self):
        rows = [
            (self.building.id, 1, 'Water', 'm3'),
            (self.building.id, 2, 'Bananas', 'kWh'),
        ]

        self.assertRaises(StopIteration, upload_meters, rows)

        self.assertEqual(0, len(Meter.objects.all()))

    def test_wrong_unit_creates_nothing(self):
        rows = [
            (self.building.id, 1, 'Water', 'm3'),
            (self.building.id, 2, 'Electricity', 'Volts'),
        ]

        self.assertRaises(StopIteration, upload_meters, rows)

        self.assertEqual(0, len(Meter.objects.all()))



class TestUploadMeterReadings(TestCase):
    def setUp(self):
        self.building = Building.objects.create(id=1, name='building 1')
        self.meter = Meter.objects.create(building_id=1, id=1, fuel=Meter.WATER, unit=Meter.CUBIC_METRES)

    def test_upload_creates_meter_reading_objects(self):
        rows = [
            (100.1, self.meter.id, '2020-01-01 00:00'),
            (200.2, self.meter.id, '2020-01-01 00:30'),
        ]

        upload_meter_readings(rows)

        MeterReading.objects.get(
            value=100.1, meter_id=self.meter.id, date_time=datetime.datetime(2020, 1, 1, 0, 0),
        )
        MeterReading.objects.get(
            value=200.2, meter_id=self.meter.id, date_time=datetime.datetime(2020, 1, 1, 0, 30),
        )

    def test_upload_deletes_meter_reading_objects_before_creating(self):
        MeterReading.objects.create(value=1, meter_id=self.meter.id, date_time=datetime.datetime(2010, 1, 1, 0, 0))
        rows = [
            (100.1, self.meter.id, '2020-01-01 00:00'),
            (200.2, self.meter.id, '2020-01-01 00:30'),
        ]

        upload_meter_readings(rows)


        self.assertEqual(2, len(MeterReading.objects.all()))
        MeterReading.objects.get(
            value=100.1, meter_id=self.meter.id, date_time=datetime.datetime(2020, 1, 1, 0, 0),
        )
        MeterReading.objects.get(
            value=200.2, meter_id=self.meter.id, date_time=datetime.datetime(2020, 1, 1, 0, 30),
        )

    def test_invalid_row_rolls_back_transaction(self):
        MeterReading.objects.create(value=1, meter_id=self.meter.id, date_time=datetime.datetime(2010, 1, 1, 0, 0))
        rows = [
            (100.1, self.meter.id, '2020-01-01 00:00'),
            (200.2, self.meter.id, 'yesterday'),
        ]

        self.assertRaises(ValidationError, upload_meter_readings, rows)

        self.assertEqual(1, len(Meter.objects.all()))
        MeterReading.objects.get(
            value=1, meter_id=self.meter.id, date_time=datetime.datetime(2010, 1, 1, 0, 0),
        )
