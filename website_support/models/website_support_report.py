from odoo import api, fields, models,_
from datetime import datetime, timedelta
from datetime import date

#REPORTE BITACORAS DE MANTENIMIENTO
class ReporteMantenimiento(models.Model):
    _name = 'website.support.ticket.report'

    fecha = fields.Date(string="Fecha de Emision", default=date.today())
    codigo = fields.Char(string="Codigo")
    vigencia = fields.Char(string="Vigencia")
    propietario = fields.Char(string="Propietario")
    version = fields.Char(string="Version")
    revision = fields.Char(string="Revision")
    fecha_inicio = fields.Date(string="Fecha Incial")
    fecha_final = fields.Date(string="Fecha Final")
    area = fields.Many2one('website.support.ticket.categories', string="Area")
    reportes = fields.Many2many('website.support.ticket', string="Reportes", compute="fn_reportes_area")
    reportes_ids = fields.Many2many('website.support.ticket', string="Reportes")
    de_reportes = fields.Boolean(string="De Reportes")

    @api.onchange('fecha_inicio','fecha_final', 'area')
    def fn_reportes_area(self):
        for s in self:
            #list_report = []
            if s.fecha_inicio and s.fecha_final and s.area:
                reportes_ids = self.env['website.support.ticket'].search([('fecha_solicitud','>=',s.fecha_inicio),
                    ('fecha_solicitud','<=',s.fecha_final),('category','=',s.area.id)])
                s.reportes = reportes_ids
                #for r in reportes:
                #    list_report.append((4,r.id))
                #s.reportes_ids = list_report

    @api.multi
    def imprimir(self):
        return self.env['report'].get_action(self, 'website_support.reporte_mantenimiento_document')

    @api.multi
    def name_get(self):
        res = super(ReporteMantenimiento, self).name_get()
        result = []
        for element in res:
            report_id = element[0]
            code = self.browse(report_id).area.name
            desc = self.browse(report_id).fecha
            name = code and '[%s] %s' % (code, desc) or '%s' % desc
            result.append((report_id, name))
        return result

class ReporteMantenimientoWizard(models.TransientModel):
    _name = 'website.support.report.wizard'

    @api.model
    def default_get(self, default_fields):
        res = super(ReporteMantenimientoWizard, self).default_get(default_fields)
        reporte_id = self._context.get('active_ids')
        reportes = self.env['website.support.ticket.report'].browse(reporte_id)
        return res

    @api.multi
    def fnCrearBitacora(self):
        reportes = self.env['website.support.ticket'].browse(self._context.get('active_ids'))
        bitacora = self.env['website.support.ticket.report'].create({
            'fecha': datetime.today(),
            'de_reportes': True,
            })
        for rep in reportes:
            bitacora.write({'reportes_ids':[(4, rep.id)]})

        return{
            'name': 'Bitacora de Mantenimiento',
            'view_id': self.env.ref('website_support.reporte_bitacora_mantenimientos_form').id,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'website.support.ticket.report',
            'res_id': bitacora.id,
            'type': 'ir.actions.act_window'

        }