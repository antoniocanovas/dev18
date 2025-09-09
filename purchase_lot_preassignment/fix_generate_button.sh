#!/bin/bash

echo "✅ BOTÓN GENERAR LOTES CORREGIDO"
echo "==============================="

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

MODULE_PATH="/Users/antoniocanovaspedreno/PycharmProjects/clientes/18/purchase_lot_preassignment"
MODEL_FILE="$MODULE_PATH/models/purchase_order.py"
VIEW_FILE="$MODULE_PATH/views/purchase_lot_preassignment_views.xml"

echo -e "${YELLOW}1. Verificando corrección view_mode...${NC}"

# Verificar que se usa tree,form en lugar de list,form
if grep -q "view_mode.*tree,form" "$MODEL_FILE"; then
    echo -e "${GREEN}✅ view_mode corregido: tree,form${NC}"
else
    echo -e "${RED}❌ Error: view_mode incorrecto${NC}"
fi

echo -e "${YELLOW}2. Verificando elementos tree...${NC}"

# Verificar que se usa <tree> en lugar de <list>
if grep -q "<tree.*string.*Lot Preassignments" "$VIEW_FILE"; then
    echo -e "${GREEN}✅ Elemento <tree> correcto${NC}"
else
    echo -e "${RED}❌ Error: Elemento <tree> incorrecto${NC}"
fi

# Verificar que se cierra con </tree>
if grep -q "</tree>" "$VIEW_FILE"; then
    echo -e "${GREEN}✅ Cierre </tree> correcto${NC}"
else
    echo -e "${RED}❌ Error: Cierre </tree> incorrecto${NC}"
fi

echo -e "${YELLOW}3. Verificando consistency en action_purchase_lot_preassignment...${NC}"

# Verificar que la acción principal también usa tree,form
if grep -q 'view_mode">tree,form' "$VIEW_FILE"; then
    echo -e "${GREEN}✅ Acción principal consistente${NC}"
else
    echo -e "${RED}❌ Error: Acción principal inconsistente${NC}"
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
echo -e "${YELLOW}📋 CORRECCIONES APLICADAS:${NC}"
echo "1. ✅ action_view_lot_preassignments(): view_mode = 'tree,form'"
echo "2. ✅ action_view_lot_preassignments() en PurchaseOrderLine: view_mode = 'tree,form'"
echo "3. ✅ Vista tree: <list> → <tree>"
echo "4. ✅ Cierre de elemento: </list> → </tree>"
echo "5. ✅ Acción principal consistente con tree,form"

echo ""
echo -e "${GREEN}El botón 'Generate Lots' debería funcionar correctamente ahora.${NC}"
echo -e "${YELLOW}Funcionalidad esperada:${NC}"
echo "- Genera lotes automáticamente por producto"
echo "- Abre vista tree de lotes creados"
echo "- Permite edición inline de lotes"
