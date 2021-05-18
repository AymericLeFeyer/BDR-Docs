# 2.1 Installation de PostgreSQL
## Question 2.1 

dans pg_hba.conf : 
la ligne : local   all postgres peer  : ça dit qu'on peut se co a la base seuleument avec l'user postgres

- psql -U postgres -d postgres. : psql: FATAL:  authentification peer échouée pour l'utilisateur « postgres » car on est dans l'environnement du root et non pas celui de  user postgres  .

DOnc si on se co en postgress ça marche bien

peer veut dire que le compte unix doit correspondre à l'utilisateur qui se connecte à la base (c'est pour ça que même root n'a pas le droit de se connecter en tant que postgres)


## Question 2.2

Plus de soucis car on a mis on a replacé les deux premiere ligne du fichier pg_hba.conf  par `local all all trust`.  

# 2.2 Création d’un rôle administrateur et de la base
## Question 2.3 


```
createuser --interactive --pwprompt
createdb -O admin labase;
psql -U admin -d labase;

REVOKE CONNECT ON DATABASE labase FROM PUBLIC; 
```

ou 
//PAS bon tout ça maus utile pour les autres 
QUAND ON SPECIFI LOGIN ET PASSWORD ON CREE UN USER EN MÊME TEMPS PAS JUSTE UN ROLE, CETTE QUERY C LA MEME QUE DE FAIRE CREATEUSER...
CREATE ROLE admin WITH LOGIN ENCRYPTED PASSWORD 'admin';

ALTER USER admin CREATEDB;

ALTER USER admin SUPERUSER;

CREATE DATABASE databasename

## Question 2.4

le proprio est posgresql car c'est lui qui a crée la base, les droits sont : postgres=UC/postgres+=UC/postgres 
uc = usage and create, ces droits veulent dire postgres a donné les droits UC a postgres et aussi à public

```
DROP SCHEMA public; 
CREATE SCHEMA music;
GRANT USAGE on schema music to PUBLIC;

```

droits mtn sont : admin=UC/admin+|=U/admin . Veut dire admin a donné UC à admin et a public

## Question 2.5

```
--parce qu'il ne sait pas dans quel schéma faire la requête.

set search_path to music;

schema script

-- pour voir l'ensemble des tables créee
\dt music.*
```
# 2.3 Autres rôles et privilèges

## Question 2.6

```
 create Role vendeurs;
 CREATE ROLE vendeur1 WITH LOGIN ENCRYPTED PASSWORD 'vendeur1' in Role vendeurs;
 CREATE ROLE vendeur2 WITH LOGIN ENCRYPTED PASSWORD 'vendeur2' in Role vendeurs;

 GRANT SELECT, INSERT, UPDATE, DELETE ON factures, lignes_factures, clients TO vendeurs;

GRANT CONNECT ON DATABASE labase TO vendeurs;

psql -U vendeur1 -d labase
 ```


## Question 2.7

psql -U admin -d labase

```
CREATE ROLE comptable WITH LOGIN ENCRYPTED PASSWORD 'comptable';
CREATE ROLE serveurweb WITH LOGIN ENCRYPTED PASSWORD 'serveurweb';

GRANT CONNECT ON DATABASE labase TO serveurweb;
GRANT CONNECT ON DATABASE labase TO comptable;

 GRANT SELECT ON music.factures, music.lignes_factures, music.employes TO comptable;

  GRANT SELECT ON music.albums, music.produits TO serveurweb;

```
# 2.4 Connexion « à distance »
## Question 2.9

```
systemctl stop postgresql
nano /etc/postgresql/11/main/postgresql.conf
systemctl start postgresql
```

- Que vous raconte psql ? 
psql: error: FATAL:  aucune entrée dans pg_hba.conf pour l'hôte « 10.0.2.2 », utilisateur « vendeur1 », base de données « labase », SSL actif FATAL:  aucune entrée dans pg_hba.conf pour l'hôte « 10.0.2.2 », utilisateur « vendeur1 », base de données « labase », SSL inactif
- Éditez pg_hba.conf pour que cela fonctionne
enfin.
de base postgresql n'accepte que les connections localhost donc 127.0.0.1 comme on peut voir avec ce ligne  : 
            # IPv4 local connections:  (=adress accepté en ipv4)
host    all             all             127.0.0.1/32            md5  

On peut juste rajouter le ligne suivante dans les adresses accepté : 

            # IPv4 local connections:  (=adress accepté en ipv4)
host    all             all             127.0.0.1/32            md5
host    all             all             10.0.2.2/32            md5

