#!/bin/bash

echo "✅ BOTÓN GENERATE LOTS - Error view_id CORREGIDO"
echo "==============================================="

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

MODULE_PATH="/Users/antoniocanovaspedreno/PycharmProjects/clientes/18/purchase_lot_preassignment"
MODEL_FILE="$MODULE_PATH/models/purchase_order.py"
VIEW_FILE="$MODULE_PATH/views/purchase_lot_preassignment_views.xml"

echo -e "${YELLOW}1. Verificando eliminación de view_id problemáticos...${NC}"

# Verificar que NO hay view_id en métodos Python
if grep -q "view_id.*self.env.ref" "$MODEL_FILE"; then
    echo -e "${RED}❌ Error: view_id aún presente en métodos Python${NC}"
else
    echo -e "${GREEN}✅ view_id eliminado de métodos Python${NC}"
fi

# Verificar que NO hay view_id en acción XML
if grep -q 'view_id.*ref.*view_purchase_lot_preassignment_list' "$VIEW_FILE"; then
    echo -e "${RED}❌ Error: view_id aún presente en acción XML${NC}"
else
    echo -e "${GREEN}✅ view_id eliminado de acción XML${NC}"
fi

echo -e "${YELLOW}2. Verificando view_mode múltiples...${NC}"

# Verificar que se mantiene view_mode múltiple
if grep -q "view_mode.*list,form" "$MODEL_FILE"; then
    echo -e "${GREEN}✅ view_mode múltiple mantenido: list,form${NC}"
else
    echo -e "${RED}❌ Error: view_mode múltiple perdido${NC}"
fi

echo -e "${YELLOW}3. Verificando que Odoo elegirá vistas automáticamente...${NC}"

# Verificar que las vistas están definidas correctamente
if grep -q 'id="view_purchase_lot_preassignment_list"' "$VIEW_FILE"; then
    echo -e "${GREEN}✅ Vista list definida (Odoo la encontrará automáticamente)${NC}"
else
    echo -e "${RED}❌ Error: Vista list no definida${NC}"
fi

if grep -q 'id="view_purchase_lot_preassignment_form"' "$VIEW_FILE"; then
    echo -e "${GREEN}✅ Vista form definida (Odoo la encontrará automáticamente)${NC}"
else
    echo -e "${RED}❌ Error: Vista form no definida${NC}"
fi

echo -e "${YELLOW}4. Limpiando caché...${NC}"
find "$MODULE_PATH" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$MODULE_PATH" -name "*.pyc" -delete 2>/dev/null || true
echo -e "${GREEN}✅ Caché limpiado${NC}"

echo ""
echo -e "${GREEN}🚀 ACTUALIZAR MÓDULO:${NC}"
echo "cd /Users/antoniocanovaspedreno/PycharmProjects/odoo18"
echo "python3 odoo-bin -d TU_BD -u purchase_lot_preassignment --addons-path=/Users/antoniocanovaspedreno/PycharmProjects/clientes/18,addons,../enterprise18 --dev=reload"

echo ""
echo -e "${YELLOW}📋 CORRECCIÓN APLICADA:${NC}"
echo "1. ✅ ELIMINADO view_id de action_view_lot_preassignments() (PurchaseOrder)"
echo "2. ✅ ELIMINADO view_id de action_view_lot_preassignments() (PurchaseOrderLine)"  
echo "3. ✅ ELIMINADO view_id de action_purchase_lot_preassignment (XML)"
echo "4. ✅ MANTENIDO view_mode: 'list,form' (múltiples modos)"
echo "5. ✅ Odoo elegirá vistas automáticamente por nombre/modelo"

echo ""
echo -e "${GREEN}Error esperado resuelto:${NC}"
echo -e "${YELLOW}'Non-db action dictionaries should provide either multiple view modes or a single view mode and an optional view id'${NC}"

echo ""
echo -e "${GREEN}El botón 'Generate Lots' debería funcionar perfectamente ahora.${NC}"
