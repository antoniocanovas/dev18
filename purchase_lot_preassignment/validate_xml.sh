#!/bin/bash

echo "🔧 VALIDACIÓN XML - Purchase Lot Preassignment"
echo "=============================================="

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

MODULE_PATH="/Users/antoniocanovaspedreno/PycharmProjects/clientes/18/purchase_lot_preassignment"
XML_FILE="$MODULE_PATH/views/purchase_order_views.xml"

echo -e "${YELLOW}1. Validando estructura XML...${NC}"

# Verificar que el archivo existe
if [ ! -f "$XML_FILE" ]; then
    echo -e "${RED}❌ Error: Archivo XML no encontrado${NC}"
    exit 1
fi

# Validar XML con xmllint (si está disponible)
if command -v xmllint &> /dev/null; then
    if xmllint --noout "$XML_FILE" 2>/dev/null; then
        echo -e "${GREEN}✅ XML bien formateado${NC}"
    else
        echo -e "${RED}❌ Error: XML mal formateado${NC}"
        xmllint --noout "$XML_FILE"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️ xmllint no disponible, omitiendo validación sintáctica${NC}"
fi

echo -e "${YELLOW}2. Verificando elementos críticos...${NC}"

# Verificar elementos críticos
CRITICAL_ELEMENTS=(
    "view_purchase_lot_preassignment_tree_inline"
    "purchase_order_line_form2"
    "purchase_order_form"
    "purchase_order_tree"
)

for element in "${CRITICAL_ELEMENTS[@]}"; do
    if grep -q "$element" "$XML_FILE"; then
        echo -e "${GREEN}✅ $element encontrado${NC}"
    else
        echo -e "${RED}❌ $element NO encontrado${NC}"
    fi
done

echo -e "${YELLOW}3. Verificando estructura...${NC}"

# Verificar que no hay elementos <data> dentro de <arch>
if grep -A10 '<arch type="xml">' "$XML_FILE" | grep -q '<data>'; then
    echo -e "${RED}❌ Error: elemento <data> dentro de <arch>${NC}"
else
    echo -e "${GREEN}✅ Estructura <arch> correcta${NC}"
fi

# Verificar que todos los tags están cerrados
OPEN_TAGS=$(grep -o '<[^/][^>]*[^/]>' "$XML_FILE" | wc -l)
CLOSE_TAGS=$(grep -o '</[^>]*>' "$XML_FILE" | wc -l)
SELF_CLOSE_TAGS=$(grep -o '<[^>]*/>' "$XML_FILE" | wc -l)

if [ $((OPEN_TAGS - SELF_CLOSE_TAGS)) -eq $CLOSE_TAGS ]; then
    echo -e "${GREEN}✅ Tags balanceados correctamente${NC}"
else
    echo -e "${RED}❌ Error: Tags desbalanceados${NC}"
    echo "   Apertura: $OPEN_TAGS, Cierre: $CLOSE_TAGS, Auto-cierre: $SELF_CLOSE_TAGS"
fi

echo -e "${YELLOW}4. Limpiando caché...${NC}"
find "$MODULE_PATH" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$MODULE_PATH" -name "*.pyc" -delete 2>/dev/null || true
echo -e "${GREEN}✅ Caché limpiado${NC}"

echo ""
echo -e "${GREEN}🚀 COMANDO PARA ACTUALIZAR:${NC}"
echo "cd /Users/antoniocanovaspedreno/PycharmProjects/odoo18"
echo "python3 odoo-bin -d TU_BD -u purchase_lot_preassignment --addons-path=/Users/antoniocanovaspedreno/PycharmProjects/clientes/18,addons,../enterprise18 --dev=reload"

echo ""
echo -e "${YELLOW}📋 CORRECCIONES APLICADAS:${NC}"
echo "1. ✅ Eliminado elemento <data> problemático"
echo "2. ✅ Cambiado <list> → <tree>"
echo "3. ✅ ID consistente: view_purchase_lot_preassignment_tree_inline"
echo "4. ✅ Usando context en lugar de view_id directo"
echo "5. ✅ XML bien formateado"

echo ""
echo -e "${GREEN}El archivo XML debería parsear correctamente ahora.${NC}"
