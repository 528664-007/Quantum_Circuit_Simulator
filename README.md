Quantum Circuit Simulator
A web-based application to build, visualize, and simulate quantum circuits using Qiskit, FastAPI, and React. Create custom quantum circuits by adding gates (e.g., Hadamard, CNOT), load example circuits (e.g., Bell State), and simulate results with histograms.
 (Replace with an actual screenshot)
Features

Interactive Circuit Building: Add quantum gates (Hadamard, Pauli-X, CNOT, Controlled-Z, Measure) to a circuit with 1–5 qubits.
Example Circuits: Load pre-built circuits like Bell State (entanglement) or Grover's Algorithm (2-qubit search).
Simulation: Run simulations with 100–10,000 shots using Qiskit’s AerSimulator.
Visualization: Display circuit diagrams and result histograms as PNG images.
Responsive UI: Built with React and Tailwind CSS for a modern, user-friendly interface.
Error Handling: Detailed error messages for invalid inputs or simulation failures.

Technologies

Backend: Python 3.12, FastAPI, Qiskit 1.0+, qiskit-aer 0.17.2, Matplotlib, pylatexenc
Frontend: React 18.2.0, Tailwind CSS, Babel (for JSX)
Deployment: Uvicorn server, Jinja2 templates

Prerequisites

Python 3.12 (Windows Store distribution or standard)
Git
A modern web browser (e.g., Chrome, Firefox)
Optional: PowerShell or Command Prompt for Windows

Setup Instructions (Windows)

Clone the Repository:
git clone https://github.com/your-username/quantum-circuit-simulator.git
cd quantum-circuit-simulator


Create and Activate a Virtual Environment:
python -m venv venv
.\venv\Scripts\activate

Or in Command Prompt:
python -m venv venv
venv\Scripts\activate


Install Dependencies:

Ensure requirements.txt contains:fastapi
uvicorn
qiskit
qiskit-aer
matplotlib
python-multipart
jinja2
pillow
pycairo
pylatexenc


Install:pip install -r requirements.txt




Verify File Structure:
quantum-circuit-simulator/
├── static/
│   ├── css/
│   │   └── style.css
│   └── assets/
│       └── screenshot.png (optional)
├── templates/
│   └── index.html
├── app.py
├── requirements.txt
└── README.md


Run the Application:
uvicorn app:app --reload


Open http://127.0.0.1:8000 in your browser (tested at 11:44 AM IST, October 17, 2025).



Usage

Build a Circuit:

Select the number of qubits (1–5) using the slider.
Choose a gate (e.g., Hadamard, CNOT) and specify target/control qubits.
Click "Add Gate" to update the circuit.
View the circuit diagram in the main panel.


Load Examples:

Select "Bell State (Entanglement)" or "Grover's Algorithm (2-Qubit Search)" from the dropdown.
The circuit diagram updates automatically.


Simulate:

Set the number of shots (100–10,000).
Click "Simulate Circuit" to run the simulation and view the histogram.


Reset:

Click "Reset Circuit" to clear gates and start over.



Troubleshooting

"Failed to add gate" Error:

Check browser console (F12 → Console) for errors like HTTP 422.
Verify control_qubit is only sent for CNOT/CZ gates.
Test the endpoint:curl -X POST http://127.0.0.1:8000/add_gate -H "Content-Type: application/json" -d "{\"gate_type\":\"H (Hadamard)\",\"target_qubit\":0,\"qubits\":2}"




Plots Not Generating:

Ensure pylatexenc, pillow, and matplotlib are installed:pip show qiskit qiskit-aer matplotlib pillow pycairo pylatexenc


Test Matplotlib:python -c "from qiskit import QuantumCircuit; import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt; circuit = QuantumCircuit(1); circuit.h(0); circuit.draw(output='mpl'); plt.savefig('circuit_test.png')"




Blank Page on Add Gate:

Ensure index.html includes event.preventDefault() in the addGate function.
Check for JavaScript errors in the browser console.



Contributing

Fork the repository.
Create a branch (git checkout -b feature/your-feature).
Commit changes (git commit -m "Add your feature").
Push to the branch (git push origin feature/your-feature).
Open a Pull Request.

License
This project is licensed under the MIT License. See the LICENSE file for details.
Acknowledgments

Built with Qiskit for quantum circuit simulation.
Powered by FastAPI and React.
Styled with Tailwind CSS.

Contact
For issues or suggestions, open an issue on GitHub or contact [your-email@example.com].
