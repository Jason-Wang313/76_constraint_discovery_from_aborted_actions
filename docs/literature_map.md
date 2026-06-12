        # Literature Map

        Paper: 76 constraint_discovery_from_aborted_actions

        Field box: robot planning and safety

        Thesis: Constraint Discovery From Aborted Actions turns the seed bet into a mechanism: Use aborted or interrupted actions as evidence for hidden constraints.

        ## Landscape Sweep Summary
        The selector ranked records from the shared 500,000-record pool. The closest visible clusters are:
        - Learning-Based End-to-End Path Planning for Lunar Rovers with Safety Constraints (2021)
- Multi-Robot Planning Under Uncertain Travel Times and Safety Constraints (2019)
- Wasserstein Distributionally Robust Motion Planning and Control with Safety Constraints Using Conditional Value-at-Risk (2020)
- Coverage Trajectory Planning Problem on 3D Terrains with safety constraints for automated lawn mower: Exact and heuristic approaches (2025)
- Parallel Optimization with Hard Safety Constraints for Cooperative Planning of Connected Autonomous Vehicles (2024)
- Time Optimal Planning-Based High-Speed Running Motion Generation for Humanoid Robots with Safety Constraints (2023)
- Provably-correct stochastic motion planning with safety constraints (2013)
- Laparoscopic automatic following motion planning of minimally invasive surgery robot based on safety constraints (2022)
- Model predictive path planning with time-varying safety constraints for highway autonomous driving (2015)
- An efficient constraint method for solving planning problems under end-effector constraints (2024)
- Collision-Free Motion Planning for Human-Robot Collaborative Safety Under Cartesian Constraint (2018)
- Identification of physically consistent dynamics parameter of the ABB IRB 360-6/1600 delta robot and its use for time-optimal motion planning under consideration of constraint forces (2024)

        ## Hidden Assumptions
        - The executed trajectory is a sufficient training target.
- Unobserved physical alternatives can be averaged into uncertainty.
- Task labels capture the mechanism that caused failure.
- A planner only needs nominal feasibility.
- Embodiment-specific contact effects are nuisance variation.

        ## Boundary
        The project avoids weak moves such as bigger models, generic uncertainty, or a benchmark-only contribution. It centers a mechanism-level change: Constraint discovery from aborted actions keeps action-critical alternatives explicit until a physical observation collapses them.
