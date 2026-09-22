import matplotlib
matplotlib.use('Agg')  # Use the Agg backend for non-interactive plotting

from flask import Flask, render_template, request, jsonify, session
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Ruta para guardar la imagen de la gráfica
GRAPH_PATH = "static/graph.png"
GRAPH_PATH2 = "static/graph2.png"

@app.route('/')
def index():
    return render_template('index.html')

# Cálculo de viscosidades y generación de gráfica
@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        visco_40 = float(request.form['visco_40'])
        visco_100 = float(request.form['visco_100'])

        # Cálculo del +10% y -10% de viscosidades
        plus_10_40 = round(visco_40 * 1.1, 2)
        minus_10_40 = round(visco_40 * 0.9, 2)
        plus_10_100 = round(visco_100 * 1.2, 2)
        minus_10_100 = round(visco_100 * 0.8, 2)

        # Generación de la tabla de interpolación
        temperaturas = np.arange(0, 105, 5)  # Valores de temperatura (0°C - 100°C cada 5°C)
        viscosidades = visco_40 + (visco_100 - visco_40) / (100 - 40) * (temperaturas - 40)

        # Guardar los datos de la primera gráfica en la sesión
        session['temperaturas'] = temperaturas.tolist()
        session['viscosidades_original'] = viscosidades.tolist()

        # Generar la gráfica
        plt.figure(figsize=(6, 4))
        plt.plot(temperaturas, viscosidades, marker='o', linestyle='-', color='b', label='Interpolación')
        plt.xlabel("Temperatura (°C)")
        plt.ylabel("Viscosidad Cinemática (cSt)")
        plt.title("Análisis Temperatura vs. Viscosidad")
        plt.legend()
        plt.grid(True)

        # Guardar la gráfica
        plt.savefig(GRAPH_PATH)
        plt.close()

        # Convertir la tabla a una lista de diccionarios para enviarla en JSON
        tabla_datos = [{"temperatura": int(temp), "viscosidad": round(visco, 2)} for temp, visco in zip(temperaturas, viscosidades)]

        return jsonify({
            'plus_10_40': plus_10_40,
            'minus_10_40': minus_10_40,
            'plus_10_100': plus_10_100,
            'minus_10_100': minus_10_100,
            'tabla_datos': tabla_datos,
            'graph_url': GRAPH_PATH
        })

    except ValueError:
        return jsonify({'error': 'Invalid input'}), 400

# Nueva ruta para interpolación y generación de gráfica basada en pruebas a 40°C y 100°C
@app.route('/interpolate', methods=['POST'])
def interpolate():
    try:
        visco_40 = float(request.form['viscosidad-40'])
        visco_100 = float(request.form['viscosidad-100'])

        # Cálculo del +10% y -10% de viscosidades
        plus_10_40 = round(visco_40 * 1.1, 2)
        minus_10_40 = round(visco_40 * 0.9, 2)
        plus_10_100 = round(visco_100 * 1.1, 2)
        minus_10_100 = round(visco_100 * 0.9, 2)

        # Realizar interpolación de datos
        temperaturas = np.arange(0, 105, 5)  # Valores de temperatura (0°C - 100°C cada 5°C)
        viscosidades = [visco_40 + ((visco_100 - visco_40) / 60) * (temp - 40) for temp in temperaturas]

        # Generar la gráfica
        plt.figure(figsize=(6, 4))
        plt.plot(temperaturas, viscosidades, marker='o', linestyle='-', color='r', label='Interpolación')
        plt.xlabel("Temperatura (°C)")
        plt.ylabel("Viscosidad Cinemática (cSt)")
        plt.title("Interpolación de Viscosidad")
        plt.legend()
        plt.grid(True)

        # Guardar la gráfica
        plt.savefig(GRAPH_PATH2)
        plt.close()

        # Convertir la tabla a una lista de diccionarios para enviarla en JSON
        tabla_datos_new = [{"temperatura": int(temp), "viscosidad": round(visco, 2)} for temp, visco in zip(temperaturas, viscosidades)]

        return jsonify({
            'tabla_datos_new': tabla_datos_new,
            'graph_url_new': GRAPH_PATH2
        })

    except ValueError:
        return jsonify({'error': 'Invalid input'}), 400

#Datos de Tabla Pruebas>

