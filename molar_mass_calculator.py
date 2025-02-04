from initialization import app 
from molar_mass_calculator import app 
from flask import Flask, render_template, redirect, request, jsonify
import copy
import json 
import time , requests

class PeriodicTable:
    
    def __init__(self):
        before = time.time()
        with open('periodic_table.json', 'r', encoding="utf-8") as f:
            self.data = json.load(f)['elements']
        self.__final = time.time() - before
        
    @staticmethod
    def list_elements():
        
        with open('periodic_table.json', 'r', encoding="utf-8") as f:
            alldata = json.load(f)['elements']
        rtn = []
        for data in alldata:
            rtn.append(data['symbol'])
        return rtn
    def get_load_time(self):
        
        return self.__final


@app.route('/molar_mass_calculator', methods=['GET', 'POST'])
def molar_mass_calculator():
    
    periodic_table = PeriodicTable()
    
    if request.method == 'GET':
        return render_template('molar_mass_calculator.html', elements = periodic_table.data, answer='')
    
    print(check_formula(request.form.get('formula_field')))
    if not check_formula(request.form.get('formula_field')):
        answer = f'{request.form.get("formula_field")} is not a valid Compound'
        return render_template('molar_mass_calculator.html', elements = periodic_table.data, answer=answer)
    
    code_field = request.form.get('code_field')
    total = 0.0
    print(code_field.split('['))
    for eq in code_field.split('[')[1:]:
        equation = eq.split(']')[0]
        print(equation)
        
        print(list(map(int,equation.split('x'))))
        
        index, multi = list(map(int,equation.split('x')))
        total += periodic_table.data[index-1]['atomic_mass'] * multi
        
    print(total)
        
    answer = f'Molar Mass of {request.form.get("formula_field")} is {total} g/mol'
        
    
    return  render_template('molar_mass_calculator.html', elements = periodic_table.data, answer=answer)

import requests

@app.route('/check_formula_<formula>', methods=['POST'])
def check_formula(formula):
    """Check if a chemical formula is a real compound using PubChem API."""
    
    # Format the formula in case there are spaces or case issues
    # formula = formula.replace(" ", "").upper()  # Remove spaces and make uppercase

    # Check if it's a single element (e.g., H, O, C)
    # This is a simple check, you might want to refine it further
    if formula in PeriodicTable.list_elements():  
        return True  # Single element (e.g., H, O, C)

    # URL to query PubChem by formula (this might not always work)
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{formula}/cids/JSON"
    
    response = requests.get(url)
    
    # Check if the request was successful and data is returned
    if response.status_code == 200:
        data = response.json()
        
        # Debug: Check the raw response data
        print(dict(data).keys())
        return 'IdentifierList' in dict(data).keys()
    print('asdw')
    return False
