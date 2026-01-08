# Control de Acceso - Shoes Analysis Module
## Resumen de Implementación

**Fecha de implementación:** 2026-01-02
**Módulo:** shoes_analysis
**Versión Odoo:** 18.0

---

## 📋 Objetivo

Implementar un sistema de control de acceso y visibilidad para los informes del modelo `shoes.analysis` basado en perfiles de usuario comercial mediante reglas de registro y un nuevo campo booleano `public`.

---

## ✅ Cambios Implementados

### 1. **Nuevo Campo `public` en el Modelo**

**Archivo:** `models/shoes_analysis.py`

```python
public = fields.Boolean(
    string='Public Report',
    default=False,
    help='If checked, this report will be visible to all sales users, '
         'even if they are not the referrer.'
)
```

**Ubicación:** Líneas 90-95
**Comportamiento:**
- Valor por defecto: `False` (privado)
- Controla la visibilidad general del informe
- Visible para todos los grupos en el formulario

---

### 2. **Grupos de Seguridad Creados**

**Archivo:** `security/shoes_analysis_groups.xml` (NUEVO)

#### Categoría de Permisos:
- **Mayorista de Calzado** (`module_category_shoes_dealer`)
  - Sección específica en la interfaz de usuarios
  - Agrupa todos los permisos relacionados con el sistema de mayorista de calzado
  - Secuencia: 5 (aparece en posición prioritaria)
  - **Ubicación en UI:** Configuración > Usuarios > pestaña "Permisos de Acceso" > sección "Mayorista de Calzado"

#### Grupos (jerarquía de menor a mayor privilegio):

1. **Comercial - Solo mis clientes** (`group_shoes_analysis_user`)
   - Hereda de: `sales_team.group_sale_salesman`
   - Acceso: Solo lectura a informes propios o públicos
   - Permisos: Read only

2. **Comercial** (`group_shoes_analysis_manager`)
   - Hereda de: `group_shoes_analysis_user`
   - Acceso: Todos los informes
   - Permisos: Read, Write, Create (NO Delete)

3. **Director Comercial** (`group_shoes_analysis_director`)
   - Hereda de: `group_shoes_analysis_manager` + `sales_team.group_sale_manager`
   - Acceso: Sin restricciones
   - Permisos: Read, Write, Create, Delete (COMPLETO)

---

### 3. **Reglas de Registro (Record Rules)**

**Archivo:** `security/shoes_analysis_rules.xml` (NUEVO)

#### Regla 1: Director Comercial - Acceso Total
- **ID:** `shoes_analysis_rule_director`
- **Dominio:** `[(1, '=', 1)]` (sin restricciones)
- **Permisos:** Read, Write, Create, Unlink ✅

#### Regla 2: Comercial - Lectura/Escritura/Creación
- **ID:** `shoes_analysis_rule_manager_read_write`
- **Dominio:** `[(1, '=', 1)]` (sin restricciones)
- **Permisos:** Read, Write, Create ✅ | Unlink ❌

#### Regla 3: Comercial - Solo mis clientes
- **ID:** `shoes_analysis_rule_user_readonly`
- **Dominio:** `['|', ('referrer_id', '=', user.id), ('public', '=', True)]`
- **Permisos:** Read ✅ | Write, Create, Unlink ❌

**Nota importante:** La regla 3 maneja correctamente casos donde `referrer_id` es `False` o vacío gracias al operador `OR` con `public = True`.

---

### 4. **Permisos de Acceso Actualizados**

**Archivo:** `security/ir.model.access.csv` (MODIFICADO)

