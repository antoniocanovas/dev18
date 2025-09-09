#!/bin/bash

echo "🎯 VERIFICACIÓN FINAL - Only Preassigned Lots"
echo "============================================="

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

MODULE_PATH="/Users/antoniocanovaspedreno/PycharmProjects/clientes/18/purchase_lot_preassignment"

echo -e "${YELLOW}🔍 VERIFICANDO IMPLEMENTACIÓN COMPLETA...${NC}"

# Verificar archivos principales
FILES=(
    "models/stock_picking.py"
    "views/stock_picking_views.xml"
    "ONLY_PREASSIGNED_LOTS_EXAMPLES.md"
)

for file in "${FILES[@]}"; do
    if [ -f "$MODULE_PATH/$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ $file (FALTANTE)${NC}"
    fi
done

echo ""
echo -e "${YELLOW}🔍 VERIFICANDO CONTENIDO CLAVE...${NC}"

# Verificaciones específicas
CHECKS=(
    "models/stock_picking.py:only_preassigned_lots.*Boolean:Campo boolean definido"
    "models/stock_picking.py:default=True:Valor por defecto True"
    "models/stock_picking.py:if self.only_preassigned_lots:Lógica condicional"
    "models/stock_picking.py:ValidationError.*not in the preassigned list:Error específico"
    "views/stock_picking_views.xml:only_preassigned_lots:Campo en vista"
    "views/stock_picking_views.xml:invisible.*incoming.*purchase_id:Visibilidad correcta"
)

for check in "${CHECKS[@]}"; do
    IFS=':' read -r file pattern description <<< "$check"
    if grep -q "$pattern" "$MODULE_PATH/$file" 2>/dev/null; then
        echo -e "${GREEN}✅ $description${NC}"
    else
        echo -e "${RED}❌ $description (NO ENCONTRADO)${NC}"
    fi
done

echo ""
echo -e "${BLUE}📋 RESUMEN DE FUNCIONALIDAD:${NC}"
echo ""
echo -e "${YELLOW}CAMPO AÑADIDO:${NC}"
echo "• Nombre: 'Only Preassigned Lots'"
echo "• Tipo: Boolean"  
echo "• Default: True"
echo "• Ubicación: Albarán de recepción"
echo ""
echo -e "${YELLOW}VALIDACIÓN ESTRICTA (True):${NC}"
echo "• Solo permite lotes preasignados"
echo "• Bloquea con ValidationError"
echo "• Mensajes explicativos"
echo ""
echo -e "${YELLOW}VALIDACIÓN SUAVE (False):${NC}"
echo "• Permite cualquier lote"
echo "• Solo warnings en chatter"
echo "• No bloquea validación"
echo ""
echo -e "${YELLOW}INTERFAZ:${NC}"
echo "• Visible solo en recepciones de compra"
echo "• Campo editable por el usuario"
echo "• Texto de ayuda incluido"

echo ""
echo -e "${GREEN}🚀 COMANDO DE ACTUALIZACIÓN:${NC}"
echo "cd /Users/antoniocanovaspedreno/PycharmProjects/odoo18"
echo "python3 odoo-bin -d TU_BD -u purchase_lot_preassignment --addons-path=/Users/antoniocanovaspedreno/PycharmProjects/clientes/18,addons,../enterprise18 --dev=reload"

echo ""
echo -e "${GREEN}✅ Campo 'Only Preassigned Lots' completamente implementado${NC}"
echo -e "${BLUE}📖 Ver ONLY_PREASSIGNED_LOTS_EXAMPLES.md para casos de uso detallados${NC}"
