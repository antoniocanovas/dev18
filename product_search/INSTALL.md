# 🚀 Guía de Instalación - Búsqueda Inteligente de Productos

## 📋 Requisitos Previos

### Sistema Operativo
- ✅ Ubuntu 20.04+ / Debian 10+
- ✅ CentOS 8+ / RHEL 8+
- ✅ macOS 10.15+
- ✅ Windows 10+ (con WSL recomendado)

### Software Requerido
- ✅ **Odoo 18.0+** (Community o Enterprise)
- ✅ **Python 3.9+**
- ✅ **PostgreSQL 12+**
- ✅ **Navegador moderno** (Chrome 90+, Firefox 88+, Safari 14+)

### Dependencias de Odoo
Los siguientes módulos deben estar instalados:
- `base` ✅ (incluido por defecto)
- `product` ✅ (gestión de productos)
- `sale` ✅ (módulo de ventas)
- `mail` ✅ (sistema de mensajería)

## 🔧 Instalación Paso a Paso

### Método 1: Instalación desde Directorio Local

1. **Copiar módulo al directorio de addons:**
```bash
# Desde el directorio donde está el módulo
cp -r product_search /path/to/odoo/addons/

# O crear symlink (recomendado para desarrollo)
ln -s /Users/antoniocanovaspedreno/PycharmProjects/dev18/product_search /path/to/odoo/addons/
```

2. **Verificar permisos:**
```bash
# Asegurar permisos correctos
sudo chown -R odoo:odoo /path/to/odoo/addons/product_search
sudo chmod -R 755 /path/to/odoo/addons/product_search
```

3. **Reiniciar servidor Odoo:**
```bash
# Detener Odoo
sudo systemctl stop odoo

# Iniciar con actualización de addons
sudo -u odoo /opt/odoo/odoo-bin -c /etc/odoo/odoo.conf -u all -d tu_database --stop-after-init

# Reiniciar servicio
sudo systemctl start odoo
```

### Método 2: Instalación en Modo Desarrollo

1. **Agregar ruta al archivo de configuración:**
```ini
# En /etc/odoo/odoo.conf
[options]
addons_path = /opt/odoo/addons,/path/to/custom/addons,/Users/antoniocanovaspedreno/PycharmProjects/dev18
```

2. **Iniciar Odoo en modo desarrollo:**
```bash
./odoo-bin --addons-path=/Users/antoniocanovaspedreno/PycharmProjects/dev18 --dev=all
```

### Método 3: Instalación con Docker

1. **Crear archivo docker-compose.yml:**
```yaml
version: '3.8'
services:
  odoo:
    image: odoo:18.0
    depends_on:
      - db
    ports:
      - "8069:8069"
    volumes:
      - ./product_search:/mnt/extra-addons/product_search
      - odoo-data:/var/lib/odoo
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo_password
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo_password
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  odoo-data:
  postgres-data:
```

2. **Ejecutar contenedores:**
```bash
docker-compose up -d
```

## 🎯 Activación del Módulo

### 1. Acceder a Odoo
- Abrir navegador en `http://localhost:8069`
- Iniciar sesión como administrador

### 2. Activar Modo Desarrollador
- Ir a **Configuración** → **Activar modo de desarrollador**
- O agregar `?debug=1` a la URL

### 3. Actualizar Lista de Aplicaciones
- Ir a **Aplicaciones**
- Hacer clic en **Actualizar Lista de Aplicaciones**
- Confirmar cuando se solicite

### 4. Instalar el Módulo
- Buscar "**Búsqueda Inteligente de Productos**"
- Hacer clic en **Instalar**
- Esperar confirmación de instalación exitosa

### 5. Verificar Instalación
- Verificar menú "🔍 **Búsqueda Inteligente**" en la barra principal
- Comprobar acceso desde **Ventas** → **Búsqueda de Productos**

## ✅ Verificación Post-Instalación

### 1. Verificar Base de Datos
```sql
-- Conectar a PostgreSQL y verificar tablas
\c tu_database
\dt product_search*

-- Debe mostrar:
-- product_search
-- product_search_result  
-- product_search_interaction
-- product_search_learning_pattern
```

### 2. Verificar Logs
```bash
# Revisar logs de Odoo para errores
tail -f /var/log/odoo/odoo.log | grep "product_search"

# Buscar mensajes de instalación exitosa:
# "✅ Se encontraron X productos activos"
# "🎉 ¡Módulo de Búsqueda Inteligente instalado correctamente!"
```

### 3. Ejecutar Tests (Opcional)
```bash
# Ejecutar tests automatizados
./odoo-bin -c odoo.conf -d test_db --test-tags=product_search --stop-after-init
```

## 🎨 Primera Configuración

### 1. Crear Productos de Prueba
Si no tienes productos en tu sistema:

```python
# Ejecutar en shell de Odoo (Configuración → Técnico → Terminal)
products_data = [
    {'name': 'HP Pavilion Gaming Laptop', 'list_price': 1299.99},
    {'name': 'Samsung Galaxy S21 Ultra', 'list_price': 899.99},
    {'name': 'Dell UltraSharp 4K Monitor', 'list_price': 599.99},
    {'name': 'Canon EOS R5 Camera', 'list_price': 2499.99},
    {'name': 'Sony WH-1000XM4 Headphones', 'list_price': 249.99}
]

for data in products_data:
    env['product.template'].create(data)
```

