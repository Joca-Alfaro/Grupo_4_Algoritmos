# Sistema de Gestión Académica Universitaria

Programa de consola en Python (solo librería estándar, **cero dependencias**) para administrar
estudiantes, profesores, cursos, inscripciones y calificaciones, con **guardado y carga de datos en JSON**.

## Requisitos

- Python 3.8 o superior (`python --version` para verificar).
- No requiere instalar nada con `pip`.

## Cómo ejecutarlo

Hay cuatro formas, de la más fácil a la más completa:

| Forma | Cómo | Requiere Python |
|-------|------|:---------------:|
| **Doble clic (Windows)** | Abrir `iniciar.bat` | Sí |
| **Terminal** | `python main.py` (Windows) o `python3 main.py` (Mac/Linux) | Sí |
| **Mac / Linux** | `sh iniciar.sh` | Sí |
| **Ejecutable `.exe`** | Abrir `SistemaAcademico.exe` (ver abajo cómo crearlo) | **No** |

Se recomienda usar la **terminal integrada** del editor (VS Code, PyCharm) o una terminal normal.

### Crear el ejecutable (.exe) en Windows

1. Instale Python desde <https://www.python.org/downloads/> marcando **"Add Python to PATH"**.
2. Haga doble clic en `crear_ejecutable.bat` (necesita internet para descargar PyInstaller).
3. Al terminar aparece `SistemaAcademico.exe` en la misma carpeta. Ya no necesita Python para abrirlo
   (puede copiarlo a otra computadora junto con la carpeta `datos`).

Notas:
- El `.exe` guarda y carga los datos en la carpeta `datos` que está **junto al `.exe`**.
- Es normal que el primer arranque tarde unos segundos.
- Windows SmartScreen o el antivirus pueden mostrar una advertencia con ejecutables recién creados que no
  están firmados. Es una falsa alarma común con PyInstaller; para presentar en clase, `iniciar.bat` evita
  el problema.
- Un `.exe` solo funciona en el sistema donde se creó: para Mac o Linux hay que ejecutar PyInstaller en ese
  sistema (`python3 -m PyInstaller --onefile --name SistemaAcademico main.py`).

## Antes de presentar: completar la carátula

Abra `config.py`, busque la sección **DATOS DE LA CARÁTULA** y reemplace cada marcador `[MOLDE]`
(universidad, curso, catedrático, fecha e integrantes con su carné). No hay que tocar nada más.

## Estructura del proyecto

```
sistema_academico/
├── main.py                  Punto de entrada: carátula, arranque, bucle del menú y salida
├── config.py                Constantes: rutas, notas, ponderaciones y datos de la carátula
├── excepciones.py           ErrorGestion, ErrorPersistencia y OperacionCancelada
├── iniciar.bat              Lanzador de doble clic para Windows
├── iniciar.sh               Lanzador para Mac / Linux
├── crear_ejecutable.bat     Crea SistemaAcademico.exe (Windows, con PyInstaller)
│
├── modelos/                 Clases del dominio (cada una sabe convertirse a/desde JSON)
│   ├── estudiante.py        Estudiante (carné, nombre, correo)
│   ├── profesor.py          Profesor (ID, nombre, especialidad)
│   ├── curso.py             Curso (código, nombre, créditos, profesor, prerrequisito)
│   └── inscripcion.py       Inscripcion: notas, promedio ponderado y estado académico
│
├── servicios/               Lógica de negocio (sin imprimir ni leer de consola)
│   ├── sistema_gestion.py   SistemaGestion: reglas, validaciones y consultas
│   ├── persistencia.py      Guardar y cargar JSON (escritura atómica y carga validada)
│   └── datos_prueba.py      Datos de ejemplo precargados
│
├── interfaz/                Todo lo que se ve en pantalla
│   ├── caratula.py          Encabezado inicial
│   ├── menu.py              Definición del menú (los números se asignan solos)
│   ├── selectores.py        Listas numeradas para elegir estudiante, curso, profesor...
│   ├── presentacion.py      Encabezados, formato de notas y resumen de datos
│   ├── opciones_estudiantes.py      Registrar, consultar, modificar y eliminar estudiantes
│   ├── opciones_profesores.py       Registrar, consultar, modificar y eliminar profesores
│   ├── opciones_cursos.py           Registrar, consultar, modificar, eliminar y asignar profesor
│   ├── opciones_inscripciones.py    Inscribir, retirar, registrar y eliminar calificaciones
│   ├── opciones_reportes.py         Los tres reportes de consulta
│   └── opciones_datos.py            Guardar/cargar JSON y datos de prueba
│
├── utilidades/
│   ├── consola.py           input_validado (con 'cancelar'), confirmar, pedir_id, pedir_id_nuevo...
│   └── validadores.py       Validación de correo y de campos leídos desde JSON
│
├── datos/
│   └── ejemplo_datos_prueba.json    Ejemplo de archivo (cárguelo con la opción 22 del menú)
│
└── tests/
    ├── test_sistema.py              33 pruebas: reglas, notas, entrada validada y JSON
    └── test_modificar_eliminar.py   53 pruebas: modificar, eliminar, listas, 'cancelar' y flujos
```

