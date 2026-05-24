import inspect
from langgraph.graph.message import add_messages
from langgraph.graph.state import StateGraph

print('add_messages source:')
print(inspect.getsource(add_messages))
print('StateGraph type validation source:')
import langgraph.graph.state as s
print(inspect.getsource(s.StateGraph.validate))
