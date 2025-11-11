Shoes Analysis Module
====================

This module provides comprehensive sales analysis for shoes dealer business with detailed reporting capabilities including a financial report-style interface.

## Features

### Main Analysis View (Pair sales)
- Detailed view of all sales transactions
- Analysis for both pairs and assortments
- Multiple view modes: List, Pivot, Graph
- Advanced filtering and grouping options

### Sales Statistics Report (P&L Style)
- **Financial report interface** similar to Accounting P&L
- **Period filters**: Current Year, Current Month, Last Year, Comparison
- **Custom filters**: Brand, Sales Team, Salesman
- **Hierarchical grouping**: Model > Color > Size
- **Ordered by sales volume** (highest to lowest)
- **Expandable/collapsible sections**
- **Columns**: Size, Sold, Delivered, Invoiced

## Menu Structure

```
Shoes Dealer
└── Analysis
    ├── Pair sales (main analysis view)
    └── Sales statistics (P&L-style report)
```

## Implementation Details

### Technical Architecture

**Financial Report Framework**:
- Uses Odoo 18's `account.report` framework
- JavaScript-based interface with expandable lines
- Custom report model: `shoes.sales.statistics.report`
- Integration with account_reports module

**Data Processing**:
- Automatic record creation from sale orders
- Real-time data aggregation
- Hierarchical grouping and sorting

### Files Structure

```
shoes_analysis/
├── models/
│   ├── shoes_dealer_analysis.py        # Main analysis model
│   └── shoes_sales_statistics_report.py # P&L-style report model
├── views/
│   ├── shoes_dealer_analysis_views.xml  # Main analysis views
│   ├── shoes_sales_statistics_filters.xml # Custom filters templates
│   └── menu_views.xml                   # Menu structure
├── data/
│   └── shoes_sales_statistics_report_data.xml # Report definition
├── static/src/
│   └── shoes_sales_statistics_report.js # JavaScript for filters
└── security/
    └── ir.model.access.csv              # Access rights
```

## How it Works

### Automatic Record Creation
The module automatically creates analysis records when:
- Sale orders are created/modified
- Sale order lines are added/changed
- Orders change state

### Record Logic
- **For Pairs**: Creates one record per sale line
- **For Assortments**: Creates one record per size/pair in the BOM
- Records include quantities from BOM calculations

### Financial Report Features

**Filters Available**:
- **Date Range**: Standard period selection
- **Comparison**: Period-to-period comparison
- **Brand**: Multi-select brand filter
- **Sales Team**: Multi-select team filter
- **Salesman**: Multi-select salesman filter

**Data Hierarchy**:
1. **Model Level**: Product template model (ordered by total sales)
2. **Color Level**: Colors within each model (ordered by sales)
3. **Size Level**: Individual sizes with detailed quantities

**Report Columns**:
- **Size**: Product size/variant
- **Sold**: Total quantity sold
- **Delivered**: Total quantity delivered
- **Invoiced**: Total quantity invoiced

## Usage

### Pair Sales View
1. Navigate to **Shoes Dealer > Analysis > Pair sales**
2. Use filters to narrow down data:
   - Current Year/Month filters
   - Pairs vs Assortments
   - Sale order states
3. Group by various fields (Customer, Product, Campaign, etc.)
4. Switch between List, Pivot, and Graph views

### Sales Statistics Report (P&L Style)
1. Navigate to **Shoes Dealer > Analysis > Sales statistics**
2. **Period Selection**: Use date range picker or predefined periods
3. **Custom Filters**: 
   - Click filter buttons to select brands, teams, or salesmen
   - Multiple selections supported
4. **Navigation**:
   - Click ► to expand model/color sections
   - Click ▼ to collapse sections
   - Models automatically ordered by sales volume
5. **Data Analysis**:
   - Compare sold vs delivered vs invoiced quantities
   - Identify top-performing models and colors
   - Analyze size distribution within color variants

### Filter Usage Examples

**Period Analysis**:
- Select "Current Year" for YTD performance
- Use "Comparison" to compare with previous year
- Filter by "Current Month" for monthly analysis

**Segmentation Analysis**:
- Filter by specific brands to analyze brand performance
- Select sales teams to compare team results
- Choose individual salesmen for performance review

## Data Structure

Each analysis record contains:
- Sale line reference
- Product information (the actual pair)
- Size, color, and assortment attributes
- Quantities (sale, delivery, invoice)
- Campaign, brand, team information
- Customer and location data

## Dependencies

### Required Modules
- `shoes_dealer` (base shoes dealer functionality)
- `sale` (sales management)
- `mrp` (manufacturing/BOM)
- `account_reports` (financial reporting framework)

### Odoo Version
- Odoo 18.0 Enterprise
- Compatible with Odoo 18's new financial reporting system

## Installation

1. Ensure all dependencies are installed:
   - `shoes_dealer`
   - `account_reports`
2. Install `shoes_analysis` module
3. Refresh the browser
4. Navigate to the new menu items

## Permissions

- **Sales Users**: Read access to analysis data
- **Sales Managers**: Full access to all reports

The module respects existing Odoo security groups and integrates seamlessly with the shoes_dealer workflow.

## Technical Notes

### JavaScript Integration
- Uses Odoo 18's OWL framework
- Extends standard account_reports components
- Custom filter handling and data loading

### Performance Considerations
- Efficient data aggregation in Python
- Optimized database queries
- Hierarchical data structure for fast rendering

### Customization Points
- Report columns can be extended
- Additional filters can be added
- Grouping logic can be modified
- Custom CSS styling supported
