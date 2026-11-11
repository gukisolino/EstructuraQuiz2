"""
UN DÍA EN EL PARQUE  -  versión con interfaz gráfica (tkinter)
================================================================
Un menú con 3 pantallas, cada una usa una estructura distinta:

  1. Montaña rusa         -> COLA   (nodos enlazados, FIFO)
  2. Registro de reclamos -> PILA   (nodos enlazados, LIFO) + "deshacer"
  3. Fuegos artificiales  -> RECURSIVIDAD (funciones que se llaman a sí mismas)

Busca estas marcas en el código:  <<< COLA  /  <<< PILA  /  <<< RECURSIÓN

CÓMO EXPANDIRLO
  1) Crea una clase nueva que herede de `Pantalla` (implementa `construir`).
  2) Agrégala a la lista PANTALLAS al final del archivo.
  El menú genera la tarjeta nueva automáticamente.

Solo usa la librería estándar (tkinter). Ejecuta:  python un_dia_en_el_parque_gui.py
"""

import itertools
import math
import random
import tkinter as tk

ANCHO, ALTO = 900, 600
BARRA, PIE = 60, 40            # alto de la barra superior e inferior
FUENTE = "Helvetica"
NOMBRES = ["Ana", "Luis", "Sofía", "Mateo", "Vale", "Diego", "Cami",
           "Andrés", "Lucía", "Pablo", "Isa", "Tomás", "Fer", "Gabo"]
COLORES_GENTE = ["#e63946", "#f4a261", "#2a9d8f", "#6a4c93", "#1982c4", "#ff595e"]


# =====================================================================
#  ESTRUCTURAS DE DATOS  (nodos enlazados, sin listas de Python)
# =====================================================================

class Nodo:
    """Un eslabón: guarda un dato y apunta al siguiente nodo."""
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None


class Cola:                                   # <<< COLA (FIFO)
    """
    El primero que entra es el primero que sale.
    Dos punteros: `frente` (quien sale) y `final` (donde se agrega).
    Así encolar y desencolar no necesitan recorrer la cola.
    """
    def __init__(self):
        self.frente = None
        self.final = None
        self.tamano = 0

    def encolar(self, dato):
        nuevo = Nodo(dato)
        if self.final is None:                # cola vacía: frente y final coinciden
            self.frente = self.final = nuevo
        else:
            self.final.siguiente = nuevo      # el último apunta al nuevo...
            self.final = nuevo                # ...y el nuevo pasa a ser el último
        self.tamano += 1

    def desencolar(self):
        if self.frente is None:
            return None
        dato = self.frente.dato
        self.frente = self.frente.siguiente   # el frente avanza
        if self.frente is None:               # si quedó vacía, también se limpia el final
            self.final = None
        self.tamano -= 1
        return dato

    def esta_vacia(self):
        return self.frente is None

    def recorrer(self):
        """Datos de frente a final (solo para dibujar)."""
        actual, datos = self.frente, []
        while actual:
            datos.append(actual.dato)
            actual = actual.siguiente
        return datos


class Pila:                                   # <<< PILA (LIFO)
    """
    El último que entra es el primero que sale.
    Un solo puntero: `tope`. Apilar = el nuevo nodo apunta al tope anterior
    y pasa a ser el tope. Desapilar = el tope baja al siguiente nodo.
    """
    def __init__(self):
        self.tope = None
        self.tamano = 0

    def apilar(self, dato):
        nuevo = Nodo(dato)
        nuevo.siguiente = self.tope
        self.tope = nuevo
        self.tamano += 1

    def desapilar(self):
        if self.tope is None:
            return None
        dato = self.tope.dato
        self.tope = self.tope.siguiente
        self.tamano -= 1
        return dato

    def esta_vacia(self):
        return self.tope is None

    def recorrer(self):
        """Datos de tope a base (solo para dibujar)."""
        actual, datos = self.tope, []
        while actual:
            datos.append(actual.dato)
            actual = actual.siguiente
        return datos


# =====================================================================
#  UTILIDADES DE DIBUJO (compartidas por todas las pantallas)
# =====================================================================

def rect_redondo(c, x1, y1, x2, y2, r=14, **kw):
    """Rectángulo con esquinas redondeadas (polígono suavizado)."""
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return c.create_polygon(pts, smooth=True, **kw)


_ids_boton = itertools.count()


