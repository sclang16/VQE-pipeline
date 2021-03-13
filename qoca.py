from typing import Optional, Union, List, Tuple

from qiskit import QuantumRegister, QuantumCircuit
from qiskit.circuit import Gate, Parameter
from qiskit.qasm import pi

from qiskit.aqua import aqua_globals
from qiskit.aqua.components.initial_states import InitialState, Zero
from qiskit.aqua.operators import WeightedPauliOperator, Z2Symmetries
from qiskit.aqua.components.variational_forms import VariationalForm
from qiskit.chemistry.fermionic_operator import FermionicOperator

from g import GGate
from zx import ZXGate
from zy import ZYGate

class QOCA(VariationalForm):
    def __init__(self, num_qubits: Optional[int] = 4, reps: int = 1, initial_state: Optional[InitialState] = Zero) -> None:
        super().__init__()

        self._num_qubits = num_qubits
        #self._num_particles = num_particles
        #self._num_spin_orbitals = num_spin_orbitals
        self._reps = reps
        self._initial_state = initial_state
        self._support_parameterized_circuit = True

        self._num_parameters = 2 * self._num_qubits

        # Qubit mapping requirements?
        # How to get num_qubits, since it likely will depend on H^?
        # What is being treated as H^?
        # Pick operator evolution for H^ (likely MatrixEvolution) - in constructor or subfunction?
    
    def num_qubits(self) -> int:
        
        return self._num_qubits

    def num_qubits(self, num_qubits: int) -> None:
        
        self._num_qubits = num_qubits

    def add_drive_layer(self, circuit: QuantumCircuit, layer_parameters: List[Parameter]):
        
        circuit.ry(layer_parameters[0],0)
        circuit.rx(layer_parameters[1],0)

        for i in range(self._num_qubits-1):
            circuit.append(ZYGate(layer_parameters[(2*i)+2]),[i,i+1],[])
            circuit.append(ZXGate(layer_parameters[(2*i)+3]),[i,i+1],[])
            circuit.cx(i,i+1)
        
        for i in range(self._num_qubits-2, 0, -1):
            circuit.cx(i-1,i)
        
        return circuit

    def construct_circuit(self, parameters: List[Parameter] = None, q: Optional[QuantumRegister] = None):

        if q is None:
            q = QuantumRegister(self._num_qubits,name='q')
        
        circuit = QuantumCircuit(q)

        if parameters is None:
            parameters = []
            [parameters.append(0) for i in range(self._num_parameters*self._reps)]

        for layer in range(self._reps):
            layer_params = parameters[(layer*self._num_parameters):((layer+1)*self._num_parameters)]
            self.add_drive_layer(circuit, layer_params)

        return circuit