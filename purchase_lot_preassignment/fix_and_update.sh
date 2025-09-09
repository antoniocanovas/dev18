#!/bin/bash

echo "🔧 Limpiando caché del módulo Purchase Lot Preassignment..."

# Limpiar archivos de caché Python
echo "Eliminando archivos __pycache__..."
find /Users/antoniocanovaspedreno/PycharmProjects/clientes/18/purchase_lot_preassignment -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find /Users/antoniocanovaspedreno/PycharmProjects/clientes/18/purchase_lot_preassignment -name "*.pyc" -delete 2>/dev/null || true

echo "✅ Caché limpiado"

echo ""
echo "🚀 Comando para actualizar el módulo:"
echo "cd /Users/antoniocanovaspedreno/PycharmProjects/odoo18"
echo "python3 odoo-bin -d TU_BASE_DE_DATOS -u purchase_lot_preassignment --addons-path=/Users/antoniocanovaspedreno/PycharmProjects/clientes/18,addons,../enterprise18 --dev=reload"

echo ""
echo "📋 PASOS A SEGUIR:"
echo "1. Parar el servidor Odoo"
echo "2. Ejecutar el comando de actualización de arriba"
echo "3. Cambiar 'TU_BASE_DE_DATOS' por el nombre real de tu BD"
echo "4. Reiniciar el servidor Odoo"
echo ""
echo "🔍 El problema del 'sequence' debería estar resuelto con la nueva estructura XML"
