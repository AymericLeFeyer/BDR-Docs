# Cours 3

Into c'est juste qu'on on est sur de récupérer une seul valeur.  
Sinon on utilise une boucle avec into

## Question 1.4
---------------
-- le schéma définit dans COMPTE la colonne : nag integer references agence
-- Comme une clé étrangère peut être NULL, un compte peut être géré par aucune agence
-- il faut simplement rajouter un NOT NULL
Alter table Compte alter column nag set not null;
## Question 1.5

PAS faire de trigger ca ça fonctione pas vu qu'on va essayer de delete toutes les row directement donc l'exception se déclenchera toujours 
```
CREATE or REPLACE FUNCTION verif_compte_belongs_to_client() RETURNS Trigger AS $$
	declare nb_cli integer;
    BEGIN
   	select count(*) into nb_cli from banque.compte_client where ncompte = old.ncompte;
	raise notice 'nb client : %' , nb_cli;
	if nb_cli = 1 then
	raise Exception 'le compte doit avoir au moins un client ';
	end if;

	return OLD;
    END;
$$ LANGUAGE plpgsql;


delete from banque.compte_client where ncompte = 145;
```

On fait une procédure de ce style :  

```
CREATE or REPLACE FUNCTION delete_Compte(idCompte integer, idCli integer) RETURNS boolean AS $$
	declare nb_cli integer;
    BEGIN
   	select count(*) into nb_cli from banque.compte_client where ncompte = idCompte;
	raise notice 'nb client : %' , nb_cli;
	if nb_cli = 1 then
	raise Exception 'le compte doit avoir au moins un client ';
	end if;
	delete from banque.compte_client where ncompte = idCompte and ncli =idCli;
	return true;
    END;
$$ LANGUAGE plpgsql;


select delete_Compte(145, 10);
```