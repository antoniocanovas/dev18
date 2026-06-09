# Módulo: Shoes Dealer Accessory

## Propósito

Este módulo extiende la funcionalidad de `shoes_dealer` para proporcionar una vista detallada y en tiempo real de la gestión de accesorios (adornos, componentes, etc.) utilizados en la fabricación de zapatos. Permite un seguimiento preciso del ciclo de vida de cada accesorio, desde la demanda generada por las ventas hasta el stock en manos del fabricante.

## Características Principales

### Modelo `shoes.accesory`

Este es el modelo central del módulo. Cada registro representa un tipo de accesorio específico vinculado a un modelo de zapato (a través de una Tarea de Proyecto).

El campo `qty` (cantidad de accesorio por par) es de tipo **Float** con precisión `Product Unit of Measure`, lo que permite fracciones adaptadas a la UoM configurada en la empresa.

### Campos Calculados

La potencia de este módulo reside en sus campos calculados, que ofrecen una visión completa del estado de cada accesorio:

#### `pairs_campaign_sold` (Pares Vendidos en Campaña)
- **¿Qué calcula?**: El número total de pares de zapatos que ya han sido vendidos a clientes.
- **¿Cómo lo calcula?**: Busca todas las líneas de pedidos de venta (`sale.order.line`) confirmados (`state = 'sale'`) cuyo producto final (zapato o surtido) esté vinculado a la misma tarea de producción que el accesorio. Suma el campo `pairs_count` de todas esas líneas.

#### `pairs_campaign_pending` (Pares Pendientes de Campaña)
- **¿Qué calcula?**: El número total de pares de zapatos que han sido vendidos pero que aún no han sido entregados al cliente.
- **¿Cómo lo calcula?**: Para las mismas líneas de venta que el campo anterior, calcula la proporción de la cantidad pendiente de entregar (`product_uom_qty - qty_delivered`). Aplica esa proporción al campo `pairs_count` de cada línea y suma los resultados.

#### `accesory_campaign_sold_qty` (Cantidad de Accesorios Vendidos)
- **¿Qué calcula?**: La cantidad total de este accesorio que se necesita para los pares ya vendidos.
- **¿Cómo lo calcula?**: `pairs_campaign_sold * qty` (donde `qty` es la cantidad de este accesorio por par, campo `Float` con precisión `Product Unit of Measure`).

#### `accesory_campaign_pending_qty` (Cantidad de Accesorios Pendientes)
- **¿Qué calcula?**: La cantidad total de este accesorio necesaria para fabricar los pares que están pendientes de entregar a los clientes.
- **¿Cómo lo calcula?**: `pairs_campaign_pending * qty`.

#### `accesory_stock` (Stock Propio)
- **¿Qué calcula?**: La cantidad de este accesorio que tienes disponible en tus propios almacenes.
- **¿Cómo lo calcula?**: Es un campo relacionado (`related`) que muestra el valor de `qty_available` del producto del accesorio.

#### `accesory_supplier_pending` (Pendiente de Proveedor)
- **¿Qué calcula?**: La cantidad total de este accesorio que está en tránsito desde un proveedor.
- **¿Cómo lo calcula?**: Suma dos cantidades:
    1.  **En camino a nuestro almacén**: Cantidad en movimientos de stock pendientes (`waiting`, `confirmed`, `assigned`) que van de un proveedor a una ubicación interna.
    2.  **En camino al fabricante (Dropshipping)**: Cantidad en movimientos de stock pendientes que van de un proveedor directamente a la ubicación del fabricante.

#### `accesory_manufacturer_stock` (Stock en Fabricante)
- **¿Qué calcula?**: El stock teórico de este accesorio en la ubicación del fabricante, calculado como un balance desde el último inventario.
- **¿Cómo lo calcula?**:
    1.  Primero, encuentra la fecha del último ajuste de inventario para este producto en la ubicación del fabricante.
    2.  **Entradas**: Suma toda la cantidad de este accesorio recibida en la ubicación del fabricante *después* de esa fecha.
    3.  **Salidas (Consumo)**: Calcula cuántos pares de zapatos terminados se han recibido del fabricante *después* de esa fecha y lo multiplica por la cantidad (`qty`) de este accesorio por par.
    4.  El resultado es `Entradas - Salidas`.

#### `accesory_manufacturer_status` (Estado del Stock del Fabricante)
- **¿Qué calcula?**: El balance entre los recursos disponibles y la necesidad de producción. Un valor negativo indica un déficit (se necesita reabastecer), mientras que un valor positivo indica un superávit.
- **¿Cómo lo calcula?**: `(accesory_manufacturer_stock + accesory_supplier_pending) - accesory_campaign_pending_qty`. En otras palabras, es `(Stock Actual + Stock en Tránsito) - Necesidad Total`.

### Vista y Agrupación

- La vista de lista está configurada para mostrar los campos clave, coloreando los valores de stock y estado en **verde (positivo/superávit)** o **rojo (negativo/déficit)** para una fácil interpretación.
- Se ha añadido una vista de búsqueda que permite agrupar los registros por **Fabricante** o por **Producto**.
- Los totales de los campos de cantidad se calculan y muestran correctamente en la vista de lista (sin agrupar).

## Instalación

1.  Asegúrate de que las dependencias (`product`, `project`, `product_brand`, `shoes_dealer`, `shoes_campaign`) estén instaladas.
2.  Copia la carpeta `shoes_accesory` en el directorio `addons` de tu instalación de Odoo.
3.  Reinicia el servidor de Odoo.
4.  Activa el modo desarrollador, ve a `Aplicaciones`, busca "Shoes Dealer Accessory" y haz clic en "Instalar" o "Actualizar".
