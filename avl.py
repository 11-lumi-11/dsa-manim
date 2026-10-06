from manim import *


# ---------------------------------------------------------------
# PARTE 1: la lógica (no tiene nada de Manim)
# ---------------------------------------------------------------
class Nodo:
    def __init__(self, valor):
        self.valor = valor
        self.izq = None
        self.der = None


def insertar_bst(raiz, valor):
    """Inserción de BST normal, sin balanceo (por ahora)."""
    if raiz is None:
        return Nodo(valor)
    if valor < raiz.valor:
        raiz.izq = insertar_bst(raiz.izq, valor)
    elif valor > raiz.valor:
        raiz.der = insertar_bst(raiz.der, valor)
    return raiz


def calcular_posiciones(raiz, sep_x=1.0, sep_y=1.3):
    """
    Devuelve {valor: (x, y)} para cada nodo.
    Truco: x = posición en el recorrido inorder, y = -profundidad.
    Así ningún nodo se solapa con otro y el árbol queda ordenado.
    """
    posiciones = {}
    contador = [0]  # lista para poder modificarla dentro de la función interna

    def recorrer(nodo, profundidad):
        if nodo is None:
            return
        recorrer(nodo.izq, profundidad + 1)
        posiciones[nodo.valor] = (contador[0] * sep_x, -profundidad * sep_y)
        contador[0] += 1
        recorrer(nodo.der, profundidad + 1)

    recorrer(raiz, 0)
    return posiciones


# ---------------------------------------------------------------
# PARTE 2: el dibujo (aquí empieza Manim)
# ---------------------------------------------------------------
def crear_nodo(valor):
    """Un nodo visual = círculo + número, agrupados en un VGroup."""
    circulo = Circle(radius=0.4, color=WHITE)
    circulo.set_fill(BLACK, opacity=1)  # relleno opaco: tapa las aristas que pasan por detrás
    texto = Text(str(valor), font_size=28)
    return VGroup(circulo, texto)  # el texto queda centrado sobre el círculo


class ArbolEstatico(Scene):
    def construct(self):
        # 1) Construimos el árbol con la lógica
        raiz = None
        for v in [10, 5, 15, 3, 7, 12, 18]:
            raiz = insertar_bst(raiz, v)

        # 2) Creamos un nodo visual por cada valor y lo ponemos en su posición
        posiciones = calcular_posiciones(raiz)
        nodos = {}
        for valor, (x, y) in posiciones.items():
            nodos[valor] = crear_nodo(valor).move_to([x, y, 0])

        # 3) Creamos las aristas (líneas padre -> hijo)
        aristas = VGroup()

        def agregar_aristas(nodo):
            if nodo is None:
                return
            for hijo in (nodo.izq, nodo.der):
                if hijo is not None:
                    linea = Line(
                        nodos[nodo.valor].get_center(),
                        nodos[hijo.valor].get_center(),
                        z_index=-1,  # se dibuja debajo de los círculos
                    )
                    aristas.add(linea)
                    agregar_aristas(hijo)

        agregar_aristas(raiz)

        # 4) Centramos todo el árbol en la pantalla
        arbol = VGroup(aristas, *nodos.values())
        arbol.move_to(ORIGIN)

        # 5) Animamos
        self.play(Create(aristas), run_time=1.5)
        self.play(LaggedStart(*[FadeIn(n) for n in nodos.values()], lag_ratio=0.2))
        self.wait(1)
