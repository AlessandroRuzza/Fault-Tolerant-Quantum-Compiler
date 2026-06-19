#ifndef COMMUTE_HPP
#define COMMUTE_HPP

#include "circuit.hpp"

#include <cstdint>

// Two gates commute iff every qubit they share plays the SAME role in both.
// Only CX-CX pairs are considered commuting; any pair involving a non-CX gate
// (h, t, ...) is treated as non-commuting (conservative — never reorder past it).
//   CX(a,b) , CX(a,c)  -> share a as control in both        -> commute
//   CX(a,b) , CX(c,b)  -> share b as target in both         -> commute
//   CX(a,b) , CX(b,c)  -> share b: target in one, control   -> do NOT commute
//
// Shared by the packing router (commutation-aware frontier) and the
// commutation-aware circuit layering so both use one definition of commutation.
inline bool gates_commute(const Gate& g1, const Gate& g2) {
    if (g1.name != "cx" || g2.name != "cx") return false;
    if (g1.qubits.size() != 2 || g2.qubits.size() != 2) return false;
    const uint32_t c1 = g1.qubits[0], t1 = g1.qubits[1];
    const uint32_t c2 = g2.qubits[0], t2 = g2.qubits[1];
    for (const uint32_t q : {c1, t1}) {
        if (q != c2 && q != t2) continue;          // not a shared qubit
        const bool is_control_in_1 = (q == c1);
        const bool is_control_in_2 = (q == c2);
        if (is_control_in_1 != is_control_in_2) return false;  // shared, different role
    }
    return true;
}

#endif // COMMUTE_HPP
