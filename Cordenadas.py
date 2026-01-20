import requests
import pandas as pd
import os
from dotenv import load_dotenv

# 🔹 Cargar API Key desde archivo .env
load_dotenv()
GH_API_KEY = os.getenv("GH_API_KEY")
GH_URL = "https://graphhopper.com/api/1/route"

# 🔹 Coordenadas fijas de destino (San Rafael)
DESTINO_LAT = -34.63072947
DESTINO_LON = -68.28236589

# 🔹 Calcular distancia en auto
def get_distance_graphhopper(lat, lon):
    try:
        params = {
            "key": GH_API_KEY,
            "point": [f"{lat},{lon}", f"{DESTINO_LAT},{DESTINO_LON}"],
            "vehicle": "car",
            "locale": "es",
            "calc_points": "false"
        }

        response = requests.get(GH_URL, params=params)
        response.raise_for_status()
        data = response.json()

        distancia_metros = data["paths"][0]["distance"]
        distancia_km = round(distancia_metros / 1000, 2)

        return distancia_km, f"{distancia_km} km"

    except requests.exceptions.RequestException as e:
        print(f"❌ Error al calcular distancia: {e}")
        return None, "Error en cálculo"

# 🔹 Guardar archivo Excel
def save_to_excel(data, filename="distancias_calculadas.xlsx"):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f"📁 Archivo guardado: {filename}")

# 🔹 Ejecutar el proceso
def main():
    input_file = "coordenadas.xlsx"

    try:
        df = pd.read_excel(input_file)

        required_columns = ["nombre", "latitud_origen", "longitud_origen"]
        if not all(col in df.columns for col in required_columns):
            print("❌ El archivo debe contener las columnas:", required_columns)
            return

        results = []

        for row in df.to_dict(orient="records"):
            nombre = row["nombre"]
            lat = row["latitud_origen"]
            lon = row["longitud_origen"]

            if pd.isnull(lat) or pd.isnull(lon):
                distancia_km, distancia_texto = None, "Coordenadas faltantes"
            else:
                print(f"🚗 {nombre} → Desde ({lat}, {lon})")
                distancia_km, distancia_texto = get_distance_graphhopper(lat, lon)

            results.append({
                "nombre": nombre,
                "latitud_origen": lat,
                "longitud_origen": lon,
                "latitud_destino": DESTINO_LAT,
                "longitud_destino": DESTINO_LON,
                "distancia_texto": distancia_texto,
                "distancia_km": distancia_km
            })

        save_to_excel(results)

    except FileNotFoundError:
        print(f"❌ Archivo '{input_file}' no encontrado.")

if __name__ == "__main__":
    main()
