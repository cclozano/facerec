class flabianos:
    """ Lista de permitidos a ingresar en el laboratorio """

    def __init__(self):
        self.Invitados=['carlos_lozano','ramon_carrillo','dennys_reyes']

    def TuSiTuNo(self,EllosSi):        
        if EllosSi in self.Invitados:
            print('Bienvenido {}'.format(EllosSi))
        else:
            print('Lo siento {}, debes solicitar acceso.'.format(EllosSi))
