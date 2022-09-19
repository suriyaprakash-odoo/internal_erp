from odoo import api, fields, models

class OnboardingConfigSettings(models.TransientModel):
    _name = 'onboarding.config.settings'
    _inherit = 'res.config.settings'
    
    welcome_template_id = fields.Many2one("mail.template",string="Welcome Template")
    pi_document_id = fields.Many2one("signature.request.template",string="Personal Information Document")
    bgv_survey_id = fields.Many2one("survey.survey",string="Background Check Survey")
    
    @api.model
    def get_values(self):
        res = super(OnboardingConfigSettings, self).get_values()
        res.update(
            welcome_template_id=self.env['ir.config_parameter'].sudo().get_param('ppts_onboarding.welcome_template_id'),
            pi_document_id = self.env['ir.config_parameter'].sudo().get_param('ppts_onboarding.pi_document_id'),
            bgv_survey_id = self.env['ir.config_parameter'].sudo().get_param('ppts_onboarding.bgv_survey_id')
        )
        res['welcome_template_id'] = int(res['welcome_template_id'])
        res['pi_document_id'] = int(res['pi_document_id'])
        res['bgv_survey_id'] = int(res['bgv_survey_id'])
        return res

    @api.multi
    def set_values(self):
        super(OnboardingConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('ppts_onboarding.welcome_template_id', self.welcome_template_id.id)
        self.env['ir.config_parameter'].sudo().set_param('ppts_onboarding.pi_document_id', self.pi_document_id.id),
        self.env['ir.config_parameter'].sudo().set_param('ppts_onboarding.bgv_survey_id', self.bgv_survey_id.id)