import inspect
from langgraph.graph import StateGraph

print('Signature:', inspect.signature(StateGraph.add_conditional_edges))
print(inspect.getsource(StateGraph.add_conditional_edges))
