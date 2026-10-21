# id-validators

Checksum validators for identifiers that turn up on every invoice and customer form: Polish NIP, REGON and PESEL (with the encoded birth date and century), IBAN (length per country and the modulo-97 rule) and EAN-8/13. Pure Python standard library, a command line and a CSV mode that lists the invalid lines.

```
python -m idval nip 526-025-02-74
python -m idval --csv customers.csv --column nip --kind nip
python -m pytest
```

Built with AI coding assistance. Tests use well-known published example numbers and every checksum is also broken on purpose to see it rejected.
