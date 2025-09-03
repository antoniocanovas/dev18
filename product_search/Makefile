# ============================================
# Makefile - Búsqueda Inteligente de Productos
# ============================================

# Configuración
MODULE_NAME := product_search
ODOO_PATH := /opt/odoo
ADDONS_PATH := /opt/odoo/addons
DB_NAME := odoo_dev
ODOO_USER := odoo
PYTHON := python3

# Colores para output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Metas predeterminadas
.PHONY: help install test clean dev setup deploy backup validate lint docs

# Meta por defecto
help: ## Mostrar esta ayuda
	@echo "$(BLUE)Búsqueda Inteligente de Productos - Makefile$(NC)"
	@echo ""
	@echo "$(YELLOW)Comandos disponibles:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ============================================
# Desarrollo Local
# ============================================

setup: ## Configurar entorno de desarrollo completo
	@echo "$(BLUE)🚀 Configurando entorno de desarrollo...$(NC)"
	@chmod +x scripts/dev_setup.sh
	@./scripts/dev_setup.sh all

dev: ## Configurar entorno básico de desarrollo
	@echo "$(BLUE)⚙️  Configurando entorno básico...$(NC)"
	@chmod +x scripts/dev_setup.sh
	@./scripts/dev_setup.sh setup

install: ## Instalar/actualizar módulo en Odoo
	@echo "$(BLUE)📦 Instalando módulo...$(NC)"
	@chmod +x scripts/dev_setup.sh
	@./scripts/dev_setup.sh install

create-db: ## Crear base de datos de desarrollo
	@echo "$(BLUE)🗄️  Creando base de datos...$(NC)"
	@chmod +x scripts/dev_setup.sh
	@./scripts/dev_setup.sh create-db

test-data: ## Generar datos de prueba
	@echo "$(BLUE)📊 Generando datos de prueba...$(NC)"
	@chmod +x scripts/dev_setup.sh
	@./scripts/dev_setup.sh test-data

# ============================================
# Testing y Validación
# ============================================

test: ## Ejecutar todos los tests
	@echo "$(BLUE)🧪 Ejecutando tests...$(NC)"
	@chmod +x scripts/dev_setup.sh
	@./scripts/dev_setup.sh test

test-unit: ## Ejecutar solo tests unitarios
	@echo "$(BLUE)🧪 Ejecutando tests unitarios...$(NC)"
	@cd $(ODOO_PATH) && $(PYTHON) odoo-bin --test-tags=$(MODULE_NAME) --stop-after-init --database=$(DB_NAME) --log-level=test

validate: ## Validar sintaxis del código
	@echo "$(BLUE)✅ Validando código...$(NC)"
	@chmod +x scripts/dev_setup.sh
	@./scripts/dev_setup.sh validate

lint: ## Ejecutar linter en el código Python
	@echo "$(BLUE)🔍 Analizando código con linter...$(NC)"
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 --max-line-length=120 --exclude=__pycache__ models/ wizard/ tests/; \
	else \
		echo "$(YELLOW)⚠️  flake8 no está instalado. Ejecutando validación básica...$(NC)"; \
		find . -name "*.py" -exec $(PYTHON) -m py_compile {} \; ; \
	fi

format: ## Formatear código Python con autopep8
	@echo "$(BLUE)✨ Formateando código...$(NC)"
	@if command -v autopep8 >/dev/null 2>&1; then \
		find . -name "*.py" -exec autopep8 --in-place --aggressive --aggressive {} \; ; \
		echo "$(GREEN)✅ Código formateado$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  autopep8 no está instalado$(NC)"; \
	fi

# ============================================
# Deployment
# ============================================

deploy-staging: ## Deployment a staging
	@echo "$(BLUE)🚀 Deployando a staging...$(NC)"
	@ENVIRONMENT=staging chmod +x scripts/deploy.sh
	@ENVIRONMENT=staging ./scripts/deploy.sh deploy

deploy-prod: ## Deployment a producción
	@echo "$(BLUE)🚀 Deployando a producción...$(NC)"
	@echo "$(RED)⚠️  CUIDADO: Deployment a producción$(NC)"
	@read -p "¿Está seguro? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@ENVIRONMENT=production chmod +x scripts/deploy.sh
	@ENVIRONMENT=production ./scripts/deploy.sh deploy

