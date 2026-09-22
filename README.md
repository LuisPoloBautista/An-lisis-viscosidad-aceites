# Análisis de viscosidad de aceites

Aplicación web desarrollada con Flask para consultar datos de viscosidad, interpolar mediciones a 40 °C y 100 °C y visualizar los resultados mediante tablas y gráficas.

## Requisitos

- Python 3.10 o superior
- `pip`

## Instalación

```bash
git clone https://github.com/LuisPoloBautista/An-lisis-viscosidad-aceites.git
cd An-lisis-viscosidad-aceites
python -m venv .venv
```

En Windows:

```powershell
.venv\Scripts\Activate.ps1
```

En Linux o macOS:

```bash
source .venv/bin/activate
```

Instala las dependencias y ejecuta la aplicación:

```bash
pip install -r requirements.txt
python app.py
```

Después abre http://127.0.0.1:5000 en el navegador.

## Datos

El archivo `viscosity_data.xlsx` contiene las tablas de referencia de las copas Ford utilizadas por la aplicación.