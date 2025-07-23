/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ProductMatrixDialog } from "@product_matrix/js/product_matrix_dialog";
import { onMounted, useRef } from "@odoo/owl";
import { useHotkey } from "@web/core/hotkeys/hotkey_hook";

patch(ProductMatrixDialog.prototype, {
    setup() {
        this.size = 'xl';

        const productMatrixRef = useRef('productMatrix');
        useHotkey("enter", () => this._onConfirm(), {
            bypassEditableProtection: true,
            area: () => productMatrixRef.el,
        });

        onMounted(() => this._safeSelectFirstInput());
    },

    /**
     * Safely selects the first available matrix input, handling empty matrices gracefully
     * @private
     */
    _safeSelectFirstInput() {
        try {
            const inputs = this._getMatrixInputs();
            if (!inputs.length) {
                console.debug('Matrix filter: No inputs found, possibly empty filtered matrix');
                return;
            }

            const targetInput = this._findTargetInput(inputs) || inputs[0];
            if (targetInput?.select) {
                targetInput.select();
            }
        } catch (error) {
            console.warn('Matrix filter: Error selecting input:', error);
        }
    },

    /**
     * Gets all matrix input elements
     * @private
     * @returns {HTMLElement[]} Array of matrix input elements
     */
    _getMatrixInputs() {
        const collection = document.getElementsByClassName('o_matrix_input');
        return collection ? Array.from(collection) : [];
    },

    /**
     * Finds the target input based on edited cell attributes
     * @private
     * @param {HTMLElement[]} inputs - Array of input elements
     * @returns {HTMLElement|null} Target input element or null
     */
    _findTargetInput(inputs) {
        const { editedCellAttributes } = this.props;
        
        if (!editedCellAttributes?.length) {
            return null;
        }

        return inputs.find(input => {
            const ptavIds = input.attributes?.ptav_ids?.nodeValue;
            return ptavIds === editedCellAttributes;
        });
    },
});