Se reemplazaron las líneas antiguas que referenciaban grupos de `sales_team` por:

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_shoes_analysis_director,access.shoes.analysis.director,model_shoes_analysis,group_shoes_analysis_director,1,1,1,1
access_shoes_analysis_manager,access.shoes.analysis.manager,model_shoes_analysis,group_shoes_analysis_manager,1,1,1,0
access_shoes_analysis_user,access.shoes.analysis.user,model_shoes_analysis,group_shoes_analysis_user,1,0,0,0
access_shoes_ranking_director,access.shoes.ranking.director,model_shoes_ranking,group_shoes_analysis_director,1,1,1,1
access_shoes_ranking_manager,access.shoes.ranking.manager,model_shoes_ranking,group_shoes_analysis_manager,1,1,1,0
access_shoes_ranking_user,access.shoes.ranking.user,model_shoes_ranking,group_shoes_analysis_user,1,0,0,0
```

**Modelos cubiertos:**
- `shoes.analysis`
- `shoes.ranking`

---

### 5. **Vista Formulario Actualizada**

**Archivo:** `views/shoes_analysis_views.xml` (MODIFICADO)

**Cambio:** Líneas 64-66

```xml
<field name="public"
       widget="boolean_toggle"
       string="Informe Público"/>
```

**Características:**
- Widget: `boolean_toggle` (interruptor visual)
- Posición: En el segundo grupo, antes del campo `resume_html`
- Visible para todos los grupos
- Editable según permisos de escritura del usuario

---

### 6. **Manifiesto Actualizado**

**Archivo:** `__manifest__.py` (MODIFICADO)

**Orden de carga crítico:**

```python
"data": [
    # Seguridad (orden importante: grupos -> accesos -> reglas)
    "security/shoes_analysis_groups.xml",      # 1. Primero grupos
    "security/ir.model.access.csv",            # 2. Luego accesos
    "security/shoes_analysis_rules.xml",       # 3. Finalmente reglas

    # Reportes y vistas
    "report/sale_report_views.xml",
    "report/account_invoice_report_views.xml",
    "views/shoes_analysis_views.xml",
    "views/shoes_analysis_menu.xml",
    "views/product_template_views.xml",
    "report/shoes_analysis_report.xml",
],
```

---

## 📊 Matriz de Permisos

| Grupo | Lectura | Escritura | Creación | Eliminación | Dominio de Acceso |
|-------|---------|-----------|----------|-------------|-------------------|
| **Director Comercial** | ✅ Todos | ✅ Todos | ✅ | ✅ | Sin restricción |
| **Comercial** | ✅ Todos | ✅ Todos | ✅ | ❌ | Sin restricción |
| **Solo mis clientes** | ✅ Filtrado | ❌ | ❌ | ❌ | `referrer_id=user` OR `public=True` |

---

## 🧪 Escenarios de Prueba

### Escenario 1: Director Comercial
- ✅ Ve todos los informes sin filtros
- ✅ Puede crear nuevos informes
- ✅ Puede editar cualquier informe
- ✅ Puede eliminar cualquier informe
- ✅ Puede marcar/desmarcar informes como públicos

### Escenario 2: Comercial
- ✅ Ve todos los informes sin filtros
- ✅ Puede crear nuevos informes
- ✅ Puede editar cualquier informe
- ❌ NO puede eliminar informes
- ✅ Puede marcar/desmarcar informes como públicos

### Escenario 3: Comercial - Solo mis clientes
- ✅ Ve solo informes donde `referrer_id = usuario actual`
- ✅ Ve informes marcados como `public = True`
- ❌ NO ve informes privados de otros usuarios
- ❌ NO puede crear nuevos informes
- ❌ NO puede editar informes (modo solo lectura)
- ❌ NO puede eliminar informes
- 👁️ Campo `public` visible pero no editable (read-only)

### Escenario 4: Informes sin referrer_id
- ✅ Si `public = True`: Visible para todos los grupos
- ❌ Si `public = False`: Solo visible para Director y Comercial
- ✅ Director y Comercial pueden editar y asignar referrer_id

---

## 🚀 Pasos para Activar

### 1. Actualizar el Módulo en Odoo

```bash
# Desde el CLI de Odoo o la interfaz web:
# Apps > Shoes Analysis > Upgrade
```

O desde línea de comandos:

```bash
odoo-bin -c /path/to/odoo.conf -u shoes_analysis -d your_database
```

### 2. Verificar Grupos Creados

Ir a: **Configuración > Usuarios y Compañías > Grupos**

Buscar categoría: **Mayorista de Calzado**

Deberían aparecer 3 grupos:
- Director Comercial
- Comercial
- Comercial - Solo mis clientes

### 3. Asignar Usuarios a Grupos

**Ruta:** Configuración > Usuarios y Compañías > Usuarios

Para cada usuario:
1. Editar usuario
2. En pestaña "Permisos de Acceso"
3. En sección "Mayorista de Calzado" seleccionar el grupo apropiado

**Recomendación:**
- Directores de ventas → **Director Comercial**
- Comerciales con visión global → **Comercial**
- Comerciales de zona/cliente → **Comercial - Solo mis clientes**

### 4. Probar Permisos

1. Crear un informe con usuario Director
2. NO marcar como público
3. NO asignar referrer_id
4. Intentar acceder con usuario "Solo mis clientes" → NO debería verlo
5. Marcar como público → Ahora todos deberían verlo
6. Asignar referrer_id a un comercial → Ese comercial lo ve aunque no sea público

---

## ⚠️ Consideraciones Importantes

### Migración de Datos Existentes

Los informes existentes tendrán `public = False` por defecto. Si se desea marcar algunos como públicos automáticamente, ejecutar:

```python
# Desde shell de Odoo (odoo-bin shell)
env['shoes.analysis'].search([]).write({'public': False})
# O marcar todos como públicos:
env['shoes.analysis'].search([]).write({'public': True})
```

### Performance

El dominio de las reglas está optimizado, pero si hay muchos registros, considerar:

```sql
-- Crear índices en PostgreSQL
CREATE INDEX idx_shoes_analysis_referrer_id ON shoes_analysis(referrer_id);
CREATE INDEX idx_shoes_analysis_public ON shoes_analysis(public);
```

### Compatibilidad

- ✅ Los nuevos grupos heredan correctamente de grupos estándar de ventas
- ✅ No interfiere con otros módulos
- ✅ Los menús existentes filtran automáticamente según las reglas

### Seguridad

- Las reglas de registro (`ir.rule`) se evalúan a nivel de base de datos
- Un usuario sin permisos NO puede saltarse las reglas mediante API
- Las reglas se aplican tanto en UI como en llamadas XML-RPC/JSON-RPC

---

## 📝 Notas Técnicas

### Jerarquía de Grupos

La jerarquía usa `implied_ids` para heredar permisos:

```
Director Comercial
    ↓ hereda de
