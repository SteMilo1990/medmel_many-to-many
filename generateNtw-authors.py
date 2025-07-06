# This

import json
import networkx as nx
from collections import defaultdict
from pyvis.network import Network
import math

folder_pitch = "pitch"
folder_spaces = "spaces-true"
folder_trim = "trim-false"
threshold = 0.9
type = "author"

# Carica il JSON dei collegamenti
with open(f"files/results/{folder_pitch}/{folder_spaces}/{folder_trim}/results.json", "r", encoding="utf-8") as f:
    results = json.load(f)

excluded = ["1592", "1545", "1727", "1728", "1736"]
def format_result_into_network_data(results):
    ntw = []
    for source_id_stave in results:
        source_id = results[source_id_stave]["source"]["id"]
        if source_id_stave not in excluded:
            for match in results[source_id_stave]["matches"]:
                if match["target"]["id_staves"] != excluded:
                    link = {#"source": source_id_stave,
                            #"source_label": source_id,
                            "source": source_id,
                            #"target": match["target"]["id_staves"],
                            "target": match["target"]["id"],
                            "target_label": match["target"]["id"],
                            "score":  match["score"],
                            "source_l": f"{source_id}.{match['source_line']}",
                            "target_l": f"{match['target']['id']}.{match['target']['n']}",
                            "source_text": results[source_id_stave]["source"]["text"][match["source_line"]],
                            "target_text": match["target"]["text"],
                            "source_melody": results[source_id_stave]["source"]["staves"][match['source_line']],
                            "target_melody": match["target"]["melody_line"]
                            }
                    ntw.append(link)
    return ntw

data = format_result_into_network_data(results)

# Carica il JSON dei collegamenti
# with open("files/network.json", "r", encoding="utf-8") as f:
#     data = json.load(f)

# Carica i nomi degli autori
with open("files/authors.json", "r", encoding="utf-8") as f:
    author_names = json.load(f)

# Dizionario per contare le connessioni uniche tra coppie di autori e sommare gli score
total_edge_scores = defaultdict(float)
node_connections = defaultdict(int)  # Conta quante connessioni ha ogni autore
labels_container = defaultdict(str)

# Crea il grafo filtrando connessioni con score > threshold e correggendo gli anonimi
for entry in data:
    source = entry["source"]
    target = entry["target"]
    source_l = entry["source_l"]
    target_l = entry["target_l"]
    source_text = entry["source_text"]
    target_text = entry["target_text"]
    source_melody = entry["source_melody"]
    target_melody = entry["target_melody"]
    score = float(entry["score"])

    # Se l'autore è anonimo (BdT 461 or Linker 265), usa source_l o target_l
    if source_l.rsplit('.')[0] == "BdT 461" or source_l.rsplit('.')[0] == "Linker 265":
        source = source_l.rsplit('.', 1)[0]
    if target_l.rsplit('.')[0] == "BdT 461" or target_l.rsplit('.')[0] == "Linker 265":
        target = target_l.rsplit('.', 1)[0]

    # Evita di aggiungere doppioni (A → B deve esistere una sola volta)
    edge = tuple(sorted([source, target]))
    if score > threshold:
        total_edge_scores[edge] += score  # Somma lo score totale per la coppia
        node_connections[source] += 1
        node_connections[target] += 1
        labels_container[edge] += f"{source_l} ~ {target_l} ({score}%)" #\n{source_text}\n{target_text}\n\n"

# Normalizza il colore con contrasto maggiore
def normalize(value, max_value, min_value=50, max_intensity=255, log_scale=False):
    if max_value == 0:
        return min_value
    if log_scale:
        value = math.log1p(value)  # Applica scala logaritmica
        max_value = math.log1p(max_value)
    intensity = int((value / max_value) * (max_intensity - min_value) + min_value)
    return min(max(intensity, min_value), max_intensity)

max_links = max(node_connections.values()) if node_connections else 1
max_score = max(total_edge_scores.values()) if total_edge_scores else 1

# Crea il grafo pesato senza doppioni
G = nx.Graph()
for (source, target), total_score in total_edge_scores.items():
    total_score = 2  # Keep same width
    G.add_edge(source, target, weight=total_score, label=labels_container[(source, target)])  # Aggiunge i pesi agli edges

# Crea il network interattivo
net = Network(height="900px", width="100%", notebook=True, cdn_resources="remote")
net.from_nx(G)

# Parametri di fisica per maggiore stabilità
net.toggle_physics(True)
net.show_buttons(filter_=['physics'])
net.barnes_hut(
    gravity=-2000,
    central_gravity=0.2,
    spring_length=400,
    damping=0.8
)

# Colorazione dei nodi basata sulle connessioni + Sostituzione degli ID con i nomi
for node in net.nodes:
    node_id = node["id"].rsplit(".")
    conn_count = node_connections.get(node_id, 1)
    intensity = normalize(conn_count, max_links, min_value=20, max_intensity=220, log_scale=True)
    node["color"] = f"rgb({255-intensity}, {255-intensity}, 255)"  # Più scuro se più connessioni

    # Sostituisci l'ID con il nome dell'autore
    if "CSM " in node_id:
        node_id = "Alfonso X"
    if node_id in author_names:
        node["label"] = author_names[str(node_id)]  # Se manca, usa l'ID
    else:
        node["label"] = str(node_id)


