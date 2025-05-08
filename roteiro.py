import streamlit as st
from google import genai

# App Streamlit para gerar roteiros de vídeos no YouTube usando Google Gemini

def main():
    # Configuração da página
    st.set_page_config(page_title="Roteiro YouTube AI", layout="wide")
    st.title("Gerador de Roteiro de Vídeo para YouTube")

    # Sidebar: Configurações da API e modelo
    st.sidebar.header("Configurações")
    api_key = st.sidebar.text_input(
        "API Key Google GenAI", 
        type="password",
        value=st.secrets.get("google_api_key", "")
    )
    default_model = st.secrets.get("default_model", "gemini-2.5-pro-exp-03-25")
    model_name = st.sidebar.text_input(
        "Modelo GenAI",
        value=default_model
    )

    # Inicializa cliente Google GenAI
    client = genai.Client(api_key=api_key)

    # Caixa de texto para roteiro original
    original = st.text_area(
        "Cole aqui seu roteiro original:",
        height=300,
        key="original"
    )

    # Botão para análise
    if st.button("Analisar roteiro", key="btn_analyze"):
        if not original.strip():
            st.error("Por favor, cole o roteiro original antes de analisar.")
        else:
            with st.spinner("Analisando roteiro..."):
                analysis = analyze_script(client, model_name, original)
                st.session_state.analysis = analysis
                st.text_area(
                    "Análise de gancho, retenção, engajamento e storytelling:",
                    analysis,
                    height=300,
                    key="analysis_box"
                )

    # Botão para gerar novo roteiro
    if st.session_state.get("analysis"):
        if st.button("Gerar novo roteiro", key="btn_generate_script"):
            with st.spinner("Gerando novo roteiro..."):
                new_script = generate_script(
                    client,
                    model_name,
                    original,
                    st.session_state.analysis
                )
                st.session_state.new_script = new_script
                st.text_area(
                    "Roteiro reescrito (aprox. 25 min):",
                    new_script,
                    height=400,
                    key="script_box"
                )
                st.download_button(
                    label="Baixar roteiro (.txt)",
                    data=new_script,
                    file_name="roteiro_reescrito.txt",
                    mime="text/plain"
                )

    # Botão para gerar títulos e descrição
    if st.session_state.get("new_script"):
        if st.button("Gerar títulos e descrição", key="btn_titles"):
            with st.spinner("Gerando títulos e descrição..."):
                titles_desc = generate_titles_and_description(
                    client,
                    model_name,
                    st.session_state.new_script
                )
                st.session_state.titles_desc = titles_desc
                st.text_area(
                    "Sugestões de títulos e descrição de vídeo:",
                    titles_desc,
                    height=300,
                    key="titles_box"
                )
                st.download_button(
                    label="Baixar títulos e descrição (.txt)",
                    data=titles_desc,
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
        "Analise este roteiro considerando o gancho inicial, retenção, engajamento e storytelling.\n"
        + script
    )
    return call_genai(client, model, prompt)


def generate_script(client, model: str, original: str, analysis: str) -> str:
    prompt = (
        "Você é um roteirista de vídeos de youtube, especialista em retenção e storytelling. "
        "Reescreva o texto, pronto para a narração via tts, sem [] ou divisões, ou marcações, aproximadamente 25 minutos, "
        "(3250 palavras), de tal forma que não incorra em plágio, contendo trechos bíblicos, e uns 3 ditados populares. "
        "Use linguagem próxima do público (não use expressão como galera, palavras difíceis ou em inglês). "
        "Abra ganchos narrativos. Não seja prolixo. Atenção: o gancho inicial com introdução deve ter no máximo 25 segundos ou 55 palavras.\n"
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
        "Ao final traga a descrição do vídeo de youtube com 1000 caracteres, hashtags e tags entre vírgulas, atentando para SEO.\n\n"
        + script
    )
    return call_genai(client, model, prompt)


if __name__ == "__main__":
    main()
