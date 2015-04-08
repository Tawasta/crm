from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import SUPERUSER_ID, tools
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)

class crm_claim(osv.Model):      

    _name='crm.claim'
    _inherit = 'crm.claim'
    _order = "stage_id, date DESC, write_date DESC"
    
    ''' When the module is installed, fetch all claims without a number and assign them one '''
    def _init_claim_numbers(self, cr, uid, ids=None, context=None):

        search_filter = [('claim_number','=',False)]
        
        matches = self.search(cr, SUPERUSER_ID, args=search_filter,order='id')
        
        settings_model = self.pool.get('crm_claim.settings')
        
        claim_number = settings_model.browse(cr, SUPERUSER_ID, [1], context)[0].next_number
        for match in self.browse(cr, SUPERUSER_ID, matches, context):
            self.write(cr, SUPERUSER_ID, [match.id], {'claim_number': claim_number }, context)
            claim_number += 1

        ''' Update the highest number in the settings '''
        settings_model.write(cr, SUPERUSER_ID, [1], {'next_number': claim_number }, context)
        
        return True 

    ''' When a claim is created, assign it a new claim number '''
    def create(self, cr, uid, vals, context=None):
        if not context:
            context = {}

        if vals.get('email_from'):
            vals['email_from_readonly'] = vals.get('email_from')

        ''' If partner doesn't exist, we need to create one '''
        if vals.get('partner_id') == False:
            vals['autogenerated'] = True
            vals['partner_id'] = self._create_partner(cr, uid, vals, context=context)
    
        vals['claim_number'] = self._get_claim_number(cr,uid)
        res = super(crm_claim, self).create(cr, uid, vals, context)
        
        if self.browse(cr, uid, [res], context)[0]:
            fetchmail_server = self.pool.get('fetchmail.server').browse(cr,uid,context.get('fetchmail_server_id'))
            
            if fetchmail_server:
                company_id = fetchmail_server.company_id.id
                reply_to = self._default_get_reply_to(cr, uid, company_id=company_id)
                
                write_vals = { 'company_id': company_id, 'reply_to': reply_to, 'user_id': False }
                
                super(crm_claim, self).write(cr, uid, [res], write_vals, context)

        ''' Remove the helpdesk email and its aliases from cc emails '''
        claim_instance = self.browse(cr, uid, res)
        if claim_instance.email_cc:        
            email_list = claim_instance.email_cc.split(',')

            try:    
                email_regex = re.compile("[<][^>]+[>]")
                email_raw = email_regex.findall(claim_instance.reply_to)[0]
                email_raw = re.sub(r'[<>]', "", email_raw)
                
                reply_to = email_raw
                
                exclude_list = self._get_exclude_list(cr, uid, context, claim_instance.company_id.id) + [reply_to]
    
                for exclude in exclude_list:
                    match = [s for s in email_list if exclude in s]
        
                    if match:
                        email_list.pop(email_list.index(match[0]))
                    
                    match = False
                    
                email_cc = ','.join(email_list)
                
                self.write(cr, uid, res, {'email_cc': email_cc})
            except Exception, e:
                _logger.error('Could not set email CC: %s', e)
        
        if vals.get('attachment_ids'):
            ''' Update attachment res_id so inline-added attachments are matched correctly '''
            attachment_obj = self.pool.get('ir.attachment')
            try:
                attachments_list = vals.get('attachment_ids')[0][2]
                for attachment in attachments_list:
                    attachment_obj.write(cr, uid, attachment, {'res_id': res})
            except:
                attachments_list = []
            
            ''' Check if attachments are removed '''
            for attachment_id in attachment_obj.search(cr, SUPERUSER_ID, [('res_id','=',res),('res_model','=','crm.claim')]):
                if attachment_id not in attachments_list:
                    attachment_obj.unlink(cr, uid, res)
            
        self._claim_send_autoreply(cr, uid, res, context)
        
        return res
    
    def write(self, cr, uid, ids, values, context=None):
        ''' When a claim stage changes, save the date '''
        
        if values.get('email_from'):
            values['email_from_readonly'] = values.get('email_from')
        
        if values.get('stage_id'):
            stage_id = values.get('stage_id')
            
            if stage_id == 2:
                # In progress
                values['date_start'] = datetime.now().replace(microsecond=0)
                if not self.browse(cr,uid,ids)[0].user_id:
                    values['user_id'] = uid
            if stage_id == 3:
                # Settled
                values['date_settled'] = datetime.now().replace(microsecond=0)
            if stage_id == 4:
                # Rejected
                values['date_rejected'] = datetime.now().replace(microsecond=0)
            if stage_id == 5:
                # Waiting
                values['date_waiting'] = datetime.now().replace(microsecond=0)
                
        if values.get('attachment_ids'):
            ''' Update attachment res_id so inline-added attachments are matched correctly '''
            attachment_obj = self.pool.get('ir.attachment')
            try:
                attachments_list = values.get('attachment_ids')[0][2]
            except:
                attachments_list = []

            for attachment in attachments_list:
                if not attachment_obj.browse(cr, uid, attachment).res_id:
                    attachment_obj.write(cr, SUPERUSER_ID, attachment, {'res_id': self.browse(cr, uid, ids).id})
                
        if values.get('message_last_post'):
            ''' Check if a closed ticket gets a message. If so, mark the ticket as new '''
            if self.browse(cr, uid, ids).stage_id.id in [3,4]:
                values['stage_id'] = 1
                msg_body = _("Re-opening claim due a new message.")
                self.message_post(cr, uid, ids, body=msg_body)
                
        if values.get('partner_id'):
            ''' Partner id is changed. Set the new partner as a follower '''
            _logger.warn(self.browse(cr,uid,ids).partner_id)
            self.message_unsubscribe(cr, uid, ids, [self.browse(cr,uid,ids).partner_id.id], context=context)
            self.message_subscribe(cr, uid, ids, [values.get('partner_id')], context=context)
                
        return super(crm_claim, self).write(cr, uid, ids, values, context=context)

    def message_new(self, cr, uid, msg, custom_values=None, context=None):
        if custom_values is None:
            custom_values = {}
        
        email_cc = msg.get('to')
        
        if msg.get('cc'):
            email_cc = email_cc + "," + msg.get('cc')
        
        defaults = {
            'email_cc': email_cc
        }
        
        defaults.update(custom_values)

        res =  super(crm_claim, self).message_new(cr, uid, msg, custom_values=defaults, context=context)
        
        return res
    
    def _create_partner(self, cr, uid, vals, context=None):
        email_from = vals.get('email_from')
        name_regex = re.compile("^[^<]+")
        email_regex = re.compile("[<][^>]+[>]")
        
        try:
            name = name_regex.findall(email_from)[0]
            email = email_regex.findall(email_from)[0]
        except IndexError:
            # The email has no name information
            name = email_from
            email = email_from
        
        email = re.sub(r'[<>]', "", email)
        name = re.sub(r'["]', "", name)
        
        partner_vals = {}
        partner_vals['name'] = name
        partner_vals['email'] = email
        partner_vals['claim_autogenerated'] = True
        partner_id = self.pool.get('res.partner').create(cr, uid, partner_vals)
        
        return partner_id
    
    # Not implemented
    def action_rejected(self, cr, uid, ids, context=None):
        _logger.warn("Rejected")
        
        return super(crm_claim, self).action_rejected(cr, uid, context)
        
    # Not implemented
    def action_settled(self, cr, uid, ids, context=None):
        _logger.warn("Settled")
        
        return super(crm_claim, self).action_settled(cr, uid, context)
    
    # Not implemented
    def _onchange_stage_id(self, cr, uid, ids, stage_id, context):
        _logger.warn(stage_id)
        return True
    
    def _claim_send_autoreply(self, cr, uid, claim_id, context):
        ''' Checks if a partner is applicable for sending a mail '''
        claim = self.browse(cr, uid, claim_id)
        partner = claim.partner_id

        ''' All claims for the partner within the last 15 minutes '''
        timestamp_search = datetime.strftime(datetime.now() - relativedelta(minutes=15), '%Y-%m-%d %H:%M:%S')
        claims_count = self.search(cr, SUPERUSER_ID, [('partner_id', '=', partner.id),('stage_id', '=', 1), ('create_date', '>=', timestamp_search)], count=True)
        
        if claims_count > 3:
            _logger.warn("This partner has more than three new claims in last 15 minutes. Autoreply is disabled")
            msg_body = _("<strong>Autoreply was not sent.</strong>") + "<br/>" 
            msg_body += _('This partner has more than three claims in the last 15 minutes.')
            msg_body += _('Sending autoreply is disabled for this partner to prevent an autoreply-loop.')
            msg_body += _('Please wait a while before creating new ticket, or mark some tickets as started.')
            self.message_post(cr, uid, [claim.id], body=msg_body)
            #raise osv.except_osv('Error', 'This partner has more than three claims in the last 15 minutes. Please wait before creating a claim.')    

            return False
        
        self._claim_created_mail(cr, uid, claim_id, context)
        return True
    
    def _claim_created_mail(self, cr, uid, claim_id, context, disabled=False):
        ''' Creates and sends a "claim created" mail to the partner '''
        claim = self.browse(cr, uid, claim_id)
        mail_message = self.pool.get('mail.message')
        values = {}

        subject = "#" + str(claim.claim_number) + ": " + claim.name
        email = claim.reply_to
    
        if claim.description == False:
            claim.description = ''

        description = claim.description.replace('\n', '<br />')

        #values['body'] = "<p style='font-weight: bold;'>" + subject + "</p>"
        values['body'] = "<p><span style='font-weight: bold;'>" + _("Received claim") + ":</span></p>"
        values['body'] += "<p><div dir='ltr' style='margin-left: 2em;'>" + str(description) + "</div></p>"
        
        values['record_name'] = subject
        values['subject'] = subject
        values['email_from'] = email
        values['reply_to'] = email
        
        values['res_id'] = claim.id
        values['model'] = claim.__class__.__name__
        values['type'] = 'email'
        values['subtype_id'] = 1
        
        if claim.attachment_ids:
            values['attachment_ids'] = [(6, 0, claim.attachment_ids.ids)]
        
        if claim.partner_id:
            self.message_subscribe(cr, uid, [claim.id], [claim.partner_id.id])
        
        context = {'default_model': 'crm.claim', 'default_res_id': claim_id}
        context['pre_header'] = "<strong>" + _("Your claim has been received.") + "</strong>"
        
        res = mail_message.create(cr, uid, values, context)
        
        return res
    
    def _default_get_value(self, cr, uid, value_name, context=None, company_id=None):
        return False
        
        if not company_id:
            company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
    
        reply_ids=self.pool.get('crm_claim.reply').search(cr, SUPERUSER_ID,[('company_id', '=', company_id)])
        assert len(reply_ids) == 1, 'There should be only one settings instance for each company.'
        
        if reply_ids:
            reply_obj = self.pool.get('crm_claim.reply').browse(cr,SUPERUSER_ID,reply_ids)[0]
        else:
            _logger.warn('There were no settings for company %s', company_id)
            return False
        
        _logger.warn(reply_obj)
        _logger.warn(value_name)
        
        res = getattr(reply_obj, value_name, False)
            
        _logger.warn("Res: %", res)
            
        return res

    def _default_get_reply_to(self, cr, uid, context=None, company_id=None):
        if not company_id:
            company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        
        reply_ids=self.pool.get('crm_claim.reply').search(cr,uid,[('company_id', '=', company_id)])
        if reply_ids:
            reply_obj = self.pool.get('crm_claim.reply').browse(cr,uid,reply_ids)
            if reply_obj.reply_to:
                reply_to=reply_obj.reply_to
                return reply_to
            
        return False
    
    def _get_exclude_list(self, cr, uid, context=None, company_id=None):
        mail_ids = self._default_get_reply_alias_ids(cr, uid, context, company_id)
        
        res = []
        
        for mail_id in mail_ids:
            res.append(mail_id.name)
            
        return res
    
    def _default_get_reply_alias_ids(self, cr, uid, context=None, company_id=None):
        #return self._default_get_value(cr, uid, 'reply_alias_ids', context, company_id)
        if not company_id:
            company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        
        reply_object = self.pool.get('crm_claim.reply')
        
        
        reply_settings_id = reply_object.search(cr,uid,[('company_id', '=', company_id)])[0]
        
        if reply_settings_id:
            result = reply_object.browse(cr,SUPERUSER_ID,reply_settings_id).reply_alias_ids

            return result
        
        return False
    
    def _default_get_reply_header(self, cr, uid, context=None, company_id=None,):
        if not company_id:
            company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        
        reply_object = self.pool.get('crm_claim.reply')
        
        
        reply_settings_id = reply_object.search(cr,uid,[('company_id', '=', company_id)])[0]
        
        if reply_settings_id:
            result = reply_object.browse(cr,uid,reply_settings_id).header

            return result
        
        return False
    
    def _default_get_reply_footer(self, cr, uid, context=None, company_id=None,):
        if not company_id:
            company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        
        reply_object = self.pool.get('crm_claim.reply')
        reply_settings_id = reply_object.search(cr,uid,[('company_id', '=', company_id)])[0]
        
        if reply_settings_id:
            result = reply_object.browse(cr,uid,reply_settings_id).footer

            return result
        
        return False
        
    def _get_claim_number(self, cr, uid, context=None):
        settings_model  = self.pool.get('crm_claim.settings')   
        
        claim_number = settings_model.browse(cr, SUPERUSER_ID, [1])[0].next_number
        
        ''' Bump number in settings by one '''
        settings_model.write(cr, SUPERUSER_ID, [1], {'next_number': claim_number+1 })
        
        return claim_number        
    
    def _get_stage_string(self, cr, uid, ids, field_name, arg, context=None):
        records = self.browse(cr, uid, ids)
        result = {}
        
        for rec in records:
            result[rec.id] = rec.stage_id.name
            
        return result
    
    def _get_company(self, cr, uid, context=None):
        current_user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        res = current_user.company_id.id
        
        return res
    
    def onchange_email(self, cr, uid, ids, email, context):
        ''' Validates email '''
    
        res = {}
    
        if not email:
            return res
        
        valid_email = tools.single_email_re.match(email)
            
        if not valid_email:
            res['warning'] = {'title':'Warning!', 'message':'The email address "%s" is not valid.' % email}
        
        res['value'] = {'email_from_readonly': email}
        
        return res
    
    _columns = {
        'claim_number': fields.char('Claim number'),
        'company_id': fields.many2one('res.company', string=_('Company'), required=True),
        'stage': fields.function(_get_stage_string, type='char', obj='crm.claim', string='Claim stage'),
        'reply_to': fields.char('Reply to', size=128, help="Provide reply to address for message thread."),
        'sla': fields.selection([('0', '-'),('1', 'Taso 1'), ('2', 'Taso 2'), ('3', 'Taso 3'), ('4', 'Taso 4')], 'Service level', select=True),
        'email_to': fields.char('Email to', help='Email recipient'),
        'email_cc': fields.char('Email CC', help='Carbon copy message recipients'),
        'email_from_readonly': fields.char('Recipient email', readonly=True),
        'date_start': fields.datetime('Start date'),
        'date_waiting': fields.datetime('Waiting date'),
        'date_settled': fields.datetime('Settled date'),
        'date_rejected': fields.datetime('Rejected date'),
        'attachment_ids': fields.many2many('ir.attachment',  string='Attachments'),
    }
    
    _defaults = {
        'sla': '1',
        'reply_to': _default_get_reply_to,
        'company_id': _get_company
    }
    
    _sql_constraints = [
        ('claim_number', 'unique(claim_number)', _('This claim number is already in use.'))
    ]

crm_claim()
    
    