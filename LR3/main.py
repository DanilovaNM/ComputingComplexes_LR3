from parser import Parser
import numpy
from solver import DommelSolver  # ваш файл с DommelSolver
import matplotlib.pyplot as plt

# 1. Парсим схему
A, Y, E, J, components, dt = Parser("RL_circ.json")

# 2. Создаём решатель
solver = DommelSolver(A, Y, E, J, components, dt)

# 3. Цикл расчёта
time_steps = 1000
U_history = []
I_history = []

for _ in range(time_steps):
    U_nodes, I_branches = solver.step()
    U_history.append(U_nodes.copy())
    I_history.append(I_branches.copy())

# 4. Визуализация (пример для первого узла и первой ветви)
U_history = numpy.array(U_history)
I_history = numpy.array(I_history)
t_axis = numpy.arange(1, time_steps + 1) * dt

plt.plot(t_axis, U_history[:, 0], label = "U_node_1")
plt.plot(t_axis, I_history[:, 0], label = "I_branch_1")
plt.xlabel("Time, s")
plt.grid(True)
plt.legend()
plt.show()