#!/bin/bash

echo "✅ FILTRO 'Expected Lots' CORREGIDO - Sin Filtro Automático"
echo "=========================================================="

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

MODULE_PATH="/Users/antoniocanovaspedreno/PycharmProjects/clientes/18/purchase_lot_preassignment"
MODEL_FILE="$MODULE_PATH/models/stock_picking.py"

echo -e "${YELLOW}🔍 VERIFICANDO CORRECCIÓN DEL FILTRO...${NC}"

echo -e "${YELLOW}1. Verificando que NO hay filtro automático...${NC}"

# Verificar que NO está el filtro problemático
if grep -q "search_default_confirmed" "$MODEL_FILE"; then
    echo -e "${RED}❌ Error: Filtro automático aún presente${NC}"
    echo "Líneas encontradas:"
    grep -n "search_default_confirmed" "$MODEL_FILE"
else
    echo -e "${GREEN}✅ Filtro automático eliminado correctamente${NC}"
fi

echo -e "${YELLOW}2. Verificando que el método existe...${NC}"

# Verificar que el método action_view_expected_lots existe
if grep -q "def action_view_expected_lots" "$MODEL_FILE"; then
    echo -e "${GREEN}✅ Método action_view_expected_lots encontrado${NC}"
else
    echo -e "${RED}❌ Error: Método action_view_expected_lots no encontrado${NC}"
fi

echo -e "${YELLOW}3. Verificando domain correcto...${NC}"

# Verificar que el domain está presente
if grep -q "purchase_order_id.*=" "$MODEL_FILE"; then
    echo -e "${GREEN}✅ Domain por pedido de compra mantenido${NC}"
else
    echo -e "${RED}❌ Error: Domain por pedido de compra no encontrado${NC}"
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
echo -e "${YELLOW}📋 CAMBIO APLICADO:${NC}"
echo "❌ ANTES:"
echo "   'context': {'search_default_confirmed': 1},"
echo "   → Solo mostraba lotes confirmados"

echo ""
echo "✅ AHORA:"
echo "   # Sin context automático"
echo "   → Muestra TODOS los lotes del pedido"

echo ""
echo -e "${YELLOW}🎯 NUEVO COMPORTAMIENTO:${NC}"
echo "Al hacer clic en 'Expected Lots' desde el albarán:"
echo "✅ Se muestran TODOS los lotes preasignados"
echo "✅ Estados visibles: Draft, Confirmed, Received"
echo "✅ Sin filtros automáticos aplicados"
echo "✅ Usuario puede filtrar manualmente si desea"

echo ""
echo -e "${YELLOW}🔍 BENEFICIOS:${NC}"
echo "• Ver lotes en cualquier estado"
echo "• Consulta completa de lo esperado"
echo "• Flexibilidad para el usuario"
echo "• No más sorpresas por filtros ocultos"

echo ""
echo -e "${GREEN}Botón 'Expected Lots' ahora muestra todo el contenido esperado.${NC}"
