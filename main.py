from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import pandas as pd
from io import BytesIO

app = FastAPI()

@app.get("/generar_excel")
def generar_excel():
    df = pd.DataFrame({
        "Nombre": ["Yael", "Verona", "Tito"],
        "Edad": [30, 5, 3],
        "Ciudad": ["Toluca", "Toluca", "Toluca"]
    })

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Datos')
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=archivo_generado.xlsx"}
    )