rollback: ## Rollback del último deployment
	@echo "$(BLUE)🔄 Ejecutando rollback...$(NC)"
	@chmod +x scripts/deploy.sh
	@./scripts/deploy.sh rollback

# ============================================
# Backup y Mantenimiento
# ============================================

backup: ## Crear backup completo
	@echo "$(BLUE)💾 Creando backup...$(NC)"
	@chmod +x scripts/dev_setup.sh
	@./scripts/dev_setup.sh backup

clean: ## Limpiar archivos temporales y caché
	@echo "$(BLUE)🧹 Limpiando archivos temporales...$(NC)"
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.log" -delete 2>/dev/null || true
	@rm -rf .pytest_cache/ .coverage htmlcov/ 2>/dev/null || true
	@echo "$(GREEN)✅ Limpieza completada$(NC)"

clean-all: clean ## Limpieza profunda (incluye backups antiguos)
	@echo "$(BLUE)🧹 Limpieza profunda...$(NC)"
	@rm -rf backups/backup_* 2>/dev/null || true
	@rm -rf /tmp/odoo_* 2>/dev/null || true
	@echo "$(GREEN)✅ Limpieza profunda completada$(NC)"

# ============================================
# Monitoreo y Logs
# ============================================

logs: ## Monitorear logs en tiempo real
	@echo "$(BLUE)📋 Monitoreando logs...$(NC)"
	@chmod +x scripts/dev_setup.sh
	@./scripts/dev_setup.sh logs

tail-odoo: ## Ver logs de Odoo (tail -f)
	@echo "$(BLUE)📋 Monitoreando logs de Odoo...$(NC)"
	@tail -f /var/log/odoo/odoo.log 2>/dev/null || tail -f $(ODOO_PATH)/odoo.log 2>/dev/null || echo "$(RED)❌ No se encontraron logs$(NC)"

grep-errors: ## Filtrar solo errores en logs
	@echo "$(BLUE)🔍 Buscando errores en logs...$(NC)"
	@tail -100 /var/log/odoo/odoo.log 2>/dev/null | grep -i error || echo "$(GREEN)✅ No se encontraron errores recientes$(NC)"

# ============================================
# Documentación
# ============================================

docs: ## Generar documentación
	@echo "$(BLUE)📚 Generando documentación...$(NC)"
	@if command -v sphinx-build >/dev/null 2>&1; then \
		sphinx-build -b html docs/ docs/_build/html/; \
		echo "$(GREEN)✅ Documentación generada en docs/_build/html/$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  Sphinx no está instalado. Creando documentación básica...$(NC)"; \
		@$(MAKE) docs-simple; \
	fi

docs-simple: ## Generar documentación simple
	@echo "$(BLUE)📚 Creando documentación simple...$(NC)"
	@mkdir -p docs/generated
	@echo "# Documentación del Módulo $(MODULE_NAME)" > docs/generated/README.md
	@echo "" >> docs/generated/README.md
	@echo "## Archivos del módulo:" >> docs/generated/README.md
	@find . -name "*.py" -not -path "./__pycache__/*" -exec echo "- {}" \; >> docs/generated/README.md
	@echo "$(GREEN)✅ Documentación simple creada en docs/generated/$(NC)"

# ============================================
# Análisis y Métricas
# ============================================

stats: ## Mostrar estadísticas del módulo
	@echo "$(BLUE)📊 Estadísticas del módulo:$(NC)"
	@echo "$(YELLOW)Archivos Python:$(NC) $$(find . -name '*.py' | wc -l)"
	@echo "$(YELLOW)Archivos XML:$(NC) $$(find . -name '*.xml' | wc -l)"
	@echo "$(YELLOW)Líneas de código Python:$(NC) $$(find . -name '*.py' -exec wc -l {} + | tail -1 | awk '{print $$1}')"
	@echo "$(YELLOW)Líneas de código XML:$(NC) $$(find . -name '*.xml' -exec wc -l {} + | tail -1 | awk '{print $$1}' || echo '0')"
	@echo "$(YELLOW)Tests:$(NC) $$(grep -r 'def test_' tests/ | wc -l || echo '0')"
	@echo "$(YELLOW)Tamaño total:$(NC) $$(du -sh . | cut -f1)"

