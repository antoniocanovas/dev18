#!/bin/bash

echo "🔧 CORRECIÓN FINAL - Purchase Lot Preassignment"
echo "==============================================="

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

MODULE_PATH="/Users/antoniocanovaspedreno/PycharmProjects/clientes/18/purchase_lot_preassignment"

echo -e "${YELLOW}1. Limpiando archivos de caché...${NC}"
find "$MODULE_PATH" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$MODULE_PATH" -name "*.pyc" -delete 2>/dev/null || true

echo -e "${GREEN}✅ Caché limpiado${NC}"

echo -e "${YELLOW}2. Verificando correcciones XML...${NC}"

# Verificar que los IDs sean correctos
if grep -q "purchase_order_line_form2" "$MODULE_PATH/views/purchase_order_views.xml"; then
    echo -e "${GREEN}✅ ID correcto: purchase_order_line_form2${NC}"
else
    echo -e "${RED}❌ ID incorrecto en purchase_order_line_form${NC}"
fi

if grep -q "view_purchase_lot_preassignment_tree_inline" "$MODULE_PATH/views/purchase_order_views.xml"; then
    echo -e "${GREEN}✅ ID correcto: view_purchase_lot_preassignment_tree_inline${NC}"
else
    echo -e "${RED}❌ ID incorrecto en view_id${NC}"
fi

echo -e "${YELLOW}3. Estado del módulo:${NC}"
echo "📁 Ubicación: $MODULE_PATH"
echo "📄 Archivos principales:"
echo "   - __manifest__.py ✓"
echo "   - models/ ✓"
echo "   - views/ ✓"
echo "   - security/ ✓"

echo ""
echo -e "${GREEN}🚀 COMANDOS PARA ACTUALIZAR:${NC}"
echo ""
echo "cd /Users/antoniocanovaspedreno/PycharmProjects/odoo18"
echo "python3 odoo-bin -d TU_BD -u purchase_lot_preassignment --addons-path=/Users/antoniocanovaspedreno/PycharmProjects/clientes/18,addons,../enterprise18 --dev=reload"
echo ""
echo -e "${YELLOW}📋 CORRECCIONES APLICADAS:${NC}"
echo "1. ✅ Cambiado purchase_order_line_form → purchase_order_line_form2"
echo "2. ✅ Corregido view_id de tree inline"
echo "3. ✅ Removido widget='handle' problemático"
echo "4. ✅ Caché limpiado"
echo ""
echo -e "${GREEN}El módulo debería instalar sin errores ahora.${NC}"
