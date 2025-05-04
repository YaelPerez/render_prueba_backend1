import variables
import pandas as pd
import binascii                     #Librerias
from datetime import date
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import utils

                                        #Funciones
def finaldataframe(df, col_nombre):  #Recibe un dataframe y la columna por la que se va agrupar
    orden_original = df[col_nombre].drop_duplicates().tolist()   

    nombres = df.groupby(col_nombre, sort=False)  

    registros = []
    columnas_base = [col for col in df.columns if col != col_nombre]  
    max_repeticiones = nombres.size().max() 

    columnas_repetidas = [] 
    for _ in range(max_repeticiones):    
        columnas_repetidas.extend(columnas_base)
    encabezado = [col_nombre] + columnas_repetidas  

    for cliente in orden_original:
        grupo = nombres.get_group(cliente)  
        fila = [cliente]                   
        for _, row in grupo.iterrows():
            fila.extend(row[col] for col in columnas_base)
        while len(fila) < len(encabezado):
            fila.append(None)
        registros.append(fila)

    return pd.DataFrame(registros, columns=encabezado)


        #Función de calculo de dimensiones
def dim(clientes_respuesta):        
    dim = []
    for cliente,j in zip(clientes_respuesta,range(len(clientes_respuesta))):
        for seccion in cliente:
            dim.append([cliente["persona"]["nombres"],seccion,len(cliente[seccion]),len(cliente[seccion])*variables.dimensiones_secciones[seccion]])
    return pd.DataFrame(dim,columns=['cliente','seccion','registros','columnas'])


def calculate_calificacion(item):
    if item.get("fechaCierreCuenta"):
        return "cerrada"
    elif not item.get("historicoPagos") or item["historicoPagos"].strip() == "":
        return "positiva"
    elif item.get("pagoActual") and item["pagoActual"].strip() != "V":
        return "negativa"
    else:
        return "positiva"

def df_secciones(seccion,clientes_respuesta):      #esta función requiere de que la variable clientes_respuesta este definida y sea información válida
    total_seccion= []
    clientes_ordenados = []
    for cliente in clientes_respuesta: 
        print(f"""comienza el cliente: {cliente["persona"]["nombres"]} , sección: {seccion}""")
        lista_seccion = [] ; nombre_cliente = cliente["persona"]['nombres']+' ' + cliente["persona"]['apellidoPaterno']+' '+cliente["persona"]['apellidoMaterno']
        clientes_ordenados.append(nombre_cliente)
        for elemento in cliente[seccion]:
            if isinstance(elemento, dict):  # Asegurar que sea un diccionario antes de convertirlo
                lista_seccion.append(pd.DataFrame(elemento, index=[0]))
            else:
                print(f"Advertencia: elemento no válido encontrado para el cliente {cliente.get('persona', {}).get('nombres', 'Desconocido')}")    
        #print(f"cantidad de registros: {len(lista_seccion)}")
        if len(lista_seccion) > 0 :
            lista_df_seccion = pd.concat(lista_seccion)         
            lista_df_seccion['Cliente'] = nombre_cliente
            print(f"LONGITUD REGISTRO: {len(lista_df_seccion.columns)}")
            total_seccion.append(lista_df_seccion)
            
        else:
            print(f'''cliente: {cliente["persona"]["nombres"]} con valor nulo para la seccion: {seccion}''')        
            #print(f"el numero de columnas: {}")
            print(f"columna a importar: {[nombre_cliente]}")
            #total_seccion.insert(0,pd.Series(nombre_cliente))   #Ultima modificación
            total_seccion.append(pd.Series(nombre_cliente))
    return pd.concat(total_seccion,axis = 0)

def sign_data(private_key, data):
    try:
        data_bytes = str.encode(data, "utf-8")
        chosen_hash = hashes.SHA256()
        hasher = hashes.Hash(chosen_hash)
        hasher.update(data_bytes)
        digest = hasher.finalize()
        signature = private_key.sign(digest, ec.ECDSA(utils.Prehashed(chosen_hash)))
        return binascii.hexlify(signature).decode()  
    except Exception as e:
        variables.log.error(f"Error al firmar los datos: {e}")
        return None

