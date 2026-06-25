# Formula della dimensione ottima (solo nostro codice)

Ginocchio dei `routing_steps` vs lato-griglia per circuito, poi fit `side*(n) = a·√n + b` per strategia. `eps` = quanto degrado di routing_steps accetti rispetto al plateau in cambio di una griglia più piccola (eps piccolo → griglia più grande, più vicina al minimo step).

- Riferimento WISQ-native: `side = 2·⌈√n⌉ + 3`.

- `flat` = circuiti dove il grid non aiuta (max_drop < 5%): il loro ottimo è la griglia minima fattibile.

- Envelope = per ogni n, il 90° percentile del ginocchio (formula che non affama il circuito più duro a quel n).


## connectivity  (253 circuiti, 99 grid-sensitive, 154 flat)

> ⚠ 35 circuiti hanno il ginocchio sul lato massimo sweepato (curva ancora in discesa): per quelli la formula è un **lower bound**, estendi `dimension_offset` verso l'alto e rilancia.


| eps | fit (tutti) | fit (solo sensitive) | fit (envelope) |
|-----|-------------|----------------------|----------------|
| 2% | side*(n) = 1.919*sqrt(n) + 2.03   [~1.92*ceil(sqrt(n)) + 2.0]   R^2=0.614  (N=253) | side*(n) = 2.370*sqrt(n) + 5.26   [~2.37*ceil(sqrt(n)) + 5.3]   R^2=0.723  (N=99) | side*(n) = 1.936*sqrt(n) + 2.70   [~1.94*ceil(sqrt(n)) + 2.7]   R^2=0.709  (N=48) |
| 5% | side*(n) = 1.900*sqrt(n) + 1.32   [~1.90*ceil(sqrt(n)) + 1.3]   R^2=0.676  (N=253) | side*(n) = 2.374*sqrt(n) + 3.14   [~2.37*ceil(sqrt(n)) + 3.1]   R^2=0.757  (N=99) | side*(n) = 1.932*sqrt(n) + 1.94   [~1.93*ceil(sqrt(n)) + 1.9]   R^2=0.751  (N=48) |
| 10% | side*(n) = 1.865*sqrt(n) + 0.74   [~1.87*ceil(sqrt(n)) + 0.7]   R^2=0.762  (N=253) | side*(n) = 2.314*sqrt(n) + 1.43   [~2.31*ceil(sqrt(n)) + 1.4]   R^2=0.827  (N=99) | side*(n) = 1.906*sqrt(n) + 1.07   [~1.91*ceil(sqrt(n)) + 1.1]   R^2=0.832  (N=48) |

### Per famiglia (eps=5%, solo famiglie grid-sensitive)

| family | n circ | n range | max_drop med | elbow/√n med |
|--------|--------|---------|--------------|--------------|
| 19qubits_511gate_153layers | 1 | 19–19 | 7% | 1.84 |
| 53qubits_332gate_152layers | 1 | 39–39 | 7% | 1.76 |
| factor | 1 | 15–15 | 8% | 2.07 |
| graphstate | 17 | 5–400 | 0% | 1.58 |
| ising | 19 | 5–420 | 0% | 1.58 |
| qaoa | 19 | 5–300 | 73% | 2.57 |
| qft | 22 | 5–400 | 58% | 2.46 |
| randomcircuit | 2 | 50–100 | 76% | 3.40 |
| seca | 1 | 11–11 | 5% | 1.81 |
| synth | 37 | 50–200 | 81% | 3.04 |
| vqe_two_local | 16 | 5–300 | 73% | 2.80 |

## cube  (254 circuiti, 106 grid-sensitive, 148 flat)

> ⚠ 21 circuiti hanno il ginocchio sul lato massimo sweepato (curva ancora in discesa): per quelli la formula è un **lower bound**, estendi `dimension_offset` verso l'alto e rilancia.


| eps | fit (tutti) | fit (solo sensitive) | fit (envelope) |
|-----|-------------|----------------------|----------------|
| 2% | side*(n) = 2.340*sqrt(n) + 2.50   [~2.34*ceil(sqrt(n)) + 2.5]   R^2=0.819  (N=254) | side*(n) = 2.226*sqrt(n) + 8.06   [~2.23*ceil(sqrt(n)) + 8.1]   R^2=0.791  (N=106) | side*(n) = 2.496*sqrt(n) + 2.56   [~2.50*ceil(sqrt(n)) + 2.6]   R^2=0.866  (N=48) |
| 5% | side*(n) = 2.312*sqrt(n) + 1.90   [~2.31*ceil(sqrt(n)) + 1.9]   R^2=0.869  (N=254) | side*(n) = 2.269*sqrt(n) + 5.82   [~2.27*ceil(sqrt(n)) + 5.8]   R^2=0.842  (N=106) | side*(n) = 2.407*sqrt(n) + 2.30   [~2.41*ceil(sqrt(n)) + 2.3]   R^2=0.907  (N=48) |
| 10% | side*(n) = 2.292*sqrt(n) + 1.05   [~2.29*ceil(sqrt(n)) + 1.1]   R^2=0.934  (N=254) | side*(n) = 2.347*sqrt(n) + 2.62   [~2.35*ceil(sqrt(n)) + 2.6]   R^2=0.922  (N=106) | side*(n) = 2.353*sqrt(n) + 1.44   [~2.35*ceil(sqrt(n)) + 1.4]   R^2=0.957  (N=48) |

### Per famiglia (eps=5%, solo famiglie grid-sensitive)

| family | n circ | n range | max_drop med | elbow/√n med |
|--------|--------|---------|--------------|--------------|
| adder | 4 | 4–433 | 2% | 2.46 |
| fredkin | 1 | 3–3 | 9% | 3.46 |
| graphstate | 17 | 5–400 | 0% | 2.21 |
| ising | 19 | 5–420 | 20% | 2.30 |
| parallel | 1 | 8–8 | 23% | 2.47 |
| qaoa | 20 | 5–400 | 23% | 2.95 |
| qft | 22 | 5–400 | 18% | 2.59 |
| qram | 1 | 9–9 | 20% | 2.33 |
| randomcircuit | 2 | 50–100 | 38% | 3.20 |
| synth | 37 | 50–200 | 28% | 3.11 |
| vqe_two_local | 16 | 5–300 | 26% | 3.47 |
