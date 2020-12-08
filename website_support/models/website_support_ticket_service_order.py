from odoo import api, fields, models,_
from datetime import datetime, timedelta
from datetime import date
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

class WebsiteSupportTicketServiceOrder(models.Model):
	_name = 'website.support.ticket.service.order'
	_description = "Ordenes de Servicio"

	name = fields.Char(string="Orden")
	fecha = fields.Datetime(string="Fecha y hora")
	taller = fields.Char(string="Taller Asignado")
	vehiculo_id = fields.Many2one('fleet.vehicle', string="Vehiculo")
	conductor_id = fields.Char(string="Conductor")
	cargo_conductor = fields.Char(string="Cargo")
	placa_vehiculo = fields.Char(string="Placa")
	numero_vehiculo = fields.Char(string="No. Unidad")
	tipo_mantenimiento = fields.Selection([('preventivo','Preventivo'),('correctivo','Correctivo')], string="Tipo de Mantenimiento")
	detalles = fields.Many2many("service.order.details", string="Detalles")
	observaciones = fields.Text(string="Observaciones")
	#DATOS DE ENTREGA
	fecha_entrega = fields.Datetime(string="Fecha y hora de entrega")
	observaciones_entrega = fields.Text(string="Observaciones")

	@api.model
	def create(self, vals):
		if vals.get('name','Nuevo') == 'Nuevo':
			vals['name'] = self.env['ir.sequence'].next_by_code('website.support.ticket.service.order') or "Nuevo"
		return  super(WebsiteSupportTicketServiceOrder, self).create(vals)

	@api.onchange('vehiculo_id')
	def onchange_vehiculo(self):
		if self.vehiculo_id:
			self.conductor_id = self.vehiculo_id.driver_id.name
			self.placa_vehiculo = self.vehiculo_id.license_plate
			self.numero_vehiculo = self.vehiculo_id.vin_sn
		else:
			self.conductor_id = False
			self.placa_vehiculo = False
			self.numero_vehiculo = False

	@api.multi
	def imprimir(self):
		return self.env['report'].get_action(self, 'website_support.reporte_orden_servicio_document')

class WebsiteSupportTicketServiceOrderDetails(models.Model):
	_name = "service.order.details"
	_description = "Detalles de Orden de Servicio"

	name = fields.Char(string="Detalle")
	tipo_mantenimiento = fields.Selection([('preventivo','Preventivo'),('correctivo','Correctivo')], string="Tipo de Mantenimiento")