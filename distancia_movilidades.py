import requests
import pandas as pd
import os
import time
from dotenv import load_dotenv

# 🔹 Cargar variables de entorno desde .env
load_dotenv()

# 🔹 API Key de GraphHopper
GH_API_KEY = os.getenv("GH_API_KEY")
print(f"🔍 API KEY cargada: {GH_API_KEY}")

# 🔹 URL de GraphHopper para calcular rutas
GH_URL = "https://graphhopper.com/api/1/route"

# 🔹 Coordenadas fijas de destino (San Rafael, Mendoza, Argentina)
DESTINO_COORDS = [-45.87907837, -67.50533342]  # [longitud, latitud]

# ---------------------------------------------------
# 🔄 Función para mapear movilidad a tipos de vehículo GraphHopper
# ---------------------------------------------------
def map_mobility(movilidad):
    movilidad = str(movilidad).strip().lower()
    if movilidad == "caminando":
        return "foot"
    elif movilidad == "moto":
        return "scooter"
    elif movilidad == "bicicleta":
        return "bike"
    elif movilidad in ["auto", "camioneta"]:
        return "car"
    else:
        return "car"  # Valor por defecto

# ---------------------------------------------------
# 📌 Cálculo de distancia usando GraphHopper
# ---------------------------------------------------
def get_distance_graphhopper(origin_coords, vehicle_type="car"):
    try:
        params = {
            "key": GH_API_KEY,
            "point": [f"{origin_coords[1]},{origin_coords[0]}", f"{DESTINO_COORDS[1]},{DESTINO_COORDS[0]}"],
            "vehicle": vehicle_type,
            "locale": "es",
            "calc_points": "false"
        }

        response = requests.get(GH_URL, params=params)
        response.raise_for_status()
        data = response.json()

        distance_meters = data["paths"][0]["distance"]
        distance_km = round(distance_meters / 1000, 2)

        return distance_km, f"{distance_km} km"

    except requests.exceptions.RequestException as e:
        print(f"❌ Error en la API de GraphHopper: {e}")
        return None, "Error en cálculo de ruta"

# ---------------------------------------------------
# 📂 Guardar resultados en Excel
# ---------------------------------------------------
def save_to_excel(data, filename="distancias_calculadas.xlsx"):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f"📂 Archivo guardado correctamente en: {filename}")

# ---------------------------------------------------
# 🚀 Proceso principal
# ---------------------------------------------------
def main():
    input_file = "Movilidad.xlsx"  # 📌 Tu archivo de entrada

    try:
        df = pd.read_excel(input_file)

        required_columns = ["nombre", "latitud_origen", "longitud_origen", "movilidad"]
        if not all(col in df.columns for col in required_columns):
            print("❌ El archivo Excel debe contener las columnas:", required_columns)
            return

        addresses = df.to_dict(orient="records")
        results = []

        for item in addresses:
            nombre = item["nombre"]
            movilidad = item["movilidad"]
            origen_coords = [item["longitud_origen"], item["latitud_origen"]]

            if None in origen_coords:
                distancia_km, distancia_texto = None, "Error: Coordenadas faltantes"
                vehicle_type = "desconocido"
            else:
                vehicle_type = map_mobility(movilidad)
                print(f"🔹 {nombre} - Modo: {vehicle_type} → Desde ({origen_coords[1]}, {origen_coords[0]})")
                distancia_km, distancia_texto = get_distance_graphhopper(origen_coords, vehicle_type)
                time.sleep(5)  # Evitar exceder el límite de la API

            results.append({
                "nombre": nombre,
                "movilidad": movilidad,
                "latitud_origen": origen_coords[1],
                "longitud_origen": origen_coords[0],
                "latitud_destino": DESTINO_COORDS[1],
                "longitud_destino": DESTINO_COORDS[0],
                "modo_transporte": vehicle_type,
                "distancia_texto": distancia_texto,
                "distancia_km": distancia_km
            })

        if results:
            save_to_excel(results)

    except FileNotFoundError:
        print(f"❌ No se encontró el archivo '{input_file}'.")

# ---------------------------------------------------
# ▶️ Ejecutar
# ---------------------------------------------------
if __name__ == "__main__":
    main()
