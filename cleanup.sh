#!/bin/bash
# Script temporal para limpiar archivos innecesarios

echo "Eliminando archivos innecesarios..."

# Crear un nuevo directorio temporal para respaldo
mkdir -p /Users/antoniocanovaspedreno/PycharmProjects/dev18/temp_backup

# Archivos a eliminar
rm -f "/Users/antoniocanovaspedreno/PycharmProjects/dev18/sale_product_matrix_configurator/FIXES.md"
rm -f "/Users/antoniocanovaspedreno/PycharmProjects/dev18/sale_product_matrix_configurator/USER_FLOW.md"

# Eliminar directorio security (no necesario)
rm -rf "/Users/antoniocanovaspedreno/PycharmProjects/dev18/sale_product_matrix_configurator/security"

# Eliminar directorio XML (no necesario)  
rm -rf "/Users/antoniocanovaspedreno/PycharmProjects/dev18/sale_product_matrix_configurator/static/src/xml"

# Eliminar cache de Python
rm -rf "/Users/antoniocanovaspedreno/PycharmProjects/dev18/sale_product_matrix_configurator/__pycache__"
rm -rf "/Users/antoniocanovaspedreno/PycharmProjects/dev18/sale_product_matrix_configurator/models/__pycache__"

echo "Limpieza completada."
