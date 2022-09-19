from odoo import fields, models, api

    
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    opportunity_id = fields.Many2one('crm.lead', string='Products For Quotation')   
    
    def _prepare_sale_order_lines_from_opportunity(self, record):
        data = {
                    'product_id':record.product_id.id,
                    'name':record.description,
                    'product_uom_qty':record.qty,
                    'product_uom':record.product_uom.id,
                    'price_unit':record.price_unit
                    }
        return data
    
    @api.onchange('opportunity_id')
    def opportunity_id_change(self):
        new_lines = []
        if not self.opportunity_id:
            return {}
        if not self.partner_id:
            self.partner_id = self.opportunity_id.partner_id.id

        for line in self.opportunity_id.lead_product_ids:
            data = self._prepare_sale_order_lines_from_opportunity(line)
            new_lines.append(data)
        self.order_line = new_lines
            
            
