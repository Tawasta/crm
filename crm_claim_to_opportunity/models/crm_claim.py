# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from openerp import fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class CrmClaim(models.Model):

    # 1. Private attributes
    _inherit = 'crm.claim'

    # 2. Fields declaration
    opportunities = fields.One2many(
        comodel_name='crm.lead',
        inverse_name='claim',
        string='Opportunity',
        readonly=True,
        copy=False,
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
