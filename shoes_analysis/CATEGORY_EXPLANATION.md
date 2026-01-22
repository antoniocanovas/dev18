# Configuración de Categoría "Mayorista de Calzado"

## 🎯 Objetivo Conseguido

Hemos creado una **sección completamente nueva** en los permisos de usuario, al mismo nivel que "SALES", "SERVICES", "INVENTORY", etc.

---

## 📋 Configuración Técnica

### Definición de la Categoría

```xml
<record id="module_category_shoes_dealer" model="ir.module.category">
    <field name="name">Mayorista de Calzado</field>
    <field name="description">Gestión de permisos para el sistema de mayorista de calzado</field>
    <field name="sequence">6</field>
</record>
```

### Elementos Clave

| Campo | Valor | Explicación |
|-------|-------|-------------|
| `name` | "Mayorista de Calzado" | Nombre de la sección en español |
| `description` | Descripción breve | Tooltip/ayuda contextual |
| `sequence` | `6` | Posición en la lista de secciones |
| `parent_id` | **NO definido** | Al no tener padre, se convierte en sección principal |

---

## 🔢 Orden de Secciones (Secuencias)

Según las secuencias definidas en Odoo:

```
sequence=4  → Invoicing (Facturación)
sequence=5  → Sales (Ventas)
sequence=6  → Mayorista de Calzado ← NUESTRA SECCIÓN
sequence=10 → Services (Servicios)
sequence=25 → Inventory (Inventario)
sequence=30 → Manufacturing (Fabricación)
...
```

**Resultado:** La sección "Mayorista de Calzado" aparecerá **justo después de "Sales"** y **antes de "Services"**.

---

## 👁️ Vista Previa de la Interfaz

### Pestaña "Permisos de Acceso" en Usuario

```
┌──────────────────────────────────────────────────┐
│ PERMISOS DE ACCESO                               │
├──────────────────────────────────────────────────┤
│                                                  │
│ INVOICING                    (sequence=4)        │
│   Invoicing                  ○ Billing          │
│                                                  │
│ SALES                        (sequence=5)        │
│   Ventas                     ○ Usuario           │
│                              ○ Administrador     │
│                                                  │
│ MAYORISTA DE CALZADO ← NUESTRA NUEVA SECCIÓN    │
│   Mayorista de Calzado       ○ Comercial - Solo mis clientes │
│                              ○ Comercial         │
│                              ○ Director Comercial│
│                                                  │
│ SERVICES                     (sequence=10)       │
│   Proyecto                   ○ Usuario           │
│                              ○ Administrador     │
│                                                  │
│ INVENTORY                    (sequence=25)       │
│   Inventario                 ○ Usuario           │
│                              ○ Administrador     │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## ✅ Diferencias Clave vs Subcategoría

### ❌ ANTES (si fuera subcategoría con parent_id):

```xml
<field name="parent_id" ref="base.module_category_sales"/>
```

Aparecería así:
```
SALES
  ↳ Ventas            ○ Usuario / ○ Administrador
  ↳ Mayorista         ○ Comercial / ○ Director  ← Dentro de Sales
```

### ✅ AHORA (categoría principal sin parent_id):

```xml
<!-- NO tiene parent_id -->
```

Aparece así:
```
SALES
  ↳ Ventas            ○ Usuario / ○ Administrador

MAYORISTA DE CALZADO  ← Sección propia al mismo nivel
  ↳ Mayorista         ○ Comercial - Solo mis clientes
                      ○ Comercial
                      ○ Director Comercial
```

---

## 🔍 Verificación Post-Instalación

### 1. En la vista de Grupos

**Ruta:** Configuración > Usuarios y Compañías > Grupos

Deberías ver:
```
📁 Sales
   ├─ Usuario de Ventas
   └─ Administrador de Ventas

📁 Mayorista de Calzado  ← Nueva sección
   ├─ Comercial - Solo mis clientes
   ├─ Comercial
   └─ Director Comercial

📁 Services
   ├─ Usuario de Proyecto
   └─ Administrador de Proyecto
```

### 2. En el formulario de Usuario

**Ruta:** Configuración > Usuarios > [Cualquier Usuario] > Pestaña "Permisos de Acceso"

Desplázate hacia abajo y verás una sección dedicada:

```
┌────────────────────────────────────────────┐
│ MAYORISTA DE CALZADO                       │
├────────────────────────────────────────────┤
│ Mayorista de Calzado                       │
│   ○ Comercial - Solo mis clientes         │
│   ○ Comercial                              │
│   ○ Director Comercial                     │
└────────────────────────────────────────────┘
```

---

## 🎨 Personalización Futura

Si en el futuro quieres añadir más grupos bajo esta misma sección, simplemente:

1. Crea nuevos grupos en el mismo archivo
2. Referencia la misma categoría:
   ```xml
   <field name="category_id" ref="module_category_shoes_dealer"/>
   ```

Ejemplo de expansión futura:
```xml
<!-- Nuevo grupo: Supervisor de Almacén -->
<record id="group_warehouse_supervisor" model="res.groups">
    <field name="name">Supervisor de Almacén</field>
    <field name="category_id" ref="module_category_shoes_dealer"/>
    ...
</record>
```

Esto añadirá automáticamente una nueva opción bajo "MAYORISTA DE CALZADO".

---

## 🚀 Ventajas de Esta Configuración

1. ✅ **Organización Clara**: Sección dedicada y visible
2. ✅ **Escalabilidad**: Fácil añadir más grupos relacionados
3. ✅ **Profesionalidad**: Aspecto coherente con el resto de Odoo
4. ✅ **Facilidad de Uso**: Administradores encuentran los permisos rápidamente
5. ✅ **Independencia**: No depende de otras secciones (no es subcategoría)
6. ✅ **Posicionamiento**: Aparece en posición prioritaria (sequence=6)

---

## 📝 Notas Importantes

### ¿Por qué NO aparecía como sección principal antes?

Posibles razones por las que podría seguir en "OTHER":

1. **Caché de Odoo**: Necesita reinicio del servidor
2. **Actualización pendiente**: Módulo no actualizado
3. **Datos no cargados**: Archivo XML no incluido en __manifest__.py

### Solución

Después de actualizar el módulo:

```bash
# Reiniciar servidor Odoo
sudo systemctl restart odoo

# O si usas docker
docker restart odoo
```

Esto asegura que los cambios en `ir.module.category` se carguen correctamente.

---

## 🔍 Comando de Verificación SQL (Opcional)

Si tienes acceso a PostgreSQL, puedes verificar:

```sql
-- Ver la categoría creada
SELECT id, name, sequence, parent_id
FROM ir_module_category
WHERE name = 'Mayorista de Calzado';

-- Ver todos los grupos bajo esa categoría
SELECT g.name, g.category_id, c.name as category_name
FROM res_groups g
JOIN ir_module_category c ON g.category_id = c.id
WHERE c.name = 'Mayorista de Calzado';
```

Resultado esperado:
```
 id  |         name         | sequence | parent_id
-----+----------------------+----------+-----------
 XXX | Mayorista de Calzado |    6     |   NULL    ← Sin parent_id = Sección principal
```

---

**Última actualización:** 2026-01-02
