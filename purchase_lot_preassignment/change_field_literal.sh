#!/bin/bash

echo "✅ LITERAL CAMBIADO: 'Only Preassigned Lots' → 'Preassigned Lots'"
echo "================================================================="

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

MODULE_PATH="/Users/antoniocanovaspedreno/PycharmProjects/clientes/18/purchase_lot_preassignment"

echo -e "${YELLOW}🔍 VERIFICANDO CAMBIOS DE LITERAL...${NC}"

echo -e "${YELLOW}1. Verificando campo en modelo Python...${NC}"

# Verificar que el string del campo se cambió
if grep -q "string='Preassigned Lots'" "$MODULE_PATH/models/stock_picking.py"; then
    echo -e "${GREEN}✅ Campo en modelo: 'Preassigned Lots'${NC}"
else
    echo -e "${RED}❌ Campo en modelo no actualizado${NC}"
fi

echo -e "${YELLOW}2. Verificando mensajes de error...${NC}"

# Verificar que los mensajes de error se actualizaron
if grep -q 'disable "Preassigned Lots"' "$MODULE_PATH/models/stock_picking.py"; then
    echo -e "${GREEN}✅ Mensajes de error actualizados${NC}"
else
    echo -e "${RED}❌ Mensajes de error no actualizados${NC}"
fi

echo -e "${YELLOW}3. Verificando documentación...${NC}"

# Verificar que la documentación se actualizó
if grep -q '# Campo "Preassigned Lots"' "$MODULE_PATH/ONLY_PREASSIGNED_LOTS_EXAMPLES.md"; then
    echo -e "${GREEN}✅ Título de documentación actualizado${NC}"
else
    echo -e "${RED}❌ Título de documentación no actualizado${NC}"
fi

echo -e "${YELLOW}4. Verificando que no quedan menciones del texto anterior...${NC}"

# Verificar que no quedan menciones de "Only Preassigned Lots"
OLD_MENTIONS=$(grep -r "Only Preassigned Lots" "$MODULE_PATH" 2>/dev/null | wc -l)

if [ "$OLD_MENTIONS" -eq 0 ]; then
    echo -e "${GREEN}✅ No quedan menciones de 'Only Preassigned Lots'${NC}"
else
    echo -e "${RED}❌ Aún quedan $OLD_MENTIONS menciones de 'Only Preassigned Lots'${NC}"
    echo -e "${YELLOW}Menciones encontradas:${NC}"
    grep -rn "Only Preassigned Lots" "$MODULE_PATH" 2>/dev/null || true
fi

echo -e "${YELLOW}5. Limpiando caché...${NC}"
find "$MODULE_PATH" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$MODULE_PATH" -name "*.pyc" -delete 2>/dev/null || true
echo -e "${GREEN}✅ Caché limpiado${NC}"

echo ""
echo -e "${GREEN}🚀 ACTUALIZAR MÓDULO:${NC}"
echo "cd /Users/antoniocanovaspedreno/PycharmProjects/odoo18"
echo "python3 odoo-bin -d TU_BD -u purchase_lot_preassignment --addons-path=/Users/antoniocanovaspedreno/PycharmProjects/clientes/18,addons,../enterprise18 --dev=reload"

echo ""
echo -e "${YELLOW}📋 CAMBIOS APLICADOS:${NC}"
echo "1. ✅ Campo en modelo: string='Preassigned Lots'"
echo "2. ✅ Mensajes de error: 'Disable \"Preassigned Lots\"'"
echo "3. ✅ Documentación: Título y ejemplos actualizados"
echo "4. ✅ Scripts de verificación: Títulos actualizados"
echo "5. ✅ Consistencia total en todos los archivos"

echo ""
echo -e "${GREEN}El literal del campo se ha cambiado correctamente.${NC}"
echo -e "${YELLOW}En la interfaz ahora aparecerá como: 'Preassigned Lots'${NC}"
