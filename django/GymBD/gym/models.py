from django.db import models

# Create your models here.

class Ciutat(models.Model):
    nom = models.CharField(max_length=50)
    codi_postal = models.IntegerField()


class Empleat(models.Model):
    dni = models.CharField(max_length=9)
    tipus = models.CharField(max_length=20)
    sou = models.DecimalField(max_digits=7, decimal_places=2)
    nom = models.CharField(max_length=20)
    cognoms = models.CharField(max_length=40)
    compte_bancari = models.CharField(max_length=24)
    telefon = models.IntegerField()
    naixement = models.DateField()
    sexe = models.CharField(max_length=1)
    horaris = models.CharField(max_length=50)
    ciutat = models.ForeignKey(Ciutat, on_delete=models.RESTRICT)


class Gimnas(models.Model):
    nom = models.CharField(max_length=50)
    adreca = models.CharField(max_length=100)
    telefon = models.IntegerField()
    correu_electronic = models.EmailField()


class Treballador(models.Model):
    dni = models.CharField(max_length=9)
    nom = models.CharField(max_length=20)
    cognoms = models.CharField(max_length=40)
    telefon = models.IntegerField()
    adreca = models.CharField(max_length=100)
    naixement = models.DateField()
    sexe = models.CharField(max_length=1)
    sou = models.DecimalField(max_digits=7, decimal_places=2)
    gimnas = models.ForeignKey(Gimnas, on_delete=models.CASCADE)


class Sala(models.Model):
    nom = models.CharField(max_length=50)
    capacitat = models.IntegerField()
    gimnas = models.ForeignKey(Gimnas, on_delete=models.CASCADE)


class Classe(models.Model):
    nom = models.CharField(max_length=50)
    descripcio = models.TextField()
    gimnas = models.ForeignKey(Gimnas, on_delete=models.CASCADE)


class Dia(models.Model):
    nom = models.CharField(max_length=10)


class Aliment(models.Model):
    nom = models.CharField(max_length=50)

class Client(models.Model):
    nom = models.CharField(max_length=50)
    cognoms = models.CharField(max_length=50)
    data_naixement = models.DateField()
    telefon = models.CharField(max_length=15)
    correu_electronic = models.EmailField()
    gimnas = models.ForeignKey(Gimnas, on_delete=models.CASCADE)

class Quantificador_Dieta(models.Model):
    nom = models.CharField(max_length=50)


class Dieta(models.Model):
    nom = models.CharField(max_length=50)
    descripcio = models.TextField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    quantificadors = models.ManyToManyField(Quantificador_Dieta, through='Quantitat_Aliment')

class Exercici(models.Model):
    nom = models.CharField(max_length=50)
    descripcio = models.TextField()


class Rutina(models.Model):
    nom = models.CharField(max_length=50)
    descripcio = models.TextField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    exercicis = models.ManyToManyField(Exercici, through='Realitza_Exercici')


class Pagament(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    import_total = models.DecimalField(max_digits=7, decimal_places=2)
    data_pagament = models.DateField()


class Quantificador_Pes(models.Model):
    nom = models.CharField(max_length=50)


class Apat(models.Model):
    nom = models.CharField(max_length=50)
    dieta = models.ForeignKey(Dieta, on_delete=models.CASCADE)
    quantificadors = models.ManyToManyField(Quantificador_Pes, through='Quantitat_Aliment')


class Franja_Horaria(models.Model):
    hora_inici = models.TimeField()
    hora_final = models.TimeField()


class Quantitat_Aliment(models.Model):
    apat = models.ForeignKey(Apat, on_delete=models.CASCADE)
    aliment = models.ForeignKey(Aliment, on_delete=models.CASCADE)
    quantificador = models.ForeignKey(Quantificador_Dieta, on_delete=models.CASCADE)
    quantitat = models.DecimalField(max_digits=7, decimal_places=2)


class Entrenament(models.Model):
    nom = models.CharField(max_length=50)
    descripcio = models.TextField()
    rutina = models.ForeignKey(Rutina, on_delete=models.CASCADE)


class Entrenament_Diari(models.Model):
    data = models.DateField()
    dia = models.ForeignKey(Dia, on_delete=models.CASCADE)
    entrenament = models.ForeignKey(Entrenament, on_delete=models.CASCADE)


class Entrenament_Personal(models.Model):
    entrenador = models.ForeignKey(Treballador, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)


class Ronda(models.Model):
    nom = models.CharField(max_length=50)
    exercici = models.ForeignKey(Exercici, on_delete=models.CASCADE)


class Serie(models.Model):
    numero = models.IntegerField()
    ronda = models.ForeignKey(Ronda, on_delete=models.CASCADE)
    exercici = models.ForeignKey(Exercici, on_delete=models.CASCADE)


class Realitza_Exercici(models.Model):
    rutina = models.ForeignKey(Rutina, on_delete=models.CASCADE)
    exercici = models.ForeignKey(Exercici, on_delete=models.CASCADE)
    serie = models.ForeignKey(Serie, on_delete=models.CASCADE)
    quantificador = models.ForeignKey(Quantificador_Pes, on_delete=models.CASCADE)
    repeticions = models.IntegerField()


class Participacio(models.Model):
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    data_hora = models.DateTimeField()

