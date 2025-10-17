from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import base64
import io
import logging
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
from qiskit.circuit.library import GroverOperator
import matplotlib
matplotlib.use('Agg')  # Set non-interactive backend
import matplotlib.pyplot as plt

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# In-memory circuit state
circuit_state = {"circuit": None, "gates": [], "qubits": 2}

class GateRequest(BaseModel):
    gate_type: str
    target_qubit: int | None = None
    control_qubit: int | None = None
    qubits: int

def circuit_to_base64(circuit, is_histogram=False):
    try:
        logger.debug("Generating plot for %s", "histogram" if is_histogram else "circuit")
        plt.figure()
        if is_histogram:
            plot_histogram(circuit).figure
        else:
            circuit.draw(output='mpl')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode('utf-8')
        logger.debug("Plot generated successfully")
        return img_data
    except Exception as e:
        logger.error(f"Error in circuit_to_base64 (is_histogram={is_histogram}): {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate image: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        with open("templates/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except Exception as e:
        logger.error(f"Error serving index.html: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load index.html")

@app.get("/reset")
async def reset_circuit(qubits: int):
    try:
        if not (1 <= qubits <= 5):
            raise HTTPException(status_code=400, detail="Qubits must be between 1 and 5")
        circuit_state["qubits"] = qubits
        circuit_state["circuit"] = QuantumCircuit(qubits, qubits)
        circuit_state["gates"] = []
        logger.debug(f"Circuit reset with {qubits} qubits")
        return {"gates": circuit_state["gates"], "circuit_image": None}
    except Exception as e:
        logger.error(f"Error in reset_circuit: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to reset circuit: {str(e)}")

@app.get("/load_example")
async def load_example(example: str, qubits: int):
    try:
        if not (1 <= qubits <= 5):
            raise HTTPException(status_code=400, detail="Qubits must be between 1 and 5")
        circuit_state["qubits"] = qubits
        circuit_state["circuit"] = QuantumCircuit(qubits, qubits)
        circuit_state["gates"] = []

        if example == "Bell State (Entanglement)":
            if qubits < 2:
                raise HTTPException(status_code=400, detail="Bell State requires at least 2 qubits")
            circuit_state["circuit"].h(0)
            circuit_state["circuit"].cx(0, 1)
            circuit_state["gates"] = [("H", 0), ("CX", 0, 1)]
        elif example == "Grover's Algorithm (2-Qubit Search)":
            if qubits != 2:
                raise HTTPException(status_code=400, detail="Grover's example requires exactly 2 qubits")
            oracle = QuantumCircuit(2)
            oracle.cz(0, 1)
            grover_op = GroverOperator(oracle)
            circuit_state["circuit"].h([0, 1])
            circuit_state["circuit"].append(grover_op, [0, 1])
            circuit_state["gates"] = [("H", [0, 1]), ("Grover Operator", [0, 1])]
        else:
            raise HTTPException(status_code=400, detail="Invalid example")

        circuit_image = circuit_to_base64(circuit_state["circuit"])
        logger.debug(f"Loaded example: {example}")
        return {"gates": circuit_state["gates"], "circuit_image": circuit_image}
    except Exception as e:
        logger.error(f"Error in load_example: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to load example: {str(e)}")

@app.post("/add_gate")
async def add_gate(request: GateRequest):
    try:
        logger.debug(f"Received add_gate payload: {request.dict()}")
        if circuit_state["circuit"] is None or circuit_state["qubits"] != request.qubits:
            circuit_state["qubits"] = request.qubits
            circuit_state["circuit"] = QuantumCircuit(request.qubits, request.qubits)
            circuit_state["gates"] = []

        if request.gate_type not in ["H (Hadamard)", "X (Pauli-X)", "CX (CNOT)", "CZ (Controlled-Z)", "Measure"]:
            raise HTTPException(status_code=400, detail="Invalid gate type")

        if request.gate_type != "Measure":
            if request.target_qubit is None or not (0 <= request.target_qubit < request.qubits):
                raise HTTPException(status_code=400, detail="Invalid target qubit")
            if request.gate_type in ["CX (CNOT)", "CZ (Controlled-Z)"]:
                if request.control_qubit is None or not (0 <= request.control_qubit < request.qubits):
                    raise HTTPException(status_code=400, detail="Invalid control qubit")
                if request.control_qubit == request.target_qubit:
                    raise HTTPException(status_code=400, detail="Control and target qubits must be different")

        if request.gate_type == "H (Hadamard)":
            circuit_state["circuit"].h(request.target_qubit)
            circuit_state["gates"].append(("H", request.target_qubit))
        elif request.gate_type == "X (Pauli-X)":
            circuit_state["circuit"].x(request.target_qubit)
            circuit_state["gates"].append(("X", request.target_qubit))
        elif request.gate_type == "CX (CNOT)":
            circuit_state["circuit"].cx(request.control_qubit, request.target_qubit)
            circuit_state["gates"].append(("CX", request.control_qubit, request.target_qubit))
        elif request.gate_type == "CZ (Controlled-Z)":
            circuit_state["circuit"].cz(request.control_qubit, request.target_qubit)
            circuit_state["gates"].append(("CZ", request.control_qubit, request.target_qubit))
        elif request.gate_type == "Measure":
            circuit_state["circuit"].measure(range(request.qubits), range(request.qubits))
            circuit_state["gates"].append(("Measure", "All"))

        circuit_image = circuit_to_base64(circuit_state["circuit"])
        logger.debug(f"Added gate: {request.gate_type}")
        return {"gates": circuit_state["gates"], "circuit_image": circuit_image}
    except Exception as e:
        logger.error(f"Error in add_gate: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add gate: {str(e)}")

@app.get("/simulate")
async def simulate_circuit(shots: int):
    try:
        if not (100 <= shots <= 10000):
            raise HTTPException(status_code=400, detail="Shots must be between 100 and 10000")
        if circuit_state["circuit"] is None:
            raise HTTPException(status_code=400, detail="No circuit defined")

        # Add measurement if not present
        if "Measure" not in [g[0] for g in circuit_state["gates"]]:
            circuit_state["circuit"].measure(range(circuit_state["qubits"]), range(circuit_state["qubits"]))
            circuit_state["gates"].append(("Measure", "All"))

        simulator = AerSimulator()
        logger.debug(f"Running simulation with {shots} shots")
        result = simulator.run(circuit_state["circuit"], shots=shots).result()
        counts = result.get_counts(circuit_state["circuit"])
        logger.debug(f"Simulation results: {counts}")

        circuit_image = circuit_to_base64(circuit_state["circuit"])
        histogram_image = circuit_to_base64(counts, is_histogram=True)
        return {"circuit_image": circuit_image, "histogram_image": histogram_image}
    except Exception as e:
        logger.error(f"Error in simulate_circuit: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to simulate circuit: {str(e)}")