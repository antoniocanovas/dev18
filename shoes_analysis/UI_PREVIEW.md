# Vista Previa de Interfaz de Usuario
## Control de Acceso - Shoes Analysis

---

## 📱 Cómo se Verá en la Interfaz de Odoo

### 1. **Sección de Permisos en Usuario**

Cuando edites un usuario en: **Configuración > Usuarios y Compañías > Usuarios > [Usuario] > Pestaña "Permisos de Acceso"**

Verás una nueva sección organizada así:

```
┌─────────────────────────────────────────────────────────────┐
│ Permisos de Acceso                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 📋 Administración                                           │
│   ☐ Acceso                                                  │
│   ☐ Configuración                                           │
│                                                             │
│ 📊 Ventas                                                   │
│   ☐ Usuario                                                 │
│   ☐ Administrador                                           │
│                                                             │
│ 👞 Mayorista de Calzado                    ← NUEVA SECCIÓN │
│   ○ Comercial - Solo mis clientes                          │
│   ○ Comercial                                               │
│   ○ Director Comercial                                      │
│                                                             │
│ 📦 Inventario                                               │
│   ☐ Usuario                                                 │
│   ☐ Administrador                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Características:**
- ✅ Sección dedicada "Mayorista de Calzado"
- ✅ Aparece en posición prioritaria (sequence=5)
- ✅ Selector tipo radio (solo se puede elegir uno)
- ✅ Jerarquía clara de permisos

---

### 2. **Vista de Grupos**

En: **Configuración > Usuarios y Compañías > Grupos**

```
┌──────────────────────────────────────────────────────────────────┐
│ Grupos                                                    🔍 Buscar│
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ 📁 Mayorista de Calzado                                          │
│   ├─ 👤 Comercial - Solo mis clientes                           │
│   │    Usuarios: 15                                              │
│   │    Acceso: Solo lectura informes propios o públicos          │
│   │                                                              │
│   ├─ 👥 Comercial                                                │
│   │    Usuarios: 8                                               │
│   │    Acceso: Lectura/escritura/creación (sin eliminación)      │
│   │                                                              │
│   └─ 👔 Director Comercial                                       │
│        Usuarios: 3                                               │
│        Acceso: Completo (CRUD)                                   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

### 3. **Campo Public en Formulario de Informe**

Al abrir/crear un informe en: **Reports > [Cualquier tipo de informe]**

```
┌────────────────────────────────────────────────────────────────┐
│ Análisis de Ventas - Campaña Primavera 2025                   │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│ Nombre del Análisis:                                          │
│ ┌──────────────────────────────────────────┐                  │
│ │ Ventas Campaña Primavera 2025           │                  │
│ └──────────────────────────────────────────┘                  │
│                                                                │
│ ┌─────────────────────────────┬─────────────────────────────┐ │
│ │                             │                             │ │
│ │ Campaña:                    │ Informe Público:            │ │
│ │ Primavera 2025 ▼            │                             │ │
│ │                             │  ◉ ━━━━━                    │ │
│ │ Comparar con:               │  ↑ Toggle ON/OFF            │ │
│ │ [Otoño 2024][Invierno 2024] │                             │ │
│ │                             │ Resumen:                    │ │
│ │ Cliente:                    │ ┌─────────────────────────┐ │ │
│ │ (vacío)                     │ │ Campaña Principal:      │ │ │
│ │                             │ │ 5,240 pares netos       │ │ │
│ │ Representante:              │ │ €234,500 facturación    │ │ │
│ │ (vacío)                     │ └─────────────────────────┘ │ │
│ │                             │                             │ │
│ └─────────────────────────────┴─────────────────────────────┘ │
│                                                                │
│ [📊 Actualizar] [🖨️ Imprimir]                                 │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Widget del campo `public`:**
- ✅ Toggle visual (switch ON/OFF)
- ✅ Posición destacada en la parte superior derecha
- ✅ Etiqueta clara: "Informe Público"
- ✅ Visible para todos los grupos
- ✅ Editable solo si el usuario tiene permisos de escritura

---

### 4. **Comportamiento Visual según Perfil**

#### 👔 Director Comercial
```
┌─────────────────────────────────────────────────────────────┐
│ 🔍 Lista de Informes - VISTA COMPLETA                       │
├─────────────────────────────────────────────────────────────┤
│ ☑️ Todos los informes (sin filtros)                         │
│ ✏️ Puede editar cualquiera                                  │
│ ➕ Puede crear nuevos                                        │
│ 🗑️ Puede eliminar                                           │
│ 🔓 Campo "Público" editable                                 │
└─────────────────────────────────────────────────────────────┘
```

#### 👥 Comercial
```
┌─────────────────────────────────────────────────────────────┐
│ 🔍 Lista de Informes - VISTA COMPLETA                       │
├─────────────────────────────────────────────────────────────┤
│ ☑️ Todos los informes (sin filtros)                         │
│ ✏️ Puede editar cualquiera                                  │
│ ➕ Puede crear nuevos                                        │
│ ❌ NO puede eliminar                                         │
│ 🔓 Campo "Público" editable                                 │
└─────────────────────────────────────────────────────────────┘
```

#### 👤 Comercial - Solo mis clientes
```
┌─────────────────────────────────────────────────────────────┐
│ 🔍 Lista de Informes - VISTA FILTRADA                       │
├─────────────────────────────────────────────────────────────┤
│ ☑️ Solo informes donde soy referrer                         │
│ ☑️ + Informes marcados como "Público"                       │
│ 👁️ Solo lectura (no puede editar)                          │
│ ❌ NO puede crear nuevos                                     │
│ ❌ NO puede eliminar                                         │
│ 🔒 Campo "Público" visible pero no editable                 │
└─────────────────────────────────────────────────────────────┘
```

---

### 5. **Indicadores Visuales en Lista de Informes**

```
┌────────────────────────────────────────────────────────────────────────┐
│ Informes de Análisis                            [🔍 Buscar] [➕ Crear] │
├────────────────────────────────────────────────────────────────────────┤
│ Nombre                      │ Campaña        │ Público │ Actualizado │ │
├────────────────────────────────────────────────────────────────────────┤
│ 📊 Ventas Primavera 2025   │ Primavera 2025 │   🌐    │ 02/01/2026  │ │
│ 📊 Ranking Productos Q4    │ Q4 2024        │   🔒    │ 28/12/2025  │ │
│ 📊 Análisis Cliente ABC    │ Primavera 2025 │   🌐    │ 15/12/2025  │ │
│ 📊 Mis Clientes - Juan     │ Invierno 2024  │   🔒    │ 10/12/2025  │ │
└────────────────────────────────────────────────────────────────────────┘

