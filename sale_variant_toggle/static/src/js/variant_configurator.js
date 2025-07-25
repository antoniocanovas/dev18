/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";
import { Component } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";

/**
 * Componente de diálogo para seleccionar formato de variantes
 */
export class VariantFormatDialog extends Component {
    static template = "sale_variant_toggle.VariantFormatDialog";
    static components = { Dialog };
    
    setup() {
        this.action = useService("action");
        this.notification = useService("notification");
        this.orm = useService("orm");
    }
    
    async onConfiguratorClick() {
        await this._handleSelection('configurator');
    }
    
    async onMatrixClick() {
        await this._handleSelection('matrix');
    }
    
    async _handleSelection(mode) {
        const { productTemplateId, orderId } = this.props;
        
        try {
            if (orderId) {
                // Llamar al método del backend
                const action = await this.orm.call(
                    'sale.order',
                    'action_open_variant_selector',
                    [orderId, productTemplateId, mode]
                );
                
                if (action) {
                    this.props.close();
                    await this.action.doAction(action);
                    return;
                }
            }
            
            // Fallback: mostrar notificación
            this.notification.add(`${mode} seleccionado para ${this.props.productName}`, { 
                type: 'success' 
            });
            
        } catch (error) {
            console.error('Error opening variant selector:', error);
            this.notification.add(`Error al abrir ${mode}`, { type: 'warning' });
        }
        
        this.props.close();
    }
}

/**
 * Servicio para gestionar la selección de variantes
 */
class VariantToggleService {
    constructor() {
        this.dialog = null;
        this.orm = null;
        this.pendingInterceptions = new Set();
    }

    setup(env) {
        this.dialog = env.services.dialog;
        this.orm = env.services.orm;
    }

    async checkAndShowDialog(productTemplateId, orderId = null) {
        try {
            // Evitar interceptar el mismo producto múltiples veces
            const key = `${productTemplateId}-${orderId}`;
            if (this.pendingInterceptions.has(key)) {
                return false;
            }
            
            this.pendingInterceptions.add(key);
            
            // Verificar si el producto tiene modo toggle
            const result = await this.orm.call(
                'sale.order',
                'check_variant_toggle_mode',
                [productTemplateId]
            );
            
            this.pendingInterceptions.delete(key);
            
            if (result && result.variant_selection_mode === 'toggle' && result.has_attributes) {
                console.log('VariantToggle: Showing dialog for product', result.name);
                
                // Mostrar el diálogo de selección
                this.dialog.add(VariantFormatDialog, {
                    title: `Configurar: ${result.name}`,
                    productTemplateId: productTemplateId,
                    orderId: orderId,
                    productName: result.name,
                });
                
                return true; // Indica que se mostró el diálogo
            }
        } catch (error) {
            console.error('Error checking product variant mode:', error);
            this.pendingInterceptions.delete(`${productTemplateId}-${orderId}`);
        }
        
        return false; // No se mostró el diálogo
    }
}

// Registrar el servicio
registry.category("services").add("variant_toggle", {
    start(env) {
        const service = new VariantToggleService();
        service.setup(env);
        return service;
    },
});

/**
 * Patch mejorado para Many2One field
 */
const Many2OneFieldPatch = {
    setup() {
        super.setup();
        try {
            this.variantToggle = useService("variant_toggle");
        } catch (error) {
            console.log('Variant toggle service not available');
            this.variantToggle = null;
        }
    },

    async _setValue(value, options = {}) {
        console.log('VariantToggle: _setValue called', this.props.name, value);
        
        // Interceptar ANTES de establecer el valor
        if (this.variantToggle && 
            this.props.name === 'product_template_id' && 
            this.props.record?.resModel === 'sale.order.line' && 
            value && value !== false) {
            
            const productTemplateId = Array.isArray(value) ? value[0] : value;
            const orderId = this.props.record?.data?.order_id?.[0];
            
            console.log('VariantToggle: Intercepting product selection', productTemplateId);
            
            // Verificar si debe mostrar el diálogo
            const dialogShown = await this.variantToggle.checkAndShowDialog(
                productTemplateId, 
                orderId
            );
            
            if (dialogShown) {
                console.log('VariantToggle: Dialog shown, preventing default behavior');
                // Si se mostró el diálogo, NO establecer el valor
                // Esto previene que se active el comportamiento estándar
                return;
            }
        }
        
        // Continuar con el comportamiento normal
        console.log('VariantToggle: Continuing with normal behavior');
        return super._setValue(value, options);
    },

    async update(value, options = {}) {
        console.log('VariantToggle: update called', this.props.name, value);
        
        // También interceptar en update por si acaso
        if (this.variantToggle && 
            this.props.name === 'product_template_id' && 
            this.props.record?.resModel === 'sale.order.line' && 
            value && Array.isArray(value) && value.length > 0) {
            
            const productTemplateId = value[0];
            const orderId = this.props.record?.data?.order_id?.[0];
            
            console.log('VariantToggle: Intercepting in update', productTemplateId);
            
            // Verificar si debe mostrar el diálogo
            const dialogShown = await this.variantToggle.checkAndShowDialog(
                productTemplateId, 
                orderId
            );
            
            if (dialogShown) {
                console.log('VariantToggle: Dialog shown in update, preventing');
                // Si se mostró el diálogo, no continuar
                return;
            }
        }
        
        // Continuar con el comportamiento normal
        return super.update(value, options);
    }
};

