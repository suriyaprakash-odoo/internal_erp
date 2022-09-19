from odoo import models, api, _, fields
from odoo.tools.misc import formatLang
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, float_is_zero


class ReportPartnerLedger(models.AbstractModel):
    _inherit = "account.partner.ledger"

    def do_query(self, options, line_id):
        account_types = [a.get('id') for a in options.get('account_type') if a.get('selected', False)]
        if not account_types:
            account_types = [a.get('id') for a in options.get('account_type')]
        select = ',COALESCE(SUM(\"account_move_line\".debit-\"account_move_line\".credit), 0),SUM(\"account_move_line\".debit),SUM(\"account_move_line\".credit)'
        if options.get('cash_basis'):
            select = select.replace('debit', 'debit_cash_basis').replace('credit', 'credit_cash_basis')
        sql = "SELECT \"account_move_line\".partner_id%s FROM %s WHERE %s%s AND \"account_move_line\".partner_id IS NOT NULL GROUP BY \"account_move_line\".partner_id"
        tables, where_clause, where_params = self.env['account.move.line']._query_get([('account_id.internal_type', 'in', account_types)])
        if not isinstance(line_id, int) and line_id:
            if  len(line_id) > 1:
                line_clause = line_id and ' AND \"account_move_line\".partner_id in (' + str(line_id) + ')' or ''
            else:
                line_clause = line_id and ' AND \"account_move_line\".partner_id = ' + str(tuple(line_id)[0]) or ''
        else:
            line_clause = line_id and ' AND \"account_move_line\".partner_id = ' + str(line_id) or ''

        if options.get('unreconciled'):
            line_clause += ' AND \"account_move_line\".full_reconcile_id IS NULL'
        query = sql % (select, tables, where_clause, line_clause)
        self.env.cr.execute(query, where_params)
        results = self.env.cr.fetchall()
        results = dict([(k[0], {'balance': k[1], 'debit': k[2], 'credit': k[3]}) for k in results])
        return results

    @api.model
    def get_lines(self, options, line_id=None):
        lines = []
        if line_id:
            line_id = line_id.replace('partner_', '')
        context = self.env.context

        # If a default partner is set, we only want to load the line referring to it.
        if options.get('partner_id'):
            line_id = options['partner_id']

        grouped_partners = self.group_by_partner_id(options, line_id)
        sorted_partners = sorted(grouped_partners, key=lambda p: p.name or '')
        unfold_all = context.get('print_mode') and not options.get('unfolded_lines') or options.get('partner_id')
        total_initial_balance = total_debit = total_credit = total_balance = 0.0
        for partner in sorted_partners:
            debit = grouped_partners[partner]['debit']
            credit = grouped_partners[partner]['credit']
            balance = grouped_partners[partner]['balance']
            initial_balance = grouped_partners[partner]['initial_bal']['balance']
            total_initial_balance += initial_balance
            total_debit += debit
            total_credit += credit
            total_balance += balance
            lines.append({
                'id': 'partner_' + str(partner.id),
                'name': partner.name,
                'columns': [{'name': v} for v in [self.format_value(initial_balance), self.format_value(debit), self.format_value(credit), self.format_value(balance)]],
                'level': 2,
                'trust': partner.trust,
                'unfoldable': True,
                'unfolded': 'partner_' + str(partner.id) in options.get('unfolded_lines') or unfold_all,
                'colspan': 5,
            })
            if 'partner_' + str(partner.id) in options.get('unfolded_lines') or unfold_all:
                progress = initial_balance
                domain_lines = []
                amls = grouped_partners[partner]['lines']
                too_many = False
                if len(amls) > 80 and not context.get('print_mode'):
                    amls = amls[-80:]
                    too_many = True
                for line in amls:
                    if options.get('cash_basis'):
                        line_debit = line.debit_cash_basis
                        line_credit = line.credit_cash_basis
                    else:
                        line_debit = line.debit
                        line_credit = line.credit
                    progress_before = progress
                    progress = progress + line_debit - line_credit
                    name = '-'.join(
                        (line.move_id.name not in ['', '/'] and [line.move_id.name] or []) +
                        (line.ref not in ['', '/', False] and [line.ref] or []) +
                        ([line.name] if line.name and line.name not in ['', '/'] else [])
                    )
                    if len(name) > 35 and not self.env.context.get('no_format'):
                        name = name[:32] + "..."
                    caret_type = 'account.move'
                    if line.invoice_id:
                        caret_type = 'account.invoice.in' if line.invoice_id.type in ('in_refund', 'in_invoice') else 'account.invoice.out'
                    elif line.payment_id:
                        caret_type = 'account.payment'
                    domain_lines.append({
                        'id': line.id,
                        'parent_id': 'partner_' + str(partner.id),
                        'name': line.date,
                        'columns': [{'name': v} for v in [line.journal_id.code, line.account_id.code, name, line.full_reconcile_id.name, self.format_value(progress_before),
                                                          line_debit != 0 and self.format_value(line_debit) or '',
                                                          line_credit != 0 and self.format_value(line_credit) or '',
                                                          self.format_value(progress)]],
                        'caret_options': caret_type,
                        'level': 4,
                    })
                if too_many:
                    domain_lines.append({
                        'id': 'too_many_' + str(partner.id),
                        'parent_id': 'partner_' + str(partner.id),
                        'action': 'view_too_many',
                        'action_id': 'partner,%s' % (partner.id,),
                        'name': _('There are more than 80 items in this list, click here to see all of them'),
                        'colspan': 8,
                        'columns': [{}],
                    })
                lines += domain_lines
        lines.append({
            'id': 'grouped_partners_total',
            'name': _('Total'),
            'level': 0,
            'class': 'o_account_reports_domain_total',
            'columns': [{'name': v} for v in ['', '', '', '', self.format_value(total_initial_balance), self.format_value(total_debit), self.format_value(total_credit), self.format_value(total_balance)]],
        })

        return lines