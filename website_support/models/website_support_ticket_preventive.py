from odoo import api, fields, models,_
from datetime import datetime, timedelta
from datetime import date

# class WebsiteSupportTicketPreventive(models.Model):
# 	_name = 'website.support.ticket.preventive'
# 	_description = "Preventivos"

class WebsiteSupportTicketExtinguisher(models.Model):
	_name = 'website.support.ticket.extinguisher'
	_description = "Mantenimiento Preventivos Extintores"

	@api.model
	def default_ids(self):
		ex_ids = []
		extintores = self.env['website.support.extinguisher'].search([])
		for e in extintores:
			ex_ids.append((0, 0, {
				'extintor_id': e.id,
				'ubicacion':e.location,
				'capacidad':e.capacity
				}))
		return ex_ids

	name = fields.Char(string="Reporte")
	fecha = fields.Date(string="Fecha de Emision", default=date.today())
	codigo = fields.Char(string="Codigo")
	vigencia = fields.Char(string="Vigencia")
	propietario = fields.Char(string="Propietario")
	version = fields.Char(string="Version")
	revision = fields.Char(string="Revision")
	extintores_ids = fields.One2many('website.support.ticket.extinguisher.line', 'reporte_id', string="Extintores", default=default_ids)
	programado = fields.Date(string="Fecha de Programacion")
	responsables = fields.Many2many('res.users', string="Responsables")
	company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env['res.company']._company_default_get('website.support.ticket.extinguisher'))
	notificado = fields.Integer(string="Notificado")
	notificado_compras = fields.Boolean(string="Notificado a Compras")

	@api.model
	def create(self, vals):
		if vals.get('name','Nuevo') == 'Nuevo':
			vals['name'] = self.env['ir.sequence'].next_by_code('website.support.ticket.extinguisher') or "Nuevo"
		return  super(WebsiteSupportTicketExtinguisher, self).create(vals)

	def programar(self):
		support_ticket_menu = self.env['ir.model.data'].sudo().get_object('website_support', 'mantenimiento_extintores')
		support_ticket_action = self.env['ir.model.data'].sudo().get_object('website_support', 'action_website_support_ticket_preventive_extinguisher')
		for my_user in self.responsables:
			notification = self.env['ir.model.data'].sudo().get_object('website_support', 'mantenimiento_extintores_notificacion')
			email_values = notification.generate_email(self.id)
			email_values['model'] = "website.support.ticket.extinguisher"
			email_values['res_id'] = self.id
			email_values['email_to'] = my_user.partner_id.email
			email_values['body_html'] = email_values['body_html'].replace("_ticket_url_", "web#id=" + str(
				self.id) + "&view_type=form&model=website.support.ticket.extinguisher&menu_id=" + str(
				support_ticket_menu.id) + "&action=" + str(support_ticket_action.id)).replace("_user_name_",
																							  my_user.partner_id.name)
			email_values['body'] = email_values['body'].replace("_user_name_", my_user.partner_id.name)
			send_mail = self.env['mail.mail'].create(email_values)
			send_mail.send()
		self.notificado += 1

	#TODO: TRABAJANDO
	def notificar_compras(self):
		config_personal = self.env['website.support.settings'].search([], order='id desc', limit=1)
		if config_personal.personal_shopping:
			notification = self.env['ir.model.data'].sudo().get_object('website_support', 'mantenimiento_extintores_compras_notificacion')
			email_values = notification.generate_email(self.id)
			email_values['model'] = "website.support.ticket.extinguisher"
			email_values['res_id'] = self.id
			email_values['email_to'] = config_personal.personal_shopping.login
			email_values['body_html'] = email_values['body_html'].replace("_user_name_", config_personal.personal_shopping.name)
			email_values['body'] = email_values['body'].replace("_user_name_", config_personal.personal_shopping.name)
			send_mail = self.env['mail.mail'].create(email_values)
			send_mail.send()
			self.notificado_compras = True

	@api.multi
	def imprimir(self):
		return self.env['report'].get_action(self, 'website_support.reporte_bitacora_extintores_document')


class WebsiteSupportTicketExtinguisherLine(models.Model):
	_name = 'website.support.ticket.extinguisher.line'

	reporte_id = fields.Many2one('website.support.ticket.extinguisher', string="Reporte")
	extintor_id = fields.Many2one('website.support.extinguisher', string="Extintor")
	ubicacion = fields.Char(related="extintor_id.location", string="Ubicacion")
	capacidad = fields.Char(related="extintor_id.capacity", string="Capacidad")	
	manometro = fields.Boolean(string="Manometro")
	manilla_accion = fields.Boolean(string="Manilla de Accion")
	manilla_soporte = fields.Boolean(string="Manilla de Soporte")
	pasador = fields.Boolean(string="Pasador de Seguridad")
	manguera = fields.Boolean(string="Manguera")
	boquilla = fields.Boolean(string="Boquilla")
	cilindro = fields.Boolean(string="Cilindro o Contenedor")
	etiquetado = fields.Boolean(string="Etiquetado")
	base = fields.Boolean(string="Gancho o Base")
	senaletica = fields.Boolean(string="Senaletica")
	recarga = fields.Selection([('si','Si'),('no','No')], string="Recarga")
	# otro = fields.Char(string="Otro")
	observaciones = fields.Text("Observaciones")

	# def aprobado_manometro(self):
	# 	return True

	# def aprobado_manilla_accion(self):
	# 	return True

	# def aprobado_manilla_soporte(self):
	# 	return True

	# def aprobado_manguera(self):
	# 	return True

	# def aprobado_boquilla(self):
	# 	return True

	# def aprobado_cilindro(self):
	# 	return True

	# def aprobado_etiquetado(self):
	# 	return True

	# def aprobado_base(self):
	# 	return True

	# def aprobado_otro(self):
	# 	return True
