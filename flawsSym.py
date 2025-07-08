import sympy as sp

# symbols
p, q, d, l, F, T = sp.symbols('p q d l F T')

# equations
eq1 = sp.Eq(q*F - p*T, 0)
eq2 = sp.Eq((q + d)*F - p*T, l)

# solve
solution = sp.solve((eq1, eq2), (F, T))

F_sol = solution[F]   # l/d
T_sol = solution[T]   # l*q/(p*d)

print("F =", F_sol)
print("T =", T_sol)
