# -*- coding: utf-8 -*-

# Para ver print() en los logs en Docker
#import logging
#rom select import select

#_logger = logging.getLogger(__name__)
#_logger.info('Mensaje')
# ----------------------------------------


from email.policy import default
import string
import locale
from tokenize import group
from odoo import models, fields, api, exceptions
from datetime import *
from dateutil.relativedelta import relativedelta

locale.setlocale(locale.LC_TIME, 'es_ES.utf8') 
#contenido_temporal = 'caca'

def get_years():
    year_list = []
    for i in range(2022, 2050):
        year_list.append((str(i), str(i)))
    return year_list

class publicadores(models.Model):
     _name = 'secretary.publicadores'
     _description = 'Publicadores'
      


     name = fields.Char(string='Nombre completo', default="apellidos, nombre", required=True)
     fecha_nacimiento = fields.Date(string='Fecha de nacimiento')
     fecha_bautismo = fields.Date(string='Fecha de bautismo')
     telefono = fields.Integer(string='Teléfono')
     genero = fields.Selection([('H','Hombre'), ('M','Mujer')], string='Género')
     nombramiento = fields.Selection([('A','Anciano'), ('S','Siervo Ministerial')], string='Nombramiento')
     direccion = fields.Char(string='Dirección')
     tipo = fields.Selection([('P','Publicador'), ('A', 'Auxiliar'), ('R','Regular')], string='Tipo', required=True)
     grupo = fields.Many2one(string='Grupo de Servicio', comodel_name="secretary.grupos")
     email = fields.Char(string='Email')
     pdf = fields.Binary(string='S-21 Antiguo')
     activo = fields.Boolean(string='Activo', default='True', readonly=True)
     voluntades = fields.Boolean(string='Voluntades anticipadas ', default='False', readonly=True)
     datos_emergencia = fields.Boolean(string='Datos emergencia ', default='False', readonly=True)
     consentimiento = fields.Boolean(string='Consentimiento de datos', default='False', readonly=True)
     informe_id = fields.One2many("secretary.informes", "nombre", string="Mis Informes")
     
     #DATOS EMERGENCIA:
     de_local_tf = fields.Char(string= "Teléfono móvil")
     de_local_tf_fijo = fields.Char(string= "Teléfono fijo")
     de_local_esTestigo = fields.Boolean(string= "¿Es Testigo?", default=False)
     de_local_consentimiento = fields.Boolean(string= " Ha dado consentimiento verbal o escrito", default=False)
     de_local_notas = fields.Char(string= "Comentario adicional")

     de_fuera_tf = fields.Char(string= "Teléfono móvil")
     de_fuera_tf_fijo = fields.Char(string= "Teléfono fijo")
     de_fuera_esTestigo = fields.Boolean(string= "¿Es Testigo?", default=False)
     de_fuera_consentimiento = fields.Boolean(string= " Ha dado consentimiento verbal o escrito", default=False)
     de_fuera_notas = fields.Char(string= "Comentario adicional")





     def current_year(self):
        mes= date.today().month
        if mes >9:
            year = date.today().year
        else:
            year = date.today().year -1
        return str(year)        
   
     def f_activo(self):
        self.activo = not self.activo
     def f_voluntades(self):
        self.voluntades = not self.voluntades
     def f_consentimiento(self):
        self.consentimiento = not self.consentimiento
     def f_emergencia(self):
        self.datos_emergencia = not self.datos_emergencia




class grupos(models.Model):
    _name = 'secretary.grupos'
    _description = 'Grupos de Servicio'

    id = fields.Integer(string= 'Nombre', default=lambda self: self.env['ir.sequence'].next_by_code('increment_your_field'))
    name = fields.Integer(string='Nombre')
    responsable = fields.Many2one('secretary.publicadores', string="Superintendente de Grupo ")
    def name_get(self):
        result = []
        for g in self:
            name = 'Grupo #%s' % (g.name)
            result.append((g.id, name))
        return result
        


