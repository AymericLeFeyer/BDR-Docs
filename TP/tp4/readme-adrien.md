
# Exercie 1

## Question 1.1

```
select ncompte,
       (select sum(montant) from emprunt e where e.ncompte = c.ncompte) as montant_emprunts,
       count(ncli) as nb_proprietaires
from compte_client c
group by ncompte;
```

by`me pas bon non plus 

```
select cc.ncompte,  count(ncli) as nb_proprio, coalesce(sum(e.montant),0) as montants 
from banque.compte_client as cc join banque.emprunt as e using(ncompte) 
where e.ncompte = cc.ncompte group by ncompte 
```

presque bon
```
(select distinct c.ncompte, count(ncli) as nb_proprio from banque.compte_client c  group by c.ncompte) union all 
(select distinct ncompte,
    sum(montant) as montants from banque.emprunt group by ncompte);
```


# Question 1.2

```
Alter table compte add nb_proprietaires integer not null default 0;
alter table compte add montant_emprunts float not null default 0
```

## Question 1.3

update compte set nb_proprietaires = (select count(ncli) from compte_client c where c.ncompte=compte.ncompte), 
                montant_emprunts = (select coalesce(sum(montant),0) from emprunt e where e.ncompte=compte.ncompte)


## Question 1.4


### trigger sur la table compte_client pour le nombre de proprio  
--TRIGGER ONLY ONCE
```
CREATE TRIGGER calcul_nb_proprio
BEFORE update OR insert or delete
ON banque.compte_client FOR EACH ROW
EXECUTE FUNCTION calcul_nb_proprio();
```

```
CREATE OR REPLACE FUNCTION calcul_nb_proprio()
RETURNS TRIGGER AS $$
BEGIN
	if (TG_OP='INSERT' or TG_OP='UPDATE') then 
		update banque.compte  set nb_proprietaires = nb_proprietaires + 1 where ncompte = new.ncompte;
	end if;
	if (TG_OP='UPDATE' or TG_OP='DELETE' )then 
		update banque.compte  set nb_proprietaires = nb_proprietaires + -1 where ncompte = old.ncompte;
	end if;
	
	
	if TG_OP = 'DELETE'
	then 
		return old;
	else return new;
	end if;
END; $$
LANGUAGE 'plpgsql' ;
```

### trigger sur la table emprunt pour montant_emprunts

--TRIGGER ONLY ONCE
```
--CREATE TRIGGER update_nb_montants
--BEFORE update OR insert or delete
--ON banque.emprunt FOR EACH ROW
--EXECUTE FUNCTION update_nb_montants() ;
```

```
CREATE OR REPLACE FUNCTION update_nb_montants()
RETURNS TRIGGER AS $$
BEGIN
IF (tg_op = 'INSERT' or tg_op = 'UPDATE') THEN
update banque.compte set montant_emprunts = montant_emprunts + new.montant where banque.compte.ncompte = new.ncompte;
raise notice 'insert old : %', new.ncompte;
END IF ;

IF (tg_op = 'UPDATE' or tg_op = 'DELETE') THEN
update banque.compte set montant_emprunts = montant_emprunts - old.montant where banque.compte.ncompte = new.ncompte;
raise notice 'delete old : %', old.ncompte;
END IF ;

raise notice 'delete old : %', old.ncompte;

if tg_op = 'DELETE' then
	return old;
end if;

return new;

END ;$$
LANGUAGE 'plpgsql' ;
```



## Question 1.5

```
DROP TRIGGER verif_compte ON banque.emprunt

alter table banque.compte ADD CONSTRAINT verif_compte
CHECK (typecpte = 'cpte courant' or compte.nb_proprietaires <= 1
);

insert into banque.compte_client values(176,10)

```

## Question 1.6

```
DROP TRIGGER verif_emprunt ON banque.emprunt

alter table banque.compte ADD CONSTRAINT verif_emprunt
CHECK (montant_emprunts <= 3*solde
);

insert into banque.emprunt values(15,145,10)

```

# EXERCICE 2

CREATE TABLE tbl (fac_num Numeric(5),  fac_date  Date not null, fac_montant  Numeric(6,2) default 0.0 not null) PARTITION BY RANGE(fac_date);  

Cela signifie que la table tbl est en quelque sorte virtuelle et est composée de plusieurs tables
qui la découpent en fonction des valeurs de la colonne col.

## Question 2.1 

```
-- pas besoin
--alter table music.facture drop  CONSTRAINT facture_pkey Cascade ;
```
if faut changer le définition dans le schéma 
```
create table facture(
  fac_num Numeric(5),
  fac_date Date not null,
  fac_montant Numeric(6,2) default 0.0 not null
) PARTITION BY RANGE(fac_date);
```

## Question 2.2 : Afin de créer les tables qui composent la partition de facture, nous allons

```
CREATE TABLE tbl_y2020m01 PARTITION OF tbl
FOR VALUES FROM ('2020-01-01') TO ('2020-02-01');