Comercial
    ↓ hereda de
Comercial - Solo mis clientes
```

Esto significa que asignar a un usuario el grupo "Director Comercial" automáticamente le da también los permisos de los grupos inferiores.

### Evaluación de Reglas

Odoo evalúa las reglas con lógica **AND** entre reglas del mismo grupo y **OR** entre grupos diferentes. Por tanto, las 3 reglas NO entran en conflicto.

### Campo `public` vs `referrer_id`

- Si un informe tiene `public = True`, es visible para TODOS, independientemente de `referrer_id`
- Si `public = False` y `referrer_id` está vacío, solo Director y Comercial lo ven
- Si `public = False` y `referrer_id = User X`, solo User X (si es "Solo mis clientes") + Director + Comercial lo ven

---

## 🎯 Resumen de Archivos Modificados/Creados

### Archivos NUEVOS:
1. ✅ `security/shoes_analysis_groups.xml`
2. ✅ `security/shoes_analysis_rules.xml`
3. ✅ `IMPLEMENTATION_SUMMARY.md` (este archivo)

### Archivos MODIFICADOS:
1. ✅ `models/shoes_analysis.py` - Añadido campo `public`
2. ✅ `security/ir.model.access.csv` - Actualizados permisos de acceso
3. ✅ `views/shoes_analysis_views.xml` - Añadido campo `public` al formulario
4. ✅ `__manifest__.py` - Actualizados archivos de datos

---

## ✨ Conclusión

La implementación está completa y lista para ser actualizada en Odoo. El sistema de control de acceso cumple con todos los requisitos especificados:

- ✅ Nuevo campo `public` añadido
- ✅ Tres grupos de usuario creados con jerarquía clara
- ✅ Reglas de registro aplicadas correctamente
- ✅ Permisos diferenciados por grupo
- ✅ Vista actualizada con el nuevo campo
- ✅ Compatibilidad mantenida con estructuras existentes

**Siguiente paso:** Actualizar el módulo en Odoo y asignar usuarios a los grupos correspondientes.
