import requests
from google.cloud import storage
import os

def download_webpage_and_save_to_gcs(request):
    """
    Cloud Function que descarga una página web y la guarda en un bucket de GCS.

    Espera un JSON en el cuerpo de la petición HTTP con la clave 'url'.
    Ejemplo de petición:
    {
      "url": "https://www.example.com"
    }
    """

    # 1. Configuración: Nombre del bucket de GCS
    # Asegúrate de que este nombre coincida con el bucket que creaste en el Paso 2.
    GCS_BUCKET_NAME = "icn8nstore"

    # 2. Procesar la petición HTTP
    request_json = request.get_json(silent=True) # Intenta obtener el JSON del cuerpo

    if request_json and 'url' in request_json:
        url_to_download = request_json['url']
    else:
        # Si no se proporciona URL, usa una por defecto o devuelve un error
        return 'Error: La URL no fue proporcionada en el cuerpo de la petición JSON.', 400

    print(f"Intentando descargar la URL: {url_to_download}")

    try:
        # 3. Descargar la página web
        response = requests.get(url_to_download, timeout=15) # Tiempo de espera de 15 segundos
        response.raise_for_status() # Lanza una excepción para códigos de estado HTTP 4xx/5xx

        # 4. Generar un nombre de archivo para GCS
        # Reemplazamos caracteres para que sea un nombre de archivo válido y único.
        # Puedes añadir una marca de tiempo para asegurar unicidad si descargas la misma URL varias veces.
        file_name = url_to_download.replace('https://', '').replace('http://', '')
        file_name = file_name.replace('/', '_').replace('.', '-').replace(':', '') + '.html'

        # Opcional: añadir una marca de tiempo para mayor unicidad
        # import datetime
        # timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        # file_name = f"{file_name.rsplit('.html', 1)[0]}_{timestamp}.html"


        content = response.text
        print(f"Página descargada exitosamente. Tamaño: {len(content)} bytes.")

        # 5. Subir el contenido a Google Cloud Storage
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(file_name)

        blob.upload_from_string(content, content_type='text/html')
        print(f"Contenido subido a gs://{GCS_BUCKET_NAME}/{file_name}")

        return f'Página {url_to_download} descargada y guardada como {file_name} en el bucket {GCS_BUCKET_NAME}.', 200

    except requests.exceptions.RequestException as e:
        print(f"Error al descargar la página {url_to_download}: {e}")
        return f'Error al descargar la página {url_to_download}: {e}', 500
    except Exception as e:
        print(f"Error inesperado: {e}")
        return f'Error inesperado: {e}', 500