class solicitudesAux(models.Model):
    
    #Funciones
    @api.model
    def create(self, vals):
    # Crear el registro
        record = super(solicitudesAux, self).create(vals)
    
    # Enviar el correo
        template = self.env.ref('secretary.email_template_solicitud_creada')
        if template:
            template.send_mail(record.id, force_send=True)
    
        return record


    @api.depends("mes")
    def _compute_date(self):
        for record in self:
            record.fecha = "%s-%s" %(record.mes,(datetime.strftime(datetime.today(),'%Y')))


    def calculoMesAInformar():
        mes_anterior= str(date.today().month)
        if mes_anterior == '1':
           mes_anterior = '12'
           año = '2022'
        else:
            mes_anterior = str((date.today().month)-1)
        mes = mes_anterior    
        return mes
    
    #Campos
    _name = 'secretary.solicitudesaux'
    _description = 'Solicitud S-205b (Prec. Aux.)'
    _order_by = "aprobada"
    id = fields.Integer(string= 'Nombre', default=lambda self: self.env['ir.sequence'].next_by_code('increment_your_field'))
    publicador = fields.Many2one("secretary.publicadores", string='Publicador')
    tipo = fields.Selection(
        selection=[('P', 'Publicador'), ('A', 'Auxiliar'), ('R', 'Regular')],
        string='Tipo',
        related='publicador.tipo'
    )
    name = fields.Char( string='Solicitante')
    mes = fields.Selection([('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre'), ], string='Mes', default=calculoMesAInformar())
    current_year = datetime.strftime(datetime.today(),'%Y')
    fecha = fields.Char(compute="_compute_date", store=True)
    año = fields.Selection(get_years(), string='Año', default=current_year)
    de_continiuo = fields.Boolean(string = "Desea ser precursor auxiliar de continuo hasta nuevo aviso.", readonly=True)
    firmaCord = fields.Boolean(string = "Aprobado por el Coordinador.", readonly=False)
    firmaServ = fields.Boolean(string = "Aprobado por el Ste. de Servicio.", readonly=False)
    firmaSecr = fields.Boolean(string = "Aprobado por el Secretario.", readonly=False)
    aprobada = fields.Boolean(string = "Aprobada", readonly=True, compute='_compute_aprobada', store=True)
    
    #Funciones automaticas
    @api.model
    def get_mes_label(self):
        """Devuelve la etiqueta legible del campo 'mes'."""
        return dict(self._fields['mes'].selection).get(self.mes, '')
    
    
    @api.depends('firmaCord', 'firmaServ', 'firmaSecr')
    def _compute_aprobada(self):
        for record in self:
            if record.firmaCord and record.firmaServ and record.firmaSecr:
                record.aprobada = True
            else:
                record.aprobada = False

    #Funciones botones
    def f_cordinador(self):
        self.firmaCord = not self.firmaCord
    def f_servicio(self):
        self.firmaServ = not self.firmaServ
    def f_secretario(self):
        self.firmaSecr = not self.firmaSecr
    #Validaciones
    _sql_constraints = [
        ('nombre_unique', 'unique(name, mes, año)', '¡Ya tiene una solicitud pendiente!')
    ]