def boton(c, x, y, w, h, texto, color, comando, fuente=13):
    """Botón dibujado en el canvas: se ve igual en Windows, Mac y Linux."""
    tag = f"btn{next(_ids_boton)}"
    forma = rect_redondo(c, x, y, x + w, y + h, 12, fill=color,
                         outline="white", width=3, tags=(tag,))
    c.create_text(x + w / 2, y + h / 2, text=texto, fill="white",
                  font=(FUENTE, fuente, "bold"), tags=(tag,))
    c.tag_bind(tag, "<Button-1>", lambda e: comando())
    c.tag_bind(tag, "<Enter>", lambda e: c.itemconfig(forma, outline="#ffe066"))
    c.tag_bind(tag, "<Leave>", lambda e: c.itemconfig(forma, outline="white"))
    return tag


def persona(c, x, y, nombre, color, *tags):
    """Dibuja un visitante con los pies en (x, y)."""
    c.create_oval(x - 14, y - 32, x + 14, y, fill=color, outline="#222", tags=tags)
    c.create_oval(x - 11, y - 56, x + 11, y - 34, fill="#ffd9b3", outline="#222", tags=tags)
    c.create_oval(x - 6, y - 48, x - 3, y - 45, fill="#222", tags=tags)
    c.create_oval(x + 3, y - 48, x + 6, y - 45, fill="#222", tags=tags)
    c.create_arc(x - 6, y - 48, x + 6, y - 38, start=200, extent=140,
                 style="arc", outline="#222", tags=tags)
    c.create_text(x, y + 12, text=nombre, fill="white",
                  font=(FUENTE, 10, "bold"), tags=tags)


class Pantalla(tk.Frame):
    """
    Base de cada pantalla: canvas + barra superior (título y botón Menú)
    + barra inferior de mensajes. Las subclases solo implementan
    `dibujar_fondo()` (opcional) y `construir()`.
    """
    titulo = ""

    def __init__(self, app):
        super().__init__(app.root)
        self.app = app
        self.ocupado = False                  # evita pulsar mientras hay una animación
        self.c = tk.Canvas(self, width=ANCHO, height=ALTO, highlightthickness=0)
        self.c.pack()
        self.dibujar_fondo()
        self.c.create_rectangle(0, 0, ANCHO, BARRA, fill="#1d3557", outline="")
        self.c.create_rectangle(0, ALTO - PIE, ANCHO, ALTO, fill="#1d3557", outline="")
        self.c.create_text(150, BARRA / 2, text=self.titulo, anchor="w",
                           fill="white", font=(FUENTE, 17, "bold"))
        self.msg = self.c.create_text(ANCHO / 2, ALTO - PIE / 2, text="",
                                      fill="#ffe066", font=(FUENTE, 13, "bold"))
        boton(self.c, 15, 12, 110, 36, "< Menú", "#e76f51", app.mostrar_menu, 12)
        self.construir()

    def dibujar_fondo(self):
        pass

    def construir(self):
        pass

    def mensaje(self, texto):
        self.c.itemconfig(self.msg, text=texto)

    def animar(self, pasos, paso, fin=None, ms=20):
        """Ejecuta `paso(i, pasos)` cada `ms` milisegundos y luego `fin()`."""
        def tick(i):
            if i >= pasos:
                if fin:
                    fin()
                return
            paso(i, pasos)
            self.after(ms, tick, i + 1)
        tick(0)


# =====================================================================
#  PANTALLA 1 - MONTAÑA RUSA  (usa COLA)
# =====================================================================

