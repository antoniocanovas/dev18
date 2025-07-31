# Sale Product Matrix Configurator

## Description

Module that allows choosing the configuration mode (Matrix Grid or Product Configurator) before selecting products in sale order lines.

## Features

* Configuration mode selector appears before product selection
* Respects user choice and doesn't auto-open unwanted configurators
* Compatible with existing sale_product_matrix functionality
* Works with both matrix and configurator products
* Preserves custom attribute values for text-type attributes

## Installation

1. Copy the module to the addons directory
2. Update module list: `./odoo-bin -u sale_product_matrix_configurator`
3. Install the module "Sale Product Matrix Configurator"

## Usage

1. In a sale order line, the "Config Mode" field appears before product selection
2. Choose between "Matrix Grid" or "Product Configurator"
3. Select the product template
4. The configurator will open according to the chosen mode
5. Custom attribute values (including free text fields) will be preserved correctly

## Module Structure

```
sale_product_matrix_configurator/
├── __manifest__.py                     # Module manifest
├── README.md                           # This documentation
├── .gitignore                          # Git exclusions
├── __init__.py                         # Module initialization
├── models/
│   ├── __init__.py
│   └── sale_order_line.py             # Extended models
├── static/src/js/
│   └── sale_product_field_configurator.js  # JavaScript configurator
└── views/
    └── sale_order_views.xml           # UI views
```

## Dependencies

- `sale`: Base sales module
- `sale_product_matrix`: Product matrix functionality  
- `product`: Product and attribute models

## Compatibility

- Odoo 18.0
- Compatible with existing product configuration modules
- Does not interfere with standard sale_product_matrix behavior
- No additional security permissions required (inherits from core models)

## Author

**Antonio Canovas Pedreno**  
📧 [GitHub](https://github.com/antoniocanovas)  
📜 License: LGPL-3
