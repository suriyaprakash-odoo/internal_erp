from odoo import fields, models, tools, api


class OpportunityReport(models.Model):

    _inherit = "crm.opportunity.report"
    
    industry_id = fields.Many2one('crm.industry', string='Industry')
    services_id = fields.Many2one('crm.services', string='Services')
    write_date = fields.Datetime(string='No Activity Since')
    
    def _select(self):
        select_str = """
        SELECT
            c.id,
            c.date_deadline,

            c.date_open as opening_date,
            c.date_closed as date_closed,
            c.date_last_stage_update as date_last_stage_update,

            c.user_id,
            c.probability,
            c.stage_id,
            stage.name as stage_name,
            c.type,
            c.company_id,
            c.priority,
            c.team_id,
            (SELECT COUNT(*)
             FROM mail_message m
             WHERE m.model = 'crm.lead' and m.res_id = c.id) as nbr_activities,
            c.active,
            c.campaign_id,
            c.source_id,
            c.medium_id,
            c.partner_id,
            c.city,
            c.country_id,
            c.planned_revenue as total_revenue,
            c.planned_revenue*(c.probability/100) as expected_revenue,
            c.create_date as create_date,
            extract('epoch' from (c.date_closed-c.create_date))/(3600*24) as  delay_close,
            abs(extract('epoch' from (c.date_deadline - c.date_closed))/(3600*24)) as  delay_expected,
            extract('epoch' from (c.date_open-c.create_date))/(3600*24) as  delay_open,
            c.lost_reason,
            c.date_conversion as date_conversion,
            c.industry_id,
            c.services_id,
            c.write_date
        """
        return select_str
    
    def _from(self):
        from_str = """
            FROM
                    "crm_lead" c
        """
        return from_str

    def _join(self):
        join_str = """
            LEFT JOIN "crm_stage" stage ON stage.id = c.stage_id
        """
        return join_str

    def _where(self):
        where_str = """
        """
        return where_str

    def _group_by(self):
        group_by_str = """
            GROUP BY c.id, stage.name
        """
        return group_by_str

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE VIEW %s AS (
            %s
            %s
            %s
            %s
            %s
        )""" % (self._table, self._select(), self._from(), self._join(), self._where(), self._group_by()))

    
