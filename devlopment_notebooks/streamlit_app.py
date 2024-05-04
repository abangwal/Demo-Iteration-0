import streamlit as st
from streamlit_tree_select import tree_select
import json


with open("example.json", "r") as file:
    data = json.load(file)


query = list(data.keys())[0]

st.title("🧑‍🔬 Researcher Pro")
st.subheader(query)
nodes = []

for sub_task in data[query]:
    children = []
    for datapoint in data[query][sub_task]:
        children.append({"label": datapoint[0], "value": datapoint[1]})

    final_node = {"label": sub_task, "value": sub_task, "children": children}
    nodes.append(final_node)

return_select = tree_select(nodes)
st.write(return_select)
