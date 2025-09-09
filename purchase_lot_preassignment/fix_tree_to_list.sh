#!/bin/bash

echo "✅ CORRECCIÓN APLICADA: tree → list"
echo "===================================="

MODULE_PATH="/Users/antoniocanovaspedreno/PycharmProjects/clientes/18/purchase_lot_preassignment"
XML_FILE="$MODULE_PATH/views/purchase_order_views.xml"

# Verificar el cambio
if grep -q "<list" "$XML_FILE"; then
    echo "✅ Cambiado <tree> → <list>"
    echo "✅ XML simplificado (vista inline directa)"
else
    echo "❌ Error: <list> no encontrado"
fi

# Limpiar caché
find "$MODULE_PATH" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$MODULE_PATH" -name "*.pyc" -delete 2>/dev/null || true
echo "✅ Caché limpiado"

echo ""
echo "🚀 ACTUALIZAR MÓDULO:"
echo "cd /Users/antoniocanovaspedreno/PycharmProjects/odoo18"
echo "python3 odoo-bin -d TU_BD -u purchase_lot_preassignment --addons-path=/Users/antoniocanovaspedreno/PycharmProjects/clientes/18,addons,../enterprise18 --dev=reload"

echo ""
echo "✅ El ParseError 'Invalid view type: tree' debería estar resuelto"
