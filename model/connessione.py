# creo la classe connessione che rappresenta un arco del grafo (sentiero tra due rifugi) (come lab 11)

import datetime #importo pacchetto data

from dataclasses import dataclass

from model.rifugio import Rifugio


@dataclass
class Connessione:
    id: int
    id_rifugio1: Rifugio
    id_rifugio2: Rifugio
    distanza: float # + corretto che int
    difficolta: str
    durata: datetime.time #per l'ora
    anno: int
    #fattore_difficolta : float #definito del dao

    def __eq__(self, other):
        return isinstance(other, Connessione) and self.id == other.id

    def __str__(self):
        return f"id: {self.id}, Connessione {self.id_rifugio1} - {self.id_rifugio2}, distanza: {self.distanza}, difficolta: {self.fattore_difficolta}, durata: {self.durata}, anno: {self.anno}"


    #mi calcolo il peso
    def calcolo_peso(self):
        fattori = {"facile": 1.0, "media": 1.5, "difficile": 2.0}
        fattore = fattori.get(self.difficolta.lower(), 1.0) #mi restituiva None altrimenti

        if self.distanza is not None:
            return float(self.distanza) * fattore
        return 0.0 #se manca la distanza restituisco 0

    def __hash__(self):
        return hash(self.id)