# Cuarto Trabajo Practico de Simulación

## Tema

Modelos de Simulación Dinámicos

## Integrantes

| Apellido | Nombre | Legajo | Mail |
| --- | --- | --- | --- |
| Vera | Geronimo | 89785 | gveranovillo@gmail.com |
| Sanchez | Luciano Enrique | 89734 | lucianoensan@gmail.com |
| Stura Murua | Fermin | 82336 | fermin.stura00@gmail.com |
| Canaan | Abigail Sara | 85860 | abigailcanaan@gmail.com |
| Delgado | Heber Alex | 89102 | heberdelgado55@gmail.com |
| Cortez | Eduardo Cesar | 89796 | cortezeduardocesar@gmail.com |
| Nass | Franco David | 88534 | david111.2nass@gmail.com |
| Piaggio | Uriel Agustin | 87599 | piaggiouriel@gmail.com |

## Instalación y ejecución del proyecto

1. Clonar el repositorio

```
git clone git@github.com:UrielPiaggio/SIMULACION_TP4.git
```

2. Navegar a la carpeta de backend

```
cd TPI\ SIM\ 2.0/backend/
```

3. Crear el entorno de Python

```
python -m venv venv
source /venv/Scripts/activate
```

O también

```
python -m venv venv
.\venv\Scripts\activate
```

4. Instalar dependencias

```
pip install -r requirements.txt
```

5. Levantar el servidor de backend

```
uvicorn main:app --reload
```