complexity: ## Análizar complejidad del código
	@echo "$(BLUE)🔍 Analizando complejidad...$(NC)"
	@if command -v radon >/dev/null 2>&1; then \
		radon cc -s models/ wizard/; \
	else \
		echo "$(YELLOW)⚠️  radon no está instalado$(NC)"; \
		echo "Instalar con: pip install radon"; \
	fi

# ============================================
# Instalación de Dependencias
# ============================================

install-dev-deps: ## Instalar dependencias de desarrollo
	@echo "$(BLUE)📦 Instalando dependencias de desarrollo...$(NC)"
	@pip3 install --user flake8 autopep8 pytest coverage
	@echo "$(GREEN)✅ Dependencias instaladas$(NC)"

install-docs-deps: ## Instalar dependencias para documentación
	@echo "$(BLUE)📦 Instalando dependencias de documentación...$(NC)"
	@pip3 install --user sphinx sphinx-rtd-theme
	@echo "$(GREEN)✅ Dependencias de documentación instaladas$(NC)"

# ============================================
# Utilidades
# ============================================

check-deps: ## Verificar dependencias del sistema
	@echo "$(BLUE)🔍 Verificando dependencias...$(NC)"
	@chmod +x scripts/dev_setup.sh
	@./scripts/dev_setup.sh check

shell: ## Abrir shell de Odoo con el módulo cargado
	@echo "$(BLUE)🐚 Abriendo shell de Odoo...$(NC)"
	@cd $(ODOO_PATH) && $(PYTHON) odoo-bin shell -c /etc/odoo/odoo.conf -d $(DB_NAME)

psql: ## Conectar a la base de datos PostgreSQL
	@echo "$(BLUE)🗄️  Conectando a PostgreSQL...$(NC)"
	@sudo -u postgres psql $(DB_NAME)

restart-odoo: ## Reiniciar servicio de Odoo
	@echo "$(BLUE)🔄 Reiniciando Odoo...$(NC)"
	@sudo systemctl restart odoo
	@echo "$(GREEN)✅ Odoo reiniciado$(NC)"

status: ## Mostrar estado del sistema
	@echo "$(BLUE)📊 Estado del sistema:$(NC)"
	@echo "$(YELLOW)Odoo:$(NC) $$(systemctl is-active odoo 2>/dev/null || echo 'No instalado como servicio')"
	@echo "$(YELLOW)PostgreSQL:$(NC) $$(systemctl is-active postgresql 2>/dev/null || echo 'No encontrado')"
	@echo "$(YELLOW)Espacio en disco:$(NC) $$(df -h / | awk 'NR==2{print $$5}')"
	@echo "$(YELLOW)Memoria libre:$(NC) $$(free -h | awk 'NR==2{print $$7}')"

# ============================================
# Targets de conveniencia
# ============================================

quick-test: clean validate test ## Limpieza + validación + tests rápidos
	@echo "$(GREEN)✅ Quick test completado$(NC)"

full-check: clean validate test lint stats ## Verificación completa del código
	@echo "$(GREEN)✅ Verificación completa terminada$(NC)"

dev-setup: setup test-data ## Configuración completa para desarrollo
	@echo "$(GREEN)✅ Entorno de desarrollo listo$(NC)"

release-prep: clean validate test lint docs ## Preparar para release
	@echo "$(BLUE)📦 Preparando release...$(NC)"
	@echo "$(GREEN)✅ Release preparado$(NC)"

# ============================================
# Información del Makefile
# ============================================

info: ## Mostrar información del proyecto
	@echo "$(BLUE)ℹ️  Información del proyecto:$(NC)"
	@echo "$(YELLOW)Módulo:$(NC) $(MODULE_NAME)"
	@echo "$(YELLOW)Ruta Odoo:$(NC) $(ODOO_PATH)"
	@echo "$(YELLOW)Base de datos:$(NC) $(DB_NAME)"
	@echo "$(YELLOW)Usuario Odoo:$(NC) $(ODOO_USER)"
	@echo "$(YELLOW)Python:$(NC) $$($(PYTHON) --version)"
	@echo "$(YELLOW)Directorio actual:$(NC) $$(pwd)"

# Meta especial para evitar errores con archivos del mismo nombre
%:
	@if [ -f "$@" ]; then \
		echo "$(YELLOW)⚠️  Archivo '$@' existe. Use 'make $@ --force' si es necesario$(NC)"; \
	fi