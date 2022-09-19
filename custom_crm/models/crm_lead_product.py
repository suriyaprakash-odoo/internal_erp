from odoo import fields, models, api


class CrmLeadProduct(models.Model):
    _name = 'crm.lead.product'
    
    product_id = fields.Many2one('product.product', string='Product', required=True)
    description = fields.Text(string='Description')
    qty = fields.Float(string='Ordered Qty', default=1.0)
    product_uom = fields.Many2one('product.uom', string='Unit of Measure')
    price_unit = fields.Float(string='Unit Price')
    lead_id = fields.Many2one('crm.lead')
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.description = self.product_id.name

    @api.onchange('product_id')
    def onchange_product_uom(self):
        if self.product_id:
            self.product_uom = self.product_id.uom_id.id

