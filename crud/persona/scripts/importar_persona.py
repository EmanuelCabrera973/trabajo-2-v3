import csv 
import sys
from django.db import transaction
from django.core.exceptions import ValidationError
from persona.models import Persona

def run(*args):
    if not args:
        print("Error: proporcionar ruta del archivo")
        print("uso:./manage.py runscript importar_personas --script-args <ruta del archivo>")
        sys.exit(1)
        
    csv_file = args[0]
    
    oficinas_map ={oficina.nombre_corto: oficina for oficina in Oficina.objects.all()}
    try:
        with open(csv_file,'r', encoding = 'utf8') as f:
            reader = csv.DictReader(f)
            personas_a_crear =[]
            
            for row in reader:
                nombre = row.get('nombre')
                edad=row.get('edad')
                email=row.get('email')
                oficina=row.get('oficina_nombre_corto')
                
                if not nombre or not edad:
                    print(f"error en fila {row}, falta el nombre o la edad")
                    continue
                
                try:
                    edad_int = int(edad)
                except (ValueError,TypeError):
                    print(f"error en fila {row}, la edad no es un numero valido")
                    continue
                
                oficina_obj = None
                if oficina_nombre_corto:
                    oficina_obj=oficinas_map.get(oficina_nombre_corto)
                    if not oficina_obj:
                        print(f"Cuidado: No existe la oficina mencionada")
                        print(f"se creara el registro sin oficina")
                
                try:
                    persona = Persona(nombre=nombre,edad=edad,email=email,oficina=oficina_obj)
                    persona.full_clean()
                    personas_a_crear.append(persona)
                except ValidationError as e:
                    print(f"Error de validacion en fila {row}.detalle:{e}")
                except Exception as e:
                    print(f"error inesperado en fila {row}. detalle:{e}")
        with transaction.atomic():
            Persona.objects.bulk.create(personas_a_crear)
            print(f"se importaron {len(personas_a_crear)} registros") 
    
    except FileNotFoundError:
        print(f"Error no se encontro el el archivo {csv_file}")
    except:
        print(f"Ocurrio un erro inesperado en la importacion")   