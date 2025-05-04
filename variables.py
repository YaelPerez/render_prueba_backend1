import logging

#Variables del FRONT
archivo_label = None ; archivo_icon = None ; consultar = None 
error_message_label = None ; mensaje_exito = None ; clientes = None 
private_key = None

#dimension de las secciones segun la documentacion
dimensiones_secciones = {'folioConsulta' : 1,
                         'folioConsultaOtorgante' : 1,
                         'persona' : 13,
                         'scores' : 4,
                         "mensajes" : 2,
                         "pldCheck" : 3,                #a partir de la documentación
                         "domicilios" : 11,
                         "empleos" : 16,
                         "resumenPorProducto" : 9,
                         "creditos" : 33,
                         "consultas" : 11}

#Secciones a tratar
secciones = ["resumenPorProducto","domicilios","mensajes","empleos","consultas","creditos","scores"]

# Configuración del logger
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s %(name)s %(filename)s:%(lineno)d - %(message)s')
log = logging.getLogger()

#Constantes para la validación del tipo de credito - MODIDFICACION
constants = {
    "tipoCredito": {
        "AA": "Arrendamiento Automotriz",
        "AB": "Automotriz Bancario",
        "AE": "Física Actividad Empresarial",
        "AM": "Aparatos/Muebles",
        "AR": "Arrendamiento",
        "AV": "Aviación",
        "BC": "Banca Comunal",
        "BL": "Bote/Lancha",
        "BR": "Bienes Raíces",
        "CA": "Compra De Automóvil",
        "CC": "Crédito Al Consumo",
        "CF": "Crédito Fiscal",
        "CO": "Consolidación",
        "CP": "Crédito Personal Al Consumo",
        "ED": "Editorial",
        "EQ": "Equipo",
        "FF": "Fondeo Fira",
        "FI": "Fianza",
        "FT": "Factoraje",
        "GS": "Grupo Solidario",
        "HB": "Hipotecario Bancario",
        "HE": "Préstamo Tipo Home Equity",
        "HV": "Hipotecario o Vivienda",
        "LC": "Línea de Crédito",
        "MC": "Mejoras a la Casa",
        "NG": "Préstamo No Garantizado",
        "PB": "Préstamo Personal Bancario",
        "PC": "Procampo",
        "PE": "Préstamo Para Estudiante",
        "PG": "Préstamo Garantizado",
        "PQ": "Préstamo Quirografario",
        "PM": "Préstamo Empresarial",
        "PN": "Préstamo de Nómina",
        "PP": "Préstamo Personal",
        "SH": "Segunda Hipoteca",
        "TC": "Tarjeta De Crédito",
        "TD": "Tarjeta Departamental",
        "TG": "Tarjeta Garantizada",
        "TS": "Tarjeta De Servicios",
        "VR": "Vehículo Recreativo",
        "OT": "Otros",
        "NC": "Desconocido"
    }
}