--si nécessaire
--drop TABLE tbl_y2020m1;
```

```
CREATE OR REPLACE FUNCTION create_partition(date Date )
RETURNS boolean AS $$
declare month varchar;
declare year varchar;
declare ltableName varchar;
--declare record record;
BEGIN

month:=to_char(date, 'MM');
year:=to_char(date, 'YYYY');
ltableName:=('facturel_y' || year || 'm' || month);
 raise notice 'tableName : % ',ltableName;
 
-- select relname FROM pg_class into record WHERE relname=ltableName ;

if Exists(select relname FROM pg_class  WHERE relname=ltableName) then 
  raise notice 'date : % %',month, year;
	return true;
end if;	
EXECUTE 'CREATE TABLE ' ||  ltableName || ' PARTITION OF music.facture
FOR VALUES FROM (' || chr(39) ||to_char(date_trunc('month',date),'YYYY-mm-dd') || chr(39) || ') TO (' || chr(39) || to_char(date_trunc('month', date + interval '1' month),'YYYY-mm-dd') || chr(39) || ')';
EXECUTE 'CREATE INDEX ON ' || ltableName || ' (fac_date);'; 
raise notice 'table crée : %',ltableName;
return false;
END; $$
LANGUAGE 'plpgsql' ;


select create_partition('2020-01-01');
```


## Question 2.3

```
CREATE OR REPLACE FUNCTION generate_partition(date Date )
RETURNS boolean AS $$

declare currentYear varchar;
declare newYear varchar;
declare record varchar;

BEGIN

currentYear := date_trunc('year',date);
newYear :=date_trunc('month', date + interval '11' month);
raise notice 'data %  , %', currentYear,newYear;
 
for record in SELECT * FROM generate_series(currentYear::DATE, newYear::DATE, '1 month') loop
perform create_partition(record::DATE);
raise notice 'var : %',record;
end loop;


return true;
END; $$
LANGUAGE 'plpgsql' ;

select generate_partition('2020-01-15');
```


## Question 2.4

```
CREATE OR REPLACE FUNCTION create_partition(date Date )
RETURNS boolean AS $$
declare month varchar;
declare year varchar;
declare ltableName varchar;
--declare record record;
BEGIN

month:=to_char(date, 'MM');
year:=to_char(date, 'YYYY');
ltableName:=('facturel_y' || year || 'm' || month);
 raise notice 'tableName : % ',ltableName;
 
-- select relname FROM pg_class into record WHERE relname=ltableName ;

if Exists(select relname FROM pg_class  WHERE relname=ltableName) then 
  raise notice 'date : % %',month, year;
	return true;
end if;	
EXECUTE 'CREATE TABLE ' ||  ltableName || '(
  fac_num Numeric(5) constraint facture_pkey primary key,
  fac_date Date not null,
  fac_montant Numeric(6,2) default 0.0 not null
);';

EXECUTE 'ALTER TABLE music.facture ATTACH PARTITION ' || ltableName || ' 
FOR VALUES FROM (' || chr(39) ||to_char(date_trunc('month',date),'YYYY-mm-dd') || chr(39) || ') TO (' || chr(39) || to_char(date_trunc('month', date + interval '1' month),'YYYY-mm-dd') || chr(39) || ')';
EXECUTE 'CREATE INDEX ON ' || ltableName || ' (fac_date);'; 
raise notice 'table crée : %',ltableName;
return false;
END; $$
LANGUAGE 'plpgsql' ;

select create_partition('2021-01-15');
```

## Question 2.5 

```
CREATE OR REPLACE FUNCTION delete_old_partition()
RETURNS boolean AS $$
declare exist boolean;
declare nameee varchar;
declare arraye text[];
declare datee date;

BEGIN
 
for nameee in SELECT inhrelid::regclass AS child -- optionally cast to text
FROM   pg_catalog.pg_inherits
WHERE  inhparent = 'music.facture'::regclass loop
select relispartition from pg_class into exist where relname=nameee;
if exist then
	arraye :=regexp_split_to_array(replace(nameee,'facturel_y',''), E'm');
 	datee:= arraye[1] || '-' ||  arraye[2] ||  '-' || '01';
 	raise notice 'name : %', nameee;
	if datee::DATE <= date_trunc('month', CURRENT_DATE - interval '6 months') then
		EXECUTE 'ALTER TABLE music.facture DETACH PARTITION ' || nameee ;
	end if;
end if;
end loop;


return true;
END; $$
LANGUAGE 'plpgsql' ;

select delete_old_partition();
```
## Question 2.6

Il faut lancer des procédure stockés tout les mois avec un JOB SCHEDULER comme *pgAgent* 