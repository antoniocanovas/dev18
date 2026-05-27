/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, useRef, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

class ShoesSkuDropCard extends Component {
    static template = "shoes_product_sku.ShoesSkuDropCard";
    static props = {
        lineId: Number,
        skuId: Number,
        skuName: String,
        colorName: String,
        imageCount: Number,
        onUploaded: Function,
    };

    setup() {
        this.state = useState({
            isDragOver: false,
            uploading: false,
            count: this.props.imageCount,
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
        if (files.length) {
            this._uploadFiles(files);
        }
    }

    onFileInput(ev) {
        const files = [...ev.target.files];
        ev.target.value = "";
        if (files.length) {
            this._uploadFiles(files);
        }
    }

    openFilePicker() {
        this.fileInputRef.el.click();
    }

    async _uploadFiles(files) {
        this.state.uploading = true;
        try {
            const images = await Promise.all(
                files.map(file =>
                    this._fileToBase64(file).then(data => ({ name: file.name, data }))
                )
            );
            const newCount = await this.orm.call(
                "shoes.sku.task.image.import.line",
                "action_bulk_upload",
                [[this.props.lineId], images]
            );
            this.state.count = newCount;
            this.props.onUploaded(this.props.lineId, newCount);
            this.notification.add(
                `${files.length} imagen(es) subida(s) para ${this.props.skuName}`,
                { type: "success" }
            );
        } catch {
            this.notification.add("Error al subir imágenes", { type: "danger" });
        } finally {
            this.state.uploading = false;
        }
    }

    _fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result.split(",")[1]);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }
}

export class ShoesSkuImageDropWidget extends Component {
    static template = "shoes_product_sku.ShoesSkuImageDropWidget";
    static props = { ...standardFieldProps };
    static components = { ShoesSkuDropCard };

    setup() {
        this.state = useState({ updatedCounts: {}, lineDataMap: {} });
        this.orm = useService("orm");

        onWillStart(async () => {
            const list = this.props.record.data[this.props.name];
            const ids = list.records.map(r => r.resId).filter(Boolean);
            if (!ids.length) return;
            const rows = await this.orm.read(
                "shoes.sku.task.image.import.line",
                ids,
                ["shoes_sku_id", "color_value_id", "existing_image_count"]
            );
            const map = {};
            for (const row of rows) map[row.id] = row;
            this.state.lineDataMap = map;
        });
    }

    get lines() {
        return this.props.record.data[this.props.name].records;
    }

    _lineInfo(line) {
        return this.state.lineDataMap[line.resId] || {};
    }

    getSkuId(line) {
        const v = this._lineInfo(line).shoes_sku_id || line.data.shoes_sku_id;
        return v ? v[0] : 0;
    }

    getSkuName(line) {
        const v = this._lineInfo(line).shoes_sku_id || line.data.shoes_sku_id;
        return v ? v[1] : "";
    }

    getColorName(line) {
        const v = this._lineInfo(line).color_value_id || line.data.color_value_id;
        return v ? v[1] : "";
    }

    getCount(line) {
        const id = line.resId;
        if (id in this.state.updatedCounts) return this.state.updatedCounts[id];
        return this._lineInfo(line).existing_image_count || line.data.existing_image_count || 0;
    }

    onCardUploaded(lineId, newCount) {
        this.state.updatedCounts[lineId] = newCount;
    }
}

registry.category("fields").add("shoes_sku_image_drop", {
    component: ShoesSkuImageDropWidget,
    supportedTypes: ["one2many"],
});
