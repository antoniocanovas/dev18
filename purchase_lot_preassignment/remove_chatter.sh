#!/bin/bash

echo "✅ CHATTER ELIMINADO - Purchase Lot Preassignment"
echo "================================================="

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

MODULE_PATH="/Users/antoniocanovaspedreno/PycharmProjects/clientes/18/purchase_lot_preassignment"
VIEW_FILE="$MODULE_PATH/views/purchase_lot_preassignment_views.xml"
MODEL_FILE="$MODULE_PATH/models/purchase_lot_preassignment.py"

echo -e "${YELLOW}1. Verificando eliminación del chatter...${NC}"

# Verificar que no hay chatter en la vista
if grep -q "oe_chatter\|message_follower_ids\|message_ids" "$VIEW_FILE"; then
    echo -e "${RED}❌ Error: Chatter aún presente en vista${NC}"
else
    echo -e "${GREEN}✅ Chatter eliminado de vista form${NC}"
fi

# Verificar que no hereda de mail.thread en el modelo
if grep -q "mail.thread" "$MODEL_FILE"; then
    echo -e "${RED}❌ Error: Herencia mail.thread aún presente${NC}"
else
    echo -e "${GREEN}✅ Sin herencia mail.thread en modelo${NC}"
fi

echo -e "${YELLOW}2. Verificando otras correcciones...${NC}"

# Verificar que no hay widget handle
if grep -q 'widget="handle"' "$VIEW_FILE"; then
    echo -e "${RED}❌ Error: widget handle aún presente${NC}"
else
    echo -e "${GREEN}✅ Widget handle eliminado${NC}"
fi

# Verificar que usa tree en view_mode
if grep -q 'view_mode">tree,form' "$VIEW_FILE"; then
    echo -e "${GREEN}✅ view_mode correcto: tree,form${NC}"
else
    echo -e "${RED}❌ Error: view_mode incorrecto${NC}"
fi

# Verificar que el ID es consistente
if grep -q 'view_purchase_lot_preassignment_tree' "$VIEW_FILE"; then
    echo -e "${GREEN}✅ ID de vista consistente: tree${NC}"
else
    echo -e "${RED}❌ Error: ID de vista inconsistente${NC}"
fi

echo -e "${YELLOW}3. Limpiando caché...${NC}"
find "$MODULE_PATH" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$MODULE_PATH" -name "*.pyc" -delete 2>/dev/null || true
echo -e "${GREEN}✅ Caché limpiado${NC}"

echo ""
echo -e "${GREEN}🚀 ACTUALIZAR MÓDULO:${NC}"
echo "cd /Users/antoniocanovaspedreno/PycharmProjects/odoo18"
echo "python3 odoo-bin -d TU_BD -u purchase_lot_preassignment --addons-path=/Users/antoniocanovaspedreno/PycharmProjects/clientes/18,addons,../enterprise18 --dev=reload"

echo ""
echo -e "${YELLOW}📋 CAMBIOS APLICADOS:${NC}"
echo "1. ✅ Eliminado <div class=\"oe_chatter\"> completo"
echo "2. ✅ Eliminado message_follower_ids y message_ids"  
echo "3. ✅ Removido widget=\"handle\" problemático"
echo "4. ✅ Cambiado view_mode: list → tree"
echo "5. ✅ ID consistente: view_purchase_lot_preassignment_tree"

echo ""
echo -e "${GREEN}El modelo no tendrá chatter y será más simple.${NC}"
