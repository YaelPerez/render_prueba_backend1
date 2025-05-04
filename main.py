from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
import io
import pandas as pd

app = FastAPI()

@app.post("/procesar_excel")
async def procesar_excel(file: UploadFile = File(...)):
    # Leer el archivo excel recibido
    contents = await file.read()
    input_excel = io.BytesIO(contents)
    
    # Cargarlo en pandas
    df = pd.read_excel(input_excel)
    
    # Realizamos algún procesamiento (ejemplo: duplicar las filas)
    df_resultado = pd.concat([df, df])
    
    # Guardar el resultado en memoria
    output_excel = io.BytesIO()
    df_resultado.to_excel(output_excel, index=False)
    output_excel.seek(0)

    return StreamingResponse(
        output_excel,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file.filename.replace('.xlsx', '_Consulta.xlsx')}"}
    )
