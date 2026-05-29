# importacion de librerias para generar numeros pseudoaleatorios y para funciones matematicas (log por ejemplo)
import random
import math

# Genera un RND y su valor usando la distribucion exponencial negativa y una media pasada por parametro
def distribucion_exponencial(media):
    # Genera el random y si llega a ser 1 (no lo va a ser), lo ajusta para q no de problema con el log
    # Capaz q este chequeo de seguridad sea al pedo pero no esta de mas hacerlo
    rnd = random.random()
    if rnd >= 0.999:
        rnd = 0.999 # ete valor evita el log(0), en cambio hace log(0.001) q es lo suficientemente representativo del log(0)
    
    rnd = round(rnd, 3)
    valor = round(-media * math.log(1 - rnd), 3)
    
    # devuelve una tupla de rnd (el random que generamos para mostrarlo despues) y valor que es el tiempo generado por la exponencial negativa 
    return rnd, valor


# Genera un RND y su valor usando la distribucion uniforme y dos valores un maximo y un minimo que se pasan por parametro
def distribucion_uniforme(minimo, maximo):

    rnd = round(random.random(), 3)

    valor = round(minimo + rnd * (maximo - minimo), 3)
    
# devuelve una tupla de rnd (el random que generamos para mostrarlo despues) y valor que es el tiempo generado por la distribucion uniforme
    return rnd, valor