from django.shortcuts import render
from .models import Ciutat, Empleat, Gimnas, Treballador, Sala, Classe, Dia, Aliment, Dieta, Rutina, Client, Pagament, Quantificador_Dieta, Quantificador_Pes, Apat, Franja_Horaria, Quantitat_Aliment, Exercici, Entrenament, Entrenament_Diari, Entrenament_Personal, Ronda, Serie, Realitza_Exercici, Participacio


# Create your views here.

def ciutats(request):
    ciutats = Ciutat.objects.all()
    return render(request, 'ciutats.html', {'ciutats': ciutats})


def empleats(request):
    empleats = Empleat.objects.all()
    return render(request, 'empleats.html', {'empleats': empleats})


def gimnasos(request):
    gimnasos = Gimnas.objects.all()
    return render(request, 'gimnasos.html', {'gimnasos': gimnasos})


def treballadors(request):
    treballadors = Treballador.objects.all()
    return render(request, 'treballadors.html', {'treballadors': treballadors})


def sales(request):
    sales = Sala.objects.all()
    return render(request, 'sales.html', {'sales': sales})


def classes(request):
    classes = Classe.objects.all()
    return render(request, 'classes.html', {'classes': classes})


def dies(request):
    dies = Dia.objects.all()
    return render(request, 'dies.html', {'dies': dies})


def aliments(request):
    aliments = Aliment.objects.all()
    return render(request, 'aliments.html', {'aliments': aliments})


def dietes(request):
    dietes = Dieta.objects.all()
    return render(request, 'dietes.html', {'dietes': dietes})


def rutines(request):
    rutines = Rutina.objects.all()
    return render(request, 'rutines.html', {'rutines': rutines})


def clients(request):
    clients = Client.objects.all()
    return render(request, 'clients.html', {'clients': clients})


def pagaments(request):
    pagaments = Pagament.objects.all()
    return render(request, 'pagaments.html', {'pagaments': pagaments})


def quantificadors_dietes(request):
    quantificadors = Quantificador_Dieta.objects.all()
    return render(request, 'quantificadors_dietes.html', {'quantificadors': quantificadors})


def quantificadors_pesos(request):
    quantificadors = Quantificador_Pes.objects.all()
    return render(request, 'quantificadors_pesos.html', {'quantificadors': quantificadors})


def apats(request):
    apats = Apat.objects.all()
    return render(request, 'apats.html', {'apats': apats})


def franges_horaries(request):
    franges = Franja_Horaria.objects.all()
    return render(request, 'franges_horaries.html', {'franges': franges})


def quantitats_aliments(request):
    quantitats = Quantitat_Aliment.objects.all()
    return render(request, 'quantitats_aliments.html', {'quantitats': quantitats})


def exercicis(request):
    exercicis = Exercici.objects.all()
    return render(request, 'exercicis.html', {'exercicis': exercicis})


def entrenaments(request):
    entrenaments = Entrenament.objects.all()
    return render(request, 'entrenaments.html', {'entrenaments': entrenaments})


def entrenaments_diaris(request):
    entrenaments_diaris = Entrenament_Diari.objects.all()
    return render(request, 'entrenaments_diaris.html', {'entrenaments_diaris': entrenaments_diaris})


def entrenaments_personals(request):
    entrenaments_personals = Entrenament_Personal.objects.all()
    return render(request, 'entrenaments_personals.html', {'entrenaments_personals': entrenaments_personals})


def rondes(request):
    rondes = Ronda.objects.all()
    return render(request, 'rondes.html', {'rondes': rondes})


def series(request):
    series = Serie.objects.all()
    return render(request, 'series.html', {'series': series})


def realitza_exercicis(request):
    realitzacions = Realitza_Exercici.objects.all()
    return render(request, 'realitza_exercicis.html', {'realitzacions': realitzacions})


def participacions(request):
    participacions = Participacio.objects.all()
    return render(request, 'participacions.html', {'participacions': participacions})