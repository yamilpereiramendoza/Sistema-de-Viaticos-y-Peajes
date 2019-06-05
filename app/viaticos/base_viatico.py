class BaseViatico():
    error=''
    errorppl=''
    errorfecha=''
    erroruser=''
    varificar=False
    def vacio(self,valor=None,mensaje=None):
        if valor == "...": 
            self.error=self.error+str(mensaje)+'\n'
            self.varificar=True
    def is_null(self,valor=None):
        ver_espacio=str(valor)
        for i in xrange(len(ver_espacio)):
                if ver_espacio[i] == " ":
                        return True
        return False
    def empty(self,valor=None):
        if len(valor) == 0:
                return True
        return False
    def isNumber(self,valor):
        if valor.isdigit() == False:
                return True
        return False
    def isString(self,valor):
            if valor.isalpha() == True:
                    return True
            return False
    def isDecimal(self,valor):
            if valor.isdecimal() == True:
                    return True
            return False
    def isDouble(self,valor):
            numero=str(valor)
            numerouno=""
            numerodos=""
            uno=True
            dos=False
            coma=False
            punto=False
            number=False
            for n in xrange(len(numero)):
                    if numero[n]==',':
                            coma=True
                            break
                    if numero[n]=='.':
                            punto=True
                            break
            if coma==False and punto==False:
                    number=True
            for n in xrange(len(numero)):
                
                    if number:
                            numerouno=numerouno+numero[n] 
                    if coma:
                            if numero[n]!=',':
                                    if uno:
                                            numerouno=numerouno+numero[n]
                                    if dos:
                                            numerodos=numerodos+numero[n]
                            else:
                                    uno=False
                                    dos=True
                    if punto:
                            if numero[n]!='.':
                                    if uno:
                                            numerouno=numerouno+numero[n]
                                    if dos:
                                            numerodos=numerodos+numero[n]
                    else:
                            uno=False
                            dos=True

            if self.isDecimal(numerouno):
                    if self.isDecimal(numerodos):
                            return False
                    return False
            else:
                    return True
    def isSolo(self,valor):
            numero=str(valor)
            coma=False
            punto=False
            for n in xrange(len(numero)):
                    if numero[n]==',':
                            coma=True
                            break
                    if numero[n]=='.':
                            punto=True
                            break
            if coma==True or punto==True:
                    return False
            return True     
    def isConvert(self,valor):
        numero=str(valor)
        numerouno=""
        numerodos=""
        uno=True
        dos=False
        coma=False
        punto=False
        number=False 
        for n in xrange(len(numero)):
                if numero[n]==',':
                        coma=True
                        break
                if numero[n]=='.':
                        punto=True
                        break

        if coma==False and punto==False:
                number=True

        for n in xrange(len(numero)):
                if number:
                        numerouno=numerouno+numero[n] 
                if coma:
                        if numero[n]!=',':
                                if uno:
                                        numerouno=numerouno+numero[n]
                                if dos:
                                        numerodos=numerodos+numero[n]
                        else:
                                uno=False
                                dos=True
                if punto:
                        if numero[n]!='.':
                                if uno:
                                        numerouno=numerouno+numero[n]
                                if dos:
                                        numerodos=numerodos+numero[n]
                        else:
                                uno=False
                                dos=True
        if number:
                return '%s.%s'%(numerouno,0)
        if self.isDecimal(numerouno):
                if self.isDecimal(numerodos):
                        return '%s.%s'%(numerouno,numerodos)
