#!/bin/bash

# Script de ayuda para gestionar el módulo product_reference
# Usar desde el directorio raíz de Odoo

MODULE_NAME="product_reference"
MODULE_PATH="$(pwd)/$MODULE_NAME"

echo "=== Gestión del Módulo Product Reference ==="
echo ""

# Verificar si estamos en el directorio correcto
if [ ! -f "odoo-bin" ]; then
    echo "❌ Error: Este script debe ejecutarse desde el directorio raíz de Odoo"
    echo "   Asegúrate de estar en el directorio que contiene 'odoo-bin'"
    exit 1
fi

# Verificar si el módulo existe
if [ ! -d "$MODULE_PATH" ]; then
    echo "❌ Error: No se encuentra el módulo '$MODULE_NAME' en $MODULE_PATH"
    echo "   Copia el módulo al directorio de addons primero"
    exit 1
fi

echo "✅ Módulo encontrado en: $MODULE_PATH"
echo ""

# Función para mostrar ayuda
show_help() {
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos disponibles:"
    echo "  install     - Instalar el módulo"
    echo "  upgrade     - Actualizar el módulo"
    echo "  uninstall   - Desinstalar el módulo"
    echo "  test        - Ejecutar tests del módulo"
    echo "  shell       - Abrir shell de Odoo con el módulo cargado"
    echo "  help        - Mostrar esta ayuda"
    echo ""
    echo "Ejemplo:"
    echo "  $0 install"
    echo ""
}

# Función para instalar módulo
install_module() {
    echo "🔧 Instalando módulo $MODULE_NAME..."
    python3 odoo-bin -d test_db -i $MODULE_NAME --stop-after-init --log-level=info
    echo "✅ Instalación completada"
}

# Función para actualizar módulo
upgrade_module() {
    echo "🔄 Actualizando módulo $MODULE_NAME..."
    python3 odoo-bin -d test_db -u $MODULE_NAME --stop-after-init --log-level=info
    echo "✅ Actualización completada"
}

# Función para desinstalar módulo
uninstall_module() {
    echo "🗑️  Desinstalando módulo $MODULE_NAME..."
    echo "⚠️  Nota: La desinstalación debe hacerse desde la interfaz web de Odoo"
    echo "   Ir a Apps > $MODULE_NAME > Uninstall"
}

# Función para ejecutar tests
test_module() {
    echo "🧪 Ejecutando tests para $MODULE_NAME..."
    python3 odoo-bin -d test_db --test-enable --stop-after-init -i $MODULE_NAME --log-level=test
    echo "✅ Tests completados"
}

# Función para abrir shell
open_shell() {
    echo "🐚 Abriendo shell de Odoo..."
    python3 odoo-bin shell -d test_db
}

# Procesar comando
case "${1:-help}" in
    install)
        install_module
        ;;
    upgrade)
        upgrade_module
        ;;
    uninstall)
        uninstall_module
        ;;
    test)
        test_module
        ;;
    shell)
        open_shell
        ;;
    help|*)
        show_help
        ;;
esac
