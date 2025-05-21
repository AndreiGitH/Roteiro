import streamlit as st
from google import genai
import google.genai.errors as genai_errors

# App Streamlit integrado para gerar, analisar, revisar roteiros e metadados de vídeos no YouTube

def call_genai(client, model: str, prompt: str) -> str:
    """Chama o Google GenAI para gerar conteúdo via modelo especificado."""
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
        return response.text.strip()
    except genai_errors.ServerError as e:
        raise RuntimeError(f"Erro de servidor ao chamar GenAI: {e}")
    except Exception as e:
        raise RuntimeError(f"Erro desconhecido ao chamar GenAI: {e}")


def analyze_script(client, model: str, script: str) -> str:
    prompt = (
        "Analise este roteiro considerando o gancho inicial, retenção, engajamento e storytelling. Traga sugestões de melhoria de forma destacada.\n"
        + script
    )
    return call_genai(client, model, prompt)


def generate_script(client, model: str, original: str, analysis: str, num_palavras: int) -> str:
    """Reescreve o roteiro original com base na análise, usando o número de palavras especificado."""
    prompt = (
        f"Você é um roteirista de vídeos de youtube, especialista em retenção e storytelling. "
        f"Reescreva o texto, com aproximadamente {num_palavras} palavras, de tal forma que não incorra em plágio ou conteúdo reutilizável, pronto para a narração via tts (nas pausas maiores ou entre as partes use ...), "
        f"sem [] ou divisões, ou marcações, contendo trechos bíblicos, e uns 3 ditados populares. "
        "Use linguagem acessível e sem abreviaturas (não use expressão como galera, palavras difíceis ou em inglês). Abra ganchos narrativos entre as partes. Não seja prolixo. "
        "Atenção: o gancho inicial com introdução deve ter no máximo 25 segundos ou 55 palavras.\n"
        "Mantenha os pontos fortes e faça as melhorias sugeridas de acordo com o texto e análise a seguir.\n\n"
        "Roteiro original:\n" + original + "\n\n"
        "Análise:\n" + analysis
    )
    return call_genai(client, model, prompt)


def generate_titles_and_description(client, model: str, script: str) -> str:
    prompt = (
        "Crie sugestões de título para vídeo de youtube com no máximo 60 caracteres. "
        "Os títulos devem despertar curiosidade, benefício e urgência e atender às melhores práticas de títulos chamativos e bem sucedidos de youtube, "
        "a fim de aumentar os cliques sem se afastar do conteúdo do vídeo. Faça um ranking entre eles. "
        "Ao final traga a descrição do vídeo de youtube com 1800 caracteres, hashtags e tags entre vírgulas, atentando para SEO, "
        "e sugestão de prompt em português e em inglês para a criação de imagem da thumb, "
        "considerando 3 elementos visuais principais na thumb (Um rosto, uma cena e algo que chame a atenção e interaja emocionalmente com o personagem), "
        "rosto visível com expressão forte, localizado à direita da imagem, com visual chamativo e que desperte a curiosidade, sem texto overlay.\n\n"
        + script
    )
    return call_genai(client, model, prompt)


