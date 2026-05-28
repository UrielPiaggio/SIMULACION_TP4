import random
import math


def distribucion_exponencial(media):
    # Generamos el random. Si llega a ser 1.0, lo ajustamos
    rnd = random.random()
    if rnd >= 0.999:
        rnd = 0.999 # O simplemente un valor que evite el log(0)
    
    rnd = round(rnd, 3)
    # math.log(1 - rnd) será seguro ahora
    valor = round(-media * math.log(1 - rnd), 3)
    
    return rnd, valor



def distribucion_uniforme(minimo, maximo):

    rnd = round(random.random(), 3)

    valor = round(minimo + rnd * (maximo - minimo), 3)
    

    return rnd, valor