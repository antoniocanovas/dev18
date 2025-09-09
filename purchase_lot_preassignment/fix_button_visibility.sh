#!/bin/bash

echo "✅ VISIBILIDAD BOTÓN CORREGIDA - Solo Pedidos Confirmados"
echo "========================================================"

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

MODULE_PATH="/Users/antoniocanovaspedreno/PycharmProjects/clientes/18/purchase_lot_preassignment"
VIEW_FILE="$MODULE_PATH/views/purchase_order_views.xml"

echo -e "${YELLOW}1. Verificando condición de visibilidad del botón...${NC}"

# Verificar que se usa state != 'purchase'
if grep -q "state != 'purchase'" "$VIEW_FILE"; then
    echo -e "${GREEN}✅ Condición correcta: state != 'purchase'${NC}"
else
    echo -e "${RED}❌ Error: Condición de estado incorrecta${NC}"
fi

# Verificar que se mantiene has_lot_tracking_lines
if grep -q "not has_lot_tracking_lines" "$VIEW_FILE"; then
    echo -e "${GREEN}✅ Condición mantenida: not has_lot_tracking_lines${NC}"
else
    echo -e "${RED}❌ Error: Condición de tracking perdida${NC}"
fi

# Verificar que NO hay la condición antigua
if grep -q "state not in \['draft', 'sent'\]" "$VIEW_FILE"; then
    echo -e "${RED}❌ Error: Condición antigua aún presente${NC}"
else
    echo -e "${GREEN}✅ Condición antigua eliminada correctamente${NC}"
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
echo -e "${YELLOW}📋 CAMBIO APLICADO:${NC}"
echo "❌ ANTES: invisible=\"not has_lot_tracking_lines or state not in ['draft', 'sent']\""
echo "✅ AHORA:  invisible=\"not has_lot_tracking_lines or state != 'purchase'\""

echo ""
echo -e "${YELLOW}🎯 COMPORTAMIENTO DEL BOTÓN 'Generate Lots':${NC}"
echo "- 📍 VISIBLE: Solo cuando el pedido está en estado 'purchase' (confirmado)"
echo "- 📍 VISIBLE: Solo si hay líneas con trazabilidad (lot/serial tracking)"
echo "- 🚫 INVISIBLE: En estados 'draft', 'sent', 'to approve', 'done', 'cancel'"
echo "- 🚫 INVISIBLE: Si no hay productos con tracking"

echo ""
echo -e "${GREEN}El botón aparecerá únicamente en pedidos confirmados con tracking.${NC}"
