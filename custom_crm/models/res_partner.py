# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo import SUPERUSER_ID

class ResPartner(models.Model):
    _inherit = 'res.partner'
 
    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if not domain:
            domain = []  
        if SUPERUSER_ID != self.env.user.id and self.env.user.has_group('custom_crm.group_own_customer'):
            domain += [("create_uid",'=', self._uid)]
        res = super(ResPartner, self).search_read(
            domain, fields, offset, limit, order)
        return res