class informes(models.Model):
     _name = 'secretary.informes'
     _description = 'Informe de predicación'
     _rec_name = 'fecha'
     _order_by = "create_date desc"

      
     @api.onchange('mes')
     def _get_publicadores_por_informar(self):
        print("[*] Fecha-->", self.fecha, flush=True)
        pub_ya_informado = []
        if self.fecha != False:
            pub_con_informe = self.env['secretary.publicadores'].search([('informe_id.fecha','=',self.fecha)])
            for x in pub_con_informe:
                pub_ya_informado.append(x.id)
            print(pub_ya_informado, flush=True)
            return {'domain':{'nombre':[('id','!=',pub_ya_informado)]}}
        else:
            pass
     def calculoMesAInformar():
        
        mes_anterior= str(date.today().month)
        
        if mes_anterior == '1':
           mes_anterior = '12'
           año = '2022'
        else:
            mes_anterior = str((date.today().month)-1)
        mes = mes_anterior    
        return mes
     
     def calculoAnyoActual():
        mes= date.today().month
        if mes >=9:
           anyo = str((date.today().year))
        else:
           anyo = str((date.today().year)-1)
        return anyo
     
     def _mesAnterior(self):
        for record in self:
            mes_anterior = (datetime.now() + relativedelta(months=-1)).strftime('%-m')
            record.mesFiltro = mes_anterior
     
     nombre = fields.Many2one("secretary.publicadores", string='Publicador')
     tipo_publicador = fields.Selection(string= "Tipo de publicador", related='nombre.tipo')
     grupo_publicador = fields.Many2one(string= "Grupo de publicador", related='nombre.grupo')# OJO: CAMBIADO RECIENTEMENTE
     mes = fields.Selection([('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre'), ], string='Mes', default=calculoMesAInformar())
     current_year = datetime.strftime(datetime.today(),'%Y')
     fecha = fields.Char(compute="_compute_date", store=True)
     #mesFiltro = fields.Char(compute="_mesAnterior", store=True)
     año = fields.Selection(get_years(), string='Año', default=current_year)
     horas = fields.Integer(string='Horas', required=True)
     revisitas = fields.Integer(string="Revisitas")
     cursos = fields.Integer(string="Cursos Bíblicos")
     publicaciones = fields.Integer(string="Publicaciones")
     videos = fields.Integer(string="Videos")
     revisitas = fields.Integer(string="Revisitas")
     notas = fields.Text(string='Notas:')
     este_mes_aux = fields.Boolean(string = "Aux. 30/50 horas", readonly=True) #TODO: Integrarlo cuando se filtre campos para mayor comodida y estetica
     ha_predicado = fields.Boolean(string= "¿Ha predicado?", default=True, readonly=True)
     tipo_informe = fields.Selection([('P','Publicador'), ('A', 'Auxiliar'), ('R','Regular')], string= "Tipo de Informe", default='P')
     

     def f_ha_predicado(self):
        self.ha_predicado = not self.ha_predicado            

     def este_mes_aux_activo(self):
        self.este_mes_aux = not self.este_mes_aux     

     @api.depends("mes")
     def _compute_date(self):
        for record in self:
            record.fecha = "%s-%s" %(record.mes,record.año)

     @api.onchange('nombre')
     def _set_tipo_informe(self):
        print("Toc,toc", self.nombre.tipo, flush=True)
        if self.nombre.tipo != False:
            self.tipo_informe = "%s" %(self.nombre.tipo)
        else:
            pass

     @api.constrains('horas')
     def _validate_horas(self):
        if self.horas < 0:
            raise exceptions.ValidationError('¡CUIDADO: EL valor de las HORAS no debe de ser menor a 0!')

   
     _sql_constraints = [
        ('nombre_unique', 'unique(nombre, mes, año)', '¡Parece que ya informaste. Solo puede introducir un informe por publicador! En caso de error, ponte en contacto con el secretario.')
    ]
   

class informes_dashboard(models.Model):
    _name = 'secretary.informes_dashboard'
    _inherits = {'secretary.informes': 'mes_id'}

    mes_id = fields.Many2one('secretary.informes', ondelete='cascade', string= 'Mes')




# MODELO PARA REPORTE TOTALES SUMADOS POR PUBLICADORES | REGULARES | AUXILIARES (S-21).    
class RegistroPublicador(models.TransientModel):
    _name = 'secretary.registro_publicador_report'
    _description = 'Formularios de Registro de publicador de la congregación (S-21)'
   # _inherit = 'secretary.informes'
   # _auto = False
   # _rec_name = 'id'
    def _año_servicio_sort(self):
        informes = self.env['secretary.informes'].search([])
        informes_sorted = informes.sorted(key= lambda i : i.año ,reverse=True)
        menu_año = []
        for informe in informes_sorted:
            menu_año.append((informe.año, informe.año))
        menu_año = list(dict.fromkeys(menu_año))
        print(menu_año, flush=True)
        return menu_año

    año_servicio = fields.Selection(_año_servicio_sort, string= "Seleccione año de servicio a generar reporte")
   
    def print_report_formularios_registro_publicador(self):
        return self.env.ref('secretary.action_registroPublicador_report').report_action(self)

    def get_publicadores_por_año(self):
        #if self.activo == 'True':
        lista_por_año = self.env['secretary.publicadores'].search([('informe_id.año','=',self.año_servicio),('activo','=','True')])
        #else:
        #    lista_por_año = self.env['secretary.publicadores'].search([('informe_id.año','=',self.año_servicio),('activo','=','False')])
            
        print("Debug: lista_por_año_____________",lista_por_año, flush=True)
        #for publicador in lista_por_año:
        #    print("Debug: nombre______", publicador.grupo[0]['name'], flush=True)
        return lista_por_año

    def lista_meses_con_informes(self):
        meses = self.env['secretary.informes'].search([('año','=',self.año_servicio)])
        print("meses---->",meses,flush=True)
        meses_sorted = meses.sorted(key= lambda i : i.mes ,reverse=True)
        lista_meses_con_informes = []
        for mes in meses_sorted:
            lista_meses_con_informes.append(int(mes.mes))
        lista_meses_con_informes = list(dict.fromkeys(lista_meses_con_informes))
        lista_meses_con_informes.sort()
        print(lista_meses_con_informes, flush=True)
        return lista_meses_con_informes

    def test(self):
        lista = [8,9,10,11]
        for l in lista:
            self.get_informes_por_tipo(l)

    def current_year(self):
        mes= date.today().month
        if mes >9:
            year = date.today().year
        else:
            year = date.today().year -1
        return str(year)
            
    def get_informes_por_tipo(self,x,y):
        mes=x
        año = y
        grouped = self.env['secretary.informes'].read_group(
                [('fecha', '=', '%s-%s' %(mes,año)),],# WHERE
                [('mes'),('año'),('horas:sum'),('publicaciones:sum'),('videos:sum'),('revisitas:sum'),('cursos:sum')], # FUNCTION IN SELECT; SELECT SUM (cv) AS total
                ['tipo_informe'] # GROUPBY
            )
        print("mes es --->",mes, flush=True)
        print("totales por mes--->",grouped, flush=True)
            
        return grouped # devuelve array de tuplas




