# drive the network flow formulation with a minimum cost flow example
# Application of the model with a NERD example
# NERD currently has 5 CDC's and 12 RDC's

import pyomo.environ as pyo
from SupplyNetwork import NetworkFlow


Manufacturing = ["BFP", "SCP"]
CDC = ["BO", "NA", "PR", "SP", "WO"]
RDC = ["BO", "BR", "CO", "HA", "MN", "NA", "NH", "NL", "PO", "PR", "SP", "WO"]
S = {"BO": 1000, "NA": 500, "PR": 1000, "SP": 500, "WO": 1000}

T = {("BFP", "BO"): 3.4, ("BFP", "NA"): 3.00 , ("BFP", "PR"): 4.4,
     ("BFP", "SP"): 3.04, ("BFP", "WO"): 3.36, ("SCP", "BO"): 4.8,
     ("SCP", "NA"): 5.25, ("SCP", "PR"): 5.12, ("SCP", "SP"): 4, 
     ("SCP", "WO"): 4.2}
d = {("BO", "BO"): 8, ("BO", "BR"): 93, ("BO", "CO"): 69,
     ("BO", "HA"): 98, ("BO", "MN"): 55, ("BO", "NA"): 37,
     ("BO", "NH"): 128, ("BO", "NL"): 95, ("BO", "PO"): 62,
     ("BO", "PR"): 42, ("BO", "SP"): 82, ("BO", "WO"): 34,
     ("NA", "BO"): 37, ("NA", "BR"): 65, ("NA", "CO"): 33,
     ("NA", "HA"): 103, ("NA", "MN"): 20, ("NA", "NA"): 12,
     ("NA", "NH"): 137, ("NA", "NL"): 113, ("NA", "PO"): 48,
     ("NA", "PR"): 72, ("NA", "SP"): 79, ("NA", "WO"): 41,
     ("PR", "BO"): 42, ("PR", "BR"): 106, ("PR", "CO"): 105,
     ("PR", "HA"): 73, ("PR", "MN"): 92, ("PR", "NA"): 72,
     ("PR", "NH"): 94, ("PR", "NL"): 57, ("PR", "PO"): 104,
     ("PR", "PR"): 17, ("PR", "SP"): 68, ("PR", "WO"): 38,
     ("SP", "BO"): 82, ("SP", "BR"): 59, ("SP", "CO"): 101,
     ("SP", "HA"): 27, ("SP", "MN"): 93, ("SP", "NA"): 79,
     ("SP", "NH"): 63, ("SP", "NL"): 57, ("SP", "PO"): 127,
     ("SP", "PR"): 68, ("SP", "SP"): 12, ("SP", "WO"): 47,
     ("WO", "BO"): 34, ("WO", "BR"): 68, ("WO", "CO"): 72,
     ("WO", "HA"): 66, ("WO", "MN"): 60, ("WO", "NA"): 41,
     ("WO", "NH"): 98, ("WO", "NL"): 71, ("WO", "PO"): 85,
     ("WO", "PR"): 38, ("WO", "SP"): 47, ("WO", "WO"): 18}

D = {"BO": 450, "BR": 60, "CO": 80, "HA": 130, "MN": 110, "NA": 140, "NH": 140, "NL": 70, "PO": 120, "PR": 310,
     "SP": 200, "WO": 190}
F = {"BO": 11000, "NA": 5000, "PR": 9000, "SP": 8000, "WO": 7000}
V = {"BO": 1.5, "NA": 0.95, "PR": 1.05, "SP": 1.1, "WO": 1.12}
M = {"BFP": 2.00, "SCP": 0.75}
service_mile = 50
Cost_per_mile = 0.55
Capital = 35000
Service_level = 0.97

# No constraint on the arc's
K2 = dict()
for a in CDC:
     for b in RDC:
          K2[(a,b)] = None

K1 = dict()
for a in Manufacturing:
     for b in CDC:
          K1[(a,b)] = None

model = NetworkFlow(Manufacturing, CDC, RDC, D, d, S, F, V, K1, K2, M, T, service_mile, Cost_per_mile, Service_level, Capital)


opt = pyo.SolverFactory('ipopt')
results = opt.solve(model)
pyo.assert_optimal_termination(results)

model.pprint()
Total_cost = pyo.value(model.MinCost)
print(Total_cost)


print("************Total Cost*************")
Total_cost = pyo.value(model.MinCost)
Fixed_Cost = sum((F[n] * pyo.value(model.indicator[n]))for n in CDC)
Transportation_cost =sum(d[i, j] * Cost_per_mile * pyo.value(model.flow_CDC_RDC[i, j]) for i in CDC for j in RDC)
Variable_cost = sum(V[i] * sum(pyo.value(model.flow_CDC_RDC[i, j]) for j in RDC) for i in CDC)

print("{:<24} {:<1} {:>6}".format("Fixed Cost for CDC's:","$", round(Fixed_Cost)))
print("{:<24} {:<1} {:>6}".format("Variable Cost for CDC's:","$", round(Variable_cost)))
print("{:<24} {:<1} {:>6}".format("Transportation Cost :","$",round(Transportation_cost)))
print("--"*25)
print("{:<24} {:<1} {:>6}".format("Total Cost :","$",  round(Total_cost)))

print()
print("************Product Flow***********")
X =dict()
print("{:<10} {:<10} {:>11}".format("CDC", "RDC", "FLow Quantity"))
print("--"*25)
for a in CDC:
     for b in RDC:
          X[a, b] = pyo.value(model.flow_CDC_RDC[a, b]) 
          if X[a, b] >0:
               print("{:<10} {:<10} {:>11}".format(a, b, round(X[a, b])))
print('')

print("********Which CDC's to Open********")
Binary = dict()
print("{:<15} {:>17}".format("CDC", "Quantity Supplied"))
print("--"*25)
for a in CDC:
     Binary[a] = pyo.value(model.indicator[a])
     if Binary[a]>0:
          flow = sum(pyo.value(model.flow_CDC_RDC[a, n])for n in RDC)
          print("{:<15} {:>17}".format(a, round(flow)))