class MontanaRusa(Pantalla):
    titulo = "MONTAÑA RUSA  ·  estructura: COLA"
    CAPACIDAD = 3        # personas por carro
    MAX_FILA = 6         # personas que caben en pantalla
    Y_SUELO = 420

    @staticmethod
    def slot_x(i):
        """Posición en pantalla de la persona i de la fila (0 = frente)."""
        return 300 - 52 * i

    def dibujar_fondo(self):
        c = self.c
        c.create_rectangle(0, 0, ANCHO, ALTO, fill="#8ecae6", outline="")      # cielo
        c.create_oval(-100, 360, 400, 520, fill="#95d5b2", outline="")         # colinas
        c.create_oval(450, 340, 1000, 540, fill="#95d5b2", outline="")
        for x, y in ((120, 130), (480, 100), (700, 170)):                      # nubes
            for dx, dy, r in ((0, 0, 30), (30, 8, 24), (-28, 10, 22)):
                c.create_oval(x + dx - r, y + dy - r, x + dx + r, y + dy + r,
                              fill="white", outline="")
        c.create_rectangle(0, self.Y_SUELO, ANCHO, ALTO, fill="#6a994e", outline="")
        rect_redondo(c, 15, 436, ANCHO - 15, ALTO - PIE - 8, 16, fill="#f1faee", outline="#1d3557", width=2)
        c.create_text(ANCHO / 2, 447, fill="#1d3557", font=(FUENTE, 11, "bold"),
                      text="Así se guarda la cola en memoria: nodos enlazados  [ dato | siguiente ]")

    def construir(self):
        self.fila = Cola()                    # <<< COLA: la fila de la montaña rusa
        self.total = 0
        self.camino = [(x, 370 - 120 * math.sin(math.pi * (x - 340) / 520)
                        - 45 * math.sin(3 * math.pi * (x - 340) / 520))
                       for x in range(340, 861, 4)]
        self.dibujar_pista()
        boton(self.c, 20, 75, 210, 42, "Llega una persona", "#2a9d8f", self.llega_persona)
        boton(self.c, 245, 75, 210, 42, f"Subir carro ({self.CAPACIDAD})", "#f77f00", self.subir_carro)
        self.contador = self.c.create_text(ANCHO - 15, BARRA / 2, anchor="e", fill="#ffe066",
                                           font=(FUENTE, 13, "bold"), text="Ya subieron: 0")
        self.dibujar_nodos()
        self.mensaje("Pulsa «Llega una persona» para formar la fila")

    # ---------- dibujo ----------
    def dibujar_pista(self):
        c = self.c
        for x, y in self.camino[::8]:                                  # soportes
            c.create_line(x, y, x, self.Y_SUELO, fill="#8d6e63", width=3)
        c.create_line([v for p in self.camino for v in p], fill="#c1121f", width=6)
        c.create_rectangle(320, 372, 372, 380, fill="#6d4c41", outline="")   # andén
        c.create_text(346, 360, text="EMBARQUE", fill="#1d3557", font=(FUENTE, 9, "bold"))

    def redibujar(self, excluir_ultimo=False):
        """Redibuja a la gente según el contenido real de la cola."""
        self.c.delete("fila")
        datos = self.fila.recorrer()
        if excluir_ultimo:
            datos = datos[:-1]
        for i, (nombre, color) in enumerate(datos):
            persona(self.c, self.slot_x(i), self.Y_SUELO, nombre, color, "fila")
        self.dibujar_nodos()

    def dibujar_nodos(self):
        """Dibuja los nodos enlazados reales de la cola (frente -> ... -> final)."""
        c = self.c
        c.delete("nodos")
        datos = self.fila.recorrer()
        if not datos:
            c.create_text(ANCHO / 2, 495, tags="nodos", fill="#1d3557", font=(FUENTE, 13, "bold"),
                          text="frente = None      final = None      (cola vacía)")
            return
        x = 40
        for i, (nombre, color) in enumerate(datos):
            ultimo = i == len(datos) - 1
            rect_redondo(c, x, 476, x + 100, 512, 8, fill=color, outline="#1d3557", width=2, tags="nodos")
            c.create_text(x + 36, 494, text=nombre, fill="white", font=(FUENTE, 11, "bold"), tags="nodos")
            c.create_line(x + 72, 476, x + 72, 512, fill="white", width=2, tags="nodos")
            if ultimo:   # el último nodo apunta a "nada" (None): se dibuja una barra
                c.create_line(x + 76, 508, x + 96, 480, fill="white", width=2, tags="nodos")
            else:        # los demás apuntan al siguiente nodo
                c.create_oval(x + 83, 491, x + 89, 497, fill="white", tags="nodos")
                c.create_line(x + 86, 494, x + 130, 494, arrow="last", fill="#1d3557", width=2, tags="nodos")
            etiqueta = " y ".join(t for t, ok in (("frente", i == 0), ("final", ultimo)) if ok)
            if etiqueta:
                c.create_text(x + 50, 466, text=etiqueta, fill="#e63946",
                              font=(FUENTE, 10, "bold"), tags="nodos")
            x += 130

    # ---------- acciones ----------
    def llega_persona(self):
        if self.ocupado:
            return
        if self.fila.tamano >= self.MAX_FILA:
            self.mensaje("¡La fila está llena! Sube un carro para liberar espacio")
            return
        nombre, color = random.choice(NOMBRES), random.choice(COLORES_GENTE)
        self.fila.encolar((nombre, color))    # <<< COLA: entra por el FINAL
        self.ocupado = True
        self.redibujar(excluir_ultimo=True)   # la recién llegada se dibuja caminando
        destino = self.slot_x(self.fila.tamano - 1)
        persona(self.c, -30, self.Y_SUELO, nombre, color, "nuevo")
        pasos = 25
        self.animar(pasos, lambda i, n: self.c.move("nuevo", (destino + 30) / pasos, 0),
                    lambda: self._fin_llegada(nombre), ms=18)

    def _fin_llegada(self, nombre):
        self.c.delete("nuevo")
        self.redibujar()
        self.ocupado = False
        self.mensaje(f"{nombre} se formó al final de la fila  ({self.fila.tamano} en fila)")

    def subir_carro(self):
        if self.ocupado:
            return
        if self.fila.esta_vacia():
            self.mensaje("No hay nadie en la fila")
            return
        self.ocupado = True
        pasajeros = []
        while len(pasajeros) < self.CAPACIDAD and not self.fila.esta_vacia():
            pasajeros.append(self.fila.desencolar())   # <<< COLA: sale por el FRENTE
        k = len(pasajeros)
        # Los que quedan siguen en sus lugares viejos y avanzan k puestos.
        self.c.delete("fila")
        self.dibujar_nodos()
        for j, (nombre, color) in enumerate(self.fila.recorrer()):
            persona(self.c, self.slot_x(j + k), self.Y_SUELO, nombre, color, "fila")
        for j, (nombre, color) in enumerate(pasajeros):
            persona(self.c, self.slot_x(j), self.Y_SUELO, nombre, color, f"p{j}", "pasajeros")
        pasos = 22

        def caminar(i, n):
            self.c.move("fila", 52 * k / pasos, 0)
            for j in range(k):
                self.c.move(f"p{j}", (346 - self.slot_x(j)) / pasos, 0)

        self.mensaje("Los primeros de la fila suben al carro...")
        self.animar(pasos, caminar, lambda: self.paseo([col for _, col in pasajeros]), ms=18)

    def paseo(self, colores):
        c = self.c
        c.delete("pasajeros")
        x0, y0 = self.camino[0]
        c.create_rectangle(x0 - 34, y0 - 24, x0 + 34, y0 - 4, fill="#d00000",
                           outline="white", width=2, tags="carro")
        for j, col in enumerate(colores):
            cx = x0 - 20 + j * 20
            c.create_oval(cx - 8, y0 - 40, cx + 8, y0 - 24, fill=col, outline="#222", tags="carro")
        for dx in (-20, 20):
            c.create_oval(x0 + dx - 6, y0 - 8, x0 + dx + 6, y0 + 4, fill="#222", tags="carro")
        c.create_text(x0, y0 - 62, text="¡WIIII!", fill="#1d3557",
                      font=(FUENTE, 14, "bold"), tags="carro")
        ruta = self.camino + self.camino[::-1]            # ida y vuelta por los rieles

        def avanzar(i, n):
            (xa, ya), (xb, yb) = ruta[i], ruta[i + 1]
            c.move("carro", xb - xa, yb - ya)

        self.mensaje("¡El carro está en marcha!")
        self.animar(len(ruta) - 1, avanzar, lambda: self._fin_paseo(len(colores)), ms=9)

    def _fin_paseo(self, k):
        self.c.delete("carro")
        self.total += k
        self.c.itemconfig(self.contador, text=f"Ya subieron: {self.total}")
        self.redibujar()
        self.ocupado = False
        self.mensaje(f"¡{k} visitantes disfrutaron el viaje! Quedan {self.fila.tamano} en la fila")