# MODELO PARA REPORTE MESUAL PARA BETEL       
class TotalesMensuales(models.TransientModel):
    _name = 'secretary.totales_mensuales_report'
    _description = 'Totales mensuales de la predicación'
   # _inherit = 'secretary.informes'
   # _auto = False
   # _rec_name = 'id'

    def total_de_grupos_existentes(self):
        record_count = self.env['secretary.grupos'].search_count([])
        return record_count
    
    def _informe_sort(self):
        informes = self.env['secretary.informes'].search([])
        #informes_sorted = informes.sorted(key= lambda i : i.fecha ,reverse=True)
        
        def custom_sort(informe):
            # Aquí debes definir tu propio criterio de ordenación personalizado.
            # Por ejemplo, si tu campo "numero_personalizado" es de tipo carácter y tiene el formato "mes-año", puedes separar mes y año y ordenar en función de ello.
            mes, anio = map(int, informe.fecha.split('-'))
            return (anio, mes)  # Ordena primero por año, luego por mes
        informes_sorted = informes.sorted(key=custom_sort, reverse=True)


        menu_fecha = []
        for informe in informes_sorted:
            menu_fecha.append((informe.fecha, informe.fecha))
        menu_fecha = list(dict.fromkeys(menu_fecha))
        return menu_fecha

    mes_seleccionado = fields.Selection(_informe_sort, string = "Escoga mes para generar informe", required = True)
    
    def print_report_totales_mensuales(self):
        return self.env.ref('secretary.action_totalesMensuales_report').report_action(self)

    def get_sum_totales_mensuales(self):
        grouped = self.env['secretary.informes'].read_group(
            [('fecha', '=', self.mes_seleccionado),('ha_predicado','=','True'),('nombre.activo','=','True')],# WHERE
            [('horas:sum'),('publicaciones:sum'),('videos:sum'),('revisitas:sum'),('cursos:sum')], # FUNCTION IN SELECT; SELECT SUM (cv) AS total
            ['tipo_informe'] # GROUPBY
        )
        #print(grouped, flush=True)
        return grouped # devuelve array de tuplas
    
    def get_totales_mensuales_por_publicador(self):
        listado = self.env['secretary.informes'].search([('fecha', '=', self.mes_seleccionado),])
        #print(listado, flush=True)
        return listado # devuelve array de tuplas

    def get_totales(self):
        total = self.env['secretary.informes'].read_group(
            [('fecha', '=', self.mes_seleccionado),('ha_predicado','=','True'),('nombre.activo','=','True')],
            [('horas:sum'),('publicaciones:sum'),('videos:sum'),('revisitas:sum'),('cursos:sum')], 
            ['fecha']
        )
        return total

    def get_publicadores_activos(self):
        p_activos = self.env['secretary.publicadores'].search([('activo', '=', 'true'),])
        
        #print(p_activos, flush=True)
        total_publicadores_activos = len(p_activos)
        return total_publicadores_activos

    def filtrar_ultimos_meses(self, lista):
        count = []
        for i in range(-6, 0):
            try:
                valor = lista[i]['nombre']
            except IndexError:
                valor = None
            if valor != None:
                count.extend(valor)
        return len(set(count))

    def get_publicadores_irregulares(self):
        lista_conInforme = self.env['secretary.informes'].search([('fecha','=',self.mes_seleccionado), ('ha_predicado','!=','True')])
        for i in lista_conInforme:
            print("[*]Lista de informes a 0 =", i.nombre.name, flush=True )
        return lista_conInforme
        



