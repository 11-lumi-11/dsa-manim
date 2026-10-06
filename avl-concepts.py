from manim import *

from avl import insertar, altura, balance
from avl_video import crear_nodo  # reutilizamos el nodo (círculo + número)

VALORES = [10, 20, 30, 40, 50]
COLOR_ALTURA = BLUE_B


# ---------------------------------------------------------------
# AYUDAS (compartidas por las tres escenas)
# ---------------------------------------------------------------
def construir_avl(valores):
    raiz = None
    for v in valores:
        raiz = insertar(raiz, v)
    return raiz


def niveles(raiz):
    """Lista de niveles: [[raíz], [hijos], [nietos], ...] (recorrido por niveles)."""
    resultado = []
    actual = [raiz]
    while actual:
        resultado.append(actual)
        actual = [h for n in actual for h in (n.izq, n.der) if h is not None]
    return resultado


def calcular_posiciones(raiz, sep_x=1.2, sep_y=1.3):
    """
    Layout simétrico: cada nivel separa a sus hijos la mitad que el nivel anterior.
    Funciona muy bien con árboles balanceados (como el AVL).
    """
    posiciones = {}

    def recorrer(nodo, x, profundidad):
        if nodo is None:
            return
        posiciones[nodo.valor] = (x, -profundidad * sep_y)
        desfase = sep_x * 2 ** (raiz.altura - profundidad - 2)
        recorrer(nodo.izq, x - desfase, profundidad + 1)
        recorrer(nodo.der, x + desfase, profundidad + 1)

    recorrer(raiz, 0, 0)
    return posiciones


class ArbolVisual:
    """Guarda los mobjects de un árbol: un VGroup por nodo y una Line por conexión."""

    def __init__(self, raiz, sep_x=1.2, sep_y=1.3, y_raiz=1.0):
        self.raiz = raiz
        pos = calcular_posiciones(raiz, sep_x, sep_y)
        xs = [x for x, _ in pos.values()]
        dx = -(min(xs) + max(xs)) / 2  # centra el árbol horizontalmente

        self.nodos = {
            v: crear_nodo(v).move_to([x + dx, y + y_raiz, 0])
            for v, (x, y) in pos.items()
        }
        self.aristas = {}                 # (padre, hijo) -> Line
        self.padres = {}                  # hijo -> padre
        self.lados = {raiz.valor: 1}      # -1 si es hijo izquierdo, 1 si es derecho
        self.logica = {raiz.valor: raiz}  # valor -> Nodo (el de la lógica)
        self._conectar(raiz)

    def _conectar(self, nodo):
        for hijo, lado in ((nodo.izq, -1), (nodo.der, 1)):
            if hijo is None:
                continue
            self.aristas[(nodo.valor, hijo.valor)] = Line(
                self.nodos[nodo.valor].get_center(),
                self.nodos[hijo.valor].get_center(),
                z_index=-1,
            )
            self.padres[hijo.valor] = nodo.valor
            self.lados[hijo.valor] = lado
            self.logica[hijo.valor] = hijo
            self._conectar(hijo)

    def todo(self):
        return VGroup(*self.aristas.values(), *self.nodos.values())


def crear_etiquetas(arbol, valor_de, color):
    """
    Un texto pequeño al lado de cada nodo.
    'valor_de' es una FUNCIÓN que recibe un Nodo y devuelve lo que se escribe.
    """
    etiquetas = {}
    for v, nodo in arbol.logica.items():
        etiqueta = Text(str(valor_de(nodo)), font_size=26, color=color)
        direccion = LEFT if arbol.lados[v] < 0 else RIGHT
        etiqueta.next_to(arbol.nodos[v], direccion, buff=0.15)
        etiquetas[v] = etiqueta
    return etiquetas


# ---------------------------------------------------------------
# ESCENA 3: "este problema lo resuelve el AVL"
# ---------------------------------------------------------------
class PresentacionAVL(Scene):
    def construct(self):
        raiz = construir_avl(VALORES)
        arbol = ArbolVisual(raiz)

        titulo = Text("La solución: el árbol AVL", font_size=44).to_edge(UP)
        subtitulo = Text(
            "Un BST que se mantiene balanceado en cada inserción",
            font_size=26,
            color=GREY_B,
        ).next_to(titulo, DOWN, buff=0.3)

        self.play(Write(titulo))
        self.play(FadeIn(subtitulo, shift=UP * 0.3))
        self.wait(1.5)

        # El árbol aparece nivel por nivel: de la raíz hacia las hojas
        for nivel in niveles(raiz):
            animaciones = []
            for nodo in nivel:
                v = nodo.valor
                if v in arbol.padres:
                    animaciones.append(Create(arbol.aristas[(arbol.padres[v], v)]))
                animaciones.append(FadeIn(arbol.nodos[v], scale=0.5))
            self.play(*animaciones)
        self.wait(1)

        mensaje = Text(
            "Los mismos 5 valores, pero la altura baja de 5 a 3",
            font_size=28,
            color=GREEN,
        ).to_edge(DOWN)
        self.play(Write(mensaje))
        self.wait(2)

        # Dejamos solo el árbol en pantalla: la siguiente escena parte de ahí
        self.play(FadeOut(titulo), FadeOut(subtitulo), FadeOut(mensaje))


