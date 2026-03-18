import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from itertools import product, combinations

st.set_page_config(page_title='Packing tridimensional')

# Título da pagina (interface streamlit)
st.markdown('<h1 style="text-align: center; font-size: 30px;">📦 Packing tridimensional de produtos</h1>', unsafe_allow_html=True)
st.write('___________')

# Dicionário com as dimensões das caixas
caixas = {
    'Miniload': {'Altura': 30, 'Largura': 36, 'Comprimento': 56, 'Peso': 2.58},
    'CS1': {'Altura': 20, 'Largura': 36, 'Comprimento': 56, 'Peso': 2.10},
    'CS2': {'Altura': 20, 'Largura': 18, 'Comprimento': 56, 'Peso': 2.43},
    'CS4': {'Altura': 20, 'Largura': 18, 'Comprimento': 28, 'Peso': 2.51},
    'Flow Altos': {'Altura': 22, 'Largura': 35, 'Comprimento': 50, 'Peso': 1.56},
    'Flow Altos 6': {'Altura': 22, 'Largura': 23, 'Comprimento': 50, 'Peso': 1.16},    
    'Flow Rack': {'Altura': 18, 'Largura': 28, 'Comprimento': 37, 'Peso': 1.05}
}

# Função para desenhar a caixa e os produtos
def draw_packing(box_dims, item_dims, positions):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
            
    # Desenhar a caixa
    r = [0, box_dims[0]], [0, box_dims[1]], [0, box_dims[2]]
    for s, e in combinations(np.array(list(product(*r))), 2):
        if np.sum(np.abs(s-e)) == r[0][1] - r[0][0]:
            ax.plot3D(*zip(s, e), color="r")
            
    # Desenhar os produtos
    for pos, dims in positions:
        x, y, z = pos
        dx, dy, dz = dims
        ax.bar3d(x, y, z, dx, dy, dz, color='b', alpha=0.5)
            
    ax.set_xlabel('Comprimento')
    ax.set_ylabel('Largura')
    ax.set_zlabel('Altura')
    return fig

def calculate_packing(box_dims, item_dims, box_weight, item_weight, weight_limit):
    orientations = [
        (item_dims[0], item_dims[1], item_dims[2]),
        (item_dims[0], item_dims[2], item_dims[1]),
        (item_dims[1], item_dims[0], item_dims[2]),
        (item_dims[1], item_dims[2], item_dims[0]),
        (item_dims[2], item_dims[0], item_dims[1]),
        (item_dims[2], item_dims[1], item_dims[0])
    ]

    # Variáveis para armazenar o melhor resultado global
    best_num_items = 0
    best_positions = []
    best_total_weight = box_weight

    def check_collision(pos, dims, current_positions):
        x, y, z = pos
        dx, dy, dz = dims
        for (px, py, pz), (pdx, pdy, pdz) in current_positions:
            if not (x + dx <= px or x >= px + pdx or
                y + dy <= py or y >= py + pdy or
                z + dz <= pz or z >= pz + pdz):
                return True
        return False

    # Testamos cada uma das 6 orientações de forma INDEPENDENTE
    for orientation in orientations:
        temp_positions = []
        temp_weight = box_weight
        temp_num = 0
        
        x = 0
        while x + orientation[0] <= box_dims[0]:
            y = 0
            while y + orientation[1] <= box_dims[1]:
                z = 0
                while z + orientation[2] <= box_dims[2]:
                    if temp_weight + item_weight <= weight_limit:
                        # Checamos colisão apenas com itens desta rodada (orientação atual)
                        if not check_collision((x, y, z), orientation, temp_positions):
                            temp_positions.append(((x, y, z), orientation))
                            temp_weight += item_weight
                            temp_num += 1
                    z += orientation[2]
                y += orientation[1]
            x += orientation[0]

        # Se esta orientação específica coube mais itens que as anteriores, ela vira a nossa "campeã"
        if temp_num > best_num_items:
            best_num_items = temp_num
            best_positions = temp_positions
            best_total_weight = temp_weight
                    
    return best_num_items, best_positions, best_total_weight

# Título da pagina (interface streamlit)
st.markdown('<h1 style="text-align: center; font-size: 30px;">3D com visualização gráfica</h1>', unsafe_allow_html=True)

# Seleção do perfil da caixa
caixa_selecionada = st.selectbox("Selecione o perfil da caixa", list(caixas.keys()))
box_dims = [caixas[caixa_selecionada]['Comprimento'], caixas[caixa_selecionada]['Largura'], caixas[caixa_selecionada]['Altura']]
box_weight = caixas[caixa_selecionada]['Peso']

# Dimensões do produto
c1, c2, c3, c4 = st.columns(4)
with c1:
    item_height = st.number_input('Altura:')
with c2:
    item_width = st.number_input('Largura:')
with c3:
    item_length = st.number_input('Comprimento:')
with c4:
    item_weight = st.number_input('Peso (kg):')

# Peso máximo
weight_limit = 25.00  # Limite de peso da caixa em kg

if item_length > 0 and item_width > 0 and item_height > 0 and item_weight > 0:  
    item_dims = [item_length, item_width, item_height]
    num_items, positions, total_weight = calculate_packing(box_dims, item_dims, box_weight, item_weight, weight_limit)
    
    st.markdown('<h1 style="text-align: center; font-size: 30px;">Capacidades em todas as caixas:</h1>', unsafe_allow_html=True)

    # Tenta recuperar as variáveis. Se não existirem ou forem 0, define como None/0 para evitar NameError
    item_dims = item_dims if 'item_dims' in locals() else [0, 0, 0]
    item_weight = item_weight if 'item_weight' in locals() else 0
    weight_limit = weight_limit if 'weight_limit' in locals() else 0

    # Valida se as medidas são válidas (maiores que zero) antes de rodar o loop
    if all(d > 0 for d in item_dims):
        resultados_gerais = []

        for nome_caixa, dados in caixas.items():
            dims_caixa = [dados['Comprimento'], dados['Largura'], dados['Altura'] ]
            peso_vazia = dados['Peso']
            
            # Executa o cálculo
            n_itens, _, p_total = calculate_packing(dims_caixa, item_dims, peso_vazia, item_weight, weight_limit)

            resultados_gerais.append({
                "Perfil da Caixa": nome_caixa,
                "Capacidade (itens)": n_itens,
                "Peso Total (kg)": round(p_total, 2),
                "Dimensões (AxLxC)": f"{dados['Altura']}x{dados['Largura']}x{dados['Comprimento']}"
            })

        df_resultados = pd.DataFrame(resultados_gerais)
        st.dataframe(df_resultados, use_container_width=True, hide_index=True)
    else:
        # Mensagem de erro técnico
        st.warning("Aguardando o preenchimento das dimensões do item para calcular as capacidades.")

    # Escrevendo a capacidade calculada 3D
    c4, c5 = st.columns(2)
    with c4:
        st.info(f"Capacidade calculada: **{num_items}**")
    # Escrevendo o peso da caixa, somada com a quantidade de produtos calculados
    with c5:
        st.info(f"Peso total da caixa: **{total_weight:.2f} kg**")

    fig = draw_packing(box_dims, item_dims, positions)
    st.pyplot(fig, use_container_width=True)