**Idea de diseño:** las capas están separadas por responsabilidad. `modelos` guarda datos,
`servicios` aplica las reglas, `interfaz` habla con el usuario y `main.py` solo coordina.
Por eso la lógica se puede probar sin consola.

## Menú

| Opción | Acción |
|-------:|--------|
| 1 / 2 / 3 / 4 | Estudiantes: registrar / consultar / **modificar** / **eliminar** |
| 5 / 6 / 7 / 8 | Profesores: registrar / consultar / **modificar** / **eliminar** |
| 9 / 10 / 11 / 12 | Cursos: registrar / consultar / **modificar** / **eliminar** |
| 13 | Asignar profesor responsable a un curso |
| 14 | Inscribir estudiante en un curso |
| 15 | **Retirar** estudiante de un curso |
| 16 | Registrar o modificar calificación |
| 17 | **Eliminar** calificación |
| 18 | Cursos inscritos de un estudiante |
| 19 | Estudiantes inscritos en un curso |
| 20 | Historial académico detallado |
| **21** | **Guardar datos en archivo JSON** |
| **22** | **Cargar datos desde archivo JSON** |
| 23 | Cargar datos de prueba |
| 0 | Salir |

Los números se asignan automáticamente en `interfaz/menu.py`; si se agrega una opción, el menú
se renumera solo.

## Elegir de listas, en lugar de escribir códigos

Ya no hay que memorizar carnés, IDs ni códigos. Cada vez que una operación necesita un estudiante,
profesor o curso, el programa muestra una **lista numerada** y solo se escribe el número:

```
  Seleccione el estudiante a modificar:
     1. [0906264094] Marvin Gonzalez - mgonzalezd16@miumg.edu.gt
     2. [2024002] Luis Pérez - luis.perez@correo.com

Número (1-2) o 'cancelar':
```

- Al **calificar, retirar o eliminar notas** solo aparecen los cursos en los que ese estudiante ya
  está inscrito (con su estado: `EN CURSO`, `APRUEBA`...).
- Al **inscribir**, la lista marca `<- YA INSCRITO` y `<- requiere aprobar XXX` para orientar. Las
  validaciones reales (duplicado y prerrequisito) se siguen aplicando igual.
- Al **registrar un curso**, el prerrequisito se elige de la lista (la opción `0` es "Sin prerrequisito").
- Solo al **registrar** algo nuevo se escribe el identificador (carné, ID o código). Si ya existe,
  el programa lo avisa y vuelve a preguntar sin perder lo que se iba haciendo.

## Cancelar una operación

En **cualquier pregunta** se puede escribir `cancelar` (mayúsculas o minúsculas) para abandonar y volver
al menú principal. Las operaciones piden primero todos los datos y solo al final los aplican, así que
cancelar **nunca deja un registro a medias**. También funciona en las listas y en las preguntas de
confirmación (s/n). En el menú principal no aplica (ahí se elige un número o `0` para salir).

## Modificar

- **Estudiante:** nombre y correo. **Profesor:** nombre y especialidad.
  **Curso:** nombre, créditos, prerrequisito y profesor.
- Se muestran los valores actuales; con **ENTER** se conserva cada uno.
- El carné, el ID y el código **no se modifican**, porque otros registros (inscripciones, notas, cursos)
  se enlazan con ellos. Si uno se escribió mal, se elimina el registro y se crea de nuevo.
- Al cambiar el prerrequisito de un curso, la lista solo ofrece cursos que no formen un **ciclo**
  (por ejemplo, A exige B y B exige A).
- Los cambios de prerrequisito no afectan a inscripciones ya hechas: el prerrequisito se valida al inscribir.

## Eliminar (siempre con confirmación)

