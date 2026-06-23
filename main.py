import threading
from nicegui import ui
from config import *
from storage import *
import time

last_value = ""
scan_delay = 0.2

crear_tablas() # --- ASEGURA QUE LAS TABLAS BD EXISTAN ---
buffer = cargar_json()  # --- CARGA DATOS JSON ---

@ui.page('/')
def main():
    # --- CONTENEDOR PRINCIPAL ---
    with ui.column().classes('w-full items-center p-6'):
        # --- TARJETA DEL FORM ---
        with ui.card().classes('w-full max-w-2xl p-6 shadow-xl rounded-xl gap-6'):
            # --- HEADER ---
            ui.label('📦 Ingreso de Activos') \
                .classes('text-3xl font-bold text-center')

            # --- INPUTS DE ENTRADA ---
            with ui.row().classes('w-full items-end gap-3'):
                input_area = ui.input('Área') \
                    .props('outlined dense') \
                    .classes('w-32')

                input_activo = ui.input('Activo (QR)') \
                    .props('outlined dense') \
                    .classes('flex-grow')

                # --- AGREGA UN ACTIVO AL BUFFER ---
                def agregar():
                    area = input_area.value
                    activo = input_activo.value

                    # --- VALIDACION CAMPOS VACIOS ---
                    if not area or not activo:
                        ui.notify('Completa los campos', type='warning')
                        return

                    # --- SI EL AREA NO EXISTE EN MEMORIA, LA CREA ---
                    if area not in buffer:
                        buffer[area] = []

                    # CONTROL DUPLICADO
                    if activo in buffer[area]:
                        ui.notify('Duplicado', type='warning')
                        input_activo.set_value('')
                        return

                    # --- AGREGA EL ACTIVO AL BUFFER ---
                    buffer[area].append(activo)
                    guardar_json(buffer)

                    ui.notify('Agregado', type='positive')

                    input_activo.set_value('')
                    render()

                # --- LOGICA AUTOENTER ---
                def check_scanner():
                    nonlocal last_val_check
                    current = input_activo.value

                    # --- SI HAY TEXTO Y NO CAMBIO. EL SCANNER TERMINO ---
                    if current and current == last_val_check:
                        agregar()
                        last_val_check = ""
                    else:
                        last_val_check = current

                last_val_check = ""
                ui.timer(0.5, check_scanner)

                # --- PERMITE AGREGAR ACTIVO CON EVENTO ENTER ---
                input_activo.on('keydown.enter', agregar)

                # --- BTN AGREGAR ---
                ui.button('Agregar', on_click=agregar) \
                    .classes('bg-primary text-white px-4 h-10')

            # --- SEPARADOR VISUAL ---
            ui.separator()

            # --- TABLA ---
            tabla = ui.column().classes('w-full gap-4 max-h-[400px] overflow-y-auto pr-2')

            # --- RENDER DE LA TABLA ---
            def render():
                tabla.clear()

                # --- LABEL SI NO EXITEN DATOS AÚN ---
                if not buffer:
                    btn_subir.set_visibility(False)
                    with tabla:
                        ui.label('Sin datos aún...') \
                            .classes('text-gray-400 italic text-center')
                    return

                # --- SI EXISTEN DATOS, MUESTRA BTN PARA SUBIR DB ---
                btn_subir.set_visibility(True)

                # --- ITERA AREAS ---
                for area, activos in buffer.items():
                    with tabla:
                        # --- CARD POR AREAS ---
                        with ui.card().classes('p-4 border-l-4 border-primary shadow-sm rounded-lg'):

                            # --- HEADER DEL AREA ---
                            with ui.row().classes('justify-between items-center'):
                                ui.label(f'Área {area}') \
                                    .classes('text-lg font-bold')

                                ui.label(f'{len(activos)} activos') \
                                    .classes('text-sm text-gray-500')

                            ui.separator()

                            # LISTA ORDENADA (ÚLTIMO ARRIBA)
                            with ui.column().classes('gap-2 mt-2'):

                                for i, a in enumerate(reversed(activos), start=1):

                                    with ui.row().classes(
                                        'justify-between items-center px-3 py-2 bg-slate-50 rounded-lg border'
                                    ):
                                        ui.label(f'#{i}') \
                                            .classes('text-xs text-gray-400 w-6')

                                        ui.label(a) \
                                            .classes('font-mono text-sm')

                                        ui.icon('qr_code') \
                                            .classes('text-gray-400')

            # --- SUBIR A BD ---
            def subir_bd():
                total = 0
                duplicados = 0

                for area, activos in buffer.items():

                    for a in activos:

                        ok = insertar_activos(area, a)

                        if ok:
                            total += 1
                        else:
                            duplicados += 1

                # --- NOTIFICACION DE EXITO ---
                ui.notify(
                    f' {total} insertados | {duplicados} duplicados',
                    type='positive'
                )

                buffer.clear()        # --- LIMPIA MEMORIA ---
                guardar_json(buffer)  # --- GUARDA JSON VACIO ---

                render()

            # --- BTN SUBIR DB ---
            btn_subir = ui.button(
                'Subir a BD',
                on_click=subir_bd, icon='upload'
            ).classes('bg-green-600 text-white w-full py-3 text-lg')

            render()


ui.run(title='Activos', port=8083)