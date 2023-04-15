# -*- coding: utf-8 -*-
from odoo import http
from datetime import *
from odoo.http import request
from werkzeug.utils import redirect


def check_password(password, expected_password):
    return password == expected_password

def auth_function(self, **kwargs):
    password = kwargs.get('password')
    if not password:
        return False
    return Pendientes.check_password(password, 'secret_password')

class DemasiadoPronto (http.Controller):

    @http.route('/demasiadopronto', auth='public')
    def index(self, **kw):
        return http.request.render("secretary.demasiadopronto")
    

class DemasiadoPronto (http.Controller):

    @http.route('/test', auth='public')
    def index(self, **kw):
        return http.request.render("secretary.test")
    

class Panel(http.Controller):
    #En desuso
    @http.route('/informar/', auth='public')
    def index(self, **kw):
        today = date.today().day
        Grupos = http.request.env['secretary.grupos']
        Publicadores = http.request.env['secretary.publicadores']
        if today >31:
            return redirect('/demasiadopronto')
        else:
            return http.request.render('secretary.index', {
                'grupos': Grupos.search([]),
                'publicadores': Publicadores.search([]),
        })

    # EL ACTUAL
    @http.route('/enviarinforme/', auth='public')
    def index2(self, **kw):
        today = date.today().day
        Grupos = http.request.env['secretary.grupos']
        Publicadores = http.request.env['secretary.publicadores']
        if today >15:
            return redirect('/demasiadopronto')
        else:
            return http.request.render('secretary.enviarinforme', {
                'grupos': Grupos.search([]),
                'publicadores': Publicadores.search([('activo', '=', True),]),
        })

    @http.route(['/panel/submit/'], type='http', auth="public", website=True)
    def informes_form_submit(self, **post):
        mes = Panel.calculoMesAInformar()[0]
        año = Panel.calculoMesAInformar()[1]
        año_default= str(date.today().year)
        #print("valor de mes_anterior--------------------->",mes, flush=True)
        informes = http.request.env['secretary.informes'].sudo().create({
            'nombre': post.get('publicador'), 
            'horas': post.get('horas'),
            'mes' : mes,
            'año' : año_default,
            'revisitas': post.get('revisitas'),
            'cursos' : post.get('cursos'),
            'videos' : post.get('videos'),                                                    
            'publicaciones' : post.get('publicaciones'),
            'tipo_informe' : post.get('tipo_informe'),
            'año' : año,
            'notas' : post.get('notas'),
            
        })
        vals = {
            'informes': informes,
        }
        #inherited the model to pass the values to the model from the form#
        return http.request.render("secretary.success", vals)
        #finally send a request to render the thank you page#
    
    def calculoMesAInformar():
        
        mes_anterior= str(date.today().month)
        año = datetime.strftime(datetime.today(),'%Y')
        
        if mes_anterior == '1':
           mes_anterior = '12'
           año = str(int(año)-1)
        else:
            mes_anterior = str((date.today().month)-1)
        fecha = (mes_anterior, año)    
        return fecha



class Pendientes (http.Controller):
    
    @http.route(['/password/'], auth="public")
    def informes_form_submit(self, **post):
        
       
        #inherited the model to pass the values to the model from the form#
        return http.request.render("secretary.password")
        #finally send a request to render the thank you page#

    @http.route('/pendientes', type='http', auth="public", website=True, csrf=False)
    def pendientes(self, **post):
        fecha= '%s-%s' % (Panel.calculoMesAInformar()[0], Panel.calculoMesAInformar()[1])
        Grupos = http.request.env['secretary.grupos']
        Publicadores_conInforme = http.request.env['secretary.publicadores'].search([('informe_id.fecha','=',fecha)])
        Publicadores_total = http.request.env['secretary.publicadores'].search([('activo', '=', 'TRUE')])
        Publicadores = Publicadores_total - Publicadores_conInforme
        Mensaje = "Querido hermano, solo recordarte que todavía no hemos recibido tu informe. Por favor, envíalo a la mayor brevedad posible. ¡Muchas gracias!%0APicha aquí --> https://secretary.raulchiclano.es/enviarinforme"
        for p in Publicadores.search([]):
            print(p.telefono, flush=True)
        
        password = post.get('password'),
        if password[0] != '7757':
            return 'Contraseña incorrecta'
        print("--------------------->>>>", password, flush=True)
        return http.request.render("secretary.pendiente", {
                'grupos': Grupos.search([]),
                'publicadores': Publicadores,
                'mensaje' : Mensaje,
                'publicadoresConInforme': Publicadores_conInforme,
               })