Leyenda:
🌐 = Público (visible para todos)
🔒 = Privado (solo referrer o Director/Comercial)
```

---

### 6. **Ejemplo de Asignación de Permisos Paso a Paso**

#### Escenario: Asignar permisos a un nuevo comercial

1. **Ir a usuario:**
   ```
   Configuración > Usuarios y Compañías > Usuarios > [Usuario]
   ```

2. **Pestaña "Permisos de Acceso":**
   ```
   Scroll hasta encontrar "👞 Mayorista de Calzado"
   ```

3. **Seleccionar nivel apropiado:**
   ```
   Si es comercial de zona:
     ○ Comercial - Solo mis clientes  ← Seleccionar este
     ○ Comercial
     ○ Director Comercial

   Si es comercial general:
     ○ Comercial - Solo mis clientes
     ○ Comercial                       ← Seleccionar este
     ○ Director Comercial

   Si es director:
     ○ Comercial - Solo mis clientes
     ○ Comercial
     ○ Director Comercial              ← Seleccionar este
   ```

4. **Guardar:**
   ```
   [💾 Guardar]
   ```

5. **Resultado inmediato:**
   - El usuario verá solo los informes según su nivel
   - Los permisos se aplican instantáneamente
   - No necesita cerrar sesión

---

## 🎨 Personalización Visual (Opcional)

Si deseas añadir iconos o colores personalizados en el futuro, puedes:

1. **Agregar CSS personalizado** para la categoría
2. **Usar badges de color** para diferenciar niveles de acceso
3. **Mostrar alertas** cuando un usuario sin permisos intenta acceder

---

## ✅ Checklist de Verificación Visual

Después de actualizar el módulo, verifica:

- [ ] La categoría "Mayorista de Calzado" aparece en la lista de grupos
- [ ] Los 3 grupos están bajo esa categoría
- [ ] El campo "Público" aparece en el formulario de informes
- [ ] El toggle funciona correctamente
- [ ] Los usuarios ven solo los informes según su grupo
- [ ] Las opciones de crear/editar/eliminar se muestran según permisos

---

## 🔍 Búsqueda Rápida en la Interfaz

Para encontrar rápidamente la configuración:

1. **Menú de búsqueda rápida** (Alt+Shift+Q o ⌘+K):
   - Escribir: "grupos"
   - Seleccionar: "Grupos"
   - Filtrar por: "Mayorista"

2. **Barra lateral de configuración:**
   - Configuración > Usuarios y Compañías
   - Click en "Grupos"
   - Buscar categoría "Mayorista de Calzado"

---

## 📊 Comparativa Visual: Antes vs. Después

### ANTES (Sin categoría específica)
```
Permisos de Acceso:
  📋 Administración
  📊 Ventas
  📦 Inventario
  ...
  ⚙️ Otros  ← Grupos aparecían aquí mezclados
    ☐ Comercial - Solo mis clientes
    ☐ Comercial
    ☐ Director Comercial
```

### DESPUÉS (Con categoría "Mayorista de Calzado")
```
Permisos de Acceso:
  📋 Administración
  👞 Mayorista de Calzado  ← Sección dedicada en posición prioritaria
    ○ Comercial - Solo mis clientes
    ○ Comercial
    ○ Director Comercial
  📊 Ventas
  📦 Inventario
  ...
```

**Beneficios:**
- ✅ Más organizado y profesional
- ✅ Fácil de encontrar
- ✅ Agrupa funcionalidades relacionadas
- ✅ Permite futuras expansiones (más grupos bajo la misma categoría)
- ✅ Mejor experiencia de usuario para administradores

---

**Última actualización:** 2026-01-02
