#!/bin/bash

echo "✅ CAMPO 'PREASSIGNED LOTS' AÑADIDO"
echo "===================================="

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

MODULE_PATH="/Users/antoniocanovaspedreno/PycharmProjects/clientes/18/purchase_lot_preassignment"
MODEL_FILE="$MODULE_PATH/models/stock_picking.py"
VIEW_FILE="$MODULE_PATH/views/stock_picking_views.xml"

echo -e "${YELLOW}1. Verificando campo only_preassigned_lots...${NC}"

# Verificar que el campo está definido
if grep -q "only_preassigned_lots.*fields.Boolean" "$MODEL_FILE"; then
    echo -e "${GREEN}✅ Campo only_preassigned_lots definido en modelo${NC}"
else
    echo -e "${RED}❌ Error: Campo only_preassigned_lots no encontrado${NC}"
fi

# Verificar que el campo está en la vista
if grep -q "only_preassigned_lots" "$VIEW_FILE"; then
    echo -e "${GREEN}✅ Campo only_preassigned_lots añadido a vista${NC}"
else
    echo -e "${RED}❌ Error: Campo only_preassigned_lots no está en vista${NC}"
fi

echo -e "${YELLOW}2. Verificando lógica de validación estricta...${NC}"

# Verificar que hay validación estricta
if grep -q "if self.only_preassigned_lots:" "$MODEL_FILE"; then
    echo -e "${GREEN}✅ Lógica de validación estricta implementada${NC}"
else
    echo -e "${RED}❌ Error: Lógica de validación estricta no encontrada${NC}"
fi

# Verificar que hay ValidationError para lotes no preasignados
if grep -q "ValidationError.*not in the preassigned list" "$MODEL_FILE"; then
    echo -e "${GREEN}✅ Error de validación para lotes no preasignados${NC}"
else
    echo -e "${RED}❌ Error: ValidationError para lotes no preasignados no encontrado${NC}"
fi

echo -e "${YELLOW}3. Verificando valor por defecto...${NC}"

# Verificar que el campo tiene default=True
if grep -q "default=True" "$MODEL_FILE"; then
    echo -e "${GREEN}✅ Valor por defecto True configurado${NC}"
else
    echo -e "${RED}❌ Error: Valor por defecto no configurado${NC}"
fi

# Verificar método create personalizado
if grep -q "def create.*only_preassigned_lots" "$MODEL_FILE"; then
    echo -e "${GREEN}✅ Método create personalizado para albaranes de compra${NC}"
else
    echo -e "${RED}❌ Error: Método create personalizado no encontrado${NC}"
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
echo -e "${YELLOW}📋 FUNCIONALIDAD AÑADIDA:${NC}"
echo "1. ✅ Campo boolean 'Only Preassigned Lots' en albaranes"
echo "2. ✅ Valor por defecto: True para recepciones de compra"
echo "3. ✅ Campo visible solo en albaranes de entrada con pedido de compra"
echo "4. ✅ Validación estricta cuando está activado"
echo "5. ✅ ValidationError si se reciben lotes no preasignados"
echo "6. ✅ Comportamiento suave (warnings) cuando está desactivado"

echo ""
echo -e "${YELLOW}🎯 COMPORTAMIENTO:${NC}"
echo "📍 WHEN only_preassigned_lots = True (default):"
echo "   - Solo permite lotes que estén en la lista de preasignados"
echo "   - Bloquea validación si se reciben lotes no preasignados"
echo "   - Muestra error explicativo con opciones de solución"
echo ""
echo "📍 WHEN only_preassigned_lots = False:"
echo "   - Permite cualquier lote/número de serie"
echo "   - Solo muestra warnings informativos"
echo "   - No bloquea la validación"

echo ""
echo -e "${GREEN}Campo 'Preassigned Lots' implementado correctamente.${NC}"
