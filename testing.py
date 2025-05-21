#!/usr/bin/env python3

import pandas as pd
import random
from datetime import datetime, timedelta

# Valores posibles para las columnas
PRIORITIES = ['P1', 'P2', 'P3', 'P4']
STATUSES = ['Open', 'Fixed', 'Wontfix', 'Reopened']
TEAMS = ['Alpha', 'Beta', 'Gamma', 'Delta', 'Excluded Team']
SEVERITIES = ['Severe', 'Moderate', 'Minor']

# Función para generar una fecha aleatoria
def random_date(start_date, end_date):
    time_delta = end_date - start_date
    random_days = random.randint(0, time_delta.days)
    return start_date + timedelta(days=random_days)

# Función para generar datos simulados
def generate_test_data(num_rows):
    data = {
        'Issue Priority': [],
        'Issue Status': [],
        'Date Created': [],
        'Date Resolved': [],
        'Severity Level': [],
        'Assigned Team': []
    }
    
    start = datetime(2022, 1, 1)
    end = datetime(2024, 12, 31)
    
    for _ in range(num_rows):
        created = random_date(start, end)
        # 60% de probabilidad de que la vulnerabilidad esté resuelta
        resolved = random_date(created, end) if random.random() < 0.6 else None
        
        data['Issue Priority'].append(random.choice(PRIORITIES))
        data['Issue Status'].append(random.choice(STATUSES))
        data['Date Created'].append(created)
        data['Date Resolved'].append(resolved)
        data['Severity Level'].append(random.choice(SEVERITIES))
        data['Assigned Team'].append(random.choice(TEAMS))
    
    # Crear DataFrame
    df = pd.DataFrame(data)
    # Formatear fechas como strings
    df['Date Created'] = df['Date Created'].dt.strftime('%Y-%m-%d')
    df['Date Resolved'] = df['Date Resolved'].dt.strftime('%Y-%m-%d').replace('NaT', '')
    return df

# Generar y guardar el CSV
if __name__ == '__main__':
    # Número de filas y nombre del archivo (puedes cambiar estos valores)
    num_rows = 50
    output_file = 'vulnerability_test_data.csv'
    
    # Generar datos
    test_data = generate_test_data(num_rows)
    
    # Guardar en CSV
    test_data.to_csv(output_file, index=False)
    print(f"Se ha generado un archivo CSV con {num_rows} filas en '{output_file}'.")