import random
import math


def distribucion_exponencial(media):

    rnd = round(random.random(), 3)

    valor = round(-media * math.log(1 - rnd), 3)

    return rnd, valor



def distribucion_uniforme(minimo, maximo):

    rnd = round(random.random(), 3)

    valor = round(minimo + rnd * (maximo - minimo), 3)
    

    return rnd, valor