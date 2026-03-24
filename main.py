from fastapi import FastAPI, Path, HTTPException, Query
import json

app = FastAPI()

def data_loader():
    with open('patient_data.json', 'r') as f:
        data = json.load(f)
        return data

@app.get('/')
def title():
    return {'message': 'Relief APP'}

@app.get('/about')
def about():
    return {'message': "A fully functional API to manager your patient's data"}

@app.get('/view')
def view():
    data = data_loader()
    return data

@app.get('/patient/{patient_id}')
def particualr_patient(patient_id: str = Path(..., description='ID of the patient in the DB', examples='P001')):
    data = data_loader()

    for key, value in data.items():
        if patient_id in key:
            return value
    raise HTTPException(status_code=404, detail='Patient not found')

@app.get('/sort')
def sort_fun(sort_by: str = Query(..., description="sort your data on the basis of Height, Weight, BMI"), order: str = Query('asc')):
    
    valid_sorting = ['height', 'weight', 'bmi']
    valid_ordering = ['asc', 'desc']

    if sort_by.lower() not in valid_sorting:
        raise HTTPException(status_code=400, detail=f"You chosed wrong for sorting, please chose from {valid_sorting}")
    
    elif order.lower() not in valid_ordering:
        raise HTTPException(status_code=400, detail=f"Invalid order selection, Chose from {valid_ordering}")
    
    data = data_loader()

    ordering = True if order == 'asc' else False

    sorted_data = sorted(data.values(), key=lambda x: x[sort_by.lower()], reverse=ordering)

    return sorted_data