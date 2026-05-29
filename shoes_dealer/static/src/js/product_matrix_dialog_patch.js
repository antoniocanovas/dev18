/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ProductMatrixDialog } from "@product_matrix/js/product_matrix_dialog";
import { useState, onWillStart, onMounted, onPatched } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

patch(ProductMatrixDialog.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.assortmentPairsState = useState({
            isPair: false,
            isAssortment: false,
            initQty: 0,
            computeMode: "auto",
        });
        this._pairsQty = 0;

        onWillStart(async () => {
            const [tmpl] = await this.orm.read(
                "product.template",
                [this.props.product_template_id],
                ["is_pair", "is_assortment", "categ_id"]
            );
            if (tmpl?.is_pair) {
                const [categ] = await this.orm.read(
                    "product.category",
                    [tmpl.categ_id[0]],
                    ["shoes_assortmentpairs_qty"]
                );
                const qty = categ?.shoes_assortmentpairs_qty || 0;
                this._pairsQty = qty;
                this.assortmentPairsState.initQty = qty;
                this.assortmentPairsState.isPair = true;
            } else if (tmpl?.is_assortment) {
                this.assortmentPairsState.isAssortment = true;
                const variants = await this.orm.searchRead(
                    "product.product",
                    [["product_tmpl_id", "=", this.props.product_template_id]],
                    ["product_template_attribute_value_ids", "pairs_count", "assortment_pair_label"]
                );
                this._assortmentPairsMap = {};
                this._assortmentPairLabelMap = {};
                for (const v of variants) {
                    const key = [...v.product_template_attribute_value_ids]
                        .sort((a, b) => a - b)
                        .join(",");
                    this._assortmentPairsMap[key] = v.pairs_count || 0;
                    if (v.assortment_pair_label) {
                        this._assortmentPairLabelMap[key] = v.assortment_pair_label;
                    }
                }
            }
        });

        onMounted(() => {
            if (this.assortmentPairsState.isPair || this.assortmentPairsState.isAssortment) {
                this._initMatrixTracking();
            }
            if (this.assortmentPairsState.isAssortment) {
                this._injectAssortmentColumnLabels();
            }
            this._updateZeroCells();
        });

        onPatched(() => {
            if (this.assortmentPairsState.isPair || this.assortmentPairsState.isAssortment) {
                this._updateAllRowTotals();
            }
            if (this.assortmentPairsState.isAssortment) {
                this._injectAssortmentColumnLabels();
            }
            this._updateZeroCells();
        });
    },

    _injectAssortmentColumnLabels() {
        const table = document.querySelector(".o_matrix_input_table");
        if (!table) return;

        const colHeaders = table.querySelectorAll("thead th");
        // colHeaders[0] = corner/row-label, colHeaders[1+] = data columns

        // Build colIndex → label scanning body cells (first available per column)
        const colLabelMap = {};
        for (const tr of table.querySelectorAll("tbody tr")) {
            let colIdx = 0;
            for (const td of tr.querySelectorAll("td.o_matrix_input_td")) {
                if (colLabelMap[colIdx] === undefined) {
                    const input = td.querySelector(".o_matrix_input");
                    if (input) {
                        const key = input.getAttribute("ptav_ids")
                            .split(",").map(Number).sort((a, b) => a - b).join(",");
                        const label = this._assortmentPairLabelMap?.[key];
                        if (label) colLabelMap[colIdx] = label;
                    }
                }
                colIdx++;
            }
        }

        for (const [colIdx, label] of Object.entries(colLabelMap)) {
            const th = colHeaders[parseInt(colIdx) + 1];
            if (!th) continue;
            let labelEl = th.querySelector(".sd_pair_label");
            if (!labelEl) {
                labelEl = document.createElement("small");
                labelEl.className = "sd_pair_label text-muted d-block";
                labelEl.style.cssText = "font-size:0.8em;";
                th.querySelector("div")?.appendChild(labelEl);
            }
            const items = label.split(",");
            labelEl.innerHTML = items.length > 3
                ? items.slice(0, 3).join(",") + "<br>" + items.slice(3).join(",")
                : label;
        }
    },

    _updateZeroCells() {
        const tbody = document.querySelector(".o_matrix_input_table tbody");
        if (!tbody) return;
        for (const input of tbody.querySelectorAll(".o_matrix_input")) {
            input.classList.toggle("sd_zero_qty", !(parseFloat(input.value) || 0));
        }
        if (!tbody._sdZeroListener) {
            tbody._sdZeroListener = true;
            tbody.addEventListener("input", () => this._updateZeroCells());
        }
    },

    _onComputeModeChange(ev) {
        this.assortmentPairsState.computeMode = ev.target.value;
    },

    _onPairsQtyInput(ev) {
        this._pairsQty = parseInt(ev.target.value) || 0;
        this._updateAllRowTotals();
    },

    _initMatrixTracking() {
        const tbody = document.querySelector(".o_matrix_input_table tbody");
        if (!tbody) return;

        tbody.querySelectorAll("tr").forEach((tr) => {
            const nameEl = tr.querySelector("strong");
            if (!nameEl) return;
            nameEl.dataset.originalName = nameEl.textContent.trim();

            // Inject per-row assortment qty input (pairs only, visible in 'specific' mode)
            if (this.assortmentPairsState.isPair) {
                const assortInput = document.createElement("input");
                assortInput.type = "number";
                assortInput.className = "o_input sd_assortment_qty ms-2";
                assortInput.style.cssText = "width: 60px; display: none;";
                assortInput.value = 1;
                assortInput.min = 1;
                nameEl.parentElement.appendChild(assortInput);
            }
        });

        this._updateAllRowTotals();
        tbody.addEventListener("input", () => this._updateAllRowTotals());
    },

    _updateAssortmentRowTotals() {
        const tbody = document.querySelector(".o_matrix_input_table tbody");
        const grandTotalEl = document.querySelector(".sd_matrix_grand_total");
        if (!tbody) return;
        let grandTotal = 0;
        for (const row of tbody.querySelectorAll("tr")) {
            let rowPairs = 0;
            for (const input of row.querySelectorAll(".o_matrix_input")) {
                const qty = parseFloat(input.value) || 0;
                if (!qty) continue;
                const ptavKey = input
                    .getAttribute("ptav_ids")
                    .split(",")
                    .map(Number)
                    .sort((a, b) => a - b)
                    .join(",");
                rowPairs += qty * (this._assortmentPairsMap?.[ptavKey] || 0);
            }
            grandTotal += rowPairs;
            const nameEl = row.querySelector("strong");
            if (nameEl) {
                const orig = nameEl.dataset.originalName || nameEl.textContent.trim();
                if (!nameEl.dataset.originalName) nameEl.dataset.originalName = orig;
                nameEl.textContent = `${orig} (${rowPairs})`;
            }
        }
        if (grandTotalEl) grandTotalEl.textContent = grandTotal;
    },

    _updateAllRowTotals() {
        if (this.assortmentPairsState.isAssortment) {
            return this._updateAssortmentRowTotals();
        }
        const tbody = document.querySelector(".o_matrix_input_table tbody");
        const grandTotalEl = document.querySelector(".sd_matrix_grand_total");
        if (!tbody) return;

        const pairsQty = this._pairsQty;
        const mode = this.assortmentPairsState.computeMode;
        let grandTotal = 0;

        for (const row of tbody.querySelectorAll("tr")) {
            let rowTotal = 0;
            for (const input of row.querySelectorAll(".o_matrix_input")) {
                rowTotal += parseFloat(input.value) || 0;
            }

            const assortQtyInput = row.querySelector(".sd_assortment_qty");
            if (assortQtyInput) {
                assortQtyInput.style.display = mode === "specific" ? "" : "none";
            }

            const boxes = mode === "specific"
                ? (assortQtyInput ? parseInt(assortQtyInput.value) || 1 : 1)
                : 1;

            grandTotal += mode === "specific" ? rowTotal * boxes : rowTotal;

            const nameEl = row.querySelector("strong");
            if (nameEl) {
                const originalName =
                    nameEl.dataset.originalName || nameEl.textContent.trim();
                if (!nameEl.dataset.originalName) {
                    nameEl.dataset.originalName = originalName;
                }
                if (mode === "loose" || pairsQty <= 0) {
                    nameEl.textContent = `${originalName} (${rowTotal})`;
                } else if (mode === "specific") {
                    nameEl.textContent = `${originalName} (${rowTotal * boxes})`;
                } else {
                    const assortments = Math.floor(rowTotal / pairsQty);
                    const remainder = rowTotal % pairsQty;
                    nameEl.textContent = `${originalName} (${rowTotal}/${assortments}/${remainder})`;
                }
            }
        }

        if (grandTotalEl) {
            grandTotalEl.textContent = grandTotal;
        }
    },

    async _onConfirm() {
        const mode = this.assortmentPairsState.computeMode;

        if (!this.assortmentPairsState.isPair || mode === "loose") {
            return super._onConfirm();
        }

        const tbody = document.querySelector(".o_matrix_input_table tbody");
        if (!tbody) {
            return super._onConfirm();
        }

        // Build color_data: one entry per row that has non-zero quantities
        const colorData = [];
        for (const row of tbody.querySelectorAll("tr")) {
            const cells = [];
            for (const input of row.querySelectorAll(".o_matrix_input")) {
                const qty = parseFloat(input.value) || 0;
                if (qty <= 0) continue;
                const ptavIds = input
                    .getAttribute("ptav_ids")
                    .split(",")
                    .map((id) => parseInt(id));
                cells.push({ ptav_ids: ptavIds, qty });
            }
            if (!cells.length) continue;

            const assortQtyInput = row.querySelector(".sd_assortment_qty");
            const assortmentQty = assortQtyInput
                ? parseInt(assortQtyInput.value) || 1
                : 1;

            colorData.push({
                assortment_qty: assortmentQty,
                cells,
            });
        }

        if (!colorData.length) {
            this.props.close();
            return;
        }

        const orderId = this.props.record.resId;

        await this.orm.call(
            "sale.order",
            "process_pair_assortment_matrix",
            [orderId, this.props.product_template_id, mode, this._pairsQty, colorData]
        );
        await this.props.record.load();
        this.props.close();
    },
});
