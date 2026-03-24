from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
import json
from pydantic import Field, BaseModel, computed_field
from typing import Annotated, Literal, Optional

app = FastAPI()

class data_validator(BaseModel):
    id: Annotated[str, Field(..., description="ID of the patient", examples=['P001'])]
    name: Annotated[str, Field(..., description="Name of the patient")]
    age: Annotated[int, Field(..., description="Age of the patient", ge=0, le=120)]
    gender: Annotated[Literal['male', 'female', 'others'], Field(..., description="Gender of the patient")]
    city: Annotated[str, Field(..., description="City where patient belong")]
    height: Annotated[float, Field(..., description="Height of the patient in meters", ge=0)]
    weight: Annotated[float, Field(..., description="Weight of the patient in kgs", ge=0)]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi_cal = round(self.weight/(self.height**2), 2)
        return bmi_cal

    @computed_field
    @property
    def verdict_cal(self) -> str:
        if self.bmi < 18.5:
            return 'underweight'
        elif self.bmi >= 18.5 and self.bmi < 24.9:
            return 'Normal'
        elif self.bmi >= 25 and self.bmi < 29.9:
            return 'overweight'
        if self.bmi >= 30:
            return 'obese'
        
class patient_update(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, ge=0, le=120)]
    gender: Annotated[Optional[Literal['male', 'female', 'others']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, ge=0)]
    weight: Annotated[Optional[float], Field(default=None, ge=0)]


def data_loader():
    with open('patient_data.json', 'r') as f:
        data = json.load(f)
        return data

def save_data(data):
    with open('patient_data.json', 'w') as f:
        json.dump(data, f)

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

@app.post('/create')
def create_patient(patient: data_validator):
    data = data_loader()

    if patient.id in data.keys():
        raise HTTPException(status_code=400, detail='Patient already exists')
    
    data[patient.id] = patient.model_dump(exclude=['id'])

    save_data(data)

    return JSONResponse(status_code=201, content={'message': 'Patient created successfully'})