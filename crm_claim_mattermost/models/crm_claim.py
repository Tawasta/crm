# -*- coding: utf-8 -*-
import os
from subprocess import call

from openerp import api, fields, models
from openerp.exceptions import ValidationError
from openerp import _


class CrmClaim(models.Model):

    _inherit = 'crm.claim'

    @api.model
    def create(self, values):
        res = super(CrmClaim, self).create(values)

        res.mattermost_claim_created()

        return res

    @api.multi
    def write(self, values):
        res = super(CrmClaim, self).write(values)

        for record in self:
            if 'user_id' in values:
                record.mattermost_claim_author_changed()

            if 'stage_id' in values:
                record.mattermost_claim_stage_changed()

        return res

    def mattermost_claim_created(self):
        if self.name and self.partner_id:
            subject = "[%s](%s)" % (self.name, self.mattermost_get_url())

            msg = ':incoming_envelope: A new claim **%(subject)s** from **%(partner)s**' \
                  % {'subject': subject, 'partner': self.partner_id.display_name}

            return self.mattermost_send_message(_(msg))

    def mattermost_claim_author_changed(self):
        subject = "[%s](%s)" % (self.name, self.mattermost_get_url())
        author = self.user_id.name or 'No one'

        msg = '**%(user)s** assigned **%(subject)s** to **%(author)s**' \
              % {'user': self.write_uid.name, 'subject':subject, 'author': author}

        return self.mattermost_send_message(_(msg))

    def mattermost_claim_stage_changed(self):
        subject = "[%s](%s)" % (self.name, self.mattermost_get_url())

        msg = '**%(user)s** changed **%(subject)s** stage to **%(stage)s**' \
              % {'user': self.write_uid.name, 'subject': subject, 'stage': self.stage_id.name}

        return self.mattermost_send_message(_(msg))

    @api.model
    def mattermost_summary(self):
        stages = self.env['crm.claim.stage'].search([('closed', '=', False)])

        for company in self.env['res.company'].search([('mattermost_active', '=', True)]):
            msg = '### Claim summary\n'

            for stage in stages:
                count = self.search_count([('company_id', '=', company.id), ('stage_id', '=', stage.id)])
                msg += '%s: **%s**\n' % (stage.name, count)

            print msg
            self.mattermost_send_message(_(msg), company)


    def mattermost_get_url(self):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        url = "%(base_url)sweb/#id=%(record_id)s&view_type=form&model=crm.claim" \
              % {'base_url': base_url, 'record_id': self.id}

        return url

    def mattermost_send_message(self, message, company=False):
        company = self.company_id or company

        if not company or not company.mattermost_active:
            # Mattermost claim integration is not set
            return False

        # Validate variables
        validation_error = self.validate_variables(company)
        if validation_error:
            raise ValidationError(validation_error)

        vars = {
            'login_id': company.mattermost_login_id,
            'password': company.mattermost_password,
            'team': company.mattermost_team,
            'channel': company.mattermost_channel,
            'url': company.mattermost_url,
            'port': company.mattermost_port,
            'basepath': company.mattermost_basepath,
            'scheme': company.mattermost_scheme,
            'verify': company.mattermost_verify,
            'message': message,
        }

        # This could be done smarter
        file_path = os.path.abspath(__file__)
        models_path = os.path.dirname(file_path)
        module_path = os.path.dirname(models_path)
        script_path = '%s/ext/mattermost_send.py' % module_path

        cmd = 'python3 %(script)s "%(vars)s"' % {'script': script_path, 'vars': vars}
        call(cmd, shell=True)

    def validate_variables(self, company):
        # TODO: actual validation for each variable and custom error messages
        error_msg = False

        if not company.mattermost_login_id:
            error_msg = 'Invalid login id'
        elif not company.mattermost_password:
            error_msg = 'Missing password'
        elif not company.mattermost_team:
            error_msg = 'Invalid team'
        elif not company.mattermost_channel:
            error_msg = 'Invalid channel'
        elif not company.mattermost_url:
            error_msg = 'Invalid url'
        elif not company.mattermost_port:
            error_msg = 'Invalid port'
        elif not company.mattermost_basepath:
            error_msg = 'Invalid path'
        elif not company.mattermost_scheme:
            error_msg = 'Invalid scheme'

        return error_msg
