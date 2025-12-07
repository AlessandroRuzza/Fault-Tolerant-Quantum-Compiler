#include <vector>


using json = nlohmann::json;

struct Node {
    int id;
    int coordX, coordY;
    std::vector<int> neighbors;  // Store neighbor IDs, not Node objects
    bool occupied = false;
    
    Node(int node_id, int x = 0, int y = 0);
    /**
     * Manhattan distance
     */
    float distance(Node b) const {
        float distX = abs(coordX - b.coordX);
        float distY = abs(coordY - b.coordY);
        return distX + distY;
    }
};

class IGraph {

protected:
    std::unordered_set<int> nodes;
    std::unordered_set<int> magic_states;
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

};