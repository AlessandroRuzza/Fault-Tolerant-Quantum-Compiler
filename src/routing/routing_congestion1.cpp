#include "routing.hpp"

Path CongestionAwareShortestPath::naive_unweighted_path(
	int start_node,
	int end_node,
	const std::unordered_set<int>& used_nodes
) const {
	if (start_node == end_node) {
		return {start_node};
	}

	std::unordered_map<int, int> parent;
	auto cmp = [&](int a, int b) {
		const Node& a_node = this->graph.get_node(a);
		const Node& b_node = this->graph.get_node(b);
		const Node& target = this->graph.get_node(end_node);
		return a_node.distance(target) > b_node.distance(target);
	};
	std::priority_queue<int, std::vector<int>, decltype(cmp)> q(cmp);

	q.push(start_node);
	parent[start_node] = -1;

	while (!q.empty()) {
		const int current = q.top();
		q.pop();

		if (current == end_node) {
			Path path;
			int node = end_node;
			while (node != -1) {
				path.push_back(node);
				node = parent[node];
			}
			std::reverse(path.begin(), path.end());
			return path;
		}

		for (int neighbor : graph.neighbors(current)) {
			if (neighbor == end_node || (used_nodes.count(neighbor) == 0 && parent.find(neighbor) == parent.end())) {
				parent[neighbor] = current;
				q.push(neighbor);
			}
		}
	}

	return {};
}

void CongestionAwareShortestPath::accumulate_path_congestion(const Path& path) const {
	if (path.size() <= 2) {
		return;
	}

	for (size_t i = 1; i + 1 < path.size(); ++i) {
		node_weights[path[i]] += 1.0f;
	}
}

void CongestionAwareShortestPath::rebuild_node_weights(
	const LayeredCircuit& circuit,
	const Mapping& mapping,
	const std::unordered_set<int>& blocked_nodes
) const {
	node_weights.clear();

	for (int layer_idx = 0; layer_idx < circuit.getNumLayers(); ++layer_idx) {
		const Layer& layer = circuit.getLayer(layer_idx);

		for (const Gate& gate : layer) {
			if (gate.qubits.empty()) {
				continue;
			}

			if (gate.qubits.size() == 1 && gate.name != "t") {
				continue;
			}

			if (gate.qubits.size() == 2) {
				const int node1 = mapping.get_mapped_node(gate.qubits[0]);
				const int node2 = mapping.get_mapped_node(gate.qubits[1]);
				if (node1 < 0 || node2 < 0) {
					continue;
				}
				const Path path = naive_unweighted_path(node1, node2, blocked_nodes);
				accumulate_path_congestion(path);
				continue;
			}

			if (gate.name == "t") {
				const int start_node = mapping.get_mapped_node(gate.qubits[0]);
				if (start_node < 0) {
					continue;
				}

				const std::vector<int> magic_states = graph.get_magic_state_ids();
				size_t best_size = std::numeric_limits<size_t>::max();
				Path best_path;
				for (int magic_state : magic_states) {
					Path path = naive_unweighted_path(start_node, magic_state, blocked_nodes);
					if (!path.empty() && path.size() < best_size) {
						best_size = path.size();
						best_path = std::move(path);
					}
				}
				accumulate_path_congestion(best_path);
			}
		}
	}

	static_weights_ready = true;
}

void CongestionAwareShortestPath::prepare_for_layer(
	const LayeredCircuit& circuit,
	const Mapping& mapping,
	const std::unordered_set<int>& blocked_nodes
) const {
	if (update_policy == CongestionUpdatePolicy::STATIC_GLOBAL && static_weights_ready) {
		return;
	}

	rebuild_node_weights(circuit, mapping, blocked_nodes);
}

Path CongestionAwareShortestPath::find_shortest_path(
	int start_node,
	int end_node,
	const std::unordered_set<int>& used_nodes
) const {
	if (start_node == end_node) {
		return {start_node};
	}

	using QueueItem = std::pair<float, int>;
	std::priority_queue<QueueItem, std::vector<QueueItem>, std::greater<QueueItem>> pq;
	std::unordered_map<int, float> distance;
	std::unordered_map<int, int> parent;

	distance[start_node] = 0.0f;
	parent[start_node] = -1;
	pq.push({0.0f, start_node});

	while (!pq.empty()) {
		const auto [current_cost, current] = pq.top();
		pq.pop();

		auto best_it = distance.find(current);
		if (best_it == distance.end() || current_cost > best_it->second) {
			continue;
		}

		if (current == end_node) {
			break;
		}

		for (int neighbor : graph.neighbors(current)) {
			const bool traversable = (neighbor == end_node) || (used_nodes.count(neighbor) == 0);
			if (!traversable) {
				continue;
			}

			float step_cost = 1.0f;
			const auto weight_it = node_weights.find(neighbor);
			if (weight_it != node_weights.end()) {
				step_cost += congestion_penalty_scale * weight_it->second;
			}

			const float new_cost = current_cost + step_cost;
			const auto old_dist_it = distance.find(neighbor);
			if (old_dist_it == distance.end() || new_cost < old_dist_it->second) {
				distance[neighbor] = new_cost;
				parent[neighbor] = current;
				pq.push({new_cost, neighbor});
			}
		}
	}

	if (parent.find(end_node) == parent.end()) {
		return {};
	}

	Path path;
	for (int node = end_node; node != -1; node = parent[node]) {
		path.push_back(node);
	}
	std::reverse(path.begin(), path.end());
	return path;
}
