#ifndef IGRAPH_HPP
#define IGRAPH_HPP

#include <algorithm>
#include <cmath>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>
#include <set>
#include <unordered_map>
#include <unordered_set>

struct Node {
    int id;
    int coordX, coordY;
    std::vector<int> neighbors;  // Store neighbor IDs, not Node objects
    bool occupied = false;
    
    Node(int node_id, int x = 0, int y = 0);

    
    float distance(Node b) const {
        float distX = std::abs(coordX - b.coordX);
        float distY = std::abs(coordY - b.coordY);
        return distX + distY; // Manhattan distance
    }

    std::tuple <int, int> get_coordinates() const {
        return std::make_tuple(coordX, coordY);
    }
};



class IGraph {

protected:
    std::vector<Node> nodes;
    std::vector<int> magic_states_ids; // Store only IDs of magic states
    std::unordered_map<int, int> mapped_magic_states;
    int node_count;
    int maxX;
    int maxY;

public:

    IGraph() : node_count(0), maxX(-1), maxY(-1) {}  // costruttore di default
    virtual ~IGraph() = default;
    virtual void add_edge(int u, int v) = 0;


    // ------get_nodes----------

    inline Node& get_node(int id) {
        return nodes[id];
    }

    inline const Node& get_node(int id) const {
        return nodes[id];
    }

    inline std::vector<Node> get_nodes() const {
        return nodes;
    }

    inline const std::vector<Node>& get_nodes_ref() const {
        return nodes;
    }


    std::vector<int> get_nodes_ids () const {
        std::vector<int> ids;
        ids.reserve(nodes.size());
        for (const Node& node : nodes) {
            ids.push_back(node.id);
        }
        return ids;
    } 

    // Get node by coordinates
    const Node& get_node_by_coordinates(int x, int y) const {
        for (const Node& node : nodes) {
            if (node.coordX == x && node.coordY == y) {
                return node;
            }
        }
        throw std::runtime_error("Node not found at coordinates: (" + std::to_string(x) + "," + std::to_string(y) + ")");
    }

    // ------get_magic_states----------

    const std::vector<Node> get_magic_states() const { 
        std::vector<Node> result;
        for (int id : magic_states_ids) {
            result.push_back(get_node(id));
        }
        return result;
    }

    inline const std::vector<int>& get_magic_state_ids() const {
        return magic_states_ids;
    }

    inline int get_magic_state_size() const {
        return magic_states_ids.size();
    }



    // ---------get_coord-----------




    inline const int get_coordX(int id) const {
        return get_node(id).coordX;
    }

    inline const int get_coordY(int id) const {
        return get_node(id).coordY;
    }

    inline const int getMaxX() const {
        return maxX;
    }

    inline const int getMaxY() const {
        return maxY;
     }



    // --------neighbours--------

    inline const std::vector<int>& neighbors(int u) const {
        return get_node(u).neighbors;
    }


    
    const std::vector<Node> neighbor_nodes(int u) const {
        std::vector<Node> result;
        const std::vector<int>& neighbors_u = neighbors(u);
        result.reserve(neighbors_u.size());
        for (int neighbor_id : neighbors_u) {
            result.emplace_back(get_node(neighbor_id));
        }
        return result;
    }


    //--------occupied-----------
    

    inline void occupy_node(int id) {
        get_node(id).occupied = true;
    }


    inline const bool is_occupied(int id) const {
        return get_node(id).occupied;
    }

    const bool is_magic(int node_id) const {
        for(int id : magic_states_ids)
            if(id == node_id) return true;
        return false;
    }

    const std::vector<Node> get_occupied_nodes() const {
        std::vector<Node> occupied_nodes;
        for (const Node& node : nodes) {
            if (node.occupied) {
                occupied_nodes.push_back(node);
            }
        }
        return occupied_nodes;
     }


    // --------------------------

    inline int get_node_count() const { 
        return node_count; 
    }

    inline int get_maxX() const {
        return maxX;
    }

    inline int get_maxY() const {
        return maxY;
    }






    // -------print ---------------
    void print() const;
    
    void print_rectangular() const;
    void print_rectangular(const std::unordered_set<int>& candidates) const;


    //-------add---------------
    void add_node(int id, int x, int y);
    void add_node(int id);



    // ------magic_states_algorithms_helpers----------



    const int getNearestMagicStateId(int node_id) const;

    const Node& getNearestMagicState(const Node& node) const;

    const int getBestMagicStateId();

    const void update_magic_states_score(int magic_state_id);

    void increment_mapped_magic_state(int magic_state_id);

    virtual void add_magic_states_rightrow(const std::vector<int>& magic_state_ids, int height, int width) = 0;

    virtual void add_magic_states_center_circle(
        const std::vector<int>& magic_state_ids,
        int height,
        int width,
        int number_of_magic_states,
        double border_distance_percentage
    ) = 0;

};


#endif
