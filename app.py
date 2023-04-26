import mysql.connector
from typing import Union
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json
from datetime import date
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html

# Declaración de modelo basandose a al base de datos
class estudiante(BaseModel):
    id: int | None = None
    nombre: str
    apellido: str
    carnet: str
    creacion: str | None = None
# Conexión a la base de datos
conect = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="20%"
)

app = FastAPI()

@app.get("/openapi.json")
async def get_open_api_endpoint():
    return JSONResponse(get_openapi(title="Tu API", version="0.0.2", routes=app.routes))

@app.get("/docs2", include_in_schema=False)
async def get_documentation():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="documentación")

# Endpoint para la obtención de todos los estudiantes
@app.get("/estudiante")
async def getEstudiantes():
    cursor = conect.cursor()
    query="select * from estudiante;"
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close
    # Realizar un mapeo de los datos recolectados
    # lambda: Función anonima
    response = list(map(lambda data: {
    "id": data[0],
    "nombre": data[1],
    "apellido": data[2],
    "carnet": data[3],
    "creacion":str(data[4])
    }, result))
    return JSONResponse(content=response)
# Endpoint para la obtención de un solo estudiante
@app.get("/estudiante/{id}")
async def getEstudiante(id: int):
    cursor = conect.cursor()
    query="select * from estudiante where id = %s;"
    cursor.execute(query,(id,))
    result = cursor.fetchone()
    cursor.close
    if result is None:
        return JSONResponse(status_code=404, content={"mensaje": "Usuario no encontrado"})
    else:
        response = {
        "id": result[0],
        "nombre": result[1],
        "apellido": result[2],
        "carnet": result[3],
        "creacion":str(result[4])
        }
    return JSONResponse(content=response)
# Endpoint para actualizar datos de un estudiante
@app.put("/estudiante/{id}")
async def putEstudiante(id: int, body :estudiante):
    cursor = conect.cursor()
    response = { **body.dict() }
    response.update({"id":id})
    sql = "UPDATE estudiante SET nombre = %s, apellido = %s, carnet = %s WHERE id = %s"
    values = (body.nombre,body.apellido,body.carnet,id)
    cursor.execute(sql,values)
    conect.commit()
    cursor.close()
    return JSONResponse(content={"mensaje": f"El usuario con id {id} ha sido actualizado"})
# Endpoint para el ingreso de un estudiante
@app.post("/estudiante")
async def postEstudiante(body:estudiante):
    cursor = conect.cursor()
    today = date.today()   
    sql = "INSERT INTO estudiante(nombre,apellido,carnet,creacion) VALUES(%s,%s,%s,%s)"
    values = (body.nombre,body.apellido,body.carnet,today)
    cursor.execute(sql,values)
    conect.commit()
    cursor.close()
    return JSONResponse(content={"mensaje": f"El usuario ha sido agregado"})

@app.delete("/estudiante/{id}")
async def deteleEstudiante(id : int):  
    cursor = conect.cursor()
    sql = "delete from estudiante where id = %s;"
    cursor.execute(sql,(id,))
    conect.commit()
    cursor.close()
    return JSONResponse(content={"mensaje": f"El usuario ha sido eliminado"})