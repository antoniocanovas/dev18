#!/bin/bash

# ============================================
# Script de Deployment - Búsqueda Inteligente de Productos
# ============================================

set -e  # Salir en caso de error

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Configuración
ENVIRONMENT=${ENVIRONMENT:-"production"}
BACKUP_RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}
MODULE_NAME="product_search"

# Configuración por entorno
case $ENVIRONMENT in
    "production")
        ODOO_USER="odoo"
        ODOO_SERVICE="odoo"
        BACKUP_DIR="/var/backups/odoo"
        LOG_LEVEL="info"
        ;;
    "staging")
        ODOO_USER="odoo-staging"
        ODOO_SERVICE="odoo-staging"
        BACKUP_DIR="/var/backups/odoo-staging"
        LOG_LEVEL="debug"
        ;;
    "test")
        ODOO_USER="odoo-test"
        ODOO_SERVICE="odoo-test"
        BACKUP_DIR="/tmp/backups"
        LOG_LEVEL="test"
        ;;
esac

print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}============================================${NC}"
}

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${PURPLE}ℹ️  $1${NC}"; }

# Pre-deployment checks
pre_deployment_checks() {
    print_header "Pre-deployment Checks"
    
    # Verificar que estamos en el servidor correcto
    HOSTNAME=$(hostname)
    print_info "Deployando en servidor: $HOSTNAME"
    print_info "Entorno: $ENVIRONMENT"
    
    # Verificar servicios
    if ! systemctl is-active --quiet $ODOO_SERVICE; then
        print_warning "Servicio $ODOO_SERVICE no está corriendo"
    else
        print_success "Servicio $ODOO_SERVICE está activo"
    fi
    
    # Verificar espacio en disco
    DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ $DISK_USAGE -gt 90 ]; then
        print_error "Espacio en disco crítico: ${DISK_USAGE}%"
        exit 1
    else
        print_success "Espacio en disco OK: ${DISK_USAGE}%"
    fi
    
    # Verificar memoria
    MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f\n", $3*100/$2}')
    if [ $MEMORY_USAGE -gt 90 ]; then
        print_warning "Uso de memoria alto: ${MEMORY_USAGE}%"
    else
        print_success "Memoria OK: ${MEMORY_USAGE}%"
    fi
}

# Crear backup completo
create_backup() {
    print_header "Creando Backup Pre-deployment"
    
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    mkdir -p $BACKUP_DIR
    
    # Backup de archivos del módulo
    print_info "Backing up module files..."
    tar -czf "$BACKUP_DIR/${MODULE_NAME}_files_$TIMESTAMP.tar.gz" \
        -C /opt/odoo/addons/$MODULE_NAME .
    
    # Backup de base de datos
    print_info "Backing up database..."
    sudo -u postgres pg_dump odoo_production | gzip > \
        "$BACKUP_DIR/odoo_db_$TIMESTAMP.sql.gz"
    
    # Backup de configuración
    print_info "Backing up configuration..."
    cp /etc/odoo/odoo.conf "$BACKUP_DIR/odoo_conf_$TIMESTAMP.conf"
    
    print_success "Backup creado en $BACKUP_DIR"
    
    # Limpiar backups antiguos
    find $BACKUP_DIR -name "*" -type f -mtime +$BACKUP_RETENTION_DAYS -delete
    print_info "Backups antiguos limpiados (>${BACKUP_RETENTION_DAYS} días)"
}

