# -*- coding: utf-8 -*-

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from openerp import api, fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class HrAnalyticTimesheet(models.Model):
    
    # 1. Private attributes
    _inherit = 'hr.analytic.timesheet'

    # 2. Fields declaration
    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges
    @api.model
    def default_get(self, fields):
        res = super(HrAnalyticTimesheet, self).default_get(fields)

        if 'crm_claim' in self._context:
            claim = self.env['crm.claim'].browse([self._context['crm_claim']])

            res['name'] = "%s (#%s): " % (claim.partner_id.name, claim.claim_number)

        return res

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
