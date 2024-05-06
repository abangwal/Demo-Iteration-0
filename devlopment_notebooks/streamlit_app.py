import streamlit as st
from streamlit_tree_select import tree_select
import json
from dynamic_input import DynamicInput

st.title("🧑‍🔬 Researcher Pro")

col1, col2 = st.columns(2)

st.session_state.submit = False
if "generated" not in st.session_state:
    st.session_state.generated = False
if "data" not in st.session_state:
    st.session_state.data = {"dummy": ["dummy"]}

with col1:

    user_input = st.text_input("Business/Industry", "Smart home appliances")
    user_input += " business analysis"

    def clicked():
        st.session_state.submit = True

    st.button(label="Submit", on_click=clicked)

    if st.session_state.submit == True:

        if (
            st.session_state.generated == False
            or list(st.session_state.data.keys())[0] != user_input
        ):
            with st.spinner(text="Please wait..."):
                st.session_state.data = DynamicInput().run(user_input)
            st.session_state.generated = True
        else:
            data = st.session_state.data

        data = st.session_state.data
        query = list(data.keys())[0]

        st.subheader(query)
        st.write("Select the components to be included in final report")
        nodes = []

        for sub_task in data[query]:
            children = []
            for datapoint in data[query][sub_task]:
                children.append({"label": datapoint[0], "value": datapoint[1]})

            final_node = {"label": sub_task, "value": sub_task, "children": children}
            nodes.append(final_node)

        return_select = tree_select(
            nodes, check_model="leaf", only_leaf_checkboxes=True, show_expand_all=True
        )

with col2:
    st.subheader("Report elements")
    if st.session_state.submit == True:
        st.write("\n* ".join(return_select["checked"]))