// Aplicar patch de forma segura
try {
    const Many2OneField = registry.category("fields").get("many2one");
    if (Many2OneField) {
        patch(Many2OneField, Many2OneFieldPatch);
        console.log('VariantToggle: Many2One field patched successfully');
    }
} catch (error) {
    console.log('VariantToggle: Could not patch Many2OneField:', error);
}

/**
 * Patch adicional para ListRenderer por si las moscas
 */
const ListRendererPatch = {
    setup() {
        super.setup();
        try {
            this.variantToggle = useService("variant_toggle");
        } catch (error) {
            this.variantToggle = null;
        }
    },

    async _onCellClicked(ev) {
        console.log('VariantToggle: Cell clicked in list', ev);
        
        // Verificar si es una celda de product_template_id
        if (this.variantToggle && ev.target) {
            const cell = ev.target.closest('[name="product_template_id"]');
            if (cell && this.props.list?.resModel === 'sale.order.line') {
                console.log('VariantToggle: Product template cell clicked');
                // Aquí podríamos interceptar también
            }
        }
        
        return super._onCellClicked(ev);
    }
};

// Aplicar patch al ListRenderer también
try {
    const ListRenderer = registry.category("renderers").get("list");
    if (ListRenderer) {
        patch(ListRenderer, ListRendererPatch);
        console.log('VariantToggle: ListRenderer patched successfully');
    }
} catch (error) {
    console.log('VariantToggle: Could not patch ListRenderer:', error);
}

/**
 * Template del diálogo
 */
registry.category("web.template").add("sale_variant_toggle.VariantFormatDialog", `
<Dialog title="'Seleccionar Formato de Variantes'" size="'lg'">
    <div class="container-fluid p-4">
        <div class="row mb-4">
            <div class="col-12 text-center">
                <h4 class="text-primary mb-3">
                    <i class="fa fa-cogs"/> 
                    <t t-esc="props.productName or 'Producto con Variantes'"/>
                </h4>
                <p class="text-muted lead">
                    ¿Cómo quieres agregar las variantes de este producto?
                </p>
            </div>
        </div>
        
        <div class="row g-4">
            <div class="col-md-6">
                <div class="card h-100 border-primary variant-card" 
                     t-on-click="onConfiguratorClick">
                    <div class="card-body text-center p-4">
                        <i class="fa fa-list-alt fa-4x text-primary mb-3"></i>
                        <h5 class="card-title text-primary">Configurador</h5>
                        <p class="card-text text-muted mb-3">
                            Selección paso a paso de variantes, 
                            ideal para productos complejos.
                        </p>
                        <span class="badge bg-primary">
                            <i class="fa fa-check-circle me-1"/>
                            Recomendado para productos complejos
                        </span>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card h-100 border-success variant-card" 
                     t-on-click="onMatrixClick">
                    <div class="card-body text-center p-4">
                        <i class="fa fa-th fa-4x text-success mb-3"></i>
                        <h5 class="card-title text-success">Matriz</h5>
                        <p class="card-text text-muted mb-3">
                            Vista de cuadrícula para selección 
                            rápida de múltiples variantes.
                        </p>
                        <span class="badge bg-success">
                            <i class="fa fa-bolt me-1"/>
                            Ideal para selección múltiple
                        </span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-12 text-center">
                <div class="alert alert-info d-inline-block">
                    <i class="fa fa-info-circle me-2"></i>
                    <small>
                        Puedes cambiar esta configuración en la ficha del producto
                    </small>
                </div>
            </div>
        </div>
    </div>
    
    <t t-set-slot="footer">
        <button class="btn btn-secondary" t-on-click="props.close">
            <i class="fa fa-times me-1"></i> Cancelar
        </button>
    </t>
</Dialog>
`);

// CSS
if (typeof document !== 'undefined') {
    const style = document.createElement('style');
    style.textContent = `
    .variant-card {
        cursor: pointer;
        transition: all 0.3s ease;
        border-width: 2px;
    }
    
    .variant-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
    }
    
    .variant-card .fa {
        transition: transform 0.3s ease;
    }
    
    .variant-card:hover .fa {
        transform: scale(1.05);
    }
    `;
    document.head.appendChild(style);
}

// Log de inicialización
console.log('VariantToggle: JavaScript loaded successfully');
