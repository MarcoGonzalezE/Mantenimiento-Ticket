# -*- coding: utf-8 -*-
from openerp import api, fields, models
from openerp import tools
from HTMLParser import HTMLParser
from random import randint
import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo import SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class WebsiteSupportParvada(models.Model):
    _name = "website.support.parvada"
    _description = "Cierre de Parvada"
    _inherit = ['mail.thread']

    name = fields.Char(string="Cierre Parvada", compute="_compute_cp_number_display")
    cp_number = fields.Integer()
    granja = fields.Many2one('website.support.ticket.categories', string="Granja", track_visibility='onchange')
    state = fields.Selection([('draft', 'Creado'),
                              ('process', 'En Proceso'),
                              ('finish', 'Terminado'),
                              ('cancel', 'Cancelado')], default='draft', string="Estado")
    fecha = fields.Date(string="Fecha de Cierre" , track_visibility='onchange')
    fecha_fin = fields.Datetime(string="Fecha fin de Cierre", track_visibility='onchange')
    tareas_ids = fields.One2many('website.support.parvada.tareas', 'tarea_id', string="Lista de Tareas")    
    company_id = fields.Many2one('res.company', string="Compania", default=lambda self: self.env['res.company']._company_default_get('website.support.parvada'))

    @api.model
    def create(self, vals):
        new_id = super(WebsiteSupportParvada, self).create(vals)
        new_id.cp_number = new_id.company_id.next_support_cp_number
        new_id.company_id.next_support_cp_number += 1
        return new_id

    @api.one
    @api.depends('cp_number')
    def _compute_cp_number_display(self):
        self.name = 'CP' + str(self.cp_number)



class WebsiteSupportParvadaTareas(models.Model):
    _name = "website.support.parvada.tareas"
    tarea_id = fields.Many2one('website.support.parvada', string="ID Tarea")
    name = fields.Char(string="Tarea")
    state = fields.Selection([('draft', 'En Espera'),
                              ('process', 'En Proceso'),
                              ('finish', 'Terminado'),
                              ('cancel', 'Cancelado'),
                              ('rejected', 'Rechazado')],
                             default='draft', string="Estado", track_visibility='onchange')
    fecha_tarea = fields.Datetime(string="Fecha inicio", track_visibility='onchange')
    fecha_tarea_final = fields.Datetime(string="Fecha terminacion", track_visibility='onchange')
    responsable = fields.Many2one('website.support.mantenimiento', string="Responsable", track_visibility='onchange')

    @api.multi
    @api.onchange('state')
    def _compute_real(self):
        for o in self:
            if o.state == 'finish':
                o.fecha_tarea_final = datetime.datetime.now()


class WebsiteSupportMantenimiento(models.Model):
    _name = "website.support.mantenimiento"
    name = fields.Many2one('res.partner', string ='Jefe de Mantenimiento')
