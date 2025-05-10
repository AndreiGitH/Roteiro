import streamlit as st
from google import genai

# App Streamlit para gerar roteiros de vídeos no YouTube usando Google Gemini

def main():
    # Configuração da página
    st.set_page_config(page_title="Roteiro YouTube AI", layout="wide")
    st.title("Gerador de Roteiro de Vídeo para YouTube")

    # API Key (não exposta no frontend)
    api_key = st.secrets.get("google_api_key", "")
    client = genai.Client(api_key=api_key)

    # Sidebar: Escolha de modelo
    st.sidebar.header("Configurações do Modelo")
    default_model = st.secrets.get("default_model", "gemini-2.5-pro-exp-03-25")
    model_name = st.sidebar.text_input(
        "Modelo GenAI",
        value=default_model
    )

    # Caixa de texto para roteiro original
    original = st.text_area(
        "Cole aqui seu roteiro original:",
        height=300,
        key="original"
    )

    # Analisar Roteiro
    if st.button("Analisar roteiro", key="btn_analyze"):
        if not original.strip():
            st.error("Por favor, cole o roteiro original antes de analisar.")
        else:
            with st.spinner("Analisando roteiro..."):
                st.session_state.analysis = analyze_script(client, model_name, original)

    # Exibir Análise se existir
    if st.session_state.get("analysis"):
        st.text_area(
            "Análise de gancho, retenção, engajamento e storytelling:",
            st.session_state.analysis,
            height=300,
            key="analysis_box",
            disabled=False
        )

    # Gerar Novo Roteiro
    if st.session_state.get("analysis") and st.button("Gerar novo roteiro", key="btn_generate_script"):
        with st.spinner("Gerando novo roteiro..."):
            st.session_state.new_script = generate_script(
                client,
                model_name,
                original,
                st.session_state.analysis
            )

    # Exibir Novo Roteiro se existir
    if st.session_state.get("new_script"):
        st.text_area(
            "Roteiro reescrito (aprox. 25 min):",
            st.session_state.new_script,
            height=400,
            key="script_box",
            disabled=False
        )
        st.download_button(
            label="Baixar roteiro (.txt)",
            data=st.session_state.new_script,
            file_name="roteiro_reescrito.txt",
            mime="text/plain"
        )

    # Gerar Títulos e Descrição
    if st.session_state.get("new_script") and st.button("Gerar títulos e descrição", key="btn_titles"):
        with st.spinner("Gerando títulos e descrição..."):
            st.session_state.titles_desc = generate_titles_and_description(
                client,
                model_name,
                st.session_state.new_script
            )

    # Exibir Títulos e Descrição se existir
    if st.session_state.get("titles_desc"):
        st.text_area(
            "Sugestões de títulos e descrição de vídeo:",
            st.session_state.titles_desc,
            height=300,
            key="titles_box",
            disabled=False
        )
        st.download_button(
            label="Baixar títulos e descrição (.txt)",
            data=st.session_state.titles_desc,
            file_name="titulos_descricao.txt",
            mime="text/plain"
        )


def call_genai(client, model: str, prompt: str) -> str:
    """Chama o Google GenAI para gerar conteúdo via modelo especificado."""
    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )
    return response.text.strip()


def analyze_script(client, model: str, script: str) -> str:
    prompt = (
        "Analise este roteiro considerando o gancho inicial, retenção, engajamento e storytelling. Traga sugestões de melhoria de forma detacada.\n"
        + script
    )
    return call_genai(client, model, prompt)


def generate_script(client, model: str, original: str, analysis: str) -> str:
    prompt = (
        "Você é um roteirista de vídeos de youtube, especialista em retenção e storytelling. "
        "Reescreva o texto, de tal forma que não incorra em plágio ou conteúdo reutilizável, pronto para a narração via tts (nas pausas maiores ou entre as partes use ...), "
        "sem [] ou divisões, ou marcações, aproximadamente 25 minutos, "
        "(3250 palavras), contendo trechos bíblicos, e uns 3 ditados populares. "
        "Use linguagem acessível e sem abreviaturas (não use expressão como galera, palavras difíceis ou em inglês). "
        "Abra ganchos narrativos entre as partes. Não seja prolixo. Atenção: o gancho inicial com introdução deve ter no máximo 25 segundos ou 55 palavras.\n"
        "Mantenha os pontos fortes e faça as melhorias sugeridas de acordo com o texto e análise a seguir. "
        "Ao final dê uma nota de comparação entre os dois textos quanto a configuração de conteúdo reutilizável ou plágio.\n\n"
        "Roteiro original:\n" + original + "\n\n"
        "Análise:\n" + analysis
    )
    return call_genai(client, model, prompt)


def generate_titles_and_description(client, model: str, script: str) -> str:
    prompt = (
        "Crie sugestões de título para vídeo de youtube com no máximo 60 caracteres. "
        "Os títulos devem despertar curiosidade, benefício e urgência e atender às melhores práticas de títulos chamativos e bem sucedidos de youtube, "
        "a fim de aumentar os cliques sem se afastar do conteúdo do vídeo. "
        "Ao final traga a descrição do vídeo de youtube com 1000 caracteres, hashtags e tags entre vírgulas, atentando para SEO, "
        "e sugestão de prompt em português e em inglês para a criação de imagem da thumb, "
        "considerando 3 elementos visuais principais na thumb (Um rosto, uma cena e algo que chame a atenção e interaja emocionalmente com o personagem), "
        "rosto visível com expressão forte, localizado à direita da imagem, com visual chamativo e que desperte a curiosidade, sem texto overlay.\n\n"
        + script
    )
    return call_genai(client, model, prompt)


if __name__ == "__main__":
    main()
