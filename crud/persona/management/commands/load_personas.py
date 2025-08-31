import os
import csv
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import transaction
from persona.models import Persona  # Ajusta el import según el nombre real de tu app


class Command(BaseCommand):
    help = 'Carga masiva de Personas desde un archivo CSV.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file', '-f',
            type=str,
            required=True,
            help='Ruta al archivo CSV de entrada. Debe tener columnas: nombre, edad, email.'
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Si se encuentra un email existente, actualiza los campos en lugar de omitir.'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo valida el archivo sin guardar nada en la base de datos.'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=500,
            help='Número de instancias a crear por lote en bulk_create (por defecto: 500).'
        )
        parser.add_argument(
            '--encoding',
            type=str,
            default='utf-8',
            help='Codificación del archivo CSV (por defecto: utf-8).'
        )
        parser.add_argument(
            '--error-log',
            type=str,
            help='Ruta de un CSV donde registrar filas con errores. Si no se provee, solo se muestran en consola.'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        do_update = options['update']
        dry_run = options['dry_run']
        batch_size = options['batch_size']
        encoding = options['encoding']
        error_log_path = options.get('error_log')

        # Verificar existencia del archivo
        if not os.path.isfile(file_path):
            raise CommandError(f"El archivo '{file_path}' no existe o no es accesible.")

        # Preparar registro de errores si se pide
        error_writer = None
        if error_log_path:
            # Intentar abrir en modo escritura; si hay error, abortar
            try:
                ef = open(error_log_path, mode='w', newline='', encoding='utf-8')
            except Exception as e:
                raise CommandError(f"No se pudo abrir para escribir el error-log en '{error_log_path}': {e}")
            error_writer = csv.writer(ef)
            # Cabecera de CSV de errores
            error_writer.writerow(['fila', 'campo', 'valor', 'mensajes'])
            self.stdout.write(f"Registrando errores en: {error_log_path}")

        created = 0
        updated = 0
        skipped = 0
        errores_detallados = []
        personas_para_crear = []
        emails_vistos = set()

        # Abrir y leer CSV
        with open(file_path, newline='', encoding=encoding) as csvfile:
            reader = csv.DictReader(csvfile)
            # Validar que existan las columnas requeridas
            expected_fields = {'nombre', 'edad', 'email'}
            if not expected_fields.issubset(set(reader.fieldnames or [])):
                raise CommandError(
                    f"El CSV debe tener las columnas: {', '.join(expected_fields)}. "
                    f"Columnas encontradas: {reader.fieldnames}"
                )

            for fila_num, row in enumerate(reader, start=2):
                nombre = (row.get('nombre') or '').strip()
                edad_str = (row.get('edad') or '').strip()
                email = (row.get('email') or '').strip()
                row_errors = []

                # Validar nombre
                if not nombre:
                    row_errors.append(('nombre', nombre, 'Nombre vacío'))

                # Validar edad
                if not edad_str:
                    row_errors.append(('edad', edad_str, 'Edad vacía'))
                else:
                    try:
                        edad = int(edad_str)
                        if edad < 0:
                            row_errors.append(('edad', edad_str, 'Edad negativa'))
                    except ValueError:
                        row_errors.append(('edad', edad_str, 'Edad no es un entero válido'))

                # Validar email
                if not email:
                    row_errors.append(('email', email, 'Email vacío'))
                else:
                    try:
                        validate_email(email)
                    except ValidationError:
                        row_errors.append(('email', email, 'Email inválido'))

                # Chequear duplicados en el mismo archivo
                if email:
                    if email in emails_vistos:
                        row_errors.append(('email', email, 'Email duplicado en archivo'))
                # Si hay errores básicos, registrar y saltar
                if row_errors:
                    skipped += 1
                    for campo, valor, msg in row_errors:
                        errores_detallados.append({'fila': fila_num, 'campo': campo, 'valor': valor, 'mensajes': msg})
                        if error_writer:
                            error_writer.writerow([fila_num, campo, valor, msg])
                    continue

                # Marcar email visto
                emails_vistos.add(email)

                # Convertir edad a entero (ya validado)
                edad = int(edad_str)

                # Si se pide actualizar y existe
                if do_update:
                    qs = Persona.objects.filter(email=email)
                    if qs.exists():
                        persona = qs.first()
                        cambios = {}
                        if persona.nombre != nombre:
                            cambios['nombre'] = (persona.nombre, nombre)
                            persona.nombre = nombre
                        if persona.edad != edad:
                            cambios['edad'] = (persona.edad, edad)
                            persona.edad = edad
                        # email no cambia pues es clave de búsqueda aquí
                        if cambios:
                            try:
                                # Validar instancias antes de guardar
                                persona.full_clean()
                                if not dry_run:
                                    persona.save()
                                updated += 1
                                self.stdout.write(f"Fila {fila_num}: actualizado Persona email={email}. Cambios: {cambios}")
                            except ValidationError as e:
                                msg = "; ".join(f"{k}: {v}" for k, v in e.message_dict.items())
                                errores_detallados.append({'fila': fila_num, 'campo': 'validación', 'valor': str(row), 'mensajes': msg})
                                skipped += 1
                                if error_writer:
                                    error_writer.writerow([fila_num, 'validación', str(row), msg])
                        else:
                            # No hubo cambios
                            self.stdout.write(f"Fila {fila_num}: Persona con email={email} ya existe y no requiere actualización.")
                        # Saltar creación
                        continue

                # Preparar nueva instancia
                instancia = Persona(nombre=nombre, edad=edad, email=email)
                try:
                    instancia.full_clean()
                except ValidationError as e:
                    # Registrar error de validación de modelo
                    mensajes = []
                    for campo, msgs in e.message_dict.items():
                        for m in msgs:
                            mensajes.append(f"{campo}: {m}")
                            errores_detallados.append({'fila': fila_num, 'campo': campo, 'valor': row.get(campo), 'mensajes': m})
                            if error_writer:
                                error_writer.writerow([fila_num, campo, row.get(campo), m])
                    skipped += 1
                    continue

                # Añadir para bulk_create
                personas_para_crear.append(instancia)

                # Si alcanzamos batch_size, hacemos bulk_create
                if len(personas_para_crear) >= batch_size:
                    if not dry_run:
                        try:
                            with transaction.atomic():
                                Persona.objects.bulk_create(personas_para_crear)
                        except Exception as be:
                            # Si bulk falla, registrar cada uno por separado
                            for idx, inst in enumerate(personas_para_crear, start=fila_num - len(personas_para_crear) + 1):
                                try:
                                    inst.full_clean()
                                    inst.save()
                                    created += 1
                                except Exception as e_single:
                                    msg = str(e_single)
                                    errores_detallados.append({'fila': idx, 'campo': 'bulk -> individual', 'valor': str(inst), 'mensajes': msg})
                                    skipped += 1
                                    if error_writer:
                                        error_writer.writerow([idx, 'bulk->individual', str(inst), msg])
                            personas_para_crear = []
                            continue
                    created += len(personas_para_crear)
                    self.stdout.write(f"Se crearon {len(personas_para_crear)} instancias (batch).")
                    personas_para_crear = []

        # Fin de lectura: crear lo que quede en la lista
        if personas_para_crear:
            if not dry_run:
                try:
                    with transaction.atomic():
                        Persona.objects.bulk_create(personas_para_crear)
                except Exception:
                    # Intentar guardar uno a uno si falla
                    for idx, inst in enumerate(personas_para_crear, start=1):
                        try:
                            inst.full_clean()
                            inst.save()
                            created += 1
                        except Exception as e_single:
                            fila_estimada = 'desconocida'
                            msg = str(e_single)
                            errores_detallados.append({'fila': fila_estimada, 'campo': 'bulk-final->individual', 'valor': str(inst), 'mensajes': msg})
                            skipped += 1
                            if error_writer:
                                error_writer.writerow([fila_estimada, 'bulk-final->individual', str(inst), msg])
                    personas_para_crear = []
                else:
                    created += len(personas_para_crear)
                    self.stdout.write(f"Se crearon {len(personas_para_crear)} instancias (batch final).")
            else:
                # dry-run: solo contamos
                created += len(personas_para_crear)
            personas_para_crear = []

        # Cerrar archivo de errores si aplica
        if error_writer:
            ef.close()

        # Mostrar resumen
        self.stdout.write(self.style.SUCCESS(
            f"Resumen de carga masiva: creadas={created}, actualizadas={updated}, omitidas={skipped}."
        ))
        if errores_detallados and not error_log_path:
            self.stdout.write("Errores detallados (solo los primeros 20):")
            for err in errores_detallados[:20]:
                self.stdout.write(
                    f"  Fila {err['fila']}: campo={err['campo']}, valor={err['valor']}, mensaje={err['mensajes']}"
                )
            if len(errores_detallados) > 20:
                self.stdout.write(f"  ... y {len(errores_detallados) - 20} errores más. Usa --error-log para guardarlos en un CSV.")