# =====================================================================
#  PANTALLA 2 - REGISTRO DE RECLAMOS  (usa PILA)
# =====================================================================

class Reclamos(Pantalla):
    titulo = "REGISTRO DE RECLAMOS  ·  estructura: PILA"
    MAX = 8                                  # reclamos que caben en pantalla
    X, ANCHO_CARD, ALTO_CARD, BASE = 400, 400, 44, 520
    COLORES = ["#ffd166", "#ef9ab7", "#8ecae6", "#b5e48c", "#cdb4db", "#ffb4a2"]
    IDEAS = ["Fila muy larga", "Baño sucio", "Helado muy caro", "Juego descompuesto"]

    def y_top(self, i):
        """Altura de la tarjeta i de la pila (0 = la de la base)."""
        return self.BASE - 52 * (i + 1) + 8

    def dibujar_fondo(self):
        c = self.c
        c.create_rectangle(0, 0, ANCHO, ALTO, fill="#fdf0d5", outline="")
        rect_redondo(c, 10, BARRA + 10, 350, ALTO - PIE - 10, 18, fill="#669bbc", outline="#1d3557", width=3)
        rect_redondo(c, self.X - 20, self.BASE, self.X + self.ANCHO_CARD + 20, self.BASE + 16, 6,
                     fill="#6d4c41", outline="")
        c.create_text(self.X + self.ANCHO_CARD / 2, self.BASE + 28, text="BASE DE LA PILA",
                      fill="#6d4c41", font=(FUENTE, 10, "bold"))

    def construir(self):
        self.pila = Pila()                    # <<< PILA: los reclamos registrados
        self.numero = 0
        c = self.c
        c.create_text(180, 95, text="Escribe un reclamo:", fill="white", font=(FUENTE, 14, "bold"))
        self.entrada = tk.Entry(self, font=(FUENTE, 13), width=24, justify="center")
        c.create_window(180, 130, window=self.entrada)
        self.entrada.bind("<Return>", lambda e: self.registrar())
        boton(c, 40, 160, 280, 42, "Registrar reclamo", "#2a9d8f", self.registrar)
        boton(c, 40, 212, 280, 42, "Deshacer el último", "#e63946", self.deshacer)
        c.create_text(180, 290, text="Ideas rápidas (clic para usar):", fill="white", font=(FUENTE, 12, "bold"))
        for k, idea in enumerate(self.IDEAS):
            boton(c, 40, 310 + k * 48, 280, 38, idea, "#457b9d",
                  lambda t=idea: self.poner_texto(t), 12)
        self.redibujar()
        self.mensaje("Cada reclamo nuevo cae encima de la pila")

    def poner_texto(self, texto):
        self.entrada.delete(0, "end")
        self.entrada.insert(0, texto)
        self.entrada.focus_set()

    # ---------- dibujo ----------
    def tarjeta(self, y, num, texto, *tags):
        c = self.c
        rect_redondo(c, self.X, y, self.X + self.ANCHO_CARD, y + self.ALTO_CARD, 10,
                     fill=self.COLORES[num % len(self.COLORES)], outline="#444", width=2, tags=tags)
        c.create_oval(self.X + 8, y + 8, self.X + 36, y + 36, fill="white", outline="#444", tags=tags)
        c.create_text(self.X + 22, y + 22, text=f"#{num}", font=(FUENTE, 9, "bold"), tags=tags)
        corto = texto if len(texto) <= 34 else texto[:33] + "…"
        c.create_text(self.X + 48, y + 22, text=corto, anchor="w", font=(FUENTE, 13), fill="#222", tags=tags)

    def redibujar(self, excluir_tope=False, indicador=True):
        """Dibuja la pila real, de la base hacia arriba."""
        c = self.c
        c.delete("pila")
        datos = self.pila.recorrer()          # tope -> base
        n = len(datos)
        for k, (num, texto) in enumerate(datos):
            if excluir_tope and k == 0:
                continue
            i = n - 1 - k
            self.tarjeta(self.y_top(i), num, texto, "pila")
            if i > 0:                         # flechita al nodo "siguiente" (el de abajo)
                c.create_line(self.X + 385, self.y_top(i) + 44, self.X + 385, self.y_top(i) + 52,
                              arrow="last", fill="#444", width=2, tags="pila")
        if n == 0:
            c.create_text(self.X + 200, 300, text="La pila está vacía\n(tope = None)", tags="pila",
                          fill="#6d4c41", font=(FUENTE, 16, "bold"), justify="center")
        elif indicador and not excluir_tope:
            c.create_text(self.X + self.ANCHO_CARD + 10, self.y_top(n - 1) + 22, anchor="w",
                          text="◀ TOPE", fill="#e63946", font=(FUENTE, 12, "bold"), tags="pila")

    # ---------- acciones ----------
    def registrar(self):
        if self.ocupado:
            return
        texto = self.entrada.get().strip()
        if not texto:
            self.mensaje("Escribe algo primero (o usa una idea rápida)")
            return
        if self.pila.tamano >= self.MAX:
            self.mensaje(f"La pila está llena ({self.MAX}). Deshaz alguno para continuar")
            return
        self.numero += 1
        self.pila.apilar((self.numero, texto))     # <<< PILA: entra por el TOPE
        self.entrada.delete(0, "end")
        self.ocupado = True
        self.redibujar(excluir_tope=True)          # la tarjeta nueva se dibuja cayendo
        y_fin, y_ini = self.y_top(self.pila.tamano - 1), -60
        self.tarjeta(y_ini, self.numero, texto, "nueva")

        def caer(k, n):                            # caída acelerada (cuadrática)
            f = lambda s: y_ini + (y_fin - y_ini) * (s / n) ** 2
            self.c.move("nueva", 0, f(k + 1) - f(k))

        num = self.numero
        self.animar(22, caer, lambda: self._fin_registro(num), ms=16)

    def _fin_registro(self, num):
        self.c.delete("nueva")
        self.redibujar()
        self.ocupado = False
        self.mensaje(f"Reclamo #{num} registrado. Hay {self.pila.tamano} en la pila")

    def deshacer(self):
        if self.ocupado:
            return
        if self.pila.esta_vacia():
            self.mensaje("No hay nada que deshacer")
            return
        y = self.y_top(self.pila.tamano - 1)
        num, texto = self.pila.desapilar()         # <<< PILA: sale el TOPE (el último)
        self.ocupado = True
        self.redibujar(indicador=False)
        self.tarjeta(y, num, texto, "saliente")
        self.animar(26, lambda i, n: self.c.move("saliente", 26, -5),
                    lambda: self._fin_deshacer(num), ms=14)

    def _fin_deshacer(self, num):
        self.c.delete("saliente")
        self.redibujar()
        self.ocupado = False
        self.mensaje(f"Se deshizo el reclamo #{num} (el último en llegar fue el primero en salir)")


