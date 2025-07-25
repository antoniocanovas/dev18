#!/bin/bash

# Script de debug para Sale Variant Toggle
# Uso: ./debug.sh

echo "🔍 Verificando Sale Variant Toggle..."

# Función para verificar estado
check_status() {
    local name="$1"
    local status="$2"
    if [ "$status" = "OK" ]; then
        echo "✅ $name"
    else
        echo "❌ $name - $status"
    fi
}

echo ""
echo "📁 Verificando archivos del módulo..."

FILES=(
    "__manifest__.py"
    "models/product_template.py"
    "models/sale_order.py" 
    "models/variant_selector_wizard.py"
    "views/product_template_views.xml"
    "views/sale_order_views.xml"
    "static/src/js/variant_configurator.js"
    "security/ir.model.access.csv"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        check_status "$file" "OK"
    else
        check_status "$file" "FALTANTE"
    fi
done

echo ""
echo "🐍 Verificando sintaxis Python..."

python3 -m py_compile models/*.py 2>/dev/null
if [ $? -eq 0 ]; then
    check_status "Sintaxis Python" "OK"
else
    check_status "Sintaxis Python" "ERROR"
fi

echo ""
echo "📝 Verificando XML..."

for xml_file in views/*.xml; do
    if xmllint --noout "$xml_file" 2>/dev/null; then
        check_status "$(basename $xml_file)" "OK"
    else
        check_status "$(basename $xml_file)" "ERROR XML"
    fi
done

echo ""
echo "🔧 Pasos para probar la funcionalidad:"
echo "1. Instalar módulo: Apps → Update Apps List → 'Sale Variant Toggle'"
echo "2. Crear producto con variantes (ej: Camiseta con Color y Talla)"
echo "3. En el producto, seleccionar 'Allow Toggle' en 'Variant Selection Mode'"
echo "4. Crear una orden de venta"
echo "5. Agregar línea → Seleccionar el producto"
echo "6. ¡Debería aparecer el diálogo de selección!"

echo ""
echo "🐛 Si no funciona:"
echo "- Verificar logs: tail -f /var/log/odoo/odoo.log"
echo "- Limpiar caché: Reiniciar Odoo completamente"
echo "- Verificar en consola del navegador si hay errores JavaScript"
echo "- Asegurar que el producto tenga atributos/variantes configuradas"

echo ""
echo "🎯 Cómo verificar en navegador:"
echo "1. F12 → Console"
echo "2. Al seleccionar producto, buscar: 'Error checking product variant mode'"
echo "3. Si aparece el error, el JavaScript no está interceptando correctamente"

echo ""
echo "📞 Debug mode:"
echo "console.log('Variant Toggle Debug:', window.odoo.services);"
echo ""
echo "¡Listo para debuggear! 🚀"
