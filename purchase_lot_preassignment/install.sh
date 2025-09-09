#!/bin/bash

# Script de instalación rápida para Purchase Lot Preassignment
# Para Odoo 18 Enterprise

echo "=== Instalación Purchase Lot Preassignment ==="

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuración
ODOO_PATH="/Users/antoniocanovaspedreno/PycharmProjects/odoo18"
ADDONS_PATH="/Users/antoniocanovaspedreno/PycharmProjects/dev18"
MODULE_NAME="purchase_lot_preassignment"

echo -e "${YELLOW}Verificando rutas...${NC}"

# Verificar que Odoo existe
if [ ! -d "$ODOO_PATH" ]; then
    echo -e "${RED}Error: Directorio Odoo no encontrado en $ODOO_PATH${NC}"
    exit 1
fi

# Verificar que el módulo existe
if [ ! -d "$ADDONS_PATH/$MODULE_NAME" ]; then
    echo -e "${RED}Error: Módulo no encontrado en $ADDONS_PATH/$MODULE_NAME${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Rutas verificadas${NC}"

# Función para ejecutar comandos Odoo
run_odoo_cmd() {
    local cmd="$1"
    echo -e "${YELLOW}Ejecutando: $cmd${NC}"
    
    cd "$ODOO_PATH"
    python3 odoo-bin "$@"
}

echo -e "${YELLOW}Instalando módulo $MODULE_NAME...${NC}"

# Comandos de instalación
DATABASE="your_database_name"  # Cambiar por el nombre real de tu BD

echo -e "${YELLOW}IMPORTANTE: Cambia 'your_database_name' por tu base de datos real${NC}"
echo -e "${YELLOW}Comando manual:${NC}"
echo "cd $ODOO_PATH"
echo "python3 odoo-bin -d your_database_name -i $MODULE_NAME --addons-path=$ADDONS_PATH,addons,../enterprise18 --dev=reload"

echo -e "${GREEN}=== Instalación completada ===${NC}"
echo -e "${YELLOW}Pasos siguientes:${NC}"
echo "1. Cambiar 'your_database_name' por tu BD real"
echo "2. Ejecutar el comando manual mostrado arriba"
echo "3. Ir a Aplicaciones > Buscar 'Purchase Lot Preassignment'"
echo "4. Instalar el módulo"
echo "5. Probar con un pedido de compra que tenga productos con trazabilidad"

echo -e "${GREEN}Documentación completa en README.md${NC}"