# =====================================================================
#  PANTALLA 3 - FUEGOS ARTIFICIALES  (usa RECURSIVIDAD)
# =====================================================================
# Toda función recursiva tiene:
#   · CASO BASE: cuándo se detiene.
#   · CASO RECURSIVO: se llama a sí misma con un problema más pequeño.
# Aquí hay 4 funciones recursivas: cuenta_regresiva, espectaculo,
# subir_cohete y explosion. Las 3 primeras se llaman a sí mismas a través
# de `after` (para que haya animación sin congelar la ventana); `explosion`
# se llama directamente a sí misma y dibuja un fractal de chispas.

class Fuegos(Pantalla):
    titulo = "CIERRE CON FUEGOS ARTIFICIALES  ·  RECURSIVIDAD"
    RAYOS = 7
    COLORES = ["#ff595e", "#ffca3a", "#8ac926", "#1982c4", "#c77dff", "#ff9f1c", "#4cc9f0"]

    def dibujar_fondo(self):
        c = self.c
        c.create_rectangle(0, 0, ANCHO, ALTO, fill="#0b1026", outline="")
        rnd = random.Random(7)
        for _ in range(110):                                         # estrellas
            x, y, r = rnd.randint(0, ANCHO), rnd.randint(0, 430), rnd.choice((1, 1, 2))
            c.create_oval(x - r, y - r, x + r, y + r, fill="#e9ecef", outline="")
        c.create_oval(785, 95, 855, 165, fill="#f1faee", outline="")  # luna
        c.create_oval(802, 88, 872, 158, fill="#0b1026", outline="")
        # silueta del parque: noria, árboles y colina
        c.create_oval(80, 370, 240, 530, outline="#26335f", width=4)
        for k in range(8):
            a = k * math.pi / 4
            c.create_line(160, 450, 160 + 80 * math.cos(a), 450 + 80 * math.sin(a), fill="#26335f", width=2)
        c.create_line(160, 450, 120, 520, fill="#26335f", width=4)
        c.create_line(160, 450, 200, 520, fill="#26335f", width=4)
        for x in (300, 350, 600, 680, 760, 830):
            c.create_polygon(x, 470, x - 22, 520, x + 22, 520, fill="#16213e", outline="")
        c.create_polygon(0, 520, 150, 490, 450, 515, 700, 495, ANCHO, 515, ANCHO, ALTO,
                         0, ALTO, fill="#16213e", outline="")

    def construir(self):
        self.activo = False
        boton(self.c, ANCHO / 2 - 140, 75, 280, 44, "Iniciar cierre del parque", "#7b2cbf", self.iniciar)
        self.c.create_text(ANCHO / 2, 140, fill="#adb5bd", font=(FUENTE, 11),
                           text="…o haz clic en el cielo para lanzar tus propios cohetes")
        self.c.bind("<Button-1>", self.clic_cielo)
        self.mensaje("El parque está por cerrar")

    def clic_cielo(self, evento):
        actual = self.c.find_withtag("current")
        if actual and any(t.startswith("btn") for t in self.c.gettags(actual[0])):
            return                                   # fue un clic en un botón, no en el cielo
        if BARRA < evento.y < 470:
            self.lanzar(evento.x, evento.y)

    def iniciar(self):
        if self.activo:
            return
        self.activo = True
        self.c.delete("final")
        self.mensaje("¡Prepárense para el cierre!")
        self.cuenta_regresiva(3)

    # ---------- recursión 1: cuenta regresiva ----------
    def cuenta_regresiva(self, n):
        self.c.delete("cuenta")
        if n == 0:                                   # CASO BASE
            self.c.create_text(ANCHO / 2, 250, text="¡FUEGO!", fill="#ffd166",
                               font=(FUENTE, 70, "bold"), tags="cuenta")
            self.after(700, self.c.delete, "cuenta")
            self.after(700, self.espectaculo, 6)
            return
        self.c.create_text(ANCHO / 2, 250, text=str(n), fill="#ffd166",
                           font=(FUENTE, 90, "bold"), tags="cuenta")
        self.after(800, self.cuenta_regresiva, n - 1)   # <<< RECURSIÓN (n-1)

    # ---------- recursión 2: espectáculo ----------
    def espectaculo(self, cohetes):
        if cohetes == 0:                             # CASO BASE: no quedan cohetes
            self.after(2500, self.fin_show)
            return
        self.lanzar(random.randint(120, 780), random.randint(110, 260))
        self.after(900, self.espectaculo, cohetes - 1)  # <<< RECURSIÓN (un cohete menos)

    def fin_show(self):
        self.c.create_text(ANCHO / 2, 250, text="¡Gracias por visitar el parque!\nHasta mañana",
                           fill="#ffd166", font=(FUENTE, 32, "bold"), justify="center", tags="final")
        self.mensaje("El parque ha cerrado. ¡Vuelve pronto!")
        self.activo = False

    # ---------- recursión 3: el cohete sube ----------
    def lanzar(self, x, y_objetivo):
        self.subir_cohete(x, 500, y_objetivo, random.choice(self.COLORES))

    def subir_cohete(self, x, y, y_final, color):
        if y <= y_final:                             # CASO BASE: llegó arriba -> explota
            self.explosion(x, y, 75, 3, color)
            return
        estela = self.c.create_line(x, y, x, y + 16, fill="#ffe8a3", width=3)
        self.after(220, self.c.delete, estela)
        self.after(14, self.subir_cohete, x, y - 9, y_final, color)  # <<< RECURSIÓN (sube 9 px)

    # ---------- recursión 4: la explosión (fractal) ----------
    def explosion(self, x, y, radio, nivel, color, rayo=0, retraso=0):
        """
        Dibuja una explosión: de (x, y) salen RAYOS chispas y, del final de
        cada chispa, nace una explosión más pequeña (nivel - 1).
          - `nivel`: profundidad. Con nivel 0 no se dibuja nada (CASO BASE).
          - `rayo`: cuál chispa toca dibujar (sustituye a un for).
          - `retraso`: ms de espera; las sub-explosiones aparecen después.
        """
        if nivel == 0 or rayo == self.RAYOS:         # CASO BASE
            return
        ang = 2 * math.pi * rayo / self.RAYOS + nivel
        nx, ny = x + radio * math.cos(ang), y + radio * math.sin(ang)
        self.after(retraso, self.chispa, x, y, nx, ny, color if nivel > 1 else "#fff3b0", nivel)
        self.explosion(nx, ny, radio * 0.55, nivel - 1, color, 0, retraso + 150)  # <<< RECURSIÓN (hacia adentro)
        self.explosion(x, y, radio, nivel, color, rayo + 1, retraso)              # <<< RECURSIÓN (siguiente rayo)

    def chispa(self, x, y, nx, ny, color, nivel):
        linea = self.c.create_line(x, y, nx, ny, fill=color, width=nivel, capstyle="round")
        punta = self.c.create_oval(nx - nivel - 1, ny - nivel - 1, nx + nivel + 1, ny + nivel + 1,
                                   fill="#fff3b0", outline="")
        self.after(550, self.c.delete, linea, punta)