def load_private_key_from_hex(private_key_hex):
    error_message_label = None
    try:
        private_key_bytes = binascii.unhexlify(private_key_hex)
        private_key = serialization.load_der_private_key(private_key_bytes, password=None)
    # Si la clave es válida, eliminar el mensaje de error (si existe)
        if error_message_label:
            error_message_label.pack_forget()  # Elimina el mensaje de error
            error_message_label = None  # Resetea la variable
        return private_key
    except Exception as e:
        if error_message_label is None:
            print(f"Error, la llave privada no es un formato válido. Favor de verificar")
            #messagebox.showerror("Error", "La llave privada no es un formato válido. Favor de verificar.")
            
            raise e     
    
def compare_and_add_fields(schema, response):
    ordered_response = {}
    for key, value in schema.items():
        value_in_response = response.get(key)

        if value_in_response is None:
            # Campo faltante
            if value["type"] == "string":
                ordered_response[key] = ""
            elif value["type"] == "number":
                ordered_response[key] = 0
            elif value["type"] == "boolean":
                ordered_response[key] = False
            elif value["type"] == "object":
                ordered_response[key] = compare_and_add_fields(value["properties"], {})
            elif value["type"] == "array":
                if value["items"]["type"] == "object":
                    # Agregar arreglo con un objeto base si se espera arreglo de objetos
                    ordered_response[key] = [compare_and_add_fields(value["items"]["properties"], {})]
                else:
                    # Arreglo de elementos simples (str, num...) → arreglo vacío
                    ordered_response[key] = []
            else:
                ordered_response[key] = None
        else:
            if value["type"] == "object":
                if isinstance(value_in_response, dict):
                    ordered_response[key] = compare_and_add_fields(value["properties"], value_in_response)
                else:
                    # Tipo incorrecto, igual lo inicializa vacío
                    ordered_response[key] = compare_and_add_fields(value["properties"], {})
            elif value["type"] == "array":
                if isinstance(value_in_response, list):
                    if len(value_in_response) > 0 and isinstance(value_in_response[0], dict):
                        # Arreglo de objetos, transformar cada uno
                        ordered_response[key] = [
                            compare_and_add_fields(value["items"]["properties"], item)
                            for item in value_in_response
                        ]
                    elif value["items"]["type"] == "object":
                        # Arreglo vacío, pero schema dice que debe ser de objetos
                        ordered_response[key] = [compare_and_add_fields(value["items"]["properties"], {})]
                    else:
                        # Arreglo vacío o con elementos simples (strings, etc.)
                        ordered_response[key] = value_in_response
                else:
                    # Tipo incorrecto (no lista), igual lo inicializa como corresponde
                    if value["items"]["type"] == "object":
                        ordered_response[key] = [compare_and_add_fields(value["items"]["properties"], {})]
                    else:
                        ordered_response[key] = []
            else:
                # Tipo simple (string, number...), copiar como viene
                ordered_response[key] = value_in_response

    return ordered_response

    
def remove_records(validated_response):     # Función para eliminar registros y modificar los objetos en 'creditos' 
    i = 1
    # Eliminar propiedades específicas
    keys_to_delete = [
        "claveOtorgante", "declaracionesConsumidor", "persona.numeroSeguridadSocial", 
        "persona.claveElectorIFE", "persona.numeroDependientes", "persona.fechaDefuncion"
    ]
    for key in keys_to_delete:
        keys = key.split(".")
        if len(keys) == 1:
            del validated_response[key]
        elif len(keys) == 2:
            del validated_response[keys[0]][keys[1]]
    # Eliminar propiedades en domicilios
    for item in validated_response.get("domicilios", []):
        del item["tipoAltaDomicilio"]
        del item["numeroOtorgantesCarga"]
        del item["numeroOtorgantesConsulta"]
        del item["idDomicilio"]
    # Modificar los objetos en 'creditos' y agregar 'secuenciaCredito' y 'calificacionCredito'
    for index, item in enumerate(validated_response.get("creditos", [])):
        del item["registroImpugnado"]
        del item["claveOtorgante"]
        del item["ultimaFechaSaldoCero"]
        del item["garantia"]
        del item["idDomicilio"]
        del item["servicios"]
        del item["CAN"]
        item["secuenciaCredito"] = i
        item["calificacionCredito"] = calculate_calificacion(item) 
        # Reordenar las propiedades, moviendo 'secuenciaCredito' y 'calificacionCredito' al principio
        keys = list(item.keys())
        reordered_keys = ["secuenciaCredito", "calificacionCredito"] + [key for key in keys if key not in ["secuenciaCredito", "calificacionCredito"]]
        # Reemplazar el objeto en la lista con el nuevo objeto reordenado
        validated_response["creditos"][index] = {key: item[key] for key in reordered_keys}
        i += 1 
    # Eliminar propiedades en consultas
    for item in validated_response.get("consultas", []):
        del item["idDomicilio"]
        del item["servicios"]
        del item["claveOtorgante"]
    return validated_response