| Se elimina | Qué ocurre con lo relacionado |
|------------|-------------------------------|
| **Estudiante** | Se borran también sus inscripciones y notas (se muestra cuántas antes de confirmar). |
| **Profesor** | Sus cursos quedan **"Sin asignar"** (se listan antes de confirmar). |
| **Curso** | Se borran sus inscripciones y notas. **Si es prerrequisito de otro curso, no se permite**: primero hay que modificar esos cursos. |
| **Inscripción** (opción 15) | Se borran sus notas; el estudiante podrá inscribirse de nuevo. |
| **Calificación** (opción 17) | Esa evaluación queda sin nota y el promedio y estado se recalculan. |

Recuerde usar la opción 21 para guardar los cambios en el JSON (el programa también pregunta al salir).

## Guardar y cargar datos (JSON)

- **Archivo por defecto:** `datos/academico.json`. Con solo presionar ENTER se usa ese archivo.
- **Otro archivo:** escriba solo un nombre (ej. `semestre1`) y se guarda en `datos/semestre1.json`,
  o escriba una ruta completa.
- **Al iniciar:** si existe `datos/academico.json`, el programa ofrece cargarlo.
- **Al salir:** si hay cambios sin guardar, pregunta si desea guardarlos.
- **Seguridad al guardar:** se escribe primero un archivo temporal y luego reemplaza al definitivo,
  así que un corte a mitad del guardado no daña el archivo anterior.
- **Seguridad al cargar:** el archivo se valida completo (formato JSON, campos, tipos, IDs duplicados,
  notas en rango, referencias a estudiantes/cursos/profesores existentes y ciclos de prerrequisitos)
  **antes** de reemplazar los datos en memoria. Un archivo dañado muestra un mensaje claro y no
  altera nada.

Formato del archivo (resumido):

```json
{
    "version_formato": 1,
    "fecha_guardado": "2026-10-10T08:04:55",
    "estudiantes":   [{"carne": "2024001", "nombre": "Ana García", "correo": "ana.garcia@correo.com"}],
    "profesores":    [{"id_profesor": "P001", "nombre": "Dr. Carlos Méndez", "especialidad": "Ingeniería de Software"}],
    "cursos":        [{"codigo": "MAT201", "nombre": "Matemática II", "creditos": 5, "id_profesor": "P002", "prerrequisito": "MAT101"}],
    "inscripciones": [{"carne": "2024001", "codigo_curso": "MAT101", "notas": {"Parcial 1": 85.0, "Examen Final": 92.0}}]
}
```

## Reglas académicas (editables en `config.py`)

- Escala de notas: **0 a 100**. Se rechazan letras, valores vacíos, `nan`, `inf` y fuera de rango.
  Para decimales se acepta punto o coma (`85.5` o `85,5`).
- Evaluaciones: Parcial 1 (20 %), Parcial 2 (20 %), Proyecto (20 %), Examen Final (40 %).
- Promedio ponderado. Con evaluaciones incompletas el estado es **EN CURSO** (promedio parcial);
  con todas registradas: **APRUEBA** si el promedio es ≥ 61, **REPRUEBA** si es < 61.
- No se puede inscribir dos veces al mismo estudiante en el mismo curso.
- No se puede inscribir un curso si el prerrequisito no está **aprobado** (con todas sus notas).

## Casos para probar rápido (con los datos de prueba)

- Inscribir a Luis `2024002` en `MAT201` → falla (reprobó `MAT101`).
- Inscribir a Ana `2024001` en `PRG201` → funciona.
- Inscribir otra vez a Ana en `MAT101` → falla (duplicado).
- Registrar la nota `150` o `abc` → vuelve a pedirla.
- Opción 3 (modificar estudiante): corregir un nombre mal escrito y dejar el correo con ENTER.
- Opción 1 y escribir `cancelar` antes de terminar → regresa al menú y no queda registrado nada.
- Opción 12 (eliminar curso) sobre `MAT101` → no se permite: es prerrequisito de `MAT201`.
- Opción 4 (eliminar estudiante) sobre Ana → avisa que se borrarán sus 3 inscripciones y pide confirmación.
- Opción 21 para guardar y, tras reiniciar, aceptar cargar el archivo.

## Pruebas automatizadas

```bash
python -m unittest discover -v
```

86 pruebas. Verifican duplicados, prerrequisitos, rango de notas, promedio y estado, `input_validado`,
el guardado/carga JSON (incluyendo archivos corruptos, referencias rotas y ciclos de prerrequisitos),
y las funciones de modificar, eliminar (con sus cascadas y bloqueos), listas numeradas y `cancelar`,
incluyendo flujos completos que simulan lo que escribe el usuario.