@app.route('/get_viscosity', methods=['POST'])
def get_viscosity():
    try:
        # Get cup number and time from form data
        num_copa = int(request.form['num_copa']) 
        tiempo = int(request.form['tiempo'])
        temp_prueba = int(request.form.get('temperatura', 40))  # Nueva línea para identificar la temperatura de prueba

        # Read viscosity data from Excel file using pandas
        df = pd.read_excel('viscosity_data.xlsx', sheet_name=f'Copa {num_copa}')
        
        # Find viscosity value for given time
        viscosidad = df.loc[df['TIEMPO (s)'] == tiempo, 'VISCOSIDAD (cSt)'].values[0]

        # Store viscosity value in session based on temperature
        if 'viscosidades_prueba' not in session:
            session['viscosidades_prueba'] = {}
        
        session['viscosidades_prueba'][str(temp_prueba)] = viscosidad

        # Check if we have both temperature measurements
        if '40' in session['viscosidades_prueba'] and '100' in session['viscosidades_prueba']:
            # Generate interpolation data using both measurements
            visco_40 = session['viscosidades_prueba']['40']
            visco_100 = session['viscosidades_prueba']['100']
            
            temperaturas = np.arange(0, 105, 5)
            viscosidades = [visco_40 + ((visco_100 - visco_40) / 60) * (temp - 40) for temp in temperaturas]

            # Generate new graph
            plt.figure(figsize=(6, 4))
            plt.plot(temperaturas, viscosidades, marker='o', linestyle='-', color='g', label='Interpolación Final')
            plt.xlabel("Temperatura (°C)")
            plt.ylabel("Viscosidad Cinemática (cSt)")
            plt.title("Interpolación")
            plt.legend()
            plt.grid(True)

            # Save the new graph
            plt.savefig(GRAPH_PATH2)
            plt.close()

            # Create new table data
            tabla_datos_new = [
                {"temperatura": int(temp), "viscosidad": round(visco, 2)} 
                for temp, visco in zip(temperaturas, viscosidades)
            ]

            # Clear session data after generating the graph
            session.pop('viscosidades_prueba')

            return jsonify({
                'viscosidad': viscosidad,
                'tabla_datos_new': tabla_datos_new,
                'graph_url_new': GRAPH_PATH2,
                'interpolacion_completa': True
            })

        return jsonify({
            'viscosidad': viscosidad,
            'interpolacion_completa': False
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/ajustar_copa_ford', methods=['POST'])
def ajustar_copa_ford():
    try:
        temp_40_ajuste = float(request.form['temp_40_ajuste'])
        temp_100_ajuste = float(request.form['temp_100_ajuste'])

        # Generación de la tabla de ajuste
        temperaturas = np.arange(0, 105, 5)
        viscosidades_ajuste = temp_40_ajuste + (temp_100_ajuste - temp_40_ajuste) / (100 - 40) * (temperaturas - 40)

        # Cargar los datos de la primera gráfica desde la sesión
        temperaturas_original = session.get('temperaturas', [])
        viscosidades_original = session.get('viscosidades_original', [])

        # Generar la gráfica de ajuste
        plt.figure(figsize=(6, 4))
        plt.plot(temperaturas, viscosidades_ajuste, marker='o', linestyle='-', color='m', label='Ajuste')
        if temperaturas_original and viscosidades_original:
            plt.plot(temperaturas_original, viscosidades_original, marker='o', linestyle='-', color='b', label='Original')
        plt.xlabel("Temperatura (°C)")
        plt.ylabel("Viscosidad Cinemática (cSt)")
        plt.title("Ajuste Temperatura vs. Viscosidad")
        plt.legend()
        plt.grid(True)

        # Guardar la gráfica de ajuste
        GRAPH_PATH_AJUSTE = "static/graph_ajuste.png"
        plt.savefig(GRAPH_PATH_AJUSTE)
        plt.close()

        # Convertir la tabla de ajuste a una lista de diccionarios para enviarla en JSON
        tabla_datos_ajuste = [{"temperatura": int(temp), "viscosidad": round(visco, 2)} for temp, visco in zip(temperaturas, viscosidades_ajuste)]

        return jsonify({
            'tabla_datos_ajuste': tabla_datos_ajuste,
            'graph_url_ajuste': GRAPH_PATH_AJUSTE
        })

    except ValueError:
        return jsonify({'error': 'Invalid input'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)