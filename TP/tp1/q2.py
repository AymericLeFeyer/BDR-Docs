# Question 2.2

def flux_carres(n):
    """Flux des carrés de 0 à n-1"""
    for i in range(n):
        yield i*i


def somme_carres(n):
    """Calcule la somme des carrés de 0 à n-1."""
    res = 0
    for i in flux_carres(n):
        res += i
    return res


def somme_carres_bis(n):
    return sum([i*i for i in range(n)])


def somme_carres_ter(n):
    res = 0
    for k in (i*i for i in range(n)):
        res += k
    return k


def somme_carres_quad(n):
    return sum(i*i for i in range(n))


print(somme_carres_bis(5))
