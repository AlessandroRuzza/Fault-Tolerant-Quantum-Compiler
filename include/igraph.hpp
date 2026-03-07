#include <vector>


using json = nlohmann::json;

struct Node {
    int id;
    int coordX, coordY;
    std::vector<int> neighbors;  // Store neighbor IDs, not Node objects
    bool occupied = false;
    
    Node(int node_id, int x = 0, int y = 0);

    
    float distance(Node b) const {
        float distX = abs(coordX - b.coordX);
        float distY = abs(coordY - b.coordY);
        return distX + distY; // Manhattan distance
    }

    std::tuple <int, int> get_coordinates() const {
        return std::make_tuple(coordX, coordY);
    }
};

class IGraph {

protected:
    std::unordered_set<int> nodes;
    std::unordered_set<int> magic_states;
    std::unordered_map<int, int> mapped_magic_states;
    int node_count;

public:
    IGraph() : node_count(0) {}  // costruttore di default
    virtual ~IGraph() = default;
    virtual void add_edge(int u, int v) = 0;
    virtual const std::vector<int>& neighbors(int u) const = 0;
    virtual std::vector<Node> neighbor_nodes(int u) const = 0;
    virtual std::vector<int> bfs(int start) const = 0;
    virtual void print() const = 0;
    virtual bool is_occupied(int id) const = 0;
    virtual Node& get_node(int id) = 0;
    virtual const Node& get_node(int id) const = 0;
    virtual void occupy_node(int id) = 0;
    
    std::unordered_set<int> get_nodes() const { 
        return nodes; 
    }

    std::unordered_set<int> get_magic_states() const { 
        return magic_states; 
    }


    int get_node_count() const { 
        return node_count; 
    }


    const int getBestMagicStateId() {
        int best_magic_state_id = -1;
        int min_mapped_qubits = INT_MAX;
        for (int magic_state_id : this->get_magic_states()) {
            int count = mapped_magic_states[magic_state_id];
            if (count < min_mapped_qubits) {
                min_mapped_qubits = count;
                best_magic_state_id = magic_state_id;
            }
        }
        return best_magic_state_id;
    }

    // const void update_magic_states_score(int magic_state_id) {
    //     // In this simple implementation, the score is just the count of mapped qubits.
    //     // More complex heuristics could be implemented here if needed.

        
    // }

    void increment_mapped_magic_state(int magic_state_id) {
        mapped_magic_states[magic_state_id]++;
        //update_magic_states_score(magic_state_id);
    }

};