# =====================================================================
#  MENÚ PRINCIPAL  +  APLICACIÓN
# =====================================================================

# Para EXPANDIR: agrega un diccionario nuevo a esta lista y listo.
PANTALLAS = [
    {"titulo": "Montaña rusa", "estructura": "COLA", "color": "#e63946", "clase": MontanaRusa,
     "descr": "Forma la fila y sube a los visitantes al carro.\nEl primero en llegar es el primero en subir."},
    {"titulo": "Reclamos", "estructura": "PILA", "color": "#2a9d8f", "clase": Reclamos,
     "descr": "Registra quejas y deshaz la última.\nEl último en llegar es el primero en salir."},
    {"titulo": "Fuegos artificiales", "estructura": "RECURSIVIDAD", "color": "#7b2cbf", "clase": Fuegos,
     "descr": "Cierra el parque con un show.\nCada explosión nace de otra explosión."},
]


class Menu(tk.Frame):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app
        c = self.c = tk.Canvas(self, width=ANCHO, height=ALTO, highlightthickness=0)
        c.pack()
        for i in range(40):                                        # cielo degradado
            t = i / 39
            col = "#%02x%02x%02x" % (int(76 + 179 * t), int(201 + 40 * t), int(240 + 0 * t))
            c.create_rectangle(0, i * ALTO / 40, ANCHO, (i + 1) * ALTO / 40 + 1, fill=col, outline="")
        c.create_oval(815, 18, 885, 88, fill="#ffd23f", outline="#ffb703", width=4)      # sol
        for tag, x, y in (("n1", 80, 90), ("n2", 420, 60), ("n3", 650, 140)):             # nubes
            for dx, dy, r in ((0, 0, 30), (32, 8, 24), (-30, 10, 22)):
                c.create_oval(x + dx - r, y + dy - r, x + dx + r, y + dy + r,
                              fill="white", outline="", tags=tag)
        c.create_rectangle(0, 520, ANCHO, ALTO, fill="#6a994e", outline="")
        c.create_oval(-80, 490, 380, 600, fill="#80b918", outline="")
        c.create_oval(520, 500, 1000, 620, fill="#80b918", outline="")
        c.create_text(ANCHO / 2 + 3, 63, text="UN DÍA EN EL PARQUE", fill="#1d3557", font=(FUENTE, 44, "bold"))
        c.create_text(ANCHO / 2, 60, text="UN DÍA EN EL PARQUE", fill="white", font=(FUENTE, 44, "bold"))
        c.create_text(ANCHO / 2, 110, text="Elige una atracción", fill="#1d3557", font=(FUENTE, 16, "bold"))
        self.dibujar_tarjetas()
        self.mover_nubes()

    def dibujar_tarjetas(self):
        c, n = self.c, len(PANTALLAS)
        ancho = min(250, (ANCHO - 80 - (n - 1) * 25) / n)
        x = (ANCHO - (n * ancho + (n - 1) * 25)) / 2
        for p in PANTALLAS:
            tag = f"tarjeta_{p['clase'].__name__}"
            forma = rect_redondo(c, x, 170, x + ancho, 450, 22, fill=p["color"],
                                 outline="white", width=4, tags=tag)
            c.create_text(x + ancho / 2, 215, text=p["titulo"], fill="white",
                          font=(FUENTE, 19, "bold"), tags=tag, width=ancho - 20, justify="center")
            rect_redondo(c, x + 25, 255, x + ancho - 25, 290, 14, fill="white", outline="", tags=tag)
            c.create_text(x + ancho / 2, 272, text=p["estructura"], fill=p["color"],
                          font=(FUENTE, 13, "bold"), tags=tag)
            c.create_text(x + ancho / 2, 350, text=p["descr"], fill="white", font=(FUENTE, 11),
                          width=ancho - 30, justify="center", tags=tag)
            c.create_text(x + ancho / 2, 420, text="Entrar  >", fill="#ffe066",
                          font=(FUENTE, 14, "bold"), tags=tag)
            c.tag_bind(tag, "<Button-1>", lambda e, k=p["clase"]: self.app.abrir(k))
            c.tag_bind(tag, "<Enter>", lambda e, f=forma: c.itemconfig(f, outline="#ffe066"))
            c.tag_bind(tag, "<Leave>", lambda e, f=forma: c.itemconfig(f, outline="white"))
            x += ancho + 25

    def mover_nubes(self):
        for t in ("n1", "n2", "n3"):
            self.c.move(t, 1, 0)
            if self.c.bbox(t)[0] > ANCHO:
                self.c.move(t, -(ANCHO + 260), 0)
        self.after(50, self.mover_nubes)


class App:
    """Controla qué pantalla se ve. Cada pantalla se crea una vez y conserva su estado."""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Un día en el parque")
        self.root.resizable(False, False)
        self.menu = Menu(self)
        self.vistas = {}
        self.actual = None
        self.mostrar_menu()

    def _cambiar(self, frame):
        if self.actual:
            self.actual.pack_forget()
        frame.pack()
        self.actual = frame

    def mostrar_menu(self):
        self._cambiar(self.menu)

    def abrir(self, clase):
        if clase not in self.vistas:
            self.vistas[clase] = clase(self)
        self._cambiar(self.vistas[clase])

    def iniciar(self):
        self.root.mainloop()


if __name__ == "__main__":
    App().iniciar()