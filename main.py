from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import StreamingResponse
import pandas as pd
import io
import funciones  # tu archivo funciones.py (no se modifica)
import variables  # tu archivo variables.py (no se modifica)
import json
import requests
import os
import importlib
import datetime as dt
from dateutil.relativedelta import relativedelta
import logging

logger = logging.getLogger("uvicorn.error")

# Crear la app de FastAPI
app = FastAPI()

@app.post("/consultar")
async def procesar_excel(
    file: UploadFile,
    us: str = Form(...),
    pw: str = Form(...),
    pk: str = Form(...),
    ak: str = Form(...)
):
    try:
        # Leer el archivo recibido
        contents = await file.read()
        excel_file = io.BytesIO(contents)

        # Mostrar valores recibidos
        print(f"Valores recibidos: us={us}, pw={pw}, pk={pk}, ak={ak}")
        logger.info(f"Valores recibidos: us={us}, pw={pw}, pk={pk}, ak={ak}")

        # Leer Excel
        df_solicitud = pd.read_excel(excel_file)

        # Transformaciones igual que en tu código original
        df_solicitud['CP'] = df_solicitud['CP'].astype(str)
        df_solicitud['fechaNacimiento'] = pd.to_datetime(df_solicitud['fechaNacimiento'], errors='coerce').dt.strftime('%Y-%m-%d')

        df_copy_solicitud = df_solicitud.copy()
        df_copy_solicitud['domicilio'] = df_copy_solicitud.apply(lambda row: {
            "direccion": row['direccion'],
            "coloniaPoblacion": row['coloniaPoblacion'],
            "delegacionMunicipio": row['delegacionMunicipio'],
            "ciudad": row['ciudad'],
            "estado": row['estado'],
            "CP": row['CP']
        }, axis=1)

        # -------------------------------
        df_copy_solicitud = df_copy_solicitud.drop(columns=['direccion', 'coloniaPoblacion', 'delegacionMunicipio', 'ciudad', 'estado', 'CP'])
        columns = ['apellidoPaterno', 'apellidoMaterno', 'primerNombre', 'fechaNacimiento', 'RFC', 'nacionalidad', 'domicilio']
        df_final = df_copy_solicitud[columns]
        json_list = [row.to_dict() for _, row in df_final.iterrows()]
        #print(json.dumps(json_list, ensure_ascii=False, indent=4))

            #Hacemos las peticiones para tener los json de respuesta / privada en formato hexadecimal
        PRIVATE_KEY_HEX = pk
        url = "https://omtaxzvaqb.execute-api.us-east-1.amazonaws.com/v1/rcc-ficoscore-pld"
        # url = "https://services.circulodecredito.com.mx/v1/rcc-ficoscore-pld

            # Cargar la clave privada  
        private_key = funciones.load_private_key_from_hex(PRIVATE_KEY_HEX)
        clientes_respuesta = []
        for record in json_list:
            try:
                signature = funciones.sign_data(private_key, json.dumps(record)) 
                if not signature:
                    variables.log.error("Error al generar la firma.")
                headers = {
                        "username": us,   
                        "password": pw,     
                        "x-signature": signature,
                        "Content-Type": "application/json",  
                        "x-api-key": ak,  
                }
                response = requests.post(url, headers=headers, json=record, timeout=10)
                # Verificar la respuesta
                if response.status_code == 200 or response.status_code == 201:
                    print(f"petición exitosa")#{response.json()}")
                    logger.info(f"petición exitosa")
                    #response_filled = funciones.compare_and_add_fields(variables.schema, response.json())
                    response_filled = funciones.compare_and_add_fields(variables.schema, response.json())
                    formated_response = funciones.remove_records(response_filled)
                    formated_response = funciones.pld_check(formated_response)
                    formated_response = funciones.resumen_por_producto(formated_response)       
                    clientes_respuesta.append(formated_response)
                    variables.log.info(f"API Security-Test Response: {response.status_code} - {response.text}")
                elif response.status_code == 400:
                    print(f"Solicitud incorrecta (400): {response.text}")
                    logger.info(f"Solicitud incorrecta (400): {response.text}")
                        #messagebox.showerror("Error", "Solicitud incorrecta, validar datos de entrada.")           #MENSAJE FRONT
                elif response.status_code == 401:
                    print("No autorizado (401): Verifique sus credenciales.")
                    logger.info("No autorizado (401): Verifique sus credenciales.")
                        #messagebox.showerror("Error", "Verifique sus credenciales")                                #MENSAJE FRONT
                elif response.status_code == 403:
                    print("Prohibido (403): Verifique permisos en el servidor.")
                    logger.info("Prohibido (403): Verifique permisos en el servidor.")
                        #messagebox.showerror("Error", "Verifique permisos en el servidor")                         #MENSAJE FRONT
                elif response.status_code == 404:
                    print("Recurso no encontrado (404).")
                    logger.info("Recurso no encontrado (404).")
                        #messagebox.showerror("Error", "Servidor no encontrado")                                    #MENSAJE FRONT
                elif response.status_code == 500:
                    print("Error interno del servidor (500).")
                    logger.info("Error interno del servidor (500).")
                        #messagebox.showerror("Error", "Error interno del servidor")                                #MENSAJE FRONT
                else:
                    print("Error:", response.status_code, response.text)
                    logger.info("Error:", response.status_code, response.text)
                    variables.log.error(f"Error en la solicitud: {response.status_code} - {response.text}")
            except requests.exceptions.Timeout:
                print("Error: Tiempo de espera excedido. Verifica la conexión o aumenta el límite de tiempo.")
                logger.info("Error: Tiempo de espera excedido. Verifica la conexión o aumenta el límite de tiempo.")
                    #messagebox.ERROR("Error en la consulta", "El servicio de Círculo no esta respondiendo...")     #MENSAJE FRONT
            except requests.exceptions.ConnectionError:
                print("Error: No se pudo conectar al servidor. Verifica tu conexión a Internet o la URL.")
                logger.info("Error: No se pudo conectar al servidor. Verifica tu conexión a Internet o la URL.")
                #messagebox.showerror("Error", "Verifica tu conexión a internet")                                   #MENSAJE FRONT
            except requests.exceptions.RequestException as e:
                print(f"Error general al realizar la solicitud: {e}")
                logger.info(f"Error general al realizar la solicitud: {e}")
            except ValueError as e:
                print(f"Error al procesar la respuesta del servidor: {e}")
                logger.info(f"Error al procesar la respuesta del servidor: {e}")
            except Exception as e:
                print(f"Error al intentar enviar el POST: {e}")
                logger.info(f"Error al intentar enviar el POST: {e}")

                                    #Determinamos la dimensión del dataframe
        df_simples = funciones.dataframes_simples(clientes_respuesta)


        dimensiones = funciones.dim(clientes_respuesta)
                                    #Creamos la Tabla final    
        #Tabla de clientes (persona, pldcheck,folioConsulta,folioConsultaOtorgante)
        clientes = []
        clientes_pld = []
        for cliente, j in zip(clientes_respuesta,range(len(clientes_respuesta))):
            clientes.append(pd.DataFrame(cliente["persona"], index= [0]))
            clientes.append(pd.DataFrame(cliente["pldCheck"], index = [1]))
            clientes[j]['folioConsulta'] = cliente['folioConsulta']         
            clientes[j]['folioConsultaOtorgante'] = cliente['folioConsultaOtorgante']   
        
        #df_clientes = pd.concat(clientes[::2],axis = 0)
        df_clientes = pd.concat(clientes,axis = 0)

        #Actualizamos el diccionario de scores para poderlo tratar de la misma forma
        for valor in clientes_respuesta:
            for valor2 in valor["scores"]:
                valor2.update({'razones' : ", ".join(valor2['razones'])})
                #print(valor2)
                
        lista_secciones = []
        for seccion,j in zip(variables.secciones,range(len(variables.secciones))):
            lista_secciones.append(funciones.df_secciones(seccion,clientes_respuesta))

        print(f"tabla consultas , dimension antes de filtrado: {lista_secciones[4].shape}")
        logger.info(f"tabla consultas , dimension antes de filtrado: {lista_secciones[4].shape}")
        print(f"tabla creditos , dimension antes de filtrado: {lista_secciones[5].shape}")
        logger.info(f"tabla creditos , dimension antes de filtrado: {lista_secciones[5].shape}")


        if dimensiones['columnas'].sum() >=16000:
            print(f"exceso de dimensiones, reduciremos los creditos a 10 años a la actualidad y las consultas a 18 meses a la actualidad")
            logger.info(f"exceso de dimensiones, reduciremos los creditos a 10 años a la actualidad y las consultas a 18 meses a la actualidad")
            df_creditos_nofilter = lista_secciones[5] ; df_consultas_nofilter = lista_secciones[4]
            df_creditos_nofilter['fechaAperturaCuenta'] = pd.to_datetime(df_creditos_nofilter['fechaAperturaCuenta'])
            df_consultas_nofilter['fechaConsulta'] = pd.to_datetime(df_consultas_nofilter['fechaConsulta'])
            #df_creditos_filtrada = ps.sqldf(""" SELECT * FROM df_creditos ORDER BY 'montoPagar' DESC """,locals())
            df_creditos_filtrada = df_creditos_nofilter[df_creditos_nofilter['fechaAperturaCuenta'] > str(dt.datetime.now()-relativedelta(years = 10))]
            df_consultas_filtrada = df_consultas_nofilter[df_consultas_nofilter['fechaConsulta'] > str(dt.datetime.now()-relativedelta(years = 1, months=8))]
            print(f"creditos eliminados: {len(df_creditos_nofilter)-len(df_creditos_filtrada)}")
            logger.info(f"creditos eliminados: {len(df_creditos_nofilter)-len(df_creditos_filtrada)}")
            print(f"consultas eliminados: {len(df_consultas_nofilter)-len(df_consultas_filtrada)}")
            logger.info(f"consultas eliminados: {len(df_consultas_nofilter)-len(df_consultas_filtrada)}")
            
            print(f"tabla consultas , dimension despues de filtrado: {df_consultas_filtrada.shape}")
            logger.info(f"tabla consultas , dimension despues de filtrado: {df_consultas_filtrada.shape}")
            print(f"tabla creditos , dimension despues de filtrado: {df_creditos_filtrada.shape}")
            logger.info(f"tabla creditos , dimension despues de filtrado: {df_creditos_filtrada.shape}")
            
            lista_secciones[4] = df_consultas_filtrada ; lista_secciones[5] = df_creditos_filtrada

        else:
            print(f"dimensiones apropiadas, todas las tablas estan en la lista lista_secciones")
            logger.info(f"dimensiones apropiadas, todas las tablas estan en la lista lista_secciones")

        df_finales = []
        for datafr in lista_secciones:
            df_final = funciones.finaldataframe(datafr, 'Cliente')
            df_df = df_final.drop('Cliente', axis=1)
            df_finales.append(df_df)

        df_scores = df_finales[6] 
        df_scores.insert(0, "scores", '')

        df_mensajes = df_finales[2]
        df_mensajes.insert(0, "mensajes", '')

        df_domicilios = df_finales[1]
        df_domicilios.insert(0, "domicilios", '')

        df_empleos = df_finales[3]
        df_empleos.insert(0, "empleos", '')

        df_resumenPorProducto = df_finales[0]
        df_resumenPorProducto.insert(0, "resumenPorProducto", '')

        df_creditos = df_finales[5]
        df_creditos.insert(0, "creditos", '')

        df_consultas = df_finales[4]     #Esta eliminando clientes
        df_consultas.insert(0, "consultas", '')

        tabla_final = pd.concat([df_simples[0],df_simples[1],df_scores,df_mensajes,df_simples[2],df_domicilios,df_empleos,df_resumenPorProducto,df_creditos], axis=1)

        # tabla_final.to_excel('ARCHIVOS_PRUEBAS_FIZ.xlsx', index=False)
        # -------------------------------

        # Para este ejemplo: solo guardamos el mismo df procesado
        output_buffer = io.BytesIO()
        tabla_final.to_excel(output_buffer, index=False)
        output_buffer.seek(0)

        # Crear nombre de archivo salida
        nombre_salida = file.filename.replace('.xlsx', '_Consulta.xlsx')

        # Devolver archivo como respuesta de descarga
        return StreamingResponse(
            output_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={nombre_salida}"}
        )
    
    except Exception as e:
        logger.exception(f"Error general: {e}")
        return {"error": str(e)}
