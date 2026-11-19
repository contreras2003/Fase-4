#Permite crear clases abstractas   
from abc import ABC, abstractmethod
import logging
import math

#Guarda los errores y las operaciones en un archivo
logging.basicConfig(
    filename="software_fj.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)
#Excepciones del sistema
class SoftwareFJError(Exception):
    pass
class DatosInvalidosError(SoftwareFJError):
    pass
class ClienteNoEncontradoError(SoftwareFJError):
    pass
class ServicioNoDisponibleError(SoftwareFJError):
    pass
class ReservaInvalidaError(SoftwareFJError):
    pass
class OperacionNoPermitidaError(SoftwareFJError):
    pass
class CalculoError(SoftwareFJError):
    pass

#Clase principal de las entidades
class Entidad(ABC):
    def __init__(self, identificador):
        if not isinstance(identificador, str) or not identificador.strip():
            raise DatosInvalidosError("El ID es obligatorio.")
        self._identificador = identificador.strip()
    @property
    def identificador(self):
        return self._identificador
    @abstractmethod
    def obtener_informacion(self):
        pass

#Clase para registrar a los clientes
class Cliente(Entidad):
    def __init__(self, identificador, nombre, correo, telefono):
        super().__init__(identificador)
        self.__nombre = nombre.strip() if isinstance(nombre, str) else nombre
        self.__correo = correo.strip() if isinstance(correo, str) else correo
        self.__telefono = telefono.strip() if isinstance(telefono, str) else telefono
        self.validar_datos()
    def validar_datos(self):
        if not isinstance(self.__nombre, str) or len(self.__nombre) < 3:
            raise DatosInvalidosError(
                "El nombre debe tener mínimo 3 caracteres."
            )
        if (
            not isinstance(self.__correo, str)
            or "@" not in self.__correo
            or "." not in self.__correo.split("@")[-1]
        ):
            raise DatosInvalidosError(
                "El correo no tiene un formato valido."
            )

        if (
            not isinstance(self.__telefono, str)
            or not self.__telefono.isdigit()
            or len(self.__telefono) < 7
        ):
            raise DatosInvalidosError(
                "El Telefono debe tener mínimo 7 números."
            )
    @property
    def nombre(self):
        return self.__nombre
    @property
    def correo(self):
        return self.__correo
    def obtener_informacion(self):
        return (
            f"ID: {self.identificador} | Nombre: {self.__nombre} | "
            f"Correo: {self.__correo} | Telefono: {self.__telefono}"
        )
#Clase general de los servicios
class Servicio(Entidad):
    def __init__(self, identificador, nombre, precio):
        super().__init__(identificador)
        if not isinstance(nombre, str) or not nombre.strip():
            raise DatosInvalidosError(
                "El nombre del servicio es obligatorio."
            )
        if (
            not isinstance(precio, (int, float))
            or isinstance(precio, bool)
            or not math.isfinite(precio)
            or precio <= 0
        ):
            raise DatosInvalidosError(
                "El precio debe ser mayor que cero."
            )
        self._nombre = nombre.strip()
        self._precio = float(precio)
        self._disponible = True
    @property
    def nombre(self):
        return self._nombre
    @property
    def precio(self):
        return self._precio
    @property
    def disponible(self):
        return self._disponible
    def cambiar_disponibilidad(self, estado):
        if not isinstance(estado, bool):
            raise DatosInvalidosError(
                "La disponibilidad debe ser verdadera o falsa."
            )
        self._disponible = estado
        logging.info(
            "Disponibilidad modificada: %s",
            self.identificador
        )
    def validar_duracion(self, duracion):
        if (
            not isinstance(duracion, (int, float))
            or isinstance(duracion, bool)
            or not math.isfinite(duracion)
            or duracion <= 0
        ):
            raise DatosInvalidosError(
                "La duracion debe ser mayor que cero."
            )
        if not self._disponible:
            raise ServicioNoDisponibleError(
                "El servicio no esta disponible."
            )

    @abstractmethod
    def calcular_costo(self, duracion):
        pass
    @abstractmethod
    def describir(self):
        pass
    def obtener_informacion(self):
        return self.describir()


#Servicio para reservar salas
class ReservaSalas(Servicio):
    def calcular_costo(self, duracion):
        self.validar_duracion(duracion)
        return self.precio * duracion
    def describir(self):
        return (
            f"Reserva de sala: {self.nombre} - "
            f"${self.precio:,.0f} por hora"
        )


#Servicio para alquilar equipos
class AlquilerEquipos(Servicio):
    def calcular_costo(self, duracion):
        self.validar_duracion(duracion)
        return self.precio * duracion
    def describir(self):
        return (
            f"Alquiler de equipo: {self.nombre} - "
            f"${self.precio:,.0f} por hora"
        )


#Servicio de asesorias
class Asesoria(Servicio):
    def calcular_costo(self, duracion):
        self.validar_duracion(duracion)
        return self.precio * duracion
    def describir(self):
        return (
            f"asesoria: {self.nombre} - "
            f"${self.precio:,.0f} por hora"
        )


#Clase para hacer cálculos de precios
class Calculadora:
    def calcular(self, precio, impuesto=0, descuento=0):
        for valor in (precio, impuesto, descuento):
            if (
                not isinstance(valor, (int, float))
                or isinstance(valor, bool)
                or not math.isfinite(valor)
            ):
                raise CalculoError(
                    "Los valores deben ser números validos."
                )
        if precio < 0 or impuesto < 0:
            raise CalculoError(
                "El precio y el impuesto no pueden ser negativos."
            )
        if not 0 <= descuento <= 100:
            raise CalculoError(
                "El descuento debe estar entre 0 y 100."
            )
        subtotal = precio - (precio * descuento / 100)
        return subtotal + (subtotal * impuesto / 100)
    #Cálculo usando descuento
    def calcular_con_descuento(self, precio, descuento):
        return self.calcular(precio, descuento=descuento)
    #Cálculo usando impuesto
    def calcular_con_impuesto(self, precio, impuesto):
        return self.calcular(precio, impuesto=impuesto)


#Clase para manejar las reservas
class Reserva:
    def __init__(self, identificador, cliente, servicio, duracion):
        if not isinstance(identificador, str) or not identificador.strip():
            raise ReservaInvalidaError(
                "El ID de la reserva es obligatorio."
            )
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError(
                "Debe seleccionar un cliente valido."
            )
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError(
                "Debe seleccionar un servicio valido."
            )
        servicio.validar_duracion(duracion)
        self._identificador = identificador.strip()
        self._cliente = cliente
        self._servicio = servicio
        self._duracion = duracion
        self._estado = "Pendiente"
        self._costo = None

    @property
    def identificador(self):
        return self._identificador
    @property
    def cliente(self):
        return self._cliente
    @property
    def servicio(self):
        return self._servicio
    @property
    def estado(self):
        return self._estado
    @property
    def costo(self):
        return self._costo
    def confirmar(self):
        if self._estado != "Pendiente":
            raise OperacionNoPermitidaError(
                "La reserva ya fue procesada."
            )
        self._costo = self._servicio.calcular_costo(
            self._duracion
        )

        self._estado = "Confirmada"
        logging.info(
            "Reserva confirmada: %s",
            self._identificador
        )
        return self._costo
    def cancelar(self):
        if self._estado != "Confirmada":
            raise OperacionNoPermitidaError(
                "Solo se puede cancelar una reserva confirmada."
            )
        self._estado = "Cancelada"
        logging.info(
            "Reserva cancelada: %s",
            self._identificador
        )

    def procesar(self):
        try:
            costo = self.confirmar()
        except SoftwareFJError as error:
            logging.exception(
                "Error al procesar la reserva"
            )
            raise ReservaInvalidaError(
                "Ocurrió un problema al procesar la reserva."
            ) from error
        else:
            return costo
        finally:
            print(
                "Terminó el proceso de la reserva:",
                self._identificador
            )
    def obtener_informacion(self):
        costo_texto = (
            f"${self._costo:,.0f}"
            if self._costo is not None
            else "Pendiente"
        )
        return (
            f"Reserva: {self._identificador} | "
            f"Cliente: {self._cliente.nombre} | "
            f"Servicio: {self._servicio.nombre} | "
            f"Estado: {self._estado} | "
            f"Costo: {costo_texto}"
        )

#Clase para administrar clientes, servicios y reservas
class Gestor:
    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []
    def registrar_cliente(self, cliente):
        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError(
                "El dato recibido no es un cliente."
            )
        if any(
            c.identificador == cliente.identificador
            for c in self.clientes
        ):
            raise DatosInvalidosError(
                "Ya existe un cliente con ese ID."
            )
        self.clientes.append(cliente)
        logging.info(
            "Cliente registrado: %s",
            cliente.identificador
        )
    def buscar_cliente(self, identificador):
        try:
            cliente = next(
                c for c in self.clientes
                if c.identificador == identificador
            )
        except StopIteration as error:
            logging.exception(
                "No se encontró el cliente %s",
                identificador
            )
            raise ClienteNoEncontradoError(
                "No se encontró un cliente con ese ID."
            ) from error
        else:
            return cliente
        finally:
            logging.info(
                "Terminó la búsqueda del cliente."
            )
    def registrar_servicio(self, servicio):
        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError(
                "El dato recibido no es un servicio."
            )
        if any(
            s.identificador == servicio.identificador
            for s in self.servicios
        ):
            raise DatosInvalidosError(
                "Ya existe un servicio con ese ID."
            )
        self.servicios.append(servicio)
        logging.info(
            "Servicio registrado: %s",
            servicio.identificador
        )
    def registrar_reserva(self, reserva):
        if not isinstance(reserva, Reserva):
            raise ReservaInvalidaError(
                "El dato recibido no es una reserva."
            )
        if any(
            r.identificador == reserva.identificador
            for r in self.reservas
        ):
            raise DatosInvalidosError(
                "Ya existe una reserva con ese ID."
            )
        if not any(
            c is reserva.cliente
            for c in self.clientes
        ):
            raise ClienteNoEncontradoError(
                "El cliente no esta registrado."
            )
        if not any(
            s is reserva.servicio
            for s in self.servicios
        ):
            raise DatosInvalidosError(
                "El servicio no esta registrado."
            )
        self.reservas.append(reserva)
        logging.info(
            "Reserva registrada: %s",
            reserva.identificador
        )
    def mostrar_clientes(self):
        print("\nCLIENTES")
        for cliente in self.clientes:
            print(cliente.obtener_informacion())
    def mostrar_servicios(self):
        print("\nSERVICIOS")
        for servicio in self.servicios:
            print(
                servicio.describir(),
                "| Disponible:",
                servicio.disponible
            )
    def mostrar_reservas(self):
        print("\nRESERVAS")
        for reserva in self.reservas:
            print(reserva.obtener_informacion())
#Se crea el gestor del sistema
gestor = Gestor()
#Prueba 1. Registrar un cliente con datos correctos.
def prueba_1():
    cliente = Cliente(
        "C01",
        "Santiago Contreras",
        "Santiago@gmail.com",
        "00000000"
    )
    gestor.registrar_cliente(cliente)
    print("Cliente registrado correctamente.")
#Prueba 2. Intentar registrar un cliente con datos incorrectos.
def prueba_2():
    cliente = Cliente(
        "C02",
        "Juan Diaz",
        "juan@gmail.com",
        "00000000"
    )
    gestor.registrar_cliente(cliente)
#Prueba 3. Registrar un servicio para reservar salas.
def prueba_3():
    servicio = ReservaSalas(
        "S01",
        "Sala principal",
        50000
    )
    gestor.registrar_servicio(servicio)
    print(servicio.describir())
#Prueba 4. Registrar un servicio para alquilar equipos.
def prueba_4():
    servicio = AlquilerEquipos(
        "S02",
        "Proyector",
        30000
    )
    gestor.registrar_servicio(servicio)
    print(servicio.describir())
#Prueba 5. Registrar un servicio de asesoria.
def prueba_5():
    servicio = Asesoria(
        "S03",
        "asesoria informatica",
        80000
    )
    gestor.registrar_servicio(servicio)
    print(servicio.describir())
#Prueba 6. Intentar registrar un servicio con precio negativo.
def prueba_6():
    servicio = ReservaSalas(
        "S04",
        "Sala secundaria",
        -500
    )
    gestor.registrar_servicio(servicio)
#Prueba 7. Crear, registrar y confirmar una reserva correctamente.
def prueba_7():
    cliente = gestor.buscar_cliente("C01")
    servicio = gestor.servicios[0]
    reserva = Reserva(
        "R01",
        cliente,
        servicio,
        3
    )
    gestor.registrar_reserva(reserva)
    costo = reserva.procesar()
    print(
        "Reserva confirmada. Costo total:",
        costo
    )
#Prueba 8 Intentar crear una reserva con duracion negativa.
def prueba_8():
    cliente = gestor.buscar_cliente("C01")
    servicio = gestor.servicios[0]
    reserva = Reserva(
        "R02",
        cliente,
        servicio,
        -2
    )
    gestor.registrar_reserva(reserva)
#Prueba 9 Buscar un cliente que no esta registrado.
def prueba_9():
    gestor.buscar_cliente("C99")
#Prueba 10 Cancelar una reserva que ya fue confirmada.
def prueba_10():
    reserva = gestor.reservas[0]
    reserva.cancelar()
    print("Reserva cancelada correctamente.")
#Prueba 11. Calcular un precio con impuesto y descuento.
def prueba_11():
    calculadora = Calculadora()
    total = calculadora.calcular(
        100000,
        19,
        10
    )
    print("Precio inicial: $100.000")
    print("Impuesto: 19%")
    print("Descuento: 10%")
    print("Total a pagar:", total)
#Prueba 12 Intentar cancelar por segunda vez una reserva cancelada.
def prueba_12():
    reserva = gestor.reservas[0]
    reserva.cancelar()
#Prueba 13 intenta resrva un servicio no disponoble
def prueba_13():
    cliente = gestor.buscar_cliente("C01")
    servicio = gestor.servicios[1]
    servicio.cambiar_disponibilidad(False)
    reserva = Reserva(
        "R03",
        cliente,
        servicio,
        2
    )
    gestor.registrar_reserva(reserva)
#Prueba 14. Mostrar los clientes registrados.
def prueba_14():
    gestor.mostrar_clientes()
#Prueba 15. Mostrar los servicios registrados.
def prueba_15():
    gestor.mostrar_servicios()
#Prueba 16 Mostrar las reservas registradas.
def prueba_16():

    gestor.mostrar_reservas()
#Ejecuta las 16 pruebas 
if __name__ == "__main__":
    pruebas = [
        ("Registrar un cliente valido", prueba_1),
        ("Registrar un cliente con datos incorrectos", prueba_2),
        ("Crear un servicio de salas", prueba_3),
        ("Crear un servicio de equipos", prueba_4),
        ("Crear un servicio de asesoria", prueba_5),
        ("Crear un servicio con precio incorrecto", prueba_6),
        ("Realizar una reserva correctamente", prueba_7),
        ("Intentar una reserva con duracion incorrecta", prueba_8),
        ("Buscar un cliente que no existe", prueba_9),
        ("Cancelar una reserva", prueba_10),
        ("Calcular un precio con impuesto y descuento", prueba_11),
        ("Intentar cancelar una reserva nuevamente", prueba_12),
        ("Intentar reservar un servicio no disponible", prueba_13),
        ("Mostrar los clientes", prueba_14),
        ("Mostrar los servicios", prueba_15),
        ("Mostrar las reservas", prueba_16)
    ]
    print("\nControl de servicios y reservas - Pruebas del sistema")
   
    for numero, (descripcion, prueba) in enumerate(
        pruebas,
        start=1
    ):
        print(f"\nOPERACION {numero}: {descripcion}")
        try:
            prueba()
            print("Resultado: OPERACION terminada.")
        except Exception as error:
            logging.exception(
                "Error en la OPERACION %s",
                numero
            )
            print("Resultado: se presento un error.")
            print("Detalle:", error)
    print("\n" + "=" * 50)
    print("EL SISTEMA TERMINÓ LAS 16 PRUEBAS.")
    print("Los errores quedaron guardados en software_fj.log.")
