# Análisis de Calzado (shoes_analysis) v1.0

## Resumen

Este módulo proporciona una herramienta para analizar y clasificar el rendimiento de ventas de productos de calzado a través de diferentes campañas. Genera un ranking de productos basado en pares netos vendidos y permite comparar una campaña principal con otras secundarias.

## Características Principales

*   **Ranking de Productos:** Calcula y muestra un ranking de productos ordenado por el número de pares netos vendidos (vendidos menos cancelados).
*   **Análisis Comparativo:** Permite seleccionar una campaña de ventas principal y compararla con los resultados de una o más campañas secundarias.
*   **Informe Visual:** Genera un informe HTML directamente en la interfaz de Odoo, mostrando el ranking con imágenes de producto, cantidades y importes.
*   **Datos para Análisis Externo:** Almacena los datos del ranking en un campo JSON, permitiendo su exportación o uso en otras integraciones.

## Modelos de Datos

*   `shoes.analysis`: Modelo principal que contiene la configuración del análisis (campañas a comparar) y muestra el informe resultante.
*   `shoes.ranking`: Modelo que almacena las líneas de datos calculadas para cada producto en el ranking.

## Uso

1.  Navega al menú de "Análisis de Calzado".
2.  Crea un nuevo registro de análisis.
3.  Asigna un nombre descriptivo al análisis.
4.  Selecciona la **Campaña Principal** que deseas analizar.
5.  Opcionalmente, añade una o más **Campañas de Comparación**.
6.  Guarda el registro. El informe de ranking se generará automáticamente en la pestaña "Análisis".

## Configuración

Para utilizar este módulo, simplemente instálalo desde la lista de aplicaciones de Odoo.
