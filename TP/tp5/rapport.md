# COURS :
## Ordonnancement O1
A = 500 => 400 => 200
B = 300 => 400 => 600

Pour T1 :
    A1 = 500 => 400
    B1 = 300 => 400

Pour T2 :
    A2 = 400=> 200
    B2 =400 => 600  
    
## Ordonnancement O2
A = 500 => 400 => 300  
B = 300 => 400 => 600

Pour T1 :
    A1 =500 => 400
    B1 =300 => 400
    
Pour T2
  A2 =500 => 300
  B2 =400 => 600

# TD

ATTENTION un verrou est mis en place jusque la fin de la trasaction qui l'a mis.
comme select for uppdate le verrou est supprimé une fois commit ou rollback
## EXERCICE 1 :
Après question 1.2:  
     a | b  
---+---  
 5 | 4  
 1 | 0  
 3 | 3  
 1 | 1  

### Q1.2
READ COMMITTED : session 1 voit les données modifiées par session 2 dès que celle-ci a fait un commit, pas avant.
Problème pour la session 1 : il fait plusieurs fois le même select dans sa transaction, mais n'obtient pas toujours le même résultat. Donc les transactions ne sont pas isolées.
les non répétable occure

### Q1.3 : Conclusion : cet ordonnancement n'est pas sériable
-- si on fait session1 avant session2, on supprime les lignes tq a=2
-- si on fait session2 avant session1 on supprime les lignes tq a=1
Ici, aucune instruction delete ne supprime de ligne.
Après la question 1.3: 
    a | b
---+---
 6 | 4
 2 | 0
 4 | 3
 2 | 1
 3 | 7
(5 rows)

### Q1.4 : dead lock lorsque session1 fait son second update.
session 1 pose un verrou sur 2 lignes (2,0) et (2,1) puis fais son update
session 2 pose un verrou sur 1 ligne (4,3) puis fais son update
session 2 attend pour poser un verrou sur des lignes bloquées par session1
session 1 attend pour poser un verrou sur une ligne bloquée par session 2 ==> dead lock
La session 1 est avortée (rollback) et la session 2 continue.

Après question 1.4 :
 a | b  
---+---  
 6 | 4  
 3 | 7  
 4 | 2  
 3 | 0  
 3 | 1  
 
 ### Q1.5
 Le select for update permet d'empêcher les autres transactions de modifier les lignes lues par le select donc verrou ligne et attends le commit pour se dévérouiller
 
 Après question 1.5:   
      a | b  
---+----  
 6 |  4    
 4 |  2  
 5 |  6  
 5 |  1  
 5 | 10  
 
 ### Q1.6
 La session 2 est avortée parce qu'elle veut écrire des lignes qui ont été modifiées par session1.
 C'est pour éviter un ordonnancement comme celui de la question 1.3  
 Après question 1.6 :  
  a | b  
---+----  
 4 |  2  
 5 |  6  
 5 |  1  
 5 | 10  
 5 |  4  
 
### Q1.7 :
     Comme la session 1 est annulée (rollback), il n'y a plus de conflit avec la session 2.
     Donc la session 2 termine normalement sans être avortée (c'est la différence avec 1.6)
     
### Q1.8 :
    ici on a résolu le problème des lectures non reproductibles.
    La session 2 fait plusieurs fois le même select et obtient toujours le même résultat, indépendamment de la session 1. La session 2 est bien isolée tout au long de son exécution (pas comme Q1.2)
    
## EXERCICE 2: 

contraine vérifié en couurs de transaction

update Ecrivain set pid = pid+1, influence=influence+1;
ERROR:  duplicate key value violates unique constraint "ecrivain_pkey"
DETAIL:  Key (pid)=(202) already exists.

### 1ère solution : 
- on diffère la contrainte de clé étrangère
- on modifie les lignes (colonnes pid et influence) par ordre décroissant de pid. Comme la contrainte de clé étrangère est vérifiée à la fin de la transaction, on n'a pas d'erreur.

```
alter table Ecrivain
alter constraint ecrivain_influence_fkey deferrable initially deferred;

DO $$
BEGIN
UPDATE ecrivain 
  SET pid = ecrivain.pid +1, influence = influence +1
 FROM (SELECT pid 
         FROM ecrivain 
        ORDER BY pid desc
      ) AS t1 
WHERE ecrivain.pid=t1.pid;
END ;
$$ LANGUAGE plpgsql;
```
### 2ème solution :
- on met un "on update cascade" sur la contrainte de clé étrangère,
- on modifie les lignes (colonnes pid uniquement) par ordre décroissant de pid. Les clé étrangères sont modifiées automatiquement en fonction des modifications de la clé primaires (pas dans le même ordre)

```
-- pas obligatoire car on la supprime après
alter table Ecrivain alter constraint ecrivain_influence_fkey not deferrable initially immediate;

alter table Ecrivain drop constraint ecrivain_influence_fkey;

alter table Ecrivain add constraint ecrivain_influence_fkey
   foreign key (influence)
   references ecrivain(pid)
   on update cascade;

DO $$
BEGIN
UPDATE ecrivain 
  SET pid = ecrivain.pid +1
 FROM (SELECT pid 
         FROM ecrivain 
        ORDER BY pid desc
      ) AS t1 
WHERE ecrivain.pid=t1.pid;
END ;
$$ LANGUAGE plpgsql;
```

-- pour ajuoter une foreig key
alter table Ecrivain
add constraint ecrivain_influence_fkey foreign key(influence) REFERENCES ecrivain(pid);
