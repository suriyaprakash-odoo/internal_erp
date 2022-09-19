from odoo import api, fields, models, _, tools
from datetime import date

class TdsSqlReport(models.Model):
    _name = "tds.sql.report"
    _description = "TDS Supplier Payment Report"
    _auto = False
    
    entry_date = fields.Date('Entry Date')
    company_id = fields.Many2one('res.company','Company')
    invoice_id = fields.Many2one('account.invoice','Invoice')
    payment_id = fields.Many2one('account.payment','Payment')
    partner_id = fields.Many2one('res.partner','Partner Name')
    internal_ref = fields.Char('Ref.No',size=64)
    supplier_ref_date = fields.Date('Supplier Invoice Date')
    tds_section_id = fields.Many2one('account.tds','TDS Section')
    account_id = fields.Many2one('account.account','TDS Account')
    access_amount = fields.Float('Assesable Amount')
    tds_total = fields.Float('TDS Total')
    tds_bal = fields.Float('TDS Balance')
    net_payable = fields.Float('Net Payable')
    invoice_state = fields.Selection([
            ('to_be_checked', 'To be Checked'),
            ('waiting_for_approval', 'Waiting for Approval'),
            ('draft','Draft'),
            ('proforma','Pro-forma'),
            ('proforma2','Pro-forma'),
            ('open','Open'),
            ('paid','Paid'),
            ('cancel','Cancelled'),
            ],'Invoice State')
    paid_state = fields.Selection([('draft', 'Draft'), ('open', 'Open'), ('paid', 'Paid')], 'TDS Payment Status')
    
    def _select(self):
        select_str = """select 
            tds.id as id,
            tds.date as entry_date,
            '' as supplier_ref_date,
            tds.name as internal_ref,
            tds.company_id as company_id,
            res.id as partner_id,
            inv.id as invoice_id,
            pay.id as payment_id,
            sec.id as tds_section_id,
            aa.id as account_id,
            tds.tds_amount as tds_total,
            tds.bal_amount as tds_bal,
            tds.amount as access_amount,
            tds.tds_payable as net_payable,
            inv.state as invoice_state,
            tds.state as paid_state"""
        return select_str
    
    def _from(self):
        from_str = """from  account_tds_payment tds"""
        return from_str

    def _join(self):
        join_str = """
            left join account_invoice_line inl on (inl.id=tds.invoice_line_id)
            left join account_invoice inv on (inv.id = tds.invoice_id)
            left join account_payment pay on (pay.id = tds.payment_id)
            left join res_partner res on (res.id=tds.partner_id)
            left join account_tds sec on (sec.id=tds.tds_section_id)
            left join account_account aa on (aa.id=tds.account_id)
        """
        return join_str

    def _where(self):
        where_str = """ """
        return where_str

    def _group_by(self):
        group_by_str = """ """
        return group_by_str

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s AS (
            %s
            %s
            %s
            %s
            %s    
        )""" % (self._table, self._select(), self._from(), self._join(), self._where(), self._group_by()))
        
        
        

