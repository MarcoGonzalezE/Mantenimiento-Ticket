from odoo import api, fields, models,_
from datetime import datetime, timedelta

#INVENTARIO
class WebsiteSupportInventory(models.Model):
	_name = 'website.support.inventory'
	_description = "Inventario de Mantenimiento"

	name = fields.Char(string="Producto")
	imagen = fields.Binary(string="Imagen", attachment=True)
	stock_min = fields.Integer(string="Minimo")
	stock_diff = fields.Integer(string="Faltante", compute="_stock_faltante")
	no_stock = fields.Boolean(string="Sin Stock", compute="_stock_faltante")
	stock = fields.Integer(string="Stock", compute="_stock")
	input_ids = fields.One2many('website.support.inventory.input', 'product_id', string="Entradas a Inventario")
	output_ids = fields.One2many('website.support.ticket.product', 'product', string="Consumos de Inventario")

	#Stock Faltante
	@api.depends('stock_min','stock')
	def _stock_faltante(self):
		for r in self:
			if r.stock < r.stock_min:
				r.stock_diff = r.stock_min - r.stock
				r.no_stock = True
			else:
				r.stock_diff = 0

	#Stock
	@api.multi
	def _stock(self):
		for rec in self:
			stock_total = 0
			stock_out = 0
			input = self.env['website.support.inventory.input'].search([('product_id','=', rec.id)])
			if input is not None:
				for i in input:
					stock_total += i.quantity
			output = self.env['website.support.ticket.product'].search([('product','=', rec.id)])
			if output is not None:
				for o in output:
					stock_out += o.quantity
			rec.stock = stock_total - stock_out



	#Registrar Entrada
	@api.multi
	def registar_entrada(self):
		return{
			'name': "Registar Entrada",
			'type': 'ir.actions.act_window',
			'view_type': 'form',
            'view_mode': 'form',
            'view_name': 'form',
            'res_model': 'website.support.inventory.input',
            'context': {'default_product_id': self.id},
            'target': 'new'
		}

#ENTRADAS DE INVENTARIO
class WebsiteSupportInventoryInput(models.Model):
	_name = 'website.support.inventory.input'
	_description = "Entradas de Inventario"

	product_id = fields.Many2one('website.support.inventory', string="Producto ID")
	quantity = fields.Integer(string="Cantidad")
	date = fields.Date(string="Fecha de Entrada")
	#purchase_id = fields.Many2one('purchase.order', string="Compra")
	note = fields.Text(string="Nota")

	@api.model
	def create(self, values):
		return super(WebsiteSupportInventoryInput, self).create(values)

	@api.multi
	def save(self):
		return True

#COMPRAS A INVENTARIO
class WebsiteSupportInventoryPurchase(models.TransientModel):
	_name = 'website.support.inventory.purchase'

	@api.model
	def default_get(self, default_fields):
		res = super(WebsiteSupportInventoryPurchase, self).default_get(default_fields)
		product_ids = self._context.get('active_ids')
		products = self.env['website.support.inventory'].browse(product_ids)
		return  res

	@api.multi
	def create_purchase_order(self):
		products = self.env['website.support.inventory'].browse(self._context.get('active_ids'))
		config_purchase = self.env['website.support.settings'].search([], order='id desc', limit=1)
		print(config_purchase.product_purchase)
		purchase = self.env['purchase.order'].create({
			'partner_id':config_purchase[0].partner_purchase.id,
		})
		for p in products:
			purchase_line = self.env['purchase.order.line'].create({
				'product_id':config_purchase.product_purchase.id,
				'name':p.name,
				'order_id':purchase.id,
				'product_uom':1,
				'price_unit': 1.0,
				'product_qty': 1,
				'date_planned': datetime.today(),
			})
		return {
			'name': 'Compras',
			'view_id': self.env.ref('purchase.purchase_order_form').id,
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'purchase.order',
			'res_id': purchase.id,
			'type': 'ir.actions.act_window'
		}

#EQUIPOS
class WebsiteSupportEquipment(models.Model):
	_name = 'website.support.equipment'
	_description = "Equipos"

	name = fields.Char(string="Equipo")
	complement_ids = fields.One2many('website.support.complement', 'equipment_id', string="Complementos")

#COMPLEMENTOS
class WebsiteSupportComplement(models.Model):
	_name = 'website.support.complement'
	_description = "Complementos"

	name = fields.Char(string="Complemento")
	equipment_id = fields.Many2one('website.support.equipment', string="Equipo ID")
	product_ids = fields.Many2many('website.support.inventory', string="Refacciones")

#REFACCIONES POR REPORTE
class WebsiteSupportParts(models.Model):
	_name = 'website.support.ticket.product'
	_description = "Refacciones de Reporte"

	product = fields.Many2one('website.support.inventory', string="Refaccion")
	quantity = fields.Integer(string="Cantidad")
	report_id = fields.Many2one('website.support.ticket', string="Reporte ID")
	state = fields.Selection([('draft', 'Reservado'), ('done', 'Consumido')], string="Estado", default='draft')