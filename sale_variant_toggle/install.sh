#!/bin/bash

# Script de instalación para sale_variant_toggle (Odoo 18)
# Uso: ./install.sh [ruta_addons] [nombre_db]

set -e

ADDONS_PATH=${1:-"/opt/odoo/addons"}
DB_NAME=${2:-"odoo18"}
MODULE_NAME="sale_variant_toggle"

echo "🚀 Instalando módulo $MODULE_NAME para Odoo 18..."

# Verificar si Odoo está corriendo
if pgrep -x "odoo" > /dev/null; then
    echo "⚠️  Odoo está corriendo. Se recomienda reiniciarlo después de la instalación."
fi

# Verificar versión de Odoo
if command -v odoo &> /dev/null; then
    ODOO_VERSION=$(odoo --version 2>/dev/null | grep -o "18\." || echo "")
    if [ -z "$ODOO_VERSION" ]; then
        echo "⚠️  Este módulo está diseñado para Odoo 18. Versión detectada: $(odoo --version 2>/dev/null || echo 'No detectada')"
        read -p "¿Continuar de todos modos? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo "✅ Odoo 18 detectado"
    fi
fi

# Copiar módulo si no está en el directorio actual
if [ "$PWD" != "$ADDONS_PATH/$MODULE_NAME" ]; then
    echo "📁 Copiando módulo a $ADDONS_PATH..."
    mkdir -p "$ADDONS_PATH"
    cp -r . "$ADDONS_PATH/$MODULE_NAME"
    echo "📁 Módulo copiado a $ADDONS_PATH/$MODULE_NAME"
fi

# Verificar dependencias
echo "📦 Verificando dependencias..."
DEPS=("sale" "product")

for dep in "${DEPS[@]}"; do
    if [ ! -d "$ADDONS_PATH/$dep" ] && [ ! -d "/opt/odoo/odoo/addons/$dep" ]; then
        echo "⚠️  Dependencia faltante: $dep"
        echo "   Asegúrate de que esté instalada en Odoo"
    else
        echo "✅ Dependencia encontrada: $dep"
    fi
done

# Verificar permisos
if [ ! -w "$ADDONS_PATH" ]; then
    echo "❌ Sin permisos de escritura en $ADDONS_PATH"
    echo "   Ejecuta: sudo chown -R $USER:$USER $ADDONS_PATH"
    exit 1
fi

echo ""
echo "✅ Módulo instalado exitosamente"
echo ""
echo "📋 Próximos pasos:"
echo "1. Reinicia Odoo si está corriendo:"
echo "   sudo systemctl restart odoo"
echo ""
echo "2. Actualiza lista de aplicaciones:"
echo "   Apps → Update Apps List" 
echo ""
echo "3. Busca e instala el módulo:"
echo "   Apps → Buscar 'Sale Variant Toggle' → Install"
echo ""
echo "🔧 Configuración:"
echo "- Ve a un producto con variantes"
echo "- Busca 'Variant Selection Mode' (aparece automáticamente)"
echo "- Selecciona 'Allow Toggle'"
echo ""
echo "🎯 Características Odoo 18:"
echo "- ✅ Sin attrs/states (deprecated)"
echo "- ✅ JavaScript OWL moderno"
echo "- ✅ Bootstrap 5 compatible"
echo "- ✅ Solo dependencias core"
echo ""
echo "🎉 ¡Listo para usar en Odoo 18!"