# ---------------------------------------------------------------
# ESCENA 4: altura
# ---------------------------------------------------------------
class Altura(Scene):
    def construct(self):
        raiz = construir_avl(VALORES)
        arbol = ArbolVisual(raiz)
        self.add(arbol.todo())  # ya está en pantalla, sin animación

        etiquetas = crear_etiquetas(arbol, lambda n: n.altura, COLOR_ALTURA)

        titulo = Text("Altura de un nodo", font_size=44).to_edge(UP)
        formula = Text(
            "altura = 1 + max(altura izquierda, altura derecha)", font_size=30
        ).to_edge(DOWN, buff=1.0)
        nota = Text(
            "(un subárbol vacío tiene altura 0)", font_size=24, color=GREY_B
        ).next_to(formula, DOWN, buff=0.25)

        self.play(Write(titulo))
        self.play(Write(formula))
        self.play(FadeIn(nota))
        self.wait(1)

        # Orden de abajo hacia arriba: las hojas primero
        orden = [n for nivel in reversed(niveles(raiz)) for n in nivel]
        hojas = [n for n in orden if n.izq is None and n.der is None]
        internos = [n for n in orden if n not in hojas]

        # 1) Todas las hojas valen 1
        calc = Text(
            "hoja: 1 + max(0, 0) = 1", font_size=32, color=YELLOW
        ).next_to(titulo, DOWN, buff=0.4)
        self.play(Write(calc))
        self.play(
            LaggedStart(
                *[FadeIn(etiquetas[n.valor], scale=1.5) for n in hojas],
                lag_ratio=0.3,
            )
        )
        self.play(FadeOut(calc))

        # 2) Los nodos internos, de abajo hacia arriba
        for nodo in internos:
            hijos = [h for h in (nodo.izq, nodo.der) if h is not None]
            calc = Text(
                f"1 + max({altura(nodo.izq)}, {altura(nodo.der)}) = {altura(nodo)}",
                font_size=32,
                color=YELLOW,
            ).next_to(titulo, DOWN, buff=0.4)

            self.play(*[Indicate(etiquetas[h.valor]) for h in hijos])
            self.play(Write(calc))
            self.play(FadeIn(etiquetas[nodo.valor], scale=1.5))
            self.wait(0.5)
            self.play(FadeOut(calc))

        # 3) La altura del árbol es la de su raíz
        self.play(Indicate(etiquetas[raiz.valor], scale_factor=1.8))
        conclusion = Text(
            "La altura del árbol es la altura de su raíz", font_size=28, color=GREEN
        ).next_to(titulo, DOWN, buff=0.4)
        self.play(Write(conclusion))
        self.wait(2)


# ---------------------------------------------------------------
# ESCENA 5: factor de balance
# ---------------------------------------------------------------
class FactorBalance(Scene):
    def construct(self):
        raiz = construir_avl(VALORES)
        arbol = ArbolVisual(raiz)

        # Partimos con las alturas ya visibles (venimos de la escena anterior)
        h_lbl = crear_etiquetas(arbol, lambda n: n.altura, COLOR_ALTURA)
        self.add(arbol.todo(), *h_lbl.values())

        # Etiquetas del factor de balance (todavía NO están en pantalla)
        bf_lbl = crear_etiquetas(arbol, balance, YELLOW)
        for v, etiqueta in bf_lbl.items():
            etiqueta.set_color(GREEN if balance(arbol.logica[v]) == 0 else YELLOW)

        titulo = Text("Factor de balance", font_size=44).to_edge(UP)
        formula = Text(
            "factor = altura izquierda - altura derecha", font_size=30
        ).to_edge(DOWN, buff=1.0)

        self.play(Write(titulo))
        self.play(Write(formula))
        self.wait(1)

        def explicar(nodo):
            """Muestra la cuenta de un nodo y convierte su altura en su factor."""
            hijos = [h for h in (nodo.izq, nodo.der) if h is not None]
            calc = Text(
                f"{altura(nodo.izq)} - {altura(nodo.der)} = {balance(nodo)}",
                font_size=32,
                color=YELLOW,
            ).next_to(titulo, DOWN, buff=0.4)

            self.play(*[Indicate(h_lbl[h.valor]) for h in hijos])
            self.play(Write(calc))
            self.play(ReplacementTransform(h_lbl[nodo.valor], bf_lbl[nodo.valor]))
            self.wait(0.5)
            self.play(FadeOut(calc))

        # La raíz es el caso interesante (-1), luego su hijo derecho (0)
        explicar(raiz)
        explicar(raiz.der)

        # Las hojas: 0 - 0 = 0, todas a la vez
        hojas = [n for n in arbol.logica.values() if n.izq is None and n.der is None]
        calc = Text("hoja: 0 - 0 = 0", font_size=32, color=YELLOW).next_to(
            titulo, DOWN, buff=0.4
        )
        self.play(Write(calc))
        self.play(
            LaggedStart(
                *[ReplacementTransform(h_lbl[n.valor], bf_lbl[n.valor]) for n in hojas],
                lag_ratio=0.3,
            )
        )
        self.play(FadeOut(calc))
        self.wait(1)

        # La regla del AVL
        regla = Text(
            "Árbol balanceado: todos los factores están en {-1, 0, 1}",
            font_size=30,
            color=GREEN,
        ).to_edge(DOWN, buff=1.0)
        self.play(FadeOut(formula))
        self.play(Write(regla))
        self.play(*[Indicate(e) for e in bf_lbl.values()])

        aviso = Text(
            "Si algún factor sale de ese rango, hay que rotar",
            font_size=28,
            color=ORANGE,
        ).next_to(regla, DOWN, buff=0.25)
        self.play(FadeIn(aviso, shift=UP * 0.2))
        self.wait(2)