#Esquema de la respuesta de la API - MODIDFICACION
schema = {
    "folioConsulta": {"type": "string"},
    "folioConsultaOtorgante": {"type": "string"},
    "claveOtorgante": {"type": "string"},
    "declaracionesConsumidor": {"type": "string"},
    "persona": {
        "type": "object",
        "properties": {
            "apellidoPaterno": {"type": "string"},
            "apellidoMaterno": {"type": "string"},
            "apellidoAdicional": {"type": "string"},
            "nombres": {"type": "string"},
            "fechaNacimiento": {"type": "string"},
            "RFC": {"type": "string"},
            "CURP": {"type": "string"},
            "numeroSeguridadSocial": {"type": "string"},
            "nacionalidad": {"type": "string"},
            "residencia": {"type": "number"},
            "estadoCivil": {"type": "string"},
            "sexo": {"type": "string"},
            "claveElectorIFE": {"type": "string"},
            "numeroDependientes": {"type": "number"},
            "fechaDefuncion": {"type": "string"}
        }
    },
    "scores": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "nombreScore": {"type": "string"},
                "valor": {"type": "number"},
                "razones": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }
    },
    "mensajes": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "tipoMensaje": {"type": "number"},
                "leyenda": {"type": "string"}
            }
        }
    },
    "domicilios": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "direccion": {"type": "string"},
                "coloniaPoblacion": {"type": "string"},
                "delegacionMunicipio": {"type": "string"},
                "ciudad": {"type": "string"},
                "estado": {"type": "string"},
                "CP": {"type": "string"},
                "fechaResidencia": {"type": "string"},
                "numeroTelefono": {"type": "string"},
                "tipoDomicilio": {"type": "string"},
                "tipoAsentamiento": {"type": "string"},
                "fechaRegistroDomicilio": {"type": "string"},
                "tipoAltaDomicilio": {"type": "number"},
                "numeroOtorgantesCarga": {"type": "number"},
                "numeroOtorgantesConsulta": {"type": "number"},
                "idDomicilio": {"type": "string"}
            }
        }
    },
    "empleos": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "nombreEmpresa": {"type": "string"},
                "direccion": {"type": "string"},
                "coloniaPoblacion": {"type": "string"},
                "delegacionMunicipio": {"type": "string"},
                "ciudad": {"type": "string"},
                "estado": {"type": "string"},
                "CP": {"type": "string"},
                "numeroTelefono": {"type": "string"},
                "extension": {"type": "string"},
                "fax": {"type": "string"},
                "puesto": {"type": "string"},
                "fechaContratacion": {"type": "string"},
                "claveMoneda": {"type": "string"},
                "salarioMensual": {"type": "number"},
                "fechaUltimoDiaEmpleo": {"type": "string"},
                "fechaVerificacionEmpleo": {"type": "string"}
            }
        }
    },
    "creditos": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "secuenciaCredito": {"type": "number"},
                "calificacionCredito": {"type": "string"},
                "fechaActualizacion": {"type": "string"},
                "registroImpugnado": {"type": "number"},
                "claveOtorgante": {"type": "string"},
                "nombreOtorgante": {"type": "string"},
                "cuentaActual": {"type": "string"},
                "tipoResponsabilidad": {"type": "string"},
                "tipoCuenta": {"type": "string"},
                "tipoCredito": {"type": "number"},
                "claveUnidadMonetaria": {"type": "string"},
                "valorActivoValuacion": {"type": "number"},
                "numeroPagos": {"type": "number"},
                "frecuenciaPagos": {"type": "string"},
                "montoPagar": {"type": "number"},
                "fechaAperturaCuenta": {"type": "string"},
                "fechaUltimoPago": {"type": "string"},
                "fechaUltimaCompra": {"type": "string"},
                "fechaCierreCuenta": {"type": "string"},
                "fechaReporte": {"type": "string"},
                "ultimaFechaSaldoCero": {"type": "string"},
                "garantia": {"type": "string"},
                "creditoMaximo": {"type": "number"},
                "saldoActual": {"type": "number"},
                "limiteCredito": {"type": "number"},
                "saldoVencido": {"type": "number"},
                "numeroPagosVencidos": {"type": "number"},
                "pagoActual": {"type": "string"},
                "historicoPagos": {"type": "string"},
                "fechaRecienteHistoricoPagos": {"type": "string"},
                "fechaAntiguaHistoricoPagos": {"type": "string"},
                "clavePrevencion": {"type": "string"},
                "totalPagosReportados": {"type": "number"},
                "peorAtraso": {"type": "number"},
                "fechaPeorAtraso": {"type": "string"},
                "saldoVencidoPeorAtraso": {"type": "number"},
                "montoUltimoPago": {"type": "number"},
                "idDomicilio": {"type": "string"},
                "servicios": {"type": "string"},
                "CAN": {
                    "type": "object",
                    "properties": {
                        "identificadorCAN": {"type": "string"},
                        "prelacionOrigen": {"type": "number"},
                        "prelacionActual": {"type": "number"},
                        "fechaAperturaCAN": {"type": "string"},
                        "fechaCancelacionCAN": {"type": "string"},
                        "historicoCAN": {"type": "string"},
                        "fechaMRCAN": {"type": "string"},
                        "fechaMACAN": {"type": "string"}
                    }
                }
            }
        }
    },
    "consultas": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "fechaConsulta": {"type": "string"},
                "claveOtorgante": {"type": "string"},
                "nombreOtorgante": {"type": "string"},
                "direccionOtorgante": {"type": "string"},
                "telefonoOtorgante": {"type": "string"},
                "tipoCredito": {"type": "string"},
                "claveUnidadMonetaria": {"type": "string"},
                "importeCredito": {"type": "number"},
                "tipoResponsabilidad": {"type": "string"},
                "idDomicilio": {"type": "string"},
                "servicios": {"type": "string"}
            }
        }
    }
}

estados_claves = {
    "AGUASCALIENTES": "AGS",
    "BAJA CALIFORNIA": "BC",
    "BAJA CALIFORNIA SUR": "BCS",
    "CAMPECHE": "CAMP",
    "CHIAPAS": "CHIS",
    "CHIHUAHUA": "CHIH",
    "DISTRITO FEDERAL": "DF",
    "COAHUILA": "COAH",
    "COLIMA": "COL",
    "DURANGO": "DGO",
    "ESTADO DE MEXICO": "MEX",
    "GUANAJUATO": "GTO",
    "GUERRERO": "GRO",
    "HIDALGO": "HGO",
    "JALISCO": "JAL",
    "MICHOACAN": "MICH",
    "MORELOS": "MOR",
    "NAYARIT": "NAY",
    "NUEVO LEON": "NL",
    "OAXACA": "OAX",
    "PUEBLA": "PUE",
    "QUERETARO": "QRO",
    "QUINTANA ROO": "QROO",
    "SAN LUIS POTOSI": "SLP",
    "SINALOA": "SIN",
    "SONORA": "SON",
    "TABASCO": "TAB",
    "TAMAULIPAS": "TAMP",
    "TLAXCALA": "TLAX",
    "VERACRUZ": "VER",
    "YUCATAN": "YUC",
    "ZACATECAS": "ZAC"
}