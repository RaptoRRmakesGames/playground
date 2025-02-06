from initialization import app 
from flask import Flask, render_template, redirect, request, jsonify
import copy
import json 
import time , requests
from functools import cache
import mysql.connector

def connect():

    with open("db_creds.json") as f:
        db_cr = json.load(f)

    db = mysql.connector.connect(
        host=db_cr["host"],
        user=db_cr["username"],
        passwd=db_cr["password"],
        database=db_cr["dbname"],
        port=db_cr["port"],
    )

    return db, db.cursor()



def execute(query: str, args=None):
    if args is None:
        args = []

    dbe, c = connect()

    try:
        c.execute(query, args)

        # Check if the query is a SELECT statement
        if "select" in query.lower():
            dbe.commit()
            return c.fetchall()
        else:
            dbe.commit()
            return None
    # except Exception as e:
    #     # Log or print the error for debugging purposes
    #     print(f"DB EXECUTION ERROR: {e}")
    #     #dbe.rollback()  # Roll back in case of an error in non-SELECT queries
    #     return None
    finally:
        try:

            c.close()
            dbe.close()
        except Exception:
            f = c.fetchall()

            c.close()
            dbe.close()

            return f
        
        

class PeriodicTable:
    def __init__(self):

        before = time.time()
        
        self.data = []
        raw_data = execute('SELECT json FROM chem_elements')

        for f in raw_data:
            json_str = f[0]  # Extract JSON string from the tuple

            if not json_str:  # Skip NULL or empty values
                print("Skipping empty entry.")
                continue  

            try:
                parsed_json = json.loads(json_str)  # Parse JSON
                self.data.append(parsed_json)
            except json.JSONDecodeError as e:
                print(f" Invalid JSON in database: {json_str}")  # Debugging output
                print(f"Error: {e}")
        
        self.__final = time.time() - before

    @staticmethod
    def list_elements():
        pt = PeriodicTable()
        print(pt.data)
        return [d for d in pt.data]

    def get_load_time(self):
        return self.__final



@app.route('/molar_mass_calculator', methods=['GET', 'POST'])
def molar_mass_calculator():
    
    periodic_table = PeriodicTable()
    print(periodic_table.data[0])
    
    if request.method == 'GET':
        return render_template('molar_mass_calculator.html', elements = periodic_table.data, answer='')
    
    print('made it to function')
    
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
    return True
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

if __name__ == '__main__':
    execute('TRUNCATE TABLE chem_elements')
    with open('periodic_table.json', 'r', encoding='utf-8') as f:
        data_list = json.load(f)['elements']
        
        for data in data_list:
            final_data = {
                'name' : data['name'],
                'symbol' : data['symbol'],
                'xpos' : data['xpos'],
                'ypos' : data['ypos'],
                'atomic_mass' : data['atomic_mass'],
                'number' : data['number'],
                'cpk-hex' : data['cpk-hex']
                }
            execute('INSERT INTO chem_elements (json) VALUES (%s)', [str(final_data).replace("'", '"'), ])