# MODELO PARA REPORTE S-21 FILTRADOS POR GRUPOS DE SERVICIO       
class TotalesMensuales(models.TransientModel):
    _name = 'secretary.totales_porgrupo_report'
    _description = 'Totales por grupo de servicio'
   # _inherit = 'secretary.informes'
   # _auto = False
   # _rec_name = 'id'

   
    def _grupo_sort(self):
        grupos = self.env['secretary.grupos'].search([])
        menu_grupo = []
        for grupo in grupos:
            menu_grupo.append((grupo.name, 'Grupo_'+ str(grupo.name)))
        return menu_grupo

    grupo_seleccionado = fields.Selection(_grupo_sort, string = "Escoga grupo para generar informe", required = True)
    
    def print_report_totales_porgrupo(self):
        return self.env.ref('secretary.action_totalesporGrupo_report').report_action(self)
    
    def print_consentimiento_totales_porgrupo(self):
        return self.env.ref('secretary.action_totalesporGrupo_consentimiento').report_action(self)
    
    def print_datosEmergencia_totales_porgrupo(self):
        return self.env.ref('secretary.action_totalesporGrupo_emergencia').report_action(self)


    def current_year(self):
        mes= date.today().month
        if mes >9:
            year = date.today().year
        else:
            year = date.today().year -1
        return str(year)
         
    def get_publicadores(self):
        lista_porgrupos = self.env['secretary.publicadores'].search([('grupo','=',self.grupo_seleccionado),('activo','=','True'),])
        print("Debug: lista_porgrupos_____________",lista_porgrupos, flush=True)
        return lista_porgrupos
    
    def get_AllPublicadores(self):
        lista_porgrupos = self.env['secretary.publicadores'].search([('grupo','=',self.grupo_seleccionado),])
        print("Debug: lista_porgrupos_____________",lista_porgrupos, flush=True)
        return lista_porgrupos
        



# MODELO PARA REPORTE S-21 FILTRADO POR TIPO PRECURSORES, AUX O NORMAL       
class TotalesMensuales(models.TransientModel):
    _name = 'secretary.totales_porprecursores_report'
    _description = 'Tarjetas S-21 de los precursores reg/aux o publicadores'
   # _inherit = 'secretary.informes'
   # _auto = False
   # _rec_name = 'id'


    tipo_precursor = fields.Selection([('A', 'Auxiliar'),('R','Regular'),('P','Publicador')], string= "Tipo de publicador", default='R')
    
    def print_report_totales_porprecursor(self):
        return self.env.ref('secretary.action_totalesporPrecursor_report').report_action(self)
    

    def current_year(self):
        mes= date.today().month
        if mes >9:
            year = date.today().year
        else:
            year = date.today().year -1
        return str(year)
         
    def get_publicadores(self):
        lista_por_regular = self.env['secretary.publicadores'].search([('tipo','=',self.tipo_precursor),('activo','=','True'),])
        return lista_por_regular
          
 


# MODELO PARA REPORTE TARJETA S-21 DE PUBLICADORES Individual      
class InformesReport(models.AbstractModel):
    _name='report.secretary.informe_mensual'

    @api.model
    def _get_report_values(self, docids, data=None):
        report_obj = self.env['ir.actions.report']
        report = report_obj._get_report_from_name('secretary.report_tarjeta_publicador')
       
        return {
            'doc_ids': docids,
            'doc_model': self.env['secretary.publicadores'],
            'docs': self.env['secretary.publicadores'].browse(docids),
            

        }




# MODELO PARA REPORTE CARTAS       
class ModeloCartas(models.TransientModel):
    _name = 'secretary.cartas_report'
    _description = 'Generador de cartas de la congregación'

    remitente = fields.Selection([('CA','Cuerpo de Ancianos'), ('CC','Comité de Servicio')], string='Remitente', default='CA')
    destinatario = fields.Char(string='A:', default="Al Cuerpo de ancianos de la congregación de ...", required=True)
    asunto = fields.Char(string='Asunto:', default="Añada un asunto aquí...", required=True)
    mensaje = fields.Text(string='Mensaje', default=lambda self: self.env['ir.config_parameter'].get_param('carta_temporal'))

    
    def print_report_cartas(self):
        return self.env.ref('secretary.action_cartas_report').report_action(self)
    
    def save_content(self):
        self.env['ir.config_parameter'].set_param('carta_temporal', self.mensaje)
        pass
        






