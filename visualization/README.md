# Graph Viewer

Questo tool legge un file JSON contenente un grafo (nodi, archi, coordinate) e genera una visualizzazione interattiva in un popup browser usando **Cytoscape.js**.

## File
- `graph_viewer.cpp` - Codice sorgente che legge il JSON e genera HTML con Cytoscape.js

## Requisiti
- Compilatore C++17 (g++, clang++)
- nlohmann/json (già presente in `../external/nlohmann_json/`)
- Browser web (per aprire il popup)

## Compilazione

Dalla cartella root del repository:

```bash
cd /mnt/c/Users/danie/Fault-Tolerant-Quantum-Compiler
g++ -std=c++17 -I./external/nlohmann_json/include visualization/graph_viewer.cpp -o graph_viewer
```

Oppure dalla cartella `visualization/`:

```bash
cd visualization
g++ -std=c++17 -I../external/nlohmann_json/include graph_viewer.cpp -o graph_viewer
```

## Esecuzione

```bash
# Usa il file di default (graph_53q_rochester.json)
./graph_viewer

# Oppure specifica un altro file JSON
./graph_viewer ../graph_description_generic.json
```

Il programma:
1. Legge il JSON specificato
2. Genera un file HTML temporaneo (`/tmp/graph_view.html`)
3. Apre automaticamente il file nel browser di default (popup)

## Formato JSON supportato

Il viewer si aspetta un JSON con questa struttura:

```json
{
  "num_nodes": 53,
  "connectivity": [
    [0, 1], [1, 2], ...
  ],
  "coordinates": {
    "0": [x, y],
    "1": [x, y],
    ...
  },
  "magic states": [7, 19, 30, ...]
}
```

- **connectivity**: lista di coppie [source, target] per gli archi
- **coordinates**: posizioni (x, y) per ogni nodo (opzionale; se assente usa layout automatico)
- **magic states**: lista di nodi da evidenziare in oro (opzionale)

## Features
- ✅ Layout basato su coordinate del JSON
- ✅ Evidenziazione "magic states" in oro
- ✅ Zoom automatico (fit con padding)
- ✅ Supporto grafi fino a centinaia di nodi

## Troubleshooting

Se il browser non si apre automaticamente, il file HTML viene comunque generato in `/tmp/graph_view.html` — puoi aprirlo manualmente.
