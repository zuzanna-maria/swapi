from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import requests
import pandas as pd
from pandas.io.json import json_normalize
import json
import csv
import math
from datetime import datetime, date
from sw_characters.models import CSVFile
import random
import string
import petl
import itertools
from django.conf import settings
from collections import OrderedDict

def index(request):
    return render(request, 'home.html')


def home_planet(request):
    planet_dict = {}

    planet_count = requests.get('https://swapi.dev/api/planets').json()['count']

    for planet in range (1, planet_count+1):
        planet_url = 'https://swapi.dev/api/planets/{}/'.format(planet)
        planet_result = requests.get(planet_url, verify=False).json()
        planet_name = planet_result['name']
        planet_dict[planet_url] = planet_name
    
    return planet_dict

def call_api(request):

    planet_dict = home_planet(request)
    
    result = requests.get('https://swapi.dev/api/people', verify=False).json()

    page_number = int((math.ceil(result["count"]/10) * 10)/10)
    complete_results = []

    for page in range(1, page_number+1):
        result = requests.get('https://swapi.dev/api/people/?page={}'.format(page), verify=False).json()
        for result_number in range(0, len(result['results'])):
            del result['results'][result_number]['url']
            del result['results'][result_number]['created']
            del result['results'][result_number]['films']
            del result['results'][result_number]['vehicles']
            del result['results'][result_number]['starships']
            del result['results'][result_number]['species']
            edited_date = result['results'][result_number]['edited']
            result['results'][result_number]['date'] = datetime.strptime(edited_date, "%Y-%m-%dT%H:%M:%S.%fZ").date()
            del result['results'][result_number]['edited']
            result['results'][result_number]['homeworld'] = planet_dict[result['results'][result_number]['homeworld']]
        
        complete_results.append(result["results"])


    df = pd.DataFrame()
    for dict_number in range(0, len(complete_results)):
        df = df.append(complete_results[dict_number])

    dte = str(datetime.now())
    new_dte = datetime.strptime(dte, "%Y-%m-%d %H:%M:%S.%f")
    dt = new_dte.strftime("%b. %d, %Y, %H:%M")
    filename = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
    csv_filename = 'characters-{}.csv'.format(filename)
    df.to_csv("{}".format(csv_filename), index=False)

    dataset = CSVFile(filename=csv_filename, date_downloaded=dt)
    dataset.save()
    
    return redirect('display_all_datasets')


def display_dataset(request, dataset_filename):
    read_obj = open(dataset_filename, 'r')
    reader = csv.DictReader(read_obj)
    headers = [col for col in reader.fieldnames]

    csv_reader = csv.reader(read_obj)
    out = [row for row in csv_reader]
    if request.POST:
        number_of_entries = int(request.POST.get('number_of_entries')) + int(request.POST.get('load_more'))
    else:
        number_of_entries = 10
    out = out[:number_of_entries]

    return render(request, 'display_dataset.html', {'headers': headers, 'data': out, 'dataset_filename' : dataset_filename})


def display_all_datasets(request):
    datasets = CSVFile.objects.all()
    return render(request, 'display_all_datasets.html', {'datasets' : datasets})

def value_counter(request):

    values = request.POST.getlist('chosen_value')

    result_table = petl.fromcsv(request.POST['dataset_filename'])

    data = pd.read_csv(request.POST['dataset_filename'])
    table = petl.fromcsv(request.POST['dataset_filename'])

    column_dict = {}
    values_dict = {}
    for l in range(0, len(values)):
        column_data = data[values[l]].to_list()
        column_data = set(column_data)
        column_data = list(map(str, column_data))
        column_dict['col{}'.format(l)] = column_data
        values_dict[l] = values[l]

    if len(values) == 1:
        occurrences_dict = petl.valuecounter(table, values[0])

        ordered_occurrences_dict = OrderedDict(sorted(occurrences_dict.items()))

        return render(request, 'value_count.html', {'value': values[0], 'occurrences': ordered_occurrences_dict.items()})
        

    elif len(values) > 1: 
        combinations = list(itertools.product(*column_dict.values()))
        values_tuple = tuple(values_dict.values())
        occurrences = []
        for combination in combinations:
            occurrence, frequency = petl.valuecount(table, values_tuple, combination)
            combination_list = list(combination)
            combination_list.append(occurrence)
            occurrences.append(combination_list)

        return render(request, 'value_counter.html', {'values': values_tuple, 'occurrences': occurrences})
    
    else:
        return render(request, 'error_page.html')

        
            