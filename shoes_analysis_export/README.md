# Exportación de Análisis de Calzado (shoes_analysis_export) v1.0

## Resumen

Este módulo proporciona la estructura de datos necesaria para exportar informes detallados basados en los análisis de ventas de calzado. Funciona como un complemento del módulo `shoes_analysis`, consolidando datos de múltiples fuentes en un formato unificado listo para ser exportado.

## Características Principales

*   **Modelo de Datos Unificado:** Define un modelo de datos (`shoes.analysis.export`) que sirve como capa intermedia para recopilar información de ventas, clientes, productos y campañas.
*   **Flexibilidad:** La estructura incluye campos para agrupar los datos por cliente, representante, país, fabricante, horma y más, permitiendo una gran variedad de informes.
*   **Datos para Exportación:** Prepara los datos para ser exportados a formatos como CSV o Excel, facilitando el análisis externo en otras herramientas.

## Modelos de Datos

*   `shoes.analysis.export` (`TransientModel`): Modelo temporal que almacena las líneas de datos consolidadas justo antes de la exportación. No guarda datos de forma permanente.

## Campos Disponibles para Exportación

El modelo incluye, entre otros, los siguientes campos:

*   **Agrupación:** Cliente, Representante, País, Fabricante, Timbrado, Horma, Marca.
*   **Métricas de Venta:** Pares Pedidos, Pares Netos, Pares Anulados, Ventas Netas.
*   **Detalles de Producto:** Producto, Material, Ranking, Color.
*   **Métricas de Stock:** Vendido, En Producción, Stock Estimado.

## Uso

Este módulo por sí solo no genera un fichero exportable. Proporciona el modelo de datos que puede ser utilizado por:

1.  Una **acción de servidor** que recopile los datos y los prepare para su descarga.
2.  Un **asistente (wizard)** que permita al usuario filtrar los datos y generar un informe personalizado (CSV, Excel, etc.).

Para activar la exportación, es necesario implementar una de estas dos opciones que utilice el modelo `shoes.analysis.export`.

## Configuración

Para utilizar este módulo, simplemente instálalo desde la lista de aplicaciones de Odoo. Asegúrate de que todos los módulos de los que depende (como `shoes_analysis`, `sale_order_type`, etc.) también estén instalados.
