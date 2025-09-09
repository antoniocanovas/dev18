#!/bin/bash

echo "✅ BOTÓN GENERATE LOTS - CORRECCIÓN FINAL"
echo "========================================="

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

MODULE_PATH="/Users/antoniocanovaspedreno/PycharmProjects/clientes/18/purchase_lot_preassignment"
MODEL_FILE="$MODULE_PATH/models/purchase_order.py"
VIEW_FILE="$MODULE_PATH/views/purchase_lot_preassignment_views.xml"

echo -e "${YELLOW}1. Verificando uso correcto de 'list' en Odoo 18...${NC}"

# Verificar que se usa list en view_mode
if grep -q "view_mode.*list,form" "$MODEL_FILE"; then
    echo -e "${GREEN}✅ view_mode correcto: list,form (Odoo 18)${NC}"
else
    echo -e "${RED}❌ Error: view_mode incorrecto${NC}"
fi

# Verificar que se usa <list> en XML
if grep -q "<list.*string.*Lot Preassignments" "$VIEW_FILE"; then
    echo -e "${GREEN}✅ Elemento <list> correcto (Odoo 18)${NC}"
else
    echo -e "${RED}❌ Error: Elemento <list> incorrecto${NC}"
fi

echo -e "${YELLOW}2. Verificando referencias de vista explícitas...${NC}"

# Verificar que hay view_id en la acción XML
if grep -q 'view_id.*ref.*view_purchase_lot_preassignment_list' "$VIEW_FILE"; then
    echo -e "${GREEN}✅ view_id explícito en acción XML${NC}"
else
    echo -e "${RED}❌ Error: view_id faltante en acción XML${NC}"
fi

# Verificar que hay view_id en métodos Python
if grep -q "view_id.*self.env.ref.*view_purchase_lot_preassignment_list" "$MODEL_FILE"; then
    echo -e "${GREEN}✅ view_id explícito en métodos Python${NC}"
else
    echo -e "${RED}❌ Error: view_id faltante en métodos Python${NC}"
fi

echo -e "${YELLOW}3. Verificando consistencia de IDs...${NC}"

# Verificar que el ID de la vista existe
if grep -q 'id="view_purchase_lot_preassignment_list"' "$VIEW_FILE"; then
    echo -e "${GREEN}✅ ID de vista consistente: view_purchase_lot_preassignment_list${NC}"
else
    echo -e "${RED}❌ Error: ID de vista inconsistente${NC}"
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
echo -e "${YELLOW}📋 CORRECCIONES APLICADAS (Odoo 18 Compatible):${NC}"
echo "1. ✅ Mantenido view_mode: 'list,form' (correcto para Odoo 18)"
echo "2. ✅ Mantenido elemento <list> (correcto para Odoo 18)"
echo "3. ✅ Agregado view_id explícito en acción XML"
echo "4. ✅ Agregado view_id explícito en métodos Python"
echo "5. ✅ IDs de vista consistentes"

echo ""
echo -e "${GREEN}El botón 'Generate Lots' debería funcionar ahora.${NC}"
echo -e "${YELLOW}Error esperado resuelto: 'View types not defined tree found'${NC}"
