import random

from disque import *


# TABLE

def table(descr, nb=10000):
    """Cette fonction génère une séquence de tuples décrits par le dictionnaire
    descr. Le dictionnaire associe à une clé une paire (k,l). La fonction
    génère nb dictionnaires de la manière suivante :
    - chaque clé de descr est une clé de ces dictionnaires
    - à chacune de ces clés x, ces dictionnaires associent un nombre tiré au hasard
      entre k et l lorsque la paire (k,l) est associée à x dans descr.
    NB : cette fonction requiert d'importer le module random.
    """
    for _ in range(nb):
        tuple_res = {}
        for a, (k, l) in descr.items():
            tuple_res[a] = random.randint(min(k, l), max(k, l))
        yield tuple_res


def exemple_table():
    """Exemple d'utilisation de la fonction table. Génère une table de 10 éléments
comportant les attributs 'a' et 'b' et les affiche en flux."""
    schema = {'a': (0, 10), 'b': (100, 100000)}
    for tuple_tbl in table(schema, nb=100):
        print(tuple_tbl)

# PROJECTION


def projection(table, champs):
    """
    Renvoie la table (sous forme de flux) obtenue à partir des tuples contenus
    dans ~table~ en n'y conservant que les attributs (les clés) qui sont
    contenus dans ~champs~.

    Renvoie une exception si un attribut de ~champs~ n'est pas un attribut des
    tuples de ~table~.
    """
    for t in table:
        tuple_res = {}
        for ch in champs:
            tuple_res[ch] = t[ch]
        yield tuple_res


def exemple_projection():
    """Exemple d'utilisation de la projection."""
    schema = {'a': (1, 10), 'b': (40, 100), 'c': (20, 30)}
    for tuple_res in projection(table(schema, nb=10),
                                ['a', 'c']):
        print(tuple_res)

# TRANSFORMATION


def transformation(table, f):
    """Renvoie un flux obtenu en appliquant ~f~ à chacun des tuples composant
~table~."""
    for tp in table:
        yield f(tp)


def exemple_transformation():
    schema = {'a': (1, 10), 'b': (40, 100), 'c': (20, 30)}
    def f(tp): return {'a': tp['a'], 'm': (tp['b']+tp['c'])//2}
    for tuple_res in transformation(table(schema, nb=100), f):
        print(tuple_res)

# PROJECTION 2


def projection2(table, champs):
    def f(tp):
        tuple_res = {}
        for ch in champs:
            tuple_res[ch] = tp[ch]
        return tuple_res
    return transformation(table, f)


# UNION


def union(t1, t2):
    for tp in t1:
        yield tp
    for tp in t2:
        yield tp


def exemple_union():
    """Exemple d'utilisation de la fonction union."""
    schema1 = {'a': (30, 100), 'b': (10, 50)}
    schema2 = {'a': (40, 50), 'n': (100, 200), 'm': (0, 10)}
    def f(tp): return {'a': tp['a']//2, 'b': (tp['m']*tp['m'])//4}
    for tp in union(table(schema1, nb=10),
                    transformation(table(schema2, nb=10), f)):
        print(tp)

# SELECTION


def selection(table, pred):
    for tp in table:
        if pred(tp):
            yield tp


def exemple_selection():
    for un_tuple in selection(table({'a': (30, 100), 'b': (10, 50)}, nb=10),
                              lambda tp: tp['a'] > 50 and tp['b'] < 45):
        print(un_tuple)


# SELECTION INDEX


def selection_index(fichier, idx, valeurs):
    """
    On suppose que ~fichier~ contient des tuples dont l'une des colonnes est
    indexée par ~idx~. La fonction renvoie le flux des tuples qui associe a la
    colonne indexée une valeur dans la séquence ~valeurs~.

    Attention : si un élément de ~valeurs~ n'est pas référencé dans ~idx~, on
    souhaite qu'il n'y ait pas d'erreur.
    """
    for v in valeurs:
        if v in idx:
            yield from trouve_sur_disque(fichier, idx[v])


def exemple_selection_index():
    schema = {'a': (0, 10), 'b': (1, 1000)}
    tbl = table(schema, nb=1000000)
    fichier = "tbl.table"
    mem_sur_disque(tbl, fichier)
    idx = index_fichier(fichier, 'a')
    for tp in selection_index(fichier, idx, range(2, 5)):
        print(tp)

# APPARIEMENT


def appariement(t1, t2):
    """Renvoie un tuple ayant pour clé les clés de ~t1~ et de ~t2~.

    Lorsqu'une clé n'apparaît que dans un tuple la valeur que lui associe ce
    tuple est celle associée à la clé dans le résultat.

    À une clé qui apparaît dans les deux tuples, le résultat associe la valeur
    que lui associe ~t2~.
    """
    tuple_res = t1.copy()
    for (k, v) in t2.items():
        tuple_res[k] = v
    return tuple_res

    # Shortcut depuis Python 3.5
    # return {**t1, **t2}

# PRODUIT CARTESIEN


def produit_cartesien(table1, table2):
    for tp1 in table1:
        for tp2 in table2:
            yield appariement(tp1, tp2)


def produit_cartesien_fichier(fichier1, fichier2):
    for tp1 in lire_sur_disque(fichier1):
        for tp2 in lire_sur_disque(fichier2):
            yield appariement(tp1, tp2)

# JOINTURE THETA


def jointure_theta(fichier1, fichier2, pred):
    return selection(produit_cartesien_fichier(fichier1, fichier2), pred)

# JOINTURE NATURELLE


def jointure_naturelle(fichier1, fichier2):
    for tp1 in lire_sur_disque(fichier1):
        for tp2 in lire_sur_disque(fichier2):
            ok = True
            for k in tp1:
                if k in tp2:
                    ok = ok and (tp1[k] == tp2[k])
            if ok:
                yield appariement(tp1, tp2)


def jointure_naturelle_mem(fichier1, fichier2):
    table2 = lire_sur_disque(fichier2)
    for tp1 in lire_sur_disque(fichier1):
        for tp2 in table2:
            ok = True
            for k in tp1:
                if k in tp2:
                    ok = ok and (tp1[k] == tp2[k])
            if ok:
                yield appariement(tp1, tp2)


exemple_selection_index()