def main():
    # Configuração da página
    st.set_page_config(page_title="Roteiro YouTube AI", page_icon="📜", layout="wide")
    st.title("Gerador Completo de Roteiro e Metadados para YouTube")
    st.markdown("Este aplicativo gera um roteiro completo, analisa, revisa e cria metadados (títulos, descrição e prompt de thumb) baseado em um tema e tamanho de roteiro.")

    # Sidebar para configuração do modelo
    st.sidebar.header("Configurações do Modelo")
    default_model = st.secrets.get("default_model", "gemini-2.5-flash-preview-04-17")
    model_name = st.sidebar.text_input("Modelo GenAI", value=default_model)

    # Inicializa cliente GenAI
    api_key = st.secrets.get("google_api_key", "")
    client = genai.Client(api_key=api_key)

    # Inputs principais
    tema = st.text_input("Tema Bíblico Específico:", "")
    num_palavras = st.number_input(
        "Número aproximado de palavras para o roteiro inicial:",
        min_value=100, max_value=10000, value=1000, step=50
    )

    # Botão para gerar todo o pipeline
    if st.button("Gerar Conteúdo Completo"):
        if not tema.strip():
            st.error("Por favor, preencha o tema bíblico.")
        else:
            try:
                # 1. Gerar roteiro inicial
                with st.spinner("Gerando roteiro inicial..."):
                    prompt_script = (
                        f"Crie um roteiro para um vídeo do YouTube com aproximadamente {num_palavras} palavras, focado no público cristão, sobre o tema bíblico: \"{tema}\".\n\n"
                        + "**I. INTRODUÇÃO E GANCHO (Aproximadamente 10-15% do roteiro):**\n\n"
                        + "1.  **Gancho Forte e Variado:**\n"
                        + "    *   Comece com uma pergunta retórica impactante, uma breve e vívida vinheta/história hipotética que o espectador possa se identificar, uma citação bíblica poderosa e menos conhecida, ou uma estatística surpreendente (se aplicável e verdadeira) relacionada ao tema.\n"
                        + "    *   **Exemplo de Variação:** \"[Comece com uma imagem mental forte: 'Imagine [personagem bíblico/situação] enfrentando [desafio relacionado ao tema]... Essa luta antiga ecoa em nossos corações hoje quando lidamos com [aspecto moderno do tema]...']\"\n\n"
                        + "2.  **Conexão Imediata:** Relacione o gancho diretamente às dores, dúvidas, anseios ou curiosidades do público sobre o [TEMA BÍBLICO ESPECÍFICO].\n\n"
                        + "3.  **Promessa de Valor Clara:**\n"
                        + "    *   Declare explicitamente o que o espectador vai aprender ou descobrir (ex: \"Nos próximos minutos, você vai descobrir [NÚMERO] chaves/sinais/principais sobre [TEMA BÍBLICO ESPECÍFICO]\"...)"
                        # Truncated: manter conforme roteirotema.py
                    )
                    roteiro_inicial = call_genai(client, model_name, prompt_script)
                    st.session_state.roteiro = roteiro_inicial

                # 2. Analisar roteiro
                with st.spinner("Analisando roteiro..."):
                    analysis = analyze_script(client, model_name, roteiro_inicial)
                    st.session_state.analysis = analysis

                # 3. Revisar roteiro (gerar novo roteiro)
                with st.spinner("Revisando e gerando novo roteiro..."):
                    roteiro_final = generate_script(client, model_name, roteiro_inicial, analysis, num_palavras)
                    st.session_state.revised = roteiro_final

                # 4. Gerar títulos, descrição e prompt de thumb (usando apenas as 2000 primeiras palavras)
                with st.spinner("Gerando títulos, descrição e prompt de thumbnail..."):
                    palavras = st.session_state.revised.split()
                    roteiro_truncado = " ".join(palavras[:2000])
                    meta = generate_titles_and_description(client, model_name, roteiro_truncado)
                    st.session_state.meta = meta

                # 5. Reescrever gancho inicial
                with st.spinner("Gerando gancho inicial revisado..."):
                    palavras_g = st.session_state.revised.split()
                    trecho_gancho = " ".join(palavras_g[:250])
                    prompt_gancho = (
                        "Você é especialista em criação de gancho inicial para vídeos, que desperta curiosidade e retenção, "
                        "melhore este gancho e introdução inicial que deverá ter apenas 90 palavras.\n\n" + trecho_gancho
                    )
                    gancho_revisado = call_genai(client, model_name, prompt_gancho)
                    st.session_state.gancho = gancho_revisado

            except RuntimeError as e:
                st.error(f"Ocorreu um erro durante o pipeline: {e}")

    # Exibir resultado final
    if st.session_state.get("gancho"):
        st.subheader("Gancho Inicial Revisado")
        st.text_area("", st.session_state.gancho, height=100)
        st.download_button(
            label="📥 Baixar Gancho Revisado",
            data=st.session_state.gancho,
            file_name="gancho_revisado.txt",
            mime="text/plain"
        )
    if st.session_state.get("revised"):
        st.subheader("Roteiro Final")
        st.text_area("", st.session_state.revised, height=300)
        st.download_button(
            label="📥 Baixar Roteiro Final",
            data=st.session_state.revised,
            file_name="roteiro_final.txt",
            mime="text/plain"
        )
    if st.session_state.get("meta"):
        st.subheader("Títulos, Descrição e Prompt de Thumbnail")
        st.text_area("", st.session_state.meta, height=300)
        st.download_button(
            label="📥 Baixar Metadados (Título, Descrição e Prompt)",
            data=st.session_state.meta,
            file_name="metadados.txt",
            mime="text/plain"
        )


if __name__ == "__main__":
    main()
