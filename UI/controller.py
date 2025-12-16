import flet as ft
from UI.view import View
from model.model import Model
import networkx as nx



class Controller:
    def __init__(self, view: View, model: Model):
        self._view = view
        self._model = model

    def handle_grafo(self, e):
        """Callback per il pulsante 'Crea Grafo'."""
        try:
            anno = int(self._view.txt_anno.value)
        except:
            self._view.show_alert("Inserisci un numero valido per l'anno.")
            return
        if anno < 1950 or anno > 2024:
            self._view.show_alert("Anno fuori intervallo (1950-2024).")
            return

        self._model.build_weighted_graph(anno)
        self._view.lista_visualizzazione_1.controls.clear()
        self._view.lista_visualizzazione_1.controls.append(
            ft.Text(f"Grafo calcolato: {self._model.G.number_of_nodes()} nodi, {self._model.G.number_of_edges()} archi")
        )
        min_p, max_p = self._model.get_edges_weight_min_max()
        self._view.lista_visualizzazione_1.controls.append(ft.Text(f"Peso min: {min_p:.2f}, Peso max: {max_p:.2f}"))
        self._view.page.update()

    def handle_conta_archi(self, e):
        """Callback per il pulsante 'Conta Archi'."""
        try:
            soglia = float(self._view.txt_soglia.value)
        except:
            self._view.show_alert("Inserisci un numero valido per la soglia.")
            return

        min_p, max_p = self._model.get_edges_weight_min_max()
        if soglia < min_p or soglia > max_p:
            self._view.show_alert(f"Soglia fuori range ({min_p:.2f}-{max_p:.2f})")
            return

        minori, maggiori = self._model.count_edges_by_threshold(soglia)
        self._view.lista_visualizzazione_2.controls.clear()
        self._view.lista_visualizzazione_2.controls.append(ft.Text(f"Archi < {soglia}: {minori}, Archi > {soglia}: {maggiori}"))
        self._view.page.update()

    """Implementare la parte di ricerca del cammino minimo"""

    def handle_cammino_minimo(self, e):
        # per il pulsante "cammino minimo"

        #controllo grafo e soglia
        if not self._model.G or nx.number_of_nodes(self._model.G) == 0:
            self._view.show_alert("Crea prima il grafico")
            return

        soglia = float(self._view.txt_soglia.value)

        if soglia is None:
            self._view.show_alert("Inserisci un soglia valida")
            return

        cammino, peso_totale = self._model.cammino_minimo_nx() #uso metodo networkx (potrei usare anche quello ricorsivo)
        #spaccattamento : risultato era una tupla

        self._view.lista_visualizzazione_3.controls.clear()

        if cammino:
            self._view.lista_visualizzazione_3.controls.append(ft.Text(f"Cammino minimo: {peso_totale:.2f}"))
            # stampo sequenza di archi del cammino
            for u, v, peso_arco in cammino:
                # utilizzo gli attributi di u e v che sono oggetti rifugio
                self._view.lista_visualizzazione_3.controls.append(ft.Text(f"{u.nome} -> {v.nome} [peso: {peso_arco:.2f}]"))
        else:
            self._view.lista_visualizzazione_3.controls.append(ft.Text("Nessun cammino minimo valido trovato che rispetti i vincoli (almeno 2 archi e peso>soglia"))

        self._view.page.update()

