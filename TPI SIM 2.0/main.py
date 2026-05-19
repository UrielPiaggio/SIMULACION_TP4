from Configuracion import ConfiguracionSimulacion
from Simulador import Simulador

config = ConfiguracionSimulacion()

sim = Simulador(config)

sim.simular()

for fila in sim.tabla_estado:

    print()

    for clave, valor in fila.items():

        print(f"{clave}: {valor}")


print(f" HOLAAAAAAAA " , len(sim.tabla_estado))


