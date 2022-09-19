# Copyright 2010-2014 Savoir-faire Linux (<http://www.savoirfairelinux.com>)
# Copyright 2016-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

UPDATE_PARTNER_FIELDS = ['firstname', 'lastname', 'user_id', 'address_home_id']


class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    @api.model
    def _get_name(self, lastname, firstname):
        return self.env['res.partner']._get_computed_name(lastname, firstname)

#     @api.onchange('firstname', 'lastname')
#     def _onchange_firstname_lastname(self):
#         if self.firstname or self.lastname:
#             self.name = self._get_name(self.lastname, self.firstname)

#     to display firstname,middlename,lastname
    @api.onchange('firstname', 'lastname', 'middlename')
    def _onchange_firstname_lastname(self):
        if self.firstname or self.lastname or self.middlename:
            self.name = str(self.firstname or '') + ' ' + str(self.middlename or '') + ' ' + str(self.lastname or '')
            
    firstname = fields.Char()
    lastname = fields.Char()
    middlename = fields.Char()

#     @api.model
#     def create(self, vals):
#         if vals.get('firstname') or vals.get('lastname'):
#             vals['name'] = self._get_name(
#                 vals.get('lastname'), vals.get('firstname'))
#         elif vals.get('name'):
#             vals['lastname'] = self.split_name(vals['name'])['lastname']
#             vals['firstname'] = self.split_name(vals['name'])['firstname']
#         else:
#             raise ValidationError(_('No name set.'))
#         res = super().create(vals)
#         res._update_partner_firstname()
#         return res

#     creating firstname,middlename,lastname
    @api.model
    def create(self, vals):
        if vals.get('firstname') or vals.get('lastname') or vals.get('middlename'):
            vals['name'] = str(vals.get('firstname') or '') + ' ' + str(vals.get('middlename') or '') + ' ' + str(vals.get('lastname') or '')
        else:
            raise ValidationError(_('No name set.'))
        return super(HrEmployee, self).create(vals)

#     @api.multi
#     def write(self, vals):
#         if 'firstname' in vals or 'lastname' in vals:
#             if 'lastname' in vals:
#                 lastname = vals.get('lastname')
#             else:
#                 lastname = self.lastname
#             if 'firstname' in vals:
#                 firstname = vals.get('firstname')
#             else:
#                 firstname = self.firstname
#             vals['name'] = self._get_name(lastname, firstname)
#         elif vals.get('name'):
#             vals['lastname'] = self.split_name(vals['name'])['lastname']
#             vals['firstname'] = self.split_name(vals['name'])['firstname']
#         res = super().write(vals)
#         if set(vals).intersection(UPDATE_PARTNER_FIELDS):
#             self._update_partner_firstname()
#         return res

#     creating new name as  firstname,middlename,lastname
    @api.multi
    def write(self, vals):
        
        fullname = ''
        if vals.get('firstname'):
            fullname = vals.get('firstname')
        elif self.firstname and 'firstname' not in vals:
            fullname = self.firstname
            
        if vals.get('middlename'):
            fullname = fullname+' '+str(vals.get('middlename')) if fullname else vals.get('middlename')
        elif self.middlename and 'middlename' not in vals:
            fullname = fullname+' '+str(self.middlename) if fullname else self.middlename
            
        if vals.get('lastname'):
            fullname = fullname+' '+str(vals.get('lastname')) if fullname else vals.get('lastname')
        elif self.lastname and 'lastname' not in vals:
            fullname = fullname+' '+str(self.lastname) if fullname else self.lastname
        
        
        vals['name'] = fullname
        return super(HrEmployee, self).write(vals)
    
    @api.model
    def split_name(self, name):
        clean_name = " ".join(name.split(None)) if name else name
        return self.env['res.partner']._get_inverse_name(clean_name)

    @api.multi
    def _inverse_name(self):
        """Try to revert the effect of :meth:`._compute_name`."""
        for record in self:
            parts = self.env['res.partner']._get_inverse_name(record.name)
            record.lastname = parts['lastname']
            record.firstname = parts['firstname']

    @api.model
    def _install_employee_firstname(self):
        """Save names correctly in the database.

        Before installing the module, field ``name`` contains all full names.
        When installing it, this method parses those names and saves them
        correctly into the database. This can be called later too if needed.
        """
        # Find records with empty firstname and lastname
        records = self.search([("firstname", "=", False),
                               ("lastname", "=", False)])

        # Force calculations there
        records._inverse_name()
        _logger.info("%d employees updated installing module.", len(records))

    def _update_partner_firstname(self):
        for employee in self:
            partners = employee.mapped('user_id.partner_id')
            partners |= employee.mapped('address_home_id')
            partners.write({
                'firstname': employee.firstname,
                'middlename': employee.middlename,
                'lastname': employee.lastname,
            })

    @api.constrains("firstname", "lastname")
    def _check_name(self):
        """Ensure at least one name is set."""
        for record in self:
            if not (record.firstname or record.lastname):
                raise ValidationError(_('No name set.'))

class HrApplicant(models.Model):

    _inherit = 'hr.applicant'

    # To display firstname,middlename,lastname
    @api.onchange('partner_name', 'lastname', 'middlename')
    def _onchange_firstname_lastname(self):
        if self.partner_name or self.lastname or self.middlename:
            self.name = str(self.partner_name or '') + ' ' + str(self.middlename or '') + ' ' + str(self.lastname or '')
            
    # firstname = fields.Char()
    lastname = fields.Char()
    middlename = fields.Char()

    @api.model
    def create(self, vals):
        if vals.get('partner_name') or vals.get('lastname') or vals.get('middlename'):
            vals['name'] = str(vals.get('partner_name') or '') + ' ' + str(vals.get('middlename') or '') + ' ' + str(vals.get('lastname') or '')
        else:
            raise ValidationError(_('No name set.'))
        return super(HrApplicant, self).create(vals)

    @api.multi
    def write(self, vals):
        
        fullname = ''
        if vals.get('partner_name'):
            fullname = vals.get('partner_name')
        elif self.partner_name and 'partner_name' not in vals:
            fullname = self.partner_name
            
        if vals.get('middlename'):
            fullname = fullname+' '+str(vals.get('middlename')) if fullname else vals.get('middlename')
        elif self.middlename and 'middlename' not in vals:
            fullname = fullname+' '+str(self.middlename) if fullname else self.middlename
            
        if vals.get('lastname'):
            fullname = fullname+' '+str(vals.get('lastname')) if fullname else vals.get('lastname')
        elif self.lastname and 'lastname' not in vals:
            fullname = fullname+' '+str(self.lastname) if fullname else self.lastname
        
        vals['name'] = fullname
        return super(HrApplicant, self).write(vals)