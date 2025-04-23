from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/sumar")
def sumar():
    resultado = 2 + 3
    return JSONResponse(content={"mensaje": f"La suma de 2 y 3 es: {resultado}"})
