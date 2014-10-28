from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)

class crm_claim(osv.Model):      

    _name='crm.claim'
    _inherit = 'crm.claim'
    # 
    _order = "stage_id, write_date DESC"
    
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
        
        res = super(crm_claim, self).create(cr, uid, vals, context)
        if self.browse(cr, uid, [res], context)[0]:
            write_vals = {'claim_number': self._get_claim_number(cr,uid) }
            super(crm_claim, self).write(cr, uid, [res], write_vals, context)
            #_logger.info('Created a claim: %s' % write_vals)
            
        return res
        
    def _default_get_reply_to(self, cr, uid, context=None):
        company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        
        reply_ids=self.pool.get('crm_claim.reply').search(cr,uid,[('company_id', '=', company_id)])
        if reply_ids:
            for reply_obj in self.pool.get('crm_claim.reply').browse(cr,uid,reply_ids):
                reply_to=reply_obj.reply_to
                return reply_to
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
    
    _columns = {
        'claim_number': fields.char('Claim number'),
        'company_id': fields.many2one('res.company', string=_('Company'), required=True),
        'stage': fields.function(_get_stage_string, type='char', obj='crm.claim', string='Claim stage'),
        'reply_to': fields.char('Reply to', size=128, help="Provide reply to address for message thread."),
        'autoreply_sent': fields.boolean('Auto-reply sent'),
        'sla': fields.selection([('0', '-'),('1', 'Taso 1'), ('2', 'Taso 2'), ('3', 'Taso 3'), ('4', 'Taso 4')], 'Service level', select=True),
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
    
    