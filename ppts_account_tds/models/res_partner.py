# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"  
    
    is_tds = fields.Boolean('Is TDS Applicable ?', track_visibility='always')
    tds_deductee_id = fields.Many2one('account.tds.deductee.type', 'TDS Deductee Type')
    tds_section_ids = fields.Many2many('account.tds',"TDS Section", related="tds_deductee_id.tds_ids")
    tds_section_id = fields.Many2one('account.tds',"TDS Section", track_visibility='always')
    
    @api.onchange('is_tds')
    def onchange_tds(self):
        if not self.is_tds:
            self.tds_section_id = False
            