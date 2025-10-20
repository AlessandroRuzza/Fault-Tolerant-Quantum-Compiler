// graph_viewer.cpp - Visualizza un grafo JSON (connectivity, coordinates) in un popup browser
// Usa nlohmann::json e genera un HTML con Cytoscape.js per la visualizzazione interattiva.

#include <fstream>
#include <iostream>
#include <string>
#include <sstream>
#include <cstdlib>
#include "../external/nlohmann_json/json.hpp"

using json = nlohmann::json;

void show_graph_with_cytoscape(const std::string &json_path) {
    // 1) Carica il JSON
    json g;
    {
        std::ifstream ifs(json_path);
        if (!ifs) {
            std::cerr << "Impossibile aprire: " << json_path << "\n";
            return;
        }
        ifs >> g;
    }

    // 2) Costruisci nodes e edges in formato JavaScript per Cytoscape
    std::ostringstream nodes_js, edges_js;
    nodes_js << "[\n";
    
    if (g.contains("coordinates")) {
        for (auto it = g["coordinates"].begin(); it != g["coordinates"].end(); ++it) {
            std::string id = it.key();
            auto coord = it.value();
            double x = coord[0].get<double>();
            double y = coord[1].get<double>();
            
            // Controlla se il nodo è uno "magic state"
            bool is_magic = false;
            if (g.contains("magic states")) {
                for (auto &m : g["magic states"]) {
                    if (std::to_string(m.get<int>()) == id) { 
                        is_magic = true; 
                        break; 
                    }
                }
            }
            
            nodes_js << "  { data: { id: \"" << id << "\", label: \"" << id << "\" }, "
                     << "position: { x: " << (x * 80) << ", y: " << (y * 80) << " }, "
                     << "selectable: true, grabbable: false, locked: true";
            
            if (is_magic) {
                nodes_js << ", classes: 'magic'";
            }
            
            nodes_js << " },\n";
        }
    } else {
        // Fallback: crea n nodi numerati da num_nodes (senza coordinate)
        int n = g.value("num_nodes", 0);
        for (int i = 0; i < n; ++i) {
            nodes_js << "  { data: { id: \"" << i << "\", label: \"" << i << "\" } },\n";
        }
    }
    nodes_js << "]\n";

    edges_js << "[\n";
    if (g.contains("connectivity")) {
        for (auto &e : g["connectivity"]) {
            int src = e[0].get<int>();
            int tgt = e[1].get<int>();
            edges_js << "  { data: { id: \"" << src << "-" << tgt 
                     << "\", source: \"" << src << "\", target: \"" << tgt << "\" } },\n";
        }
    }
    edges_js << "]\n";

    // 3) Template HTML con Cytoscape.js da CDN
    std::string html = R"HTML(<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Graph Viewer - Quantum Compiler</title>
  <script src="https://unpkg.com/cytoscape@3.24.0/dist/cytoscape.min.js"></script>
  <style>
    html, body, #cy { 
      height: 100%; 
      margin: 0; 
      padding: 0; 
      font-family: Arial, sans-serif;
    }
    .magic { 
      background-color: gold; 
    }
  </style>
</head>
<body>
<div id="cy"></div>
<script>
  const elements = {
    nodes: )HTML" + nodes_js.str() + R"HTML(,
    edges: )HTML" + edges_js.str() + R"HTML(
  };

  const cy = cytoscape({
    container: document.getElementById('cy'),
    elements: [].concat(elements.nodes, elements.edges),
    style: [
      {
        selector: 'node',
        style: {
          'background-color': '#666',
          'label': 'data(label)',
          'width': 30,
          'height': 30,
          'text-valign': 'center',
          'text-halign': 'center',
          'color': '#fff',
          'font-size': 12
        }
      },
      {
        selector: 'node.magic',
        style: {
          'background-color': 'gold',
          'border-color': '#b8860b',
          'border-width': 3
        }
      },
      {
        selector: 'edge',
        style: {
          'width': 3,
          'line-color': '#bbb',
          'target-arrow-shape': 'none'
        }
      }
    ],
    layout: { name: 'preset' } // usa le posizioni fornite nel JSON
  });

  // Adatta il viewport al grafo con padding
  cy.fit(undefined, 50);
</script>
</body>
</html>)HTML";

    // 4) Scrivi file HTML temporaneo
    std::string out = "/tmp/graph_view.html"; // WSL-friendly path
    std::ofstream ofs(out);
    if (!ofs) {
        std::cerr << "Impossibile scrivere HTML su: " << out << "\n";
        return;
    }
    ofs << html;
    ofs.close();

    std::cout << "HTML generato: " << out << "\n";

    // 5) Apri nel browser: prova wslview -> xdg-open -> cmd.exe start (fallback)
    int r = std::system(("wslview " + out + " >/dev/null 2>&1").c_str());
    if (r != 0) {
        r = std::system(("xdg-open " + out + " >/dev/null 2>&1").c_str());
    }
    if (r != 0) {
        // Fallback per aprire con browser Windows (da WSL)
        std::string winpath = "/mnt/c/Windows/System32/cmd.exe /C start \"\" \"" + out + "\"";
        r = std::system(winpath.c_str());
        if (r != 0) {
            std::cerr << "Non sono riuscito ad aprire il file nel browser automaticamente.\n";
            std::cerr << "Apri manualmente: " << out << "\n";
        }
    }
}

int main(int argc, char **argv) {
    const char *path = "graph_53q_rochester.json";
    if (argc > 1) {
        path = argv[1];
    }
    
    std::cout << "Visualizzazione grafo: " << path << "\n";
    show_graph_with_cytoscape(path);
    
    return 0;
}
