# Network Flow - various formulations

import pyomo.environ as pyo


def NetworkFlow(Manufacturing, CDC, RDC, D, d, S, F, V, K1, K2, M, T, service_mile, Cost_per_mile, Service_level, Capital,
                sense=pyo.minimize):
    """
    Args:
        Manufacturing : Manufacturing facilities
        CDC (tuple of warehouses) : set of Warehouses
        RDC (tuple of demand regions) : set of demand regions
        d (dict[a][a'] of float) : distance between CDC's and RDC's.
        D (dict[a] of float) : demand for the RDC
        K (dict[a] of float): capacity of each arc
        F (dict[a] of float) : fixed cost of the CDC facility
        S (dic[a] of float) : capacity of CDC facilities
        V (dict[a] of float) : Variable cost for CDC's
        sense: Objective maximization or minimization
        Service_level: required service lelvel
        service_mile : Distance the WH can service
        Cost_per_mile : Cost of transporting unit product for one mile
        Capital : Total budget available

    Returns:
        model (Pyomo ConcreteModel) : the instantiated model
    """

    # creating calaulated paprmeter A = {0,1} - 1 if d_ij>Service distance,0 otherwise
    A = dict()
    for a in CDC:
        for b in RDC:
            if d[a, b] <= service_mile:
                A[a, b] = 1
            else:
                A[a, b] = 0

    # Creating a big number for linking constraint
    B = sum(D[b] for b in D)

    # Creating a model
    model = pyo.ConcreteModel(name='MinCostFlow')

    # Creating boundaries for the arcs with capacity K
    def bounds_rule2(m, i,j):
        return (0, K2[(i,j)])
    def bounds_rule1(m, i,j):
        return (0, K1[(i,j)])

    
    # Giving the model decision variable x_ij
    model.flow_manufacturing_CDC = pyo.Var(Manufacturing, CDC, bounds = bounds_rule1)
    model.flow_CDC_RDC = pyo.Var(CDC, RDC, bounds=bounds_rule2)

    # Giving the model binary decision variable y_i
    model.indicator = pyo.Var(CDC, domain=pyo.Binary)  # delta

    # Objective function for the model
    model.MinCost = pyo.Objective(expr=\
                                        sum(M[a] * sum(model.flow_manufacturing_CDC[a, b] for b in CDC) for a in Manufacturing)\
                                        +sum(T[a, b] * model.flow_manufacturing_CDC[a, b] for a in Manufacturing for b in CDC)\
                                        +sum(d[a, b] * Cost_per_mile * model.flow_CDC_RDC[a, b] for a in CDC for b in RDC)\
                                       + sum(F[a] * model.indicator[a] for a in CDC)\
                                       + sum(V[a] * sum(model.flow_CDC_RDC[a, b] for b in RDC) for a in CDC), 
                                  sense=sense)

    # Supply constraint of the CDC facilities
    def Supply_Constraint(m, n):
        return sum(m.flow_CDC_RDC[n, a] for a in RDC) <= S[n]

    model.Supply = pyo.Constraint(CDC, rule=Supply_Constraint)

    # Demand Constraint of the Regionale DC's
    def Demand_Constraint(m, n):
        return sum(m.flow_CDC_RDC[a, n] for a in CDC) >= D[n]

    model.Demand = pyo.Constraint(RDC, rule=Demand_Constraint)

    # Linking constraint for the model
    def Indicator_rule(m, n):
        return m.indicator[n] * B >= sum(m.flow_CDC_RDC[n, a] for a in RDC)

    model.make_indicator = pyo.Constraint(CDC, rule=Indicator_rule)

    # Total capital constraint
    def Capital_constraint(m):
        return sum(F[a] * m.indicator[a] for a in CDC) <= Capital

    model.Capital = pyo.Constraint(rule=Capital_constraint)

    # Flow constraint
    def Flow_constraint(m, n):
        return sum(m.flow_manufacturing_CDC[a, n] for a in Manufacturing) == sum(m.flow_CDC_RDC[n, b] for b in RDC)

    model.Flow = pyo.Constraint(CDC, rule=Flow_constraint)

    # Service constraint of the model
    def Service_constraint(m):
        return sum(A[a, b] * m.flow_CDC_RDC[a, b] for a in CDC for b in RDC)/B >= Service_level

    model.service = pyo.Constraint(rule=Service_constraint)

    return model