# Deployment del módulo
deploy_module() {
    print_header "Deployando Módulo"
    
    # Detener servicio Odoo
    print_info "Deteniendo servicio Odoo..."
    systemctl stop $ODOO_SERVICE
    
    # Copiar archivos del módulo
    print_info "Copiando archivos del módulo..."
    rsync -av --delete ./ /opt/odoo/addons/$MODULE_NAME/
    
    # Configurar permisos
    print_info "Configurando permisos..."
    chown -R $ODOO_USER:$ODOO_USER /opt/odoo/addons/$MODULE_NAME
    chmod -R 755 /opt/odoo/addons/$MODULE_NAME
    
    # Actualizar módulo en base de datos
    print_info "Actualizando módulo en base de datos..."
    sudo -u $ODOO_USER /opt/odoo/odoo-bin \
        --config=/etc/odoo/odoo.conf \
        --update=$MODULE_NAME \
        --database=odoo_production \
        --stop-after-init \
        --log-level=$LOG_LEVEL
    
    # Iniciar servicio Odoo
    print_info "Iniciando servicio Odoo..."
    systemctl start $ODOO_SERVICE
    
    # Verificar que el servicio se inició correctamente
    sleep 10
    if systemctl is-active --quiet $ODOO_SERVICE; then
        print_success "Servicio $ODOO_SERVICE iniciado correctamente"
    else
        print_error "Error iniciando servicio $ODOO_SERVICE"
        exit 1
    fi
}

# Tests post-deployment
post_deployment_tests() {
    print_header "Post-deployment Tests"
    
    # Test de conectividad HTTP
    print_info "Probando conectividad HTTP..."
    if curl -sf http://localhost:8069/web/database/selector > /dev/null; then
        print_success "Conectividad HTTP OK"
    else
        print_error "Error de conectividad HTTP"
        exit 1
    fi
    
    # Test de base de datos
    print_info "Verificando conexión a base de datos..."
    if sudo -u postgres psql -c "SELECT 1;" odoo_production > /dev/null; then
        print_success "Conexión a BD OK"
    else
        print_error "Error de conexión a BD"
        exit 1
    fi
    
    # Test específico del módulo
    print_info "Verificando instalación del módulo..."
    MODULE_INSTALLED=$(sudo -u postgres psql -t -c \
        "SELECT state FROM ir_module_module WHERE name='$MODULE_NAME';" \
        odoo_production | xargs)
    
    if [ "$MODULE_INSTALLED" = "installed" ]; then
        print_success "Módulo instalado correctamente"
    else
        print_error "Módulo no está instalado: $MODULE_INSTALLED"
        exit 1
    fi
    
    print_success "Todos los tests post-deployment pasaron ✨"
}

# Rollback en caso de fallo
rollback() {
    print_header "🔄 Ejecutando Rollback"
    
    # Buscar backup más reciente
    LATEST_BACKUP=$(ls -t $BACKUP_DIR/${MODULE_NAME}_files_*.tar.gz | head -1)
    LATEST_DB_BACKUP=$(ls -t $BACKUP_DIR/odoo_db_*.sql.gz | head -1)
    
    if [ -z "$LATEST_BACKUP" ]; then
        print_error "No se encontró backup para rollback"
        exit 1
    fi
    
    print_warning "Realizando rollback a: $LATEST_BACKUP"
    
    # Detener Odoo
    systemctl stop $ODOO_SERVICE
    
    # Restaurar archivos
    print_info "Restaurando archivos del módulo..."
    rm -rf /opt/odoo/addons/$MODULE_NAME
    mkdir -p /opt/odoo/addons/$MODULE_NAME
    tar -xzf "$LATEST_BACKUP" -C /opt/odoo/addons/$MODULE_NAME
    
    # Restaurar base de datos
    if [ -n "$LATEST_DB_BACKUP" ]; then
        print_info "Restaurando base de datos..."
        sudo -u postgres dropdb odoo_production
        sudo -u postgres createdb -O odoo odoo_production
        zcat "$LATEST_DB_BACKUP" | sudo -u postgres psql odoo_production
    fi
    
    # Configurar permisos
    chown -R $ODOO_USER:$ODOO_USER /opt/odoo/addons/$MODULE_NAME
    chmod -R 755 /opt/odoo/addons/$MODULE_NAME
    
    # Iniciar Odoo
    systemctl start $ODOO_SERVICE
    
    print_success "Rollback completado"
}

