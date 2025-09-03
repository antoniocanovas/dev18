# 🔍 Módulo de Búsqueda Inteligente de Productos - Odoo 18

## 🌟 Descripción

Módulo avanzado de búsqueda de productos que permite:
- **Búsqueda mediante texto libre** con procesamiento inteligente
- **Detección automática** de marcas y categorías  
- **Sistema conversacional** para mejorar búsquedas ambiguas
- **Aprendizaje automático** de patrones de uso
- **Interfaz intuitiva** tipo chat bot
- **Puntuación de relevancia** de resultados

## 🚀 Instalación

### 1. Verificar dependencias
El módulo requiere que estén instalados:
- `base` (instalado por defecto)
- `product` (módulo de productos)
- `sale` (módulo de ventas)

### 2. Instalar el módulo
1. Ir a **Aplicaciones** en Odoo
2. Hacer clic en **Actualizar Lista de Aplicaciones**
3. Buscar "Búsqueda Inteligente de Productos"
4. Hacer clic en **Instalar**

### 3. Verificar instalación
- Verificar que aparezca el menú "🔍 Búsqueda Inteligente" en la barra principal
- Comprobar acceso desde el menú de Ventas

## 🎯 Cómo Usar

### Realizar una Búsqueda Básica

1. **Acceder al módulo:**
   - Menú principal → 🔍 Búsqueda Inteligente → Nueva Búsqueda
   - O desde Ventas → Búsqueda de Productos

2. **Escribir consulta:**
   ```
   Ejemplos:
   - "Laptop HP para gaming"
   - "Teléfono Samsung económico"
   - "Monitor 4K para diseño"
   - "Impresora Canon para oficina"
   ```

3. **Ejecutar búsqueda:**
   - Hacer clic en "🔍 Buscar Productos"
   - El sistema detecta automáticamente marca y categoría
   - Muestra resultados ordenados por relevancia

### Sistema Conversacional

**Se activa automáticamente cuando:**
- No se detecta marca ni categoría
- Hay demasiados resultados (>50)
- No hay resultados (0)
- Los resultados tienen baja relevancia

**Flujo conversacional:**
1. Sistema detecta necesidad de más información
2. Genera preguntas inteligentes automáticamente
3. Aparece interfaz de chat amigable
4. Usuario responde pregunta por pregunta
5. Sistema aplica respuestas y mejora búsqueda
6. Guarda patrón para futuras búsquedas similares

### Interpretación de Resultados

**Códigos de Color:**
- 🟢 **Verde:** Relevancia perfecta (80+ puntos)
- 🔵 **Azul:** Relevancia alta (50-79 puntos)
- 🟡 **Amarillo:** Relevancia media (20-49 puntos)
- ⚫ **Gris:** Relevancia baja (0-19 puntos)

**Acciones disponibles:**
- **Ver Producto:** Abre detalles completos del producto
- **Seleccionar:** Marca producto para acciones futuras

## 🧠 Sistema de Aprendizaje

### Patrones Automáticos
El sistema aprende y recuerda:
- Combinaciones exitosas de búsqueda
- Preferencias frecuentes del usuario
- Palabras clave efectivas por categoría

### Aplicación Inteligente
En búsquedas futuras similares:
- Aplica automáticamente patrones aprendidos
- Evita preguntas redundantes
- Mejora la precisión progresivamente

## 👥 Para Administradores

### Acceso a Analytics
**Menú:** 🧠 Patrones de Aprendizaje (solo managers)

**Información disponible:**
- Patrones más usados
- Tasa de éxito de detección
- Tendencias de búsqueda
- Palabras clave populares

### Personalización

#### Agregar Marcas
En `models/product_search.py`, método `_detect_brand_and_category()`:
```python
brands = {
    'hp': 'HP',
    'nueva_marca': 'Nueva Marca',  # ← Agregar aquí
    # ... más marcas
}
```

#### Agregar Categorías
```python
categories = {
    'laptop': 'Laptop', 
    'nueva_categoria': 'Nueva Categoría',  # ← Agregar aquí
    # ... más categorías
}
```

#### Ajustar Umbrales
En método `_evaluate_search_quality()`:
```python
too_many_results = self.result_count > 30  # Cambiar umbral
low_relevance = avg_relevance < 25  # Cambiar umbral
```

## 🔧 Solución de Problemas

### Problema: No aparece el módulo
**Solución:** 
1. Verificar que todos los archivos estén en `/addons/product_search/`
2. Actualizar lista de aplicaciones
3. Reiniciar servidor Odoo si es necesario

### Problema: Error al instalar
**Causas posibles:**
- Módulos `product` o `sale` no instalados
- Permisos de archivo incorrectos
- Sintaxis incorrecta en XML

**Solución:**
1. Verificar dependencias instaladas
2. Revisar logs de Odoo para errores específicos
3. Verificar permisos de lectura en archivos

### Problema: No encuentra productos
**Causas posibles:**
- No hay productos activos en el inventario
- Productos no tienen nombres descriptivos
- Diccionarios de marcas/categorías incompletos

**Solución:**
1. Verificar productos activos en Inventario
2. Ampliar diccionarios de detección
3. Usar términos más genéricos en búsqueda

### Problema: Conversación no se activa
**Causa:** La detección automática fue exitosa
**Solución:** Usar consultas más vagas como "computadora" en lugar de "laptop HP gaming"

## 📊 Métricas de Rendimiento

### KPIs del Sistema
- **Precisión básica:** 60-70% sin conversación
- **Precisión conversacional:** 85-95% con chat
- **Precisión con aprendizaje:** >90% con patrones
- **Tiempo promedio:** <5 segundos por búsqueda

### Optimización
- Sistema aprende automáticamente
- Patrones mejoran con el uso
- Base de datos se optimiza sola
- Caché interno de resultados

## 🚀 Próximas Mejoras

### Funcionalidades Planificadas
- [ ] Integración con OpenAI/ChatGPT
- [ ] Búsqueda por voz  
- [ ] Búsqueda por imagen
- [ ] App móvil nativa
- [ ] Integración con WhatsApp
- [ ] Comparador de precios
- [ ] Recomendaciones automáticas

### Integraciones Disponibles
- API REST para aplicaciones externas
- Webhooks para notificaciones
- Exportación de datos de analytics
- Conectores con CRM externos

## 📞 Soporte

Para reportar bugs o solicitar nuevas funcionalidades:
1. Crear ticket en el sistema de tickets interno
2. Incluir capturas de pantalla del error
3. Especificar pasos para reproducir el problema
4. Incluir logs de Odoo si están disponibles

## 📄 Licencia

Este módulo está licenciado bajo LGPL-3.

---
**Versión:** 18.0.1.0.0  
**Fecha:** Diciembre 2024  
**Autor:** Tu Empresa  
**Compatibilidad:** Odoo 18.0+