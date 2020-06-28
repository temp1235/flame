import csv, io
import numpy as np

from django.contrib import messages
from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.shortcuts import render

from energy_consumption.models import Building, Meter, MeterReading
from energy_consumption.uploaders import upload_buildings, upload_meters, upload_meter_readings


def index(request):
    return render(request, 'chart.html')

def water_chart(request):
    labels = []
    datasets_dict = {}

    queryset = (
        MeterReading.objects
        .annotate(date=TruncDate('date_time'))
        .values('date')
        .annotate(date_consumption=Sum('value'))
        .values('meter__building__name', 'date_consumption', 'date')
    )
    dates = sorted(list(set([reading['date'] for reading in queryset])))
    for date in dates:
        labels.append(date)
        for reading in [reading for reading in queryset if reading['date'] == date]:
            building_name = reading['meter__building__name']
            if building_name in datasets_dict:
                datasets_dict[building_name].append(reading['date_consumption'])
            else:
                datasets_dict[building_name] = [reading['date_consumption']]

    def create_random_colour():
        return f'rgba{tuple(np.random.randint(256, size=4))}'

    datasets = [{
        'label': k,
        'fill': 'false',
        'backgroundColor': create_random_colour(),
        'data': datasets_dict[k]
    } for k in datasets_dict]

    return JsonResponse(data={
        'labels': labels,
        'datasets': datasets,
    })

def building_detail(request, pk: int):
    template = "buildings.html"
    buildings = Building.objects.filter(id=pk)
    context = {
        'buildings': buildings
    }
    return render(request, template, context)

def buildings(request):
    template = "buildings.html"
    buildings = Building.objects.all()
    context = {
        'buildings': buildings
    }
    return render(request, template, context)

def meter_detail(request, pk: int):
    template = "meters.html"

    meters = Meter.objects.filter(id=pk)

    for meter in meters:
        meter.fuel_name = Meter.fuel_label_from_fuel(meter.fuel)
        meter.unit_name = Meter.unit_label_from_unit(meter.unit)

    context = {
        'meters': meters,
    }
    return render(request, template, context)

def meters(request):
    template = "meters.html"

    meters = Meter.objects.all()

    for meter in meters:
        meter.fuel_name = Meter.fuel_label_from_fuel(meter.fuel)
        meter.unit_name = Meter.unit_label_from_unit(meter.unit)

    context = {
        'meters': meters,
    }
    return render(request, template, context)

def meter_readings(request):
    template = "meter_readings.html"
    context = {
        'meter_readings': MeterReading.objects.all()
    }
    return render(request, template, context)

def data_upload(request):
    template = "data_upload.html"

    building_data_file_name = 'building_data'
    meter_data_file_name = 'meter_data'
    meter_reading_data_file_name = 'meter_reading_data'
    context = {
        'uploaders': [
            {
                'id': 'buildingData',
                'file_name': building_data_file_name,
                'type': 'Building',
                'columns': 'id, name',
                'result': '',
                'view': 'buildings',
            },
            {
                'id': 'meterData',
                'file_name': meter_data_file_name,
                'type': 'Meter',
                'columns': 'building id, id, fuel, unit',
                'result': '',
                'view': 'meters',
            },
            {
                'id': 'meterReadingData',
                'file_name': meter_reading_data_file_name,
                'type': 'Meter Reading',
                'columns': 'consumption, meter id, date time',
                'result': '',
                'warning': 'This will overwrite all meter reading data in the system.',
                'view': 'meter_readings',
            },
        ]
    }
    if request.method == "GET":
        return render(request, template, context)
    

    for uploader in context['uploaders']:
        if uploader['file_name'] in request.POST:
            functions_by_file_name = {
                building_data_file_name: upload_buildings,
                meter_data_file_name: upload_meters,
                meter_reading_data_file_name: upload_meter_readings,
            }

            csv_file = request.FILES[uploader['file_name']]
            if not csv_file.name.endswith('.csv'):
                uploader['result'] = 'Your data upload was unsuccessful. Make sure you are uploading a csv file'
                continue

            data_set = csv_file.read().decode('UTF-8')
            io_string = io.StringIO(data_set)
            next(io_string)

            rows = csv.reader(io_string, delimiter=',', quotechar="|")
            try:
                upload_function = functions_by_file_name[uploader['file_name']]
                upload_function(rows)
                uploader['result'] = 'Success!'
            except Exception as e:
                uploader['result'] = f'Unsuccessful upload attempt: {e}'
    return render(request, template, context)
