from manim import *
import numpy as np


# ---------------------------------------------------------------
# LÓGICA (Python puro)
# ---------------------------------------------------------------
class Nodo:
    def __init__(self, valor):
        self.valor = valor
        self.izq = None
        self.der = None


def insertar_bst(raiz, valor):
    if raiz is None:
        return Nodo(valor)
    if valor < raiz.valor:
        raiz.izq = insertar_bst(raiz.izq, valor)
    elif valor > raiz.valor:
        raiz.der = insertar_bst(raiz.der, valor)
    return raiz


def camino_busqueda(raiz, valor):
    """Valores de los nodos que se comparan al insertar 'valor' (de la raíz hacia abajo)."""
    camino = []
    actual = raiz
    while actual is not None:
        camino.append(actual.valor)
        actual = actual.izq if valor < actual.valor else actual.der
    return camino


def calcular_posiciones(raiz, sep_x=1.0, sep_y=1.3):
    posiciones = {}
    contador = 0

    def recorrer(nodo, profundidad):
        nonlocal contador
        if nodo is None:
            return
        recorrer(nodo.izq, profundidad + 1)
        posiciones[nodo.valor] = (contador * sep_x, -profundidad * sep_y)
        contador += 1
        recorrer(nodo.der, profundidad + 1)

    recorrer(raiz, 0)
    return posiciones


# ---------------------------------------------------------------
# DIBUJO
# ---------------------------------------------------------------
def crear_nodo(valor):
    circulo = Circle(radius=0.4, color=WHITE)
    circulo.set_fill(BLACK, opacity=1)
    texto = Text(str(valor), font_size=28)
    return VGroup(circulo, texto)


def crear_celda(valor):
    cuadro = Square(side_length=0.8, color=WHITE)
    texto = Text(str(valor), font_size=28)
    return VGroup(cuadro, texto)


# ---------------------------------------------------------------
# ESCENA 1: título
# ---------------------------------------------------------------
class Titulo(Scene):
    def construct(self):
        titulo = Text("AVL Tree", font_size=96, weight=BOLD)
        subtitulo = Text(
            "Un árbol de búsqueda siempre balanceado",
            font_size=32,
            color=GREY_B,
        )
        subtitulo.next_to(titulo, DOWN, buff=0.5)

        self.play(Write(titulo))
        self.play(FadeIn(subtitulo, shift=UP * 0.3))
        self.wait(2)
        self.play(FadeOut(VGroup(titulo, subtitulo)))


# ---------------------------------------------------------------
# ESCENA 2: motivación (el BST que se vuelve una lista)
# ---------------------------------------------------------------
class Motivacion(Scene):
    def construct(self):
        valores = [10, 20, 30, 40, 50]

        # --- La lista de arriba ---
        celdas = VGroup(*[crear_celda(v) for v in valores])
        celdas.arrange(RIGHT, buff=0)  # una al lado de otra, sin espacio
        celdas.to_edge(UP)
        self.play(FadeIn(celdas))
        self.wait(0.5)

        # --- Posiciones finales de cada nodo ---
        # Truco: construimos el árbol final solo para saber DÓNDE va cada nodo.
        raiz_final = None
        for v in valores:
            raiz_final = insertar_bst(raiz_final, v)
        pos = calcular_posiciones(raiz_final, sep_x=1.0, sep_y=0.9)
        desplazamiento = np.array([-2.0, 1.2, 0])
        destino = {
            v: np.array([x, y, 0]) + desplazamiento for v, (x, y) in pos.items()
        }

        # --- Inserción uno a uno ---
        raiz = None
        nodos = {}
        for i, v in enumerate(valores):
            celda = celdas[i]

            # 1) Resaltamos el valor que vamos a insertar
            self.play(celda[0].animate.set_fill(YELLOW, opacity=0.4))

            # 2) Aparece el nodo sobre su celda
            nodo = crear_nodo(v).move_to(celda.get_center())
            nodos[v] = nodo
            self.play(FadeIn(nodo, scale=0.5))

            # 3) Mostramos contra quién se compara (si ya hay nodos)
            camino = camino_busqueda(raiz, v)
            if camino:
                self.play(
                    LaggedStart(
                        *[Indicate(nodos[a], color=YELLOW) for a in camino],
                        lag_ratio=0.4,
                    )
                )
            raiz = insertar_bst(raiz, v)

            # 4) El nodo viaja a su lugar en el árbol
            self.play(nodo.animate.move_to(destino[v]))

            # 5) Se dibuja la arista desde el padre, y la celda se apaga
            animaciones = [celda.animate.set_color(GREY)]
            if camino:
                padre = camino[-1]
                arista = Line(destino[padre], destino[v], z_index=-1)
                animaciones.append(Create(arista))
            self.play(*animaciones)

        self.wait(1)

        # --- Remate ---
        mensaje = Text(
            "¡Es una lista! Buscar ahora cuesta O(n)",
            font_size=32,
            color=RED,
        )
        mensaje.to_edge(DOWN)
        self.play(Write(mensaje))
        self.wait(2)
