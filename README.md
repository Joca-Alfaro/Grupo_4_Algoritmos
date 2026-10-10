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
├── excepciones.py           ErrorGestion y ErrorPersistencia
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
│   ├── menu.py              Definición y dibujo del menú
│   └── opciones.py          Una función por cada opción del menú
│
├── utilidades/
│   ├── consola.py           input_validado, confirmar, pedir_id, limpiar_pantalla, pausar
│   └── validadores.py       Validación de correo y de campos leídos desde JSON
│
├── datos/
│   └── ejemplo_datos_prueba.json    Ejemplo de archivo (cárguelo con la opción 14)
│
└── tests/
    └── test_sistema.py      33 pruebas automatizadas (unittest)
```

**Idea de diseño:** las capas están separadas por responsabilidad. `modelos` guarda datos,
`servicios` aplica las reglas, `interfaz` habla con el usuario y `main.py` solo coordina.
Por eso la lógica se puede probar sin consola.

## Menú

| Opción | Acción |
|-------:|--------|
| 1 / 2 | Registrar / consultar estudiantes |
| 3 / 4 | Registrar / consultar profesores |
| 5 / 6 | Registrar / consultar cursos (con prerrequisito opcional) |
| 7 | Asignar profesor responsable a un curso |
| 8 | Inscribir estudiante en un curso |
| 9 | Registrar o modificar calificación |
| 10 | Cursos inscritos de un estudiante |
| 11 | Estudiantes inscritos en un curso |
| 12 | Historial académico detallado |
| **13** | **Guardar datos en archivo JSON** |
| **14** | **Cargar datos desde archivo JSON** |
| 15 | Cargar datos de prueba |
| 0 | Salir |

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
- Opción 13 para guardar y, tras reiniciar, aceptar cargar el archivo.

## Pruebas automatizadas

```bash
python -m unittest discover -v
```

Verifican duplicados, prerrequisitos, rango de notas, promedio y estado, `input_validado`, y el
guardado/carga JSON (incluyendo archivos corruptos, referencias rotas y ciclos de prerrequisitos).
