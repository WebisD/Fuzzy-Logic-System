import numpy as np
import skfuzzy as fuzz
from matplotlib import pyplot as plt
from skfuzzy.control import Antecedent, Consequent, Rule, ControlSystem, ControlSystemSimulation

from Fuzzifier import Fuzzifier


class PendulumStabilizationFuzzifier(Fuzzifier):
    cart_position: Antecedent
    cart_velocity: Antecedent

    def define_antecedents(self) -> None:
        # region angle
        self.angle = Antecedent(np.arange(-30, 30, 0.5), 'angle')

        self.angle['NVB'] = fuzz.trapmf(self.angle.universe, [-30, -30, -18, -12])
        self.angle['NB'] = fuzz.trimf(self.angle.universe, [-16.5, -10.5, -4.5])
        self.angle['N'] = fuzz.trimf(self.angle.universe, [-9, -4.5, 0])
        self.angle['ZO'] = fuzz.trimf(self.angle.universe, [-3, 0, 3])
        self.angle['P'] = fuzz.trimf(self.angle.universe, [0, 4.5, 9])
        self.angle['PB'] = fuzz.trimf(self.angle.universe, [4.5, 10.5, 16.5])
        self.angle['PVB'] = fuzz.trapmf(self.angle.universe, [12, 18, 30, 30])
        # endregion

        # region angular velocity
        self.angular_velocity = Antecedent(np.arange(-6, 6, 0.1), 'angularVelocity')

        self.angular_velocity['NB'] = fuzz.trapmf(self.angular_velocity.universe, [-6, -6, -4.2, -1.7])
        self.angular_velocity['N'] = fuzz.trimf(self.angular_velocity.universe, [-3.6, -1.7, 0])
        self.angular_velocity['ZO'] = fuzz.trimf(self.angular_velocity.universe, [-1.7, 0, 1.7])
        self.angular_velocity['P'] = fuzz.trimf(self.angular_velocity.universe, [0, 1.7, 3.6])
        self.angular_velocity['PB'] = fuzz.trapmf(self.angular_velocity.universe, [1.7, 4.2, 6, 6])
        # endregion

        # region cart position
        self.cart_position = Antecedent(np.arange(-0.4, 0.4, 0.05), 'cartPosition')

        self.cart_position['NBIG'] = fuzz.trapmf(self.cart_position.universe, [-0.4, -0.4, -0.3, -0.15])
        self.cart_position['NEG'] = fuzz.trimf(self.cart_position.universe, [-0.3, -0.15, 0])
        self.cart_position['Z'] = fuzz.trimf(self.cart_position.universe, [-0.15, 0, 0.15])
        self.cart_position['POS'] = fuzz.trimf(self.cart_position.universe, [0, 0.15, 0.3])
        self.cart_position['PBIG'] = fuzz.trapmf(self.cart_position.universe, [0.15, 0.3, 0.4, 0.4])
        # endregion

        # region cart_velocity
        self.cart_velocity = Antecedent(np.arange(-1, 1, 0.1), 'cartVelocity')

        self.cart_velocity['NEG'] = fuzz.trapmf(self.cart_velocity.universe, [-1, -1, -0.1, 0])
        self.cart_velocity['ZERO'] = fuzz.trimf(self.cart_velocity.universe, [-0.1, 0, 0.1])
        self.cart_velocity['POS'] = fuzz.trapmf(self.cart_velocity.universe, [0, 0.1, 1, 1])
        # endregion

    def define_rules(self) -> None:
        self.rules = [
            Rule(self.cart_position['NBIG'] & self.cart_velocity['NEG'], self.applied_force['PVVB']),
            Rule(self.cart_position['NEG'] & self.cart_velocity['NEG'], self.applied_force['PVB']),
            Rule(self.cart_position['Z'] & self.cart_velocity['NEG'], self.applied_force['PB']),
            Rule(self.cart_position['Z'] & self.cart_velocity['ZERO'], self.applied_force['Z']),
            Rule(self.cart_position['Z'] & self.cart_velocity['POS'], self.applied_force['NB']),
            Rule(self.cart_position['POS'] & self.cart_velocity['POS'], self.applied_force['NVB']),
            Rule(self.cart_position['PBIG'] & self.cart_velocity['POS'], self.applied_force['NVVB']),

            Rule(self.angle['NVB'] & self.angular_velocity['NB'], self.applied_force['NVVB']),
            Rule(self.angle['NVB'] & self.angular_velocity['N'], self.applied_force['NVVB']),
            Rule(self.angle['NVB'] & self.angular_velocity['ZO'], self.applied_force['NVB']),
            Rule(self.angle['NVB'] & self.angular_velocity['P'], self.applied_force['NB']),
            Rule(self.angle['NVB'] & self.angular_velocity['PB'], self.applied_force['N']),

            Rule(self.angle['NB'] & self.angular_velocity['NB'], self.applied_force['NVVB']),
            Rule(self.angle['NB'] & self.angular_velocity['N'], self.applied_force['NVB']),
            Rule(self.angle['NB'] & self.angular_velocity['ZO'], self.applied_force['NB']),
            Rule(self.angle['NB'] & self.angular_velocity['P'], self.applied_force['N']),
            Rule(self.angle['NB'] & self.angular_velocity['PB'], self.applied_force['Z']),

            Rule(self.angle['N'] & self.angular_velocity['NB'], self.applied_force['NVB']),
            Rule(self.angle['N'] & self.angular_velocity['N'], self.applied_force['NB']),
            Rule(self.angle['N'] & self.angular_velocity['ZO'], self.applied_force['N']),
            Rule(self.angle['N'] & self.angular_velocity['P'], self.applied_force['Z']),
            Rule(self.angle['N'] & self.angular_velocity['PB'], self.applied_force['P']),

            Rule(self.angle['ZO'] & self.angular_velocity['NB'], self.applied_force['NB']),
            Rule(self.angle['ZO'] & self.angular_velocity['N'], self.applied_force['N']),
            Rule(self.angle['ZO'] & self.angular_velocity['ZO'], self.applied_force['Z']),
            Rule(self.angle['ZO'] & self.angular_velocity['P'], self.applied_force['P']),
            Rule(self.angle['ZO'] & self.angular_velocity['PB'], self.applied_force['PB']),

            Rule(self.angle['P'] & self.angular_velocity['NB'], self.applied_force['N']),
            Rule(self.angle['P'] & self.angular_velocity['N'], self.applied_force['Z']),
            Rule(self.angle['P'] & self.angular_velocity['ZO'], self.applied_force['P']),
            Rule(self.angle['P'] & self.angular_velocity['P'], self.applied_force['PB']),
            Rule(self.angle['P'] & self.angular_velocity['PB'], self.applied_force['PVB']),

            Rule(self.angle['PB'] & self.angular_velocity['NB'], self.applied_force['Z']),
            Rule(self.angle['PB'] & self.angular_velocity['N'], self.applied_force['P']),
            Rule(self.angle['PB'] & self.angular_velocity['ZO'], self.applied_force['PB']),
            Rule(self.angle['PB'] & self.angular_velocity['P'], self.applied_force['PVB']),
            Rule(self.angle['PB'] & self.angular_velocity['PB'], self.applied_force['PVVB']),

            Rule(self.angle['PVB'] & self.angular_velocity['NB'], self.applied_force['P']),
            Rule(self.angle['PVB'] & self.angular_velocity['N'], self.applied_force['PB']),
            Rule(self.angle['PVB'] & self.angular_velocity['ZO'], self.applied_force['PVB']),
            Rule(self.angle['PVB'] & self.angular_velocity['P'], self.applied_force['PVVB']),
            Rule(self.angle['PVB'] & self.angular_velocity['PB'], self.applied_force['PVVB'])
        ]

    def plot_antecedents(self) -> None:
        self.angle.view()
        self.angular_velocity.view()
        self.cart_position.view()
        self.cart_velocity.view()
        plt.show()

    def simulate(self, attrs: 'list[float]') -> float:
        input_angle,  input_angular_velocity, input_cart_position, input_cart_velocity = attrs
        simulation = ControlSystemSimulation(ControlSystem(self.rules))

        simulation.input['angle'] = input_angle
        simulation.input['angularVelocity'] = input_angular_velocity
        simulation.input['cartPosition'] = input_cart_position
        simulation.input['cartVelocity'] = input_cart_velocity
        simulation.compute()

        applied_force_value = simulation.output['appliedForce']

        self.plot_simulation(simulation)

        return applied_force_value

    def plot_simulation(self, simulation: ControlSystemSimulation) -> None:
        self.angle.view(simulation)
        self.angular_velocity.view(simulation)
        self.cart_position.view(simulation)
        self.cart_velocity.view(simulation)
        self.applied_force.view(simulation)

        plt.show()
