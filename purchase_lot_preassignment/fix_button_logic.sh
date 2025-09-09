#!/bin/bash

echo "✅ LÓGICA BOTÓN CORREGIDA - Solo Visible en Confirmados"
echo "======================================================"

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

MODULE_PATH="/Users/antoniocanovaspedreno/PycharmProjects/clientes/18/purchase_lot_preassignment"
VIEW_FILE="$MODULE_PATH/views/purchase_order_views.xml"

echo -e "${YELLOW}1. Verificando corrección de lógica...${NC}"

# Verificar que se usa la nueva condición
if grep -q "not (has_lot_tracking_lines and state == 'purchase')" "$VIEW_FILE"; then
    echo -e "${GREEN}✅ Nueva condición aplicada: not (has_lot_tracking_lines and state == 'purchase')${NC}"
else
    echo -e "${RED}❌ Error: Nueva condición no encontrada${NC}"
fi

# Verificar que NO está la condición problemática anterior
if grep -q "state != 'purchase'" "$VIEW_FILE"; then
    echo -e "${RED}❌ Error: Condición problemática aún presente${NC}"
else
    echo -e "${GREEN}✅ Condición problemática eliminada${NC}"
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
echo -e "${YELLOW}📋 CORRECCIÓN DE LÓGICA:${NC}"
echo "❌ ANTES (Problemático):"
echo "   invisible=\"not has_lot_tracking_lines or state != 'purchase'\""
echo "   → Lógica confusa que causaba comportamiento inverso"

echo ""
echo "✅ AHORA (Correcto):"
echo "   invisible=\"not (has_lot_tracking_lines and state == 'purchase')\""
echo "   → Lógica clara: visible SOLO cuando ambas condiciones se cumplen"

echo ""
echo -e "${YELLOW}🎯 NUEVA LÓGICA:${NC}"
echo "El botón será VISIBLE cuando:"
echo "✅ has_lot_tracking_lines = True"
echo "✅ Y state = 'purchase'"
echo ""
echo "El botón será INVISIBLE en cualquier otro caso:"
echo "❌ Si no hay líneas con tracking"
echo "❌ Si el estado no es 'purchase'"
echo "❌ Si ambas condiciones no se cumplen simultáneamente"

echo ""
echo -e "${GREEN}Ahora el botón aparecerá SOLO en pedidos confirmados.${NC}"
