"""
Lógica pura del AVL (sin Manim). Es tu código C++ traducido casi línea por línea.
"""


class NodoAVL:
    def __init__(self, valor):
        self.valor = valor
        self.izq = None
        self.der = None
        self.altura = 1


def altura(nodo):
    return 0 if nodo is None else nodo.altura


def balance(nodo):
    return 0 if nodo is None else altura(nodo.izq) - altura(nodo.der)


def actualizar_altura(nodo):
    nodo.altura = 1 + max(altura(nodo.izq), altura(nodo.der))


def rotar_derecha(y):
    x = y.izq
    t2 = x.der
    x.der = y
    y.izq = t2
    actualizar_altura(y)
    actualizar_altura(x)
    return x


def rotar_izquierda(x):
    y = x.der
    t2 = y.izq
    y.izq = x
    x.der = t2
    actualizar_altura(x)
    actualizar_altura(y)
    return y


def insertar(nodo, valor):
    if nodo is None:
        return NodoAVL(valor)

    if valor < nodo.valor:
        nodo.izq = insertar(nodo.izq, valor)
    elif valor > nodo.valor:
        nodo.der = insertar(nodo.der, valor)
    else:
        return nodo

    actualizar_altura(nodo)
    b = balance(nodo)

    if b > 1 and valor < nodo.izq.valor:        # caso izquierda-izquierda
        return rotar_derecha(nodo)
    if b > 1 and valor > nodo.izq.valor:        # caso izquierda-derecha
        nodo.izq = rotar_izquierda(nodo.izq)
        return rotar_derecha(nodo)
    if b < -1 and valor > nodo.der.valor:       # caso derecha-derecha
        return rotar_izquierda(nodo)
    if b < -1 and valor < nodo.der.valor:       # caso derecha-izquierda
        nodo.der = rotar_derecha(nodo.der)
        return rotar_izquierda(nodo)

    return nodo
