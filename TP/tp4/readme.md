# Exercice 1

## 1.1

```sql
SELECT ca.ncompte, count(*) as proprio, SUM(emp.montant) as total_emprunt
FROM banque.compte_client as ca, banque.emprunt as emp
WHERE ca.ncompte = emp.ncompte
GROUP BY ca.ncompte
```

## 1.3

```sql
UPDATE banque.compte com
SET nb_proprietaires = (
	SELECT count(*)
	FROM banque.compte_client as cc
	WHERE cc.ncompte = com.ncompte
	GROUP BY cc.ncompte
),
montant_emprunts = (
	SELECT SUM(montant)
	FROM banque.emprunt as emp
	WHERE emp.ncompte = com.ncompte
	GROUP BY emp.ncompte
)
```
## 1.4

### Function

```sql
DROP FUNCTION IF EXISTS banque."trigger_compte_client";

CREATE FUNCTION banque."trigger_compte_client"()
    RETURNS trigger AS $$
	DECLARE
	clienttmp record;
	comptetmp record;
 	BEGIN
	SELECT * INTO clienttmp FROM banque.client WHERE ncli = NEW.ncli;
	IF NOT FOUND THEN
		raise notice 'CLIENT ABSENT';
	END IF;
	
    SELECT * INTO comptetmp
	FROM banque.compte as Compte
	WHERE Compte.ncompte = NEW.ncompte;
	IF FOUND THEN
		raise notice 'YOUPI';
		UPDATE banque.compte SET nb_proprietaires = nb_proprietaires + 1 WHERE ncompte = comptetmp.ncompte;
	END IF;
	
	return NEW;
	END;$$
	LANGUAGE 'plpgsql';
```

### Trigger

```sql
CREATE TRIGGER after_insert_delete_update_compte
    AFTER INSERT or UPDATE or DELETE
    ON banque.compte_client
    FOR EACH ROW
    EXECUTE PROCEDURE banque."trigger_compte_client"();
```

# Exercice 2

## 2.1

```sql
CREATE TABLE music.facture_virtuel (fac_num integer, fac_date integer, fac_montant integer) PARTITION BY RANGE(fac_date);
```

## 2.2

```sql

```

## 2.3

```sql

```

## 2.4

```sql

```

## 2.5

```sql

```

## 2.6

```sql

```