from django.db import models


class Building(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()


class Meter(models.Model):
    WATER = 0
    NATURAL_GAS = 1
    ELECTRICITY = 2
    FUEL_CHOICES = (
        (WATER, 'Water'),
        (NATURAL_GAS, 'Natural Gas'),
        (ELECTRICITY, 'Electricity'),
    )
    @classmethod
    def fuel_label_from_fuel(cls, fuel):
        return next(fuel_choice[1] for fuel_choice in Meter.FUEL_CHOICES if fuel_choice[0] == fuel)
    @classmethod
    def fuel_from_label(cls, label):
        return next(fuel_choice[0] for fuel_choice in Meter.FUEL_CHOICES if fuel_choice[1] == label)

    CUBIC_METRES = 0
    KILOWATT_HOURS = 1
    UNIT_CHOICES = (
        (CUBIC_METRES, 'm3'),
        (KILOWATT_HOURS, 'kWh'),
    )
    @classmethod
    def unit_label_from_unit(cls, unit):
        return next(unit_choice[1] for unit_choice in Meter.UNIT_CHOICES if unit_choice[0] == unit)
    @classmethod
    def unit_from_label(cls, label):
        return next(unit_choice[0] for unit_choice in Meter.UNIT_CHOICES if unit_choice[1] == label)
        
    id = models.IntegerField(primary_key=True)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    fuel = models.IntegerField(default=0, choices=FUEL_CHOICES)
    unit = models.IntegerField(default=0, choices=UNIT_CHOICES)


class MeterReading(models.Model):
    value = models.DecimalField(max_digits=12, decimal_places=6)
    meter = models.ForeignKey(Meter, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
