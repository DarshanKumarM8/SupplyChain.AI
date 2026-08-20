# SupplyChain.AI — Mathematical Formulas Reference

This document contains the core mathematical formulas used in the AI Engine. Use this as a reference during the presentation or Q&A if asked how the AI actually works under the hood.

## 1. 2D Fokker-Planck Density Field (Agent Rerouting)
We model the collective rerouting behavior of supply chain agents as a density field $\rho(x,t)$ evolving over the lane-time grid using the Fokker-Planck equation.

$$ \frac{\partial \rho}{\partial t} = -\nabla \cdot (\mu \rho) + D \nabla^2 \rho $$

* **$\rho(x, t)$**: Agent density at lane/week coordinate $x$ at time $t$.
* **$\mu$ (Drift)**: The vector field pointing toward popular lanes, driven by competitor panic ($\beta$).
* **$D$ (Diffusion)**: The entropy budget allocated to randomize assignments and spread the load.

**Why we use it:** Instead of tracking 1,000 individual shipments (which is computationally slow), we treat them as a fluid. We apply diffusion ($D$) to "smear" the fluid away from bottlenecks, naturally de-phasing the shipments over time.

---

## 2. SupplyChainAI Stampede Index ($S_t$)
The Stampede Index is a composite score from 0 to 100 measuring the severity of herd behavior.

$$ S_t = 100 \times \left[ w_1 \left( \frac{1 + \rho_{\text{Spearman}}}{2} \right) + w_2 v_{\text{deplete}} + w_3 \sigma_{\text{rate}} \right] $$

* **$\rho_{\text{Spearman}}$**: Mean pairwise Spearman rank correlation of order vectors across all firms. (High correlation = everyone ordering the same thing).
* **$v_{\text{deplete}}$**: Normalized capacity depletion velocity across bottleneck nodes.
* **$\sigma_{\text{rate}}$**: Realized volatility of spot shipping rates.
* **Weights ($w_1, w_2, w_3$)**: Tunable hyperparameters summing to 1.0 (default: 0.4, 0.4, 0.2).

**Why we use it:** It translates complex multi-variate graph state into a single, intuitive "panic gauge" for the dashboard.

---

## 3. Buffer Diversity Score ($D_{\text{buffer}}^{(i)}$)
Measures how similar a firm's inventory buffer strategy is to the rest of the market. Low diversity means the firm is vulnerable to the exact same shocks as everyone else.

$$ D_{\text{buffer}}^{(i)} = 1 - \cos(\mathbf{b}_i, \mathbf{\bar{b}}_{-i}) = 1 - \frac{\mathbf{b}_i \cdot \mathbf{\bar{b}}_{-i}}{\|\mathbf{b}_i\|_2 \|\mathbf{\bar{b}}_{-i}\|_2} $$

* **$\mathbf{b}_i$**: SKU-level buffer vector for firm $i$.
* **$\mathbf{\bar{b}}_{-i}$**: The mean buffer vector of all *other* firms in the market.

**Why we use it:** We use this to assign firms to phased release tranches (W1, W3, W5). Firms with the lowest diversity (most synchronized) are released first to forcibly desynchronize the market.

---

## 4. Meta-Herd Detection (Second-Order Herding)
If too many firms use the same AI to avoid the herd, they form a "meta-herd" on the backup routes. We detect this by computing the pairwise cosine similarity of their temporal de-phasing strategies.

$$ \text{Clique if: } \forall i, j \in \text{Cohort}: \cos(\mathbf{d}_i, \mathbf{d}_j) > 0.85 $$

* **$\mathbf{d}_i$**: The temporal de-phasing allocation vector (W1, W3, W5 percentages) for firm $i$.

**Why we use it:** If a clique of size $\ge 3$ forms, the AI automatically activates the Entropy Budget to randomize assignments, breaking the meta-herd.

---

## 5. Secure Multi-Party Computation (SMPC) - Quiet Coalitions
We use a mock Private Set Intersection (PSI) with $\epsilon$-Differential Privacy to allow firms to attest to available capacity without revealing their exact volume or full network.

$$ \text{Noised Capacity} = \text{True Capacity} + \text{Laplace}(0, 1/\epsilon) $$

* **$\epsilon$**: Privacy budget. Lower $\epsilon$ = more noise = stronger privacy guarantee.

**Why we use it:** Firms will never share their raw supply chain data with competitors. SMPC allows them to collaborate on alleviating bottlenecks while remaining cryptographically blind to each other's proprietary operations.