def dataframes_simples(clientes_respuesta):
    single_values = []
    for json_data in clientes_respuesta:
        single_value_fields = {
        "folioConsulta": json_data["folioConsulta"],
        "folioConsultaOtorgante": json_data["folioConsultaOtorgante"]
        }
        single_values.append(single_value_fields)
    df_single = pd.DataFrame(single_values)
    persona_values = []
    for json_data in clientes_respuesta:
        persona = json_data["persona"]
        persona_values.append(persona)
    df_persona = pd.DataFrame(persona_values)
    df_persona.insert(0, "persona", '')
    df_persona['fechaNacimiento'] = pd.to_datetime(df_persona['fechaNacimiento']).dt.date
    hoy = date.today()  
    df_persona['edad'] = df_persona['fechaNacimiento'].apply(lambda x: hoy.year - x.year - ((hoy.month, hoy.day) < (x.month, x.day)))
    col = df_persona.pop('edad')  
    df_persona.insert(8, 'edad', col)
    pld = []
    for json_data in clientes_respuesta:
        pld_c = json_data["pldCheck"]
        pld.append(pld_c)
    df_pldcheck = pd.DataFrame(pld)  
    df_pldcheck.insert(0, "pldCheck", '')
    return df_single,df_persona,df_pldcheck

def pld_check(validated_response):  # Función para llenar PLDCHECK
    pld_check = {}
    # Buscar el mensaje con tipoMensaje "3" y extraer el tipoMensaje y leyenda
    pld_check = {
        "consecutivo": next((item["tipoMensaje"] for item in validated_response["mensajes"] if item["tipoMensaje"] == "3"), ""),
        "mensaje": next((item["leyenda"] for item in validated_response["mensajes"] if item["tipoMensaje"] == "3"), "")
    }
    # Agregar el objeto pldCheck al objeto validatedResponse
    validated_response["pldCheck"] = pld_check
    return validated_response

def resumen_por_producto(validated_response):       # Función para generar el resumen por producto
    resumen_por_producto = []
    # Agrupar créditos por tipo
    tipos_credito = list(set(credito["tipoCredito"] for credito in validated_response.get("creditos", [])))
    tipos_credito = [tipo for tipo in tipos_credito if tipo is not None]
    for tipo in tipos_credito:
        creditos_tipo = [credito for credito in validated_response.get("creditos", []) if credito["tipoCredito"] == tipo]
        resumen = {
            "producto": variables.constants["tipoCredito"].get(tipo, "Desconocido"),
            "cuentas": len(creditos_tipo),
            "limite": sum(credito.get("limiteCredito", 0) if credito.get("limiteCredito") is not None else 0 for credito in creditos_tipo),
            "aprobado": sum(credito.get("creditoMaximo", 0) if credito.get("creditoMaximo") is not None else 0 for credito in creditos_tipo),
            "actual": sum(credito.get("saldoActual", 0) if credito.get("saldoActual") is not None else 0 for credito in creditos_tipo),
            "vencido": sum(credito.get("saldoVencido", 0) if credito.get("saldoVencido") is not None else 0 for credito in creditos_tipo),
            "pagoSemanal": 0,
            "pagoQuincenal": 0,
            "pagoMensual": 0
        }
        # Calcular y asignar los valores de pago por periodo según la frecuencia de cada crédito
        for credito in creditos_tipo:
            monto_por_periodo = credito.get("montoPagar", 0)
            monto_por_periodo = float(monto_por_periodo) if monto_por_periodo is not None else 0.0
            if credito.get("frecuenciaPagos") == 'S':
                resumen["pagoSemanal"] += monto_por_periodo
            elif credito.get("frecuenciaPagos") == 'Q':
                resumen["pagoQuincenal"] += monto_por_periodo
            elif credito.get("frecuenciaPagos") == 'M':
                resumen["pagoMensual"] += monto_por_periodo
        resumen_por_producto.append(resumen)
    validated_response["resumenPorProducto"] = resumen_por_producto
    return validated_response
