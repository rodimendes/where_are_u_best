import streamlit as st
import pandas as pd

# st.title("Where U are best")

# materials_list = ["banana", "laranja"]

# col1, col2, col3 = st.columns(3)


# for pos, product in enumerate(selected_product):
#     with col1:
#         st.subheader(f"{pos + 1}° produto:")
#         st.write(product)
#         with col2:
#             st.number_input("Quantidade:", min_value=0, value=0, key=pos)
#             with col3:
#                 st.image(f"{product}.jpeg", width=100)
#     st.write("---")

##############

produtos = {
        "1000 mm": {
            "ripa 1000x100x10": 10,
            "prego": 50,
        },
        "1200 mm": {
            "ripa 1200x100x10": 12,
            "prego": 75,
        },
        "1500 mm": {
            "ripa 1500x100x10": 15,
            "prego": 100,
        },
    }


# selected_product = st.multiselect("Escolha seu produto", produtos, help="Clique ou digite o nome do produto desejado.")
# quantidade = st.number_input("Quantidade:", min_value=1, step=1)

# pedido = {}

# if st.button("Inserir"):
#     for escolha in selected_product:
#         pedido[selected_product[0]] = quantidade
#         st.subheader(f"**{escolha.capitalize()}**")
#         st.write("Insumos necessários:")
#         for key, value in produtos[escolha].items():
#             st.write(f"{value * quantidade} unidades de {key}")
#         produtos.pop(selected_product[0])
    # st.write(pedido)
    # st.write(produtos)

###############


selected_product = st.selectbox("Escolha seu produto", produtos, help="Clique ou digite o nome do produto desejado.")
quantidade = st.number_input("Quantidade:", min_value=1, step=1)

pedido = {}

if st.button("Inserir"):
    pedido[selected_product] = quantidade
    st.subheader(f"Palete de **{selected_product.capitalize()}**")
    st.write("Insumos necessários:")

    for key, value in produtos[selected_product].items():
        st.write(f"{key.capitalize()} - {value * quantidade} unidades.")
    # produtos.pop(selected_product)
# st.write(pedido)
# st.write(produtos)
