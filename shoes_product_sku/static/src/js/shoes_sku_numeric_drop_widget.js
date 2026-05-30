/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, useRef, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

// ─── Single slot drop zone ────────────────────────────────────────────────────

class ShoesSkuSlotZone extends Component {
    static template = "shoes_product_sku.ShoesSkuSlotZone";
    static props = {
        lineId: Number,
        slotIndex: Number,
        slotData: Object,       // { has_image, url }
        label: String,
        onUploaded: Function,
    };

    setup() {
        this.state = useState({
            isDragOver: false,
            uploading: false,
            hasImage: this.props.slotData.has_image,
            imgUrl: this.props.slotData.url,
        });
        this.fileInputRef = useRef("fileInput");
        this.orm = useService("orm");
        this.notification = useService("notification");
    }

    onDragOver(ev) {
        ev.preventDefault();
        ev.dataTransfer.dropEffect = "copy";
        this.state.isDragOver = true;
    }

    onDragLeave(ev) {
        if (!ev.currentTarget.contains(ev.relatedTarget)) {
            this.state.isDragOver = false;
        }
    }

    onDrop(ev) {
        ev.preventDefault();
        this.state.isDragOver = false;
        const files = [...ev.dataTransfer.files].filter(f => f.type.startsWith("image/"));
        if (files.length) this._upload(files[0]);
    }

    onFileInput(ev) {
        const file = ev.target.files[0];
        ev.target.value = "";
        if (file) this._upload(file);
    }

    openFilePicker() {
        this.fileInputRef.el.click();
    }

    async _upload(file) {
        this.state.uploading = true;
        try {
            const data = await this._toBase64(file);
            const result = await this.orm.call(
                "shoes.sku.numeric.import.line",
                "action_upload_slot",
                [[this.props.lineId], this.props.slotIndex, data]
            );
            this.state.hasImage = result.has_image;
            this.state.imgUrl = result.url ? result.url + "?t=" + Date.now() : false;
            this.props.onUploaded(this.props.lineId, this.props.slotIndex, result);
            this.notification.add(
                `Imagen guardada (slot ${this.props.slotIndex})`,
                { type: "success" }
            );
        } catch {
            this.notification.add("Error al subir imagen", { type: "danger" });
        } finally {
            this.state.uploading = false;
        }
    }

    _toBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result.split(",")[1]);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }
}

// ─── Main widget ─────────────────────────────────────────────────────────────

export class ShoesSkuNumericDropWidget extends Component {
    static template = "shoes_product_sku.ShoesSkuNumericDropWidget";
    static props = { ...standardFieldProps };
    static components = { ShoesSkuSlotZone };

    setup() {
        this.state = useState({ lineDataMap: {}, slotDataMap: {} });
        this.orm = useService("orm");

        onWillStart(async () => {
            const list = this.props.record.data[this.props.name];
            const ids = list.records.map(r => r.resId).filter(Boolean);
            if (!ids.length) return;

            // Line metadata
            const rows = await this.orm.read(
                "shoes.sku.numeric.import.line",
                ids,
                ["shoes_sku_id", "color_value_id", "photo_count"]
            );
            const lineMap = {};
            for (const row of rows) lineMap[row.id] = row;
            this.state.lineDataMap = lineMap;

            // All slot data in one RPC
            const slotData = await this.orm.call(
                "shoes.sku.numeric.import.line",
                "get_all_lines_slot_data",
                [ids]
            );
            // Keys come back as strings from JSON
            const slotMap = {};
            for (const [k, v] of Object.entries(slotData)) slotMap[Number(k)] = v;
            this.state.slotDataMap = slotMap;
        });
    }

    get lines() {
        return this.props.record.data[this.props.name].records;
    }

    get photoCount() {
        const vals = Object.values(this.state.lineDataMap);
        return vals.length ? vals[0].photo_count : 1;
    }

    get slotIndices() {
        return Array.from({ length: this.photoCount }, (_, i) => i + 1);
    }

    getLineInfo(line) {
        return this.state.lineDataMap[line.resId] || {};
    }

    getSlotData(lineId, slotIndex) {
        const slots = this.state.slotDataMap[lineId];
        return slots ? slots[slotIndex - 1] : { has_image: false, url: false };
    }

    slotLabel(index) {
        return index === 1 ? "Main" : `Photo ${index}`;
    }

    onSlotUploaded(lineId, slotIndex, result) {
        const slots = this.state.slotDataMap[lineId];
        if (slots) slots[slotIndex - 1] = result;
    }
}

registry.category("fields").add("shoes_sku_numeric_drop", {
    component: ShoesSkuNumericDropWidget,
    supportedTypes: ["one2many"],
});
