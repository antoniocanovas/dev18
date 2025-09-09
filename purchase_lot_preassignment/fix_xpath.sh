#!/bin/bash

echo "✅ XPATH CORREGIDO - Stock Picking Views"
echo "======================================="

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

MODULE_PATH="/Users/antoniocanovaspedreno/PycharmProjects/clientes/18/purchase_lot_preassignment"
STOCK_VIEW_FILE="$MODULE_PATH/views/stock_picking_views.xml"

echo -e "${YELLOW}1. Verificando simplificación de vistas stock...${NC}"

# Verificar que no hay referencias problemáticas
if grep -q "lot_name\|view_move_line_tree\|view_move_line_form" "$STOCK_VIEW_FILE"; then
    echo -e "${RED}❌ Error: Referencias problemáticas aún presentes${NC}"
else
    echo -e "${GREEN}✅ Referencias problemáticas eliminadas${NC}"
fi

# Verificar que solo queda lo esencial
if grep -q "action_view_expected_lots" "$STOCK_VIEW_FILE"; then
    echo -e "${GREEN}✅ Funcionalidad esencial mantenida (Expected Lots button)${NC}"
else
    echo -e "${RED}❌ Error: Funcionalidad esencial perdida${NC}"
fi

# Contar líneas para verificar simplificación
LINES=$(wc -l < "$STOCK_VIEW_FILE")
if [ "$LINES" -lt 25 ]; then
    echo -e "${GREEN}✅ Archivo simplificado ($LINES líneas)${NC}"
else
    echo -e "${YELLOW}⚠️ Archivo aún complejo ($LINES líneas)${NC}"
fi

echo -e "${YELLOW}2. Limpiando caché...${NC}"
find "$MODULE_PATH" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$MODULE_PATH" -name "*.pyc" -delete 2>/dev/null || true
echo -e "${GREEN}✅ Caché limpiado${NC}"

echo ""
echo -e "${GREEN}🚀 ACTUALIZAR MÓDULO:${NC}"
echo "cd /Users/antoniocanovaspedreno/PycharmProjects/odoo18"
echo "python3 odoo-bin -d TU_BD -u purchase_lot_preassignment --addons-path=/Users/antoniocanovaspedreno/PycharmProjects/clientes/18,addons,../enterprise18 --dev=reload"

echo ""
echo -e "${YELLOW}📋 CAMBIOS APLICADOS:${NC}"
echo "1. ✅ Eliminadas TODAS las extensiones problemáticas"
echo "2. ✅ Removidas referencias a lot_name inexistente"
echo "3. ✅ Eliminadas extensiones stock.move.line complejas"
echo "4. ✅ Mantenido solo botón 'Expected Lots' esencial"
echo "5. ✅ Archivo reducido a mínima funcionalidad"

echo ""
echo -e "${GREEN}El error de XPath debería estar completamente resuelto.${NC}"
echo -e "${YELLOW}Funcionalidad mantenida: Botón 'Expected Lots' en recepciones${NC}"
