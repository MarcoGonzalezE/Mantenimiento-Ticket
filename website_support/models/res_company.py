# -*- coding: utf-8 -*-
from openerp import api, fields, models

class ResCompanyTicket(models.Model):

    _inherit = "res.company"
    
    next_support_ticket_number = fields.Integer(string="Next Support Ticket Number", default="1")
    next_support_cp_number = fields.Integer(string="Siguiente Cierre de Parvada", default="1")