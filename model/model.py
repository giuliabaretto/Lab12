import networkx as nx
from database.dao import DAO
from model.connessione import Connessione
from model.rifugio import Rifugio  # per la id map

class Model:
    def __init__(self):
        """Definire le strutture dati utili"""
        self.rifugi = []
        self.G = nx.Graph()
        self._rifugi = DAO.read_rifugio() #tutti i rifugi
        self._rifugi_dict = {rifugio.id: rifugio for rifugio in self._rifugi} # id map -> da id a oggetto rifugio
        # inizializzo minimo e massimo dei pesi degli archi
        min_peso = 0.0
        max_peso = 0.0
        self._current_soglia = 0.0

    def build_weighted_graph(self, anno: int):
        """
        Costruisce il grafo pesato dei rifugi considerando solo le connessioni con campo `anno` <= year passato
        come argomento.
        Il peso del grafo è dato dal prodotto "distanza * fattore_difficolta"
        """
        self.G.clear()

        #archi
        connessioni = DAO.read_connessioni_per_anno(self._rifugi_dict, anno)
        self._pesi = []

        if not connessioni:
            return

        for connessione in connessioni:
            # calcolo_peso() implementato nella classe Connessione
            peso = connessione.calcolo_peso()
            self._pesi.append(peso)
            # aggiungo un arco tra i due rifugi, gli Oggetti Rifugio sono nodi
            self.G.add_edge(connessione.id_rifugio1, connessione.id_rifugio2, weight=peso)
            # mi definisce in automatico anche i nodi


    def get_edges_weight_min_max(self):
        """
        Restituisce min e max peso degli archi nel grafo
        :return: il peso minimo degli archi nel grafo
        :return: il peso massimo degli archi nel grafo
        """
        min_peso = min(self._pesi)
        max_peso = max(self._pesi)
        return min_peso, max_peso

    def count_edges_by_threshold(self, soglia):
        """
        Conta il numero di archi con peso < soglia e > soglia
        :param soglia: soglia da considerare nel conteggio degli archi
        :return minori: archi con peso < soglia
        :return maggiori: archi con peso > soglia
        """
        minori = 0
        maggiori = 0
        self._current_soglia = soglia  #soglia memorizzata per l'Esercizio 2

        for u, v, data in self.G.edges(data=True):
            peso = data['weight']
            if peso < soglia:
                minori += 1
            elif peso > soglia:
                maggiori += 1
            #non prendo i pesi esattamente uguali alla soglia

        return minori, maggiori


    """Implementare la parte di ricerca del cammino minimo"""
    #filtro il grafo in base alla soglia inserita dall'utente -> creo un sottografo con solo gli archi di peso > self._current_soglia

    #  ES 2

    def sottografo_soglia_minima(self):
        """ Il percorso deve essere composto solo da archi con peso maggiore di una soglia S. """

        soglia = self._current_soglia

        nuovo_grafo = nx.Graph()

        # aggiungo solo gli archi di peso > self._current_soglia
        for u, v, data in self.G.edges(data=True): #u e v sono i rifugi collegati al sentiero
            if data['weight'] > soglia: # data è un dizionario che contiene gli attributi dell'arco ovvero weight (distanza x fattore_difficolta)
                nuovo_grafo.add_edge(u, v, weight=data['weight'])

        return nuovo_grafo

    # metodo networkx
    def cammino_minimo_nx(self):
        """
        Il percorso deve contenere almeno 2 archi (quindi almeno 3 nodi, per evitare soluzioni banali di un solo arco).
        Al termine della ricerca, deve essere stampata la sequenza di rifugi che costituisce il cammino trovato,
        ordinata dal nodo di partenza al nodo finale.
        Se non esiste alcun cammino valido che rispetti questi vincoli, deve essere restituita una lista vuota.

        Ricerco il cammino più breve (ovvero la somma dei pesi minima) composto da:
        1. Archi con peso > soglia (self._current_soglia).
        2. Almeno 2 archi (3 nodi).
        Testare entrambe le tecniche: NetworkX e Ricorsiva
        """
        nuovo_grafo = self.sottografo_soglia_minima()

        # il cammino deve vere almeno 2 archi / 3 nodi
        if nuovo_grafo.number_of_nodes() < 3 or nuovo_grafo.number_of_edges() < 2:
            return [], 0  #termino e restituisco lista vuota

        cammino = []
        somma_pesi_minima = float('inf')

        nodes = list(nuovo_grafo.nodes)

        # devo trovare il cammino migliore su qualunque coppia di rifugi (sorgente, destinazione)
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                nodo_partenza = nodes[i]
                nodo_destinazione = nodes[j]

                # metodo NetworkX (algoritmo di Dijkstra)
                try:
                    # shortest_path per trovare il cammino minimo in grafi pesati
                    current_path = nx.shortest_path(nuovo_grafo, source=nodo_partenza, target=nodo_destinazione, weight='weight')
                    current_total_weight = nx.shortest_path_length(nuovo_grafo, source=nodo_partenza, target=nodo_destinazione, weight='weight')

                    # verifico che abbia almeno 2 archi (3 nodi)
                    if len(current_path) >= 3:

                        # Aggiornamento del cammino migliore
                        if current_total_weight < somma_pesi_minima:
                            somma_pesi_minima = current_total_weight
                            cammino = current_path

                except nx.NetworkXNoPath:
                    continue  # nessun cammino valido trovato per questa coppia

        # trasformo da nodi ad archi con peso
        path_archi_con_peso = []

        if cammino:
            for k in range(len(cammino) - 1):
                u = cammino[k]
                v = cammino[k + 1]
                # recupero il peso dell'arco dal sottografo
                peso_arco = nuovo_grafo[u][v]['weight']
                path_archi_con_peso.append((u, v, peso_arco))

            # ordine  richiesto dal ciclo for nel controller
            return path_archi_con_peso, somma_pesi_minima

        return [], 0.0





    #metodo ricorsivo
    def cammino_minimo_ricorsione(self):

        self._cammino = []
        self._somma_pesi_minima = float('inf')

        #considero solo i nodi che hanno almeno un arco > soglia
        nodi_validi = list(self.G.nodes)

        for nodo_partenza in nodi_validi:
            #ricorsione da ogni rifugio
            self.ricorsione(nodo_partenza, 0.0, [nodo_partenza]) #0.0 è il costo iniziale, cioè il peso accumulato finora, ovvero 0.0 in partenza; [partenza] è la lista che memorizza il persorso fatto

        # trasformo la lista di nodi in lista di tuple arco + peso)
        if self._cammino:
            risultato = []
            for i in range(len(self._cammino) - 1):
                u = self._cammino[i]
                v = self._cammino[i + 1]
                peso = self.G[u][v]['weight']

                # I nodi u e v sono oggetti Rifugio
                risultato.append((u, v, peso))

            # il risultato è del tipo: [(RifugioA, RifugioB, Peso) ...]
            return risultato, self._somma_pesi_minima
        else:
            return [], 0.0

    def ricorsione(self, nodo_corrente, costo_corrente, sequenza_parziale):
        # taglio i rami inutili
        if costo_corrente >= self._somma_pesi_minima:
            return
        #se condizioni sono verificate -> aggiorno
        if len(sequenza_parziale) >= 3:
            if costo_corrente < self._somma_pesi_minima:
                self._somma_pesi_minima = costo_corrente
                self._cammino = list(sequenza_parziale)
        #ciclo sui vicini
        for vicino in self.G.neighbors(nodo_corrente):
            #non ripasso sullo stesso rifugio
            if vicino not in sequenza_parziale:
                peso = self.G[nodo_corrente][vicino]['weight']
                #solo gli archi con peso > soglia
                if peso > self._current_soglia:
                    #ricorsione
                    sequenza_parziale.append(vicino)
                    self._ricorsione(vicino, costo_corrente+peso, sequenza_parziale)
                    #backtracking
                    sequenza_parziale.pop()
        return