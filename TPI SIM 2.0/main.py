from Configuracion import ConfiguracionSimulacion
from Simulador import Simulador

config = ConfiguracionSimulacion()

sim = Simulador(config)

# =====================================
# INICIALIZAR
# =====================================

sim.inicializar_simulacion()

# =====================================
# PROCESAR UNA LLEGADA
# =====================================

for i in range(10):


      evento, hora, tipo = (
            sim.buscar_proximo_evento()
      )

      sim.avanzar_reloj(hora)

      print("\n=========================")
      print(f"ITERACIÓN {sim.iteracion}")
      print("=========================")

      print("Evento:", evento)

      print("Reloj:", sim.reloj)

    # =========================
    # LLEGADA
    # =========================

      if evento == "Llegada Paciente":
            sim.procesar_llegada()

    # =========================
    # FIN VACUNACIÓN
    # =========================

      elif evento == "Fin Vacunacion":

            sim.procesar_fin_vacunacion(
                  tipo
            )
      elif evento == "Fin Observacion":
            sim.procesar_fin_observacion(tipo)

    # =========================
    # ESTADO SISTEMA
    # =========================

      print()

      for s in sim.servidores:

            print(

                  f"Servidor {s.id}: "
                  f"{s.estado}"
            )

            if s.paciente_actual is not None:

                  print(
                  f"Paciente actual: "
                  f"{s.paciente_actual.id}"
                  )

                  print(
                  f"Fin vacunación: "
                  f"{s.fin_vacunacion}"
                  )

      print()

      print(

            "Cola espera:",
            len(sim.cola_espera)
      )

      print(
            "Observación:",
            len(sim.zona_observacion)
      )

      print(
            "No ingresan:",
            sim.cantidad_no_ingresan
      )