# Monitoreo post-deployment
monitor_deployment() {
    print_header "Monitoreando Deployment"
    
    print_info "Monitoreando logs por 2 minutos..."
    timeout 120 tail -f /var/log/odoo/odoo.log | grep -E "(ERROR|WARNING|$MODULE_NAME)" &
    
    # Monitorear métricas del sistema
    echo "Timestamp,CPU%,Memory%,Disk%" > /tmp/deployment_metrics.csv
    
    for i in {1..12}; do
        CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
        MEMORY=$(free | awk 'NR==2{printf "%.1f", $3*100/$2}')
        DISK=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
        
        echo "$(date '+%H:%M:%S'),$CPU,$MEMORY,$DISK" >> /tmp/deployment_metrics.csv
        sleep 10
    done
    
    print_info "Métricas guardadas en /tmp/deployment_metrics.csv"
}

# Notificaciones
send_notification() {
    local status=$1
    local message=$2
    
    # Slack notification (si está configurado)
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🚀 Deployment $MODULE_NAME [$ENVIRONMENT]: $status - $message\"}" \
            $SLACK_WEBHOOK_URL
    fi
    
    # Email notification (si está configurado)
    if [ -n "$NOTIFICATION_EMAIL" ]; then
        echo "Deployment $MODULE_NAME [$ENVIRONMENT]: $status - $message" | \
            mail -s "Odoo Deployment Notification" $NOTIFICATION_EMAIL
    fi
}

# Generar reporte de deployment
generate_report() {
    print_header "Generando Reporte de Deployment"
    
    REPORT_FILE="/tmp/deployment_report_$(date +%Y%m%d_%H%M%S).txt"
    
    cat << EOF > $REPORT_FILE
============================================
REPORTE DE DEPLOYMENT - $MODULE_NAME
============================================

Fecha: $(date)
Entorno: $ENVIRONMENT
Servidor: $(hostname)
Usuario: $(whoami)
Módulo: $MODULE_NAME

MÉTRICAS DEL SISTEMA:
- CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}')
- Memoria: $(free -h | awk 'NR==2{print $3"/"$2}')
- Disco: $(df -h / | awk 'NR==2{print $3"/"$2}')

ESTADO DE SERVICIOS:
- Odoo: $(systemctl is-active $ODOO_SERVICE)
- PostgreSQL: $(systemctl is-active postgresql)
- Nginx: $(systemctl is-active nginx 2>/dev/null || echo "N/A")

ESTADO DEL MÓDULO:
- Estado en BD: $(sudo -u postgres psql -t -c "SELECT state FROM ir_module_module WHERE name='$MODULE_NAME';" odoo_production | xargs)
- Versión: $(grep version /opt/odoo/addons/$MODULE_NAME/__manifest__.py | cut -d"'" -f2)

ARCHIVOS DE LOG:
- /var/log/odoo/odoo.log
- /var/log/postgresql/postgresql-*.log

$(if [ -f /tmp/deployment_metrics.csv ]; then
    echo "MÉTRICAS DE DEPLOYMENT:"
    cat /tmp/deployment_metrics.csv
fi)

============================================
EOF

    print_success "Reporte generado: $REPORT_FILE"
    
    # Enviar reporte por email si está configurado
    if [ -n "$NOTIFICATION_EMAIL" ]; then
        mail -s "Deployment Report - $MODULE_NAME" $NOTIFICATION_EMAIL < $REPORT_FILE
    fi
}

# Función principal
main() {
    local action=${1:-"deploy"}
    
    case $action in
        "deploy")
            pre_deployment_checks
            create_backup
            deploy_module
            post_deployment_tests
            monitor_deployment
            generate_report
            send_notification "SUCCESS" "Deployment completado exitosamente"
            print_success "🎉 Deployment completado exitosamente!"
            ;;
        "rollback")
            rollback
            send_notification "ROLLBACK" "Rollback ejecutado"
            print_success "🔄 Rollback completado"
            ;;
        "check")
            pre_deployment_checks
            ;;
        "backup")
            create_backup
            ;;
        "test")
            post_deployment_tests
            ;;
        "monitor")
            monitor_deployment
            ;;
        "report")
            generate_report
            ;;
        *)
            echo "Uso: $0 [deploy|rollback|check|backup|test|monitor|report]"
            exit 1
            ;;
    esac
}

# Verificar si se ejecuta como root
if [ "$EUID" -ne 0 ]; then
    print_error "Este script debe ejecutarse como root"
    exit 1
fi

# Ejecutar función principal
main "$@"