### 2. Configurar Parámetros del Sistema
Ir a **Configuración** → **Técnico** → **Parámetros** → **Parámetros del Sistema**

```
product_search.max_results = 50
product_search.enable_learning = True
product_search.interaction_threshold = 30
product_search.debug_mode = False
```

### 3. Configurar Permisos de Usuario
- **Usuarios normales:** Acceso básico a búsquedas
- **Gerentes de ventas:** Acceso a analytics y patrones

## 🧪 Prueba de Funcionamiento

### 1. Búsqueda Básica
1. Ir a **🔍 Búsqueda Inteligente** → **Nueva Búsqueda**
2. Escribir: "Laptop HP para gaming"
3. Hacer clic en **🔍 Buscar Productos**
4. Verificar resultados ordenados por relevancia

### 2. Sistema Conversacional
1. Escribir búsqueda ambigua: "Computadora"
2. El sistema debe activar el chat conversacional
3. Responder las preguntas paso a paso
4. Verificar mejora en resultados

### 3. Aprendizaje Automático
1. Realizar varias búsquedas similares
2. Ir a **🧠 Patrones de Aprendizaje** (solo gerentes)
3. Verificar creación automática de patrones

## 🔧 Solución de Problemas Comunes

### Error: "Módulo no encontrado"
```bash
# Verificar ruta en addons_path
grep addons_path /etc/odoo/odoo.conf

# Verificar permisos
ls -la /path/to/odoo/addons/product_search

# Reiniciar Odoo
sudo systemctl restart odoo
```

### Error: "Dependencias faltantes"
```bash
# Verificar módulos base instalados
./odoo-bin shell -c odoo.conf -d tu_database
>>> env['ir.module.module'].search([('name', 'in', ['product', 'sale'])])
```

### Error: "Base de datos sin productos"
```sql
-- Verificar productos existentes
SELECT COUNT(*) FROM product_template WHERE active = true;

-- Si es 0, crear productos de prueba
```

### Error: "Permisos insuficientes"
```bash
# Verificar usuario y grupos
id odoo

# Corregir permisos
sudo chown -R odoo:odoo /opt/odoo
sudo chmod -R 755 /opt/odoo
```

## 📊 Monitoreo y Mantenimiento

### 1. Logs Importantes
```bash
# Monitorear actividad del módulo
tail -f /var/log/odoo/odoo.log | grep -E "(product_search|🔍|🤖)"
```

### 2. Estadísticas de Uso
- Ir a **🧠 Patrones de Aprendizaje**
- Revisar búsquedas más frecuentes
- Analizar tasa de éxito

### 3. Limpieza Periódica
```python
# Limpiar búsquedas antiguas (ejecutar mensualmente)
old_searches = env['product.search'].search([
    ('create_date', '<', fields.Date.today() - timedelta(days=90)),
    ('state', 'in', ['draft', 'no_results'])
])
old_searches.unlink()
```

## 🆙 Actualizaciones Futuras

### Backup antes de actualizar
```bash
# Backup de base de datos
pg_dump -U odoo -h localhost tu_database > backup_pre_update.sql

# Backup de archivos personalizados
tar -czf custom_addons_backup.tar.gz /path/to/custom/addons
```

### Proceso de actualización
```bash
# 1. Detener Odoo
sudo systemctl stop odoo

# 2. Actualizar código del módulo
git pull origin main  # Si usas Git

# 3. Actualizar módulo en Odoo
sudo -u odoo ./odoo-bin -c odoo.conf -u product_search -d tu_database --stop-after-init

# 4. Reiniciar servicio
sudo systemctl start odoo
```

## 📞 Soporte y Recursos

### Documentación
- **README.md** - Documentación completa
- **Wiki interna** - Casos de uso específicos
- **Videos de entrenamiento** - Disponibles en el portal interno

### Canales de Soporte
- 🎫 **Sistema de tickets** - Para reportar bugs
- 💬 **Chat interno** - Soporte rápido
- 📧 **Email** - soporte@tuempresa.com
- 📞 **Teléfono** - +1 (555) 123-4567

### Recursos Adicionales
- **Foro de usuarios** - Comunidad y mejores prácticas
- **Repositorio GitHub** - Código fuente y issues
- **Roadmap** - Funcionalidades futuras

---

## ✅ Lista de Verificación Final

Antes de considerar la instalación completa:

- [ ] ✅ Odoo 18.0+ instalado y funcionando
- [ ] ✅ Módulos base (product, sale) instalados
- [ ] ✅ Módulo "Búsqueda Inteligente" instalado sin errores
- [ ] ✅ Menú "🔍 Búsqueda Inteligente" visible
- [ ] ✅ Productos de prueba creados
- [ ] ✅ Búsqueda básica funcionando
- [ ] ✅ Sistema conversacional activo
- [ ] ✅ Permisos de usuario configurados
- [ ] ✅ Logs sin errores críticos
- [ ] ✅ Tests automatizados pasando (opcional)
- [ ] ✅ Equipo capacitado en uso básico

**🎉 ¡Instalación completada exitosamente!**

Para soporte adicional, consulta la documentación técnica o contacta al equipo de desarrollo.