# Applica il peso e il colore agli edges con più contrasto
for edge in net.edges:
    node1, node2 = edge["from"], edge["to"]
    if G.has_edge(node1, node2):
        total_score = G[node1][node2].get("width", 1)
        edge["width"] = total_score  # Spessore proporzionale al punteggio totale
        intensity = normalize(total_score, max_score, min_value=30, max_intensity=200, log_scale=True)
        edge["color"] = f"rgb({255-intensity}, {255-intensity}, 255)"  # Più scuro se score alto
        edge["label"] = G[node1][node2].get("label", f"{total_score:.2f}") # f"{total_score:.2f}"  # Etichetta con lo score
        edge["font"] = {"size": 0}  # Nasconde inizialmente la label

net.show(f"generated-networks/{folder_pitch}_{folder_spaces}_{folder_trim}_network-{threshold}-{type}.html")
net.write_html(f"generated-networks/{folder_pitch}_{folder_spaces}_{folder_trim}_network-{threshold}-{type}.html", open_browser=False)

highlight_js = """
window.onload = function () {
    if (typeof network === "undefined") {
        console.error("Errore: la variabile network non è stata inizializzata.");
        return;
    }

    console.log("Attendere il caricamento completo del network...");

    network.once("afterDrawing", function () {
        console.log("Network caricato e pronto!");
        
        var sidebar = document.createElement("div");
        sidebar.id = "edge-info";
        sidebar.style.position = "fixed";
        sidebar.style.right = "10px";
        sidebar.style.top = "10px";
        sidebar.style.width = "300px";
        sidebar.style.padding = "10px";
        sidebar.style.border = "1px solid black";
        sidebar.style.background = "white";
        sidebar.style.display = "none";
        sidebar.style.boxShadow = "2px 2px 10px rgba(0,0,0,0.2)";
        sidebar.innerHTML = "<strong>Edge Info:</strong><p id='edge-label'></p>";
        
        // Aggiungi la sidebar al body
        document.body.appendChild(sidebar);

        // Salva i colori originali
        var originalColors = {};
        network.body.data.nodes.get().forEach(node => {
            originalColors[node.id] = node.color;
        });
        network.body.data.edges.get().forEach(edge => {
            originalColors[edge.id] = edge.color;
        });

        function highlightConnectedNodes() {
            network.on("click", function (params) {
                if (params.nodes.length > 0) {
                    var selectedNode = params.nodes[0];
                    var connectedNodes = new Set(network.getConnectedNodes(selectedNode));
                    connectedNodes.add(selectedNode);

                    network.body.data.nodes.update(
                        network.body.data.nodes.get().map(node => ({
                            id: node.id,
                            color: connectedNodes.has(node.id) ? node.color : "rgba(200, 200, 200, 0.3)"
                        }))
                    );

                    network.body.data.edges.update(
                        network.body.data.edges.get().map(edge => ({
                            id: edge.id,
                            color: (connectedNodes.has(edge.from) && connectedNodes.has(edge.to))
                                ? edge.color
                                : "rgba(200, 200, 200, 0.1)"
                        }))
                    );
                } 
                
                
               else if (params.edges.length > 0) {
                    var selectedEdge = params.edges[0];
                    var edge = network.body.data.edges.get(selectedEdge);
                
                    document.getElementById("edge-label").innerText = edge.label || "Nessuna etichetta";
                    document.getElementById("edge-info").style.display = "block";
                }
                else {
                document.getElementById("edge-info").style.display = "none"; // Nasconde la sidebar

                    // Ripristina i colori originali
                    network.body.data.nodes.update(
                        network.body.data.nodes.get().map(node => ({
                            id: node.id,
                            color: originalColors[node.id]
                        }))
                    );

                    // Nasconde tutte le etichette degli edges quando si clicca fuori
                    network.body.data.edges.update(
                        network.body.data.edges.get().map(edge => ({
                            id: edge.id,
                            font: { size: 0 } // Nasconde il label
                        }))
                    );

                    network.body.data.edges.update(
                        network.body.data.edges.get().map(edge => ({
                            id: edge.id,
                            color: originalColors[edge.id]
                        }))
                    );
                }
            });
        }

        highlightConnectedNodes();
    });
};

// Create the dropdown menu dynamically
var dropdown = document.createElement("select");
dropdown.id = "author-select";
dropdown.style.position = "fixed";
dropdown.style.top = "10px";
dropdown.style.left = "10px";
dropdown.style.padding = "5px";
dropdown.style.border = "1px solid black";
dropdown.style.background = "white";

// Default option
var defaultOption = document.createElement("option");
defaultOption.value = "";
defaultOption.innerText = "Select an author";
dropdown.appendChild(defaultOption);

// Add the dropdown to the page
document.body.appendChild(dropdown);

// Populate the dropdown with author names
function populateDropdown(authors) {
    Object.keys(authors).forEach(function(authorId) {
        var option = document.createElement("option");
        option.value = authorId;
        option.innerText = authors[authorId];
        dropdown.appendChild(option);
    });
}

// When an author is selected, "click" the corresponding node
dropdown.addEventListener("change", function () {
    var selectedAuthorId = this.value;
    if (selectedAuthorId && network.body.nodes[selectedAuthorId]) {
        network.selectNodes([selectedAuthorId]);  // Select the node visually
        network.emit("click", { nodes: [selectedAuthorId], edges: [] });  // Trigger a click event
    }
});

"""

# Inietta il codice JS nel file HTML generato
net.set_options("""
{
  "interaction": { "hover": true }
}
""")
author_js = f"var authorNames = {json.dumps(author_names)};"  # Convert to JS format

with open(f"generated-networks/{folder_pitch}_{folder_spaces}_{folder_trim}_network-{threshold}-{type}.html", "a", encoding="utf-8") as f:
    f.write(f"<script>{highlight_js}; {author_js} populateDropdown(authorNames);</script>")

print("Grafo interattivo salvato in 'network.html'. Aprilo nel browser per testarlo!")
