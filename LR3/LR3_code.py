import numpy as np
import matplotlib.pyplot as plt
from parser import Parser
from solver import DommelSolver

# ==================== НАСТРОЙКИ ПЛОТТИНГА ====================
CONFIG = {
    "json_file": "RLC_E_sin.json",        # путь к JSON-файлу схемы
    "time_steps": 1500,                 # количество шагов расчёта
    "plot_all": True,                  # True = рисовать для всех ветвей, False = только для selected_branches
    "selected_branches": [0, 1, 2],     # номера ветвей для отображения (индексы из elements в JSON)
    "plot_current": True,               # рисовать графики токов
    "plot_voltage": True,               # рисовать графики напряжений на элементах
}
# =============================================================

def get_component_label(comp, idx):
    """Формирует читаемую подпись для компонента на графике."""
    t = type(comp).__name__
    if t == "Resistor":
        return f"R{idx+1} = {comp.R} Ом"
    elif t == "Inductor":
        return f"L{idx+1} = {comp.L} Гн"
    elif t == "Capacitor":
        return f"C{idx+1} = {comp.C*1e6:.1f} Ф"
    elif t == "VoltageSource":
        freq = comp.freq
        label = f"E{idx+1} = {comp.volt} В"
        if freq > 0:
            label += f", {freq} Гц"
        return label
    elif t == "CurrentSource":
        return f"J{idx+1} = {comp.J0} А"

def plot_results(t_axis, U_history, I_history, components, config):
    """Строит графики токов и напряжений."""
    
    # Определяем, какие ветви показывать
    if config["plot_all"]:
        branches_to_plot = range(len(components))
    else:
        branches_to_plot = [b for b in config["selected_branches"] if 0 <= b < len(components)]

    # ---------- ГРАФИКИ ТОКОВ ----------
    if config["plot_current"]:
        plt.figure(figsize = (10, 6))
        for idx in branches_to_plot:
            comp = components[idx]
            label = get_component_label(comp, idx)
            plt.plot(t_axis, I_history[:, idx], label = f"I({label})")
        plt.xlabel("Время, с")
        plt.ylabel("Ток, А")
        plt.title("Токи в ветвях")
        plt.grid(True, alpha = 0.3)
        plt.legend(fontsize = 8, ncol = 2)
        plt.tight_layout()
        plt.show()

    # ---------- ГРАФИКИ НАПРЯЖЕНИЙ НА ЭЛЕМЕНТАХ ----------
    if config["plot_voltage"]:
        plt.figure(figsize = (10, 6))
        for idx in branches_to_plot:
            comp = components[idx]
            label = get_component_label(comp, idx)
            # Напряжение на элементе = разность потенциалов узлов
            U_elem = U_history[:, comp.get_node_begin()-1] if comp.get_node_begin() != 0 else 0
            if comp.get_node_end() != 0:
                U_elem -= U_history[:, comp.get_node_end()-1]
            # Для земли (узел 0) потенциал = 0, учтено выше
            plt.plot(t_axis, U_elem, label = f"U({label})")
        plt.xlabel("Время, с")
        plt.ylabel("Напряжение, В")
        plt.title("Напряжения на элементах")
        plt.grid(True, alpha = 0.3)
        plt.legend(fontsize = 8, ncol = 2)
        plt.tight_layout()
        plt.show()


def main():
    # 1. Парсинг схемы
    A, Y, E, J, components, dt = Parser(CONFIG["json_file"])

    # 2. Инициализация решателя
    solver = DommelSolver(A, Y, E, J, components, dt)

    # 3. Цикл расчёта
    U_history = []  # потенциалы узлов (без земли)
    I_history = []  # токи ветвей

    for step in range(CONFIG["time_steps"]):
        U_nodes, I_branches = solver.step()
        U_history.append(U_nodes.copy())
        I_history.append(I_branches.copy())

    # Конвертируем списки в массивы для удобной работы
    U_history = np.array(U_history)  # форма: (time_steps, n_free_nodes)
    I_history = np.array(I_history)  # форма: (time_steps, n_branches)
    t_axis = np.arange(1, CONFIG["time_steps"] + 1) * dt


    plot_results(t_axis, U_history, I_history, components, CONFIG)


if __name__ == "__main__":
    main()