from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta


def add_years(start, years):
    result = start + timedelta(366 * years)
    if years > 0:
        while result.year - start.year > years or start.month < result.month or start.day < result.day:
            result += timedelta(-1)
    elif years < 0:
        while result.year - start.year < years or start.month > result.month or start.day > result.day:
            result += timedelta(1)
    return result


class StockPickingInstallation(models.TransientModel):
    _name = 'stock.picking.installation'

    date_installed = fields.Datetime(string='Date Installed')
    stock_picking_id = fields.Many2one('stock.picking', 'Stock Picking')

    @api.multi
    def button_update_installation(self):
        self.ensure_one()
        if not self._context.get('date_installed'):
            raise UserError(_('Please enter the installed date.'))
        stock_move = self.sudo().env['stock.picking'].browse(self._context.get('stock_picking_id'))
        stock_move.date_installed = self._context.get('date_installed')
        stock_move.installation_status = 'completed'
        stock_move.installation_desc = 'Completed on ' + self._context.get('date_installed')
        license_plan = self.sudo().env['tbm.subscription.license'].search([('partner_id', '=', stock_move.partner_id.id)])
        warranty_plan = self.sudo().env['tbm.subscription.warranty'].search([('partner_id', '=', stock_move.partner_id.id)])
        date_start = stock_move.date_installed.date()
        license_plan.status = 'active'
        license_plan.date_start = date_start
        license_plan.date_end = add_years(stock_move.date_installed.date(), license_plan.plan_id.period)
        warranty_plan.status = 'active'
        warranty_plan.date_start = date_start
        warranty_plan.date_end = add_years(stock_move.date_installed.date(), warranty_plan.plan_id.period)
        self.env['res.users'].tbm_notify(stock_move, ['Finance - Administrator', 'Finance - Manager', 'Finance - Receivables', 'CRM - Administrator', 'Materials - Administrator',
                                                          'Materials - Manager'],
                                         'Installation Complete', 'crm_tbm_advanced.message_done_delivery')
        return {'type': 'ir.actions.act_window_close'}
