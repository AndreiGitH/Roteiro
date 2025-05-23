import streamlit as st
from google import genai # Usando o import original
import google.genai.errors as genai_errors # Usando o import original

# App Streamlit integrado para gerar, analisar, revisar roteiros e metadados de vídeos no YouTube

def call_genai(client, model: str, prompt: str) -> str:
    """Chama o Google GenAI para gerar conteúdo via modelo especificado."""
    try:
        # Esta é a forma de chamada que estava no seu código original
        response = client.models.generate_content(
            model=model, # Passa o nome do modelo aqui
            contents=prompt,
        )
        # Verifica se a resposta tem o atributo 'text' antes de acessá-lo
        # Alguns modelos/versões da API podem retornar a resposta em response.candidates[0].content.parts[0].text
        # Mas vamos seguir o original que esperava response.text
        if hasattr(response, 'text') and response.text is not None:
            return response.text.strip()
        elif hasattr(response, 'candidates') and response.candidates:
            # Tentativa de fallback para a estrutura mais comum da API Gemini atual
            try:
                return response.candidates[0].content.parts[0].text.strip()
            except (AttributeError, IndexError, TypeError) as e_alt:
                st.warning(f"Resposta não continha 'text' diretamente, nem a estrutura 'candidates[0].content.parts[0].text'. Erro no fallback: {e_alt}")
                st.json(response._result) # Mostra a estrutura da resposta para depuração
                raise RuntimeError(f"Formato de resposta inesperado do GenAI. Verifique a estrutura da resposta: {str(response._result)[:500]}")
        else:
            st.warning("Resposta do GenAI não continha o atributo 'text' nem 'candidates' esperados.")
            st.json(response._result) # Mostra a estrutura da resposta para depuração
            raise RuntimeError(f"Formato de resposta inesperado do GenAI. Resposta (início): {str(response._result)[:500]}")

    except genai_errors.ServerError as e:
        st.error(f"Erro de servidor ao chamar GenAI: {e}")
        raise RuntimeError(f"Erro de servidor ao chamar GenAI: {e}")
    except Exception as e:
        st.error(f"Erro desconhecido ao chamar GenAI: {e}")
        st.error(f"Prompt enviado: {prompt[:300]}...") # Log do início do prompt para depuração
        # Se a resposta já foi obtida e o erro ocorreu ao processá-la, ela pode não estar disponível aqui.
        # Mas se o erro foi na chamada, a 'response' não existirá.
        raise RuntimeError(f"Erro desconhecido ao chamar GenAI: {e}")

def generate_initial_script(client, model: str, tema: str, objetivo: str, num_palavras: int) -> str:
    """Gera o roteiro inicial com base no tema, objetivo e número de palavras."""
    prompt = f"""
1. Tema Central do Vídeo: {tema}
2. Objetivo Principal/Mensagem Chave (O "Quê" e o "Porquê"): Qual a ÚNICA coisa mais importante que você quer que o espectador aprenda ou sinta ao final do vídeo? Por que isso é relevante para ele AGORA?: {objetivo}
3. Público-Alvo (Ideal): Pessoas buscando introdução à fé de forma simples, Cristãos experientes precisando de renovação, geralmente homens e mulheres entre 18 a 75 anos.
4. Tom/Estilo Desejado: Conversacional e amigável, Dinâmico e direto ao ponto.
5. Estrutura do Roteiro (com foco em dinamismo e clareza):
A0: Numero de palavras totais do roteiro: {num_palavras};
A. Gancho Inicial (Primeiros 5-10 segundos OBRIGATÓRIOS):
Crie uma pergunta intrigante, uma afirmação surpreendente, uma estatística chocante ou uma mini-história ultra curta (1-2 frases) relacionada ao tema.
Objetivo: Despertar curiosidade IMEDIATA e fazer o espectador pensar "Preciso saber mais sobre isso".
Exemplo para Salomão (se fosse começar de novo): "O homem mais sábio do mundo... destruiu a própria vida. Como? E como você pode evitar o mesmo erro?"

B. Introdução Rápida (Até 30-45 segundos no máximo - 65 a 95 palavras):
Apresente o tema de forma concisa, conectando-o ao gancho.
Promessa de Valor: Diga claramente o que o espectador vai ganhar/aprender/descobrir assistindo ao vídeo. "Neste vídeo, vamos desvendar..." ou "Você vai descobrir 3 passos para...".

C. Desenvolvimento do Conteúdo (Corpo do Vídeo):
Divida o tema em 2-4 pontos principais NO MÁXIMO. Menos é mais se os pontos forem bem desenvolvidos.
Para cada ponto:
Explicação Clara e Concisa: Use frases predominantemente curtas e diretas. Evite parágrafos muito longos.
Linguagem: Priorize linguagem conversacional e acessível. Se precisar usar um termo teológico ou complexo, explique-o de forma simples imediatamente. Pense: "Como eu explicaria isso para um amigo tomando um café?".
Exemplos, Analogias ou Mini-Histórias: Para cada ponto abstrato, tente trazer um exemplo prático, uma analogia do dia a dia ou uma breve ilustração para torná-lo tangível e memorável.
Conexão com o Espectador: Use "você", "nós". Faça perguntas retóricas curtas ("Já se sentiu assim?", "Faz sentido?").
Pausas Naturais (...): Escreva de forma que as pausas para respiração e ênfase (indicadas por ... ou naturalmente pela pontuação como vírgulas e pontos finais) soem orgânicas para narração TTS. Quebre ideias complexas em frases menores.

D. Lições Práticas / Aplicações / "E Daí?" (se aplicável):
Transforme o conhecimento em ação. O que o espectador pode FAZER com essa informação?
Apresente de forma clara e acionável. Em vez de longas listas, foque nos 2-3 pontos mais impactantes e práticos.

E. Conclusão e Chamada Para Ação (CTA):
Recapitulação Breve: Em 1-2 frases, reforce a mensagem chave do vídeo.
Chamada Para Ação Clara e Direta:
Peça o like: "Se este vídeo te ajudou de alguma forma, deixe seu like para eu saber!"
Incentive comentários com uma pergunta específica: "Qual foi a lição que mais te tocou? Comente abaixo!" ou "Você já passou por algo parecido? Compartilhe sua experiência nos comentários." ou uma frase específica: “Eu amo Jesus” ou “Eu acredito na Provisão”.
Peça a inscrição: "E se você quer mais conteúdo como este, inscreva-se no canal e ative o sininho."
Sugira compartilhar: "Compartilhe este vídeo com alguém que precisa ouvir essa mensagem."

Encerramento: Uma frase final curta e positiva/encorajadora.

6. Diretrizes Adicionais para Manter o Ritmo e Evitar a Monotonia:
Variedade: Alterne entre explicação, exemplo, pergunta, afirmação.
Clareza Acima de Tudo: Se uma ideia é complexa, simplifique-a ou divida-a em partes menores. É melhor ser claro do que tentar ser exaustivo e perder o espectador.
Relevância Constante: Sempre se pergunte: "Por que o meu público se importaria com isso?". Conecte o conteúdo à vida, dores, desejos e desafios do espectador.
Duração: Mire em uma duração que respeite o tempo do espectador e a densidade do conteúdo. Para temas complexos, considere dividir em uma minissérie de vídeos mais curtos. (Este prompt ajuda a focar, o que naturalmente pode levar a vídeos mais concisos).
Lembre-se do TTS: Frases mais curtas e linguagem clara facilitam muito uma boa narração TTS. Evite construções frasais muito rebuscadas ou períodos longuíssimos. Não use abreviaturas.
O roteiro deve ser escrito em português do Brasil.
O roteiro deve ser formatado para narração, usando "..." para pausas maiores ou entre seções.
Não inclua marcações como "[INÍCIO DO GANCHO]" ou divisões explícitas como "SEÇÃO C". O texto deve fluir naturalmente.
O roteiro deve conter alguns trechos bíblicos relevantes ao tema e uns 3 ditados populares brasileiros, integrados de forma natural.
Use linguagem acessível, sem gírias (como "galera"), palavras excessivamente difíceis ou termos em inglês, a menos que sejam universalmente compreendidos e não tenham um bom equivalente em português.
Mantenha o gancho inicial com introdução em, no máximo, 95 palavras. O texto total deverá ter aproximadamente {num_palavras} palavras.
Evite ser prolixo ou repetitivo. Crie ganchos narrativos sutis entre as partes para manter o interesse.
O resultado final deve ser apenas o texto do roteiro, pronto para ser narrado.
"""
    return call_genai(client, model, prompt)

def revise_script(client, model: str, original_script: str, num_palavras: int) -> str:
    """Revisa o roteiro inicial com base em sugestões de melhoria."""
    prompt = (
        f"Analise o roteiro inicial a seguir. Seu objetivo é identificar pontos onde ele pode ser menos prolixo, menos chato, mais dinâmico e mais direto ao ponto. "
        f"Após a análise, reescreva o texto incorporando essas sugestões de melhoria. "
        f"O novo roteiro deve ter aproximadamente {num_palavras} palavras. "
        f"Mantenha o foco em retenção e storytelling para vídeos do YouTube. "
        f"O texto reescrito deve estar pronto para narração via TTS (use '...' para pausas maiores ou entre partes), "
        f"sem marcadores como '[]', divisões explícitas ou anotações. "
        f"Deve conter trechos bíblicos relevantes e cerca de 3 ditados populares brasileiros, integrados naturalmente. "
        f"Use linguagem acessível, sem abreviaturas, gírias (como 'galera'), palavras difíceis ou termos em inglês desnecessários. "
        f"Abra ganchos narrativos sutis entre as partes. Não seja prolixo ou repetitivo. "
        f"O gancho inicial com introdução deve ter no máximo 95 palavras. "
        f"O texto total deverá ter aproximadamente {num_palavras} palavras. "
        "Roteiro original a ser analisado e reescrito:\n"
        f"{original_script}"
    )
    return call_genai(client, model, prompt)

def generate_titles_and_description(client, model: str, script: str) -> str:
    """Gera títulos, descrição, hashtags, tags e prompt de thumbnail para o YouTube."""
    prompt = (
        "Com base no roteiro de vídeo fornecido:\n\n"
        "1.  **Títulos (Ranking):** Crie 5 sugestões de título para vídeo de YouTube, cada um com no máximo 60 caracteres. Os títulos devem despertar curiosidade, prometer um benefício claro e/ou criar um senso de urgência. Eles devem seguir as melhores práticas para títulos chamativos e bem-sucedidos no YouTube, visando aumentar os cliques sem se afastar do conteúdo do vídeo. Apresente os títulos em um ranking, do melhor para o menos preferido, com uma breve justificativa para o título principal.\n\n"
        "2.  **Descrição do Vídeo:** Elabore uma descrição otimizada para SEO com aproximadamente 1800 caracteres. A descrição deve:\n"
        "    *   Começar com 1-2 frases que expandam o título e o gancho do vídeo, incluindo palavras-chave principais.\n"
        "    *   Resumir os pontos chave e benefícios do vídeo.\n"
        "    *   Incluir chamadas para ação (inscrever-se, assistir outros vídeos, links relevantes se houver).\n"
        "    *   Conter um bloco de hashtags relevantes (ex: #fé #bíblia #mensagemdodia).\n\n"
        "3.  **Tags:** Liste de 10 a 15 tags relevantes para o vídeo, separadas por vírgulas.\n\n"
        "4.  **Prompt para Thumbnail (Português e Inglês):** Sugira um prompt detalhado para a criação da imagem da thumbnail usando IA (ex: Midjourney, DALL-E). O prompt deve considerar:\n"
        "    *   **3 Elementos Visuais Principais:** Um rosto humano com expressão forte e visível (localizado preferencialmente à direita da imagem), uma cena de fundo ou elemento que remeta ao tema do vídeo, e um terceiro elemento que chame a atenção, crie curiosidade ou interaja emocionalmente com o personagem/tema.\n"
        "    *   **Estilo Visual:** Chamativo, cores vibrantes (ou paleta específica se relevante ao tema), boa iluminação no rosto.\n"
        "    *   **Composição:** Foco no rosto, evitando texto overlay na imagem (o título do vídeo já cumpre essa função).\n"
        "    *   **Objetivo:** Despertar curiosidade e impacto emocional.\n"
        "    Forneça o prompt em Português e sua tradução para o Inglês.\n\n"
        "--- ROTEIRO DO VÍDEO PARA ANÁLISE ---\n"
        + script
    )
    return call_genai(client, model, prompt)


def main():
    st.set_page_config(page_title="Roteiro YouTube AI", page_icon="📜", layout="wide")
    st.title("Gerador de Roteiro e Metadados para YouTube")
    st.markdown("Crie roteiros iniciais, metadados e revise-os com IA para seus vídeos do YouTube.")

    # Sidebar para configuração do modelo (CONFORME SOLICITADO)
    st.sidebar.header("Configurações do Modelo")
    # Nota: "gemini-2.5-flash-preview-04-17" pode ser um nome de modelo específico ou de uma API mais antiga.
    # Para a API Gemini mais recente (google-generativeai), os nomes são como "models/gemini-1.5-flash-latest".
    # Certifique-se de que este nome de modelo é compatível com a forma como genai.Client() e client.models.generate_content() são usados.
    default_model = st.secrets.get("default_model", "gemini-1.5-flash-latest") # Alterado para um modelo mais comum, mas mantenha o seu se funcionar
    model_name = st.sidebar.text_input("Modelo GenAI", value=default_model, help="Ex: gemini-1.5-flash-latest, gemini-1.5-pro-latest. Alguns modelos mais antigos podem não usar o prefixo 'models/'.")

    # Inicializa cliente GenAI (CONFORME SOLICITADO)
    api_key = st.secrets.get("google_api_key", "")

    if not api_key:
        st.sidebar.error("Chave API do Google (google_api_key) não encontrada nos secrets.")
        st.error("Por favor, configure a chave API do Google nos secrets do Streamlit para continuar.")
        st.stop()

    client = None # Inicializa client como None
    try:
        # A forma como 'genai.Client(api_key=api_key)' é usada sugere uma biblioteca
        # como 'google-ai-generativelanguage' ou uma versão mais antiga de 'google-generativeai'.
        # Se estiver usando 'google-generativeai' >= 0.3.0, a inicialização seria:
        # genai.configure(api_key=api_key)
        # E para chamadas: model_instance = genai.GenerativeModel(model_name)
        # response = model_instance.generate_content(...)
        # No entanto, vamos seguir o padrão do código original fornecido:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"Erro ao inicializar o cliente GenAI: {e}")
        st.sidebar.error(f"Erro ao inicializar cliente GenAI: {e}")
        st.stop()

    if client is None: # Verificação adicional
        st.error("Falha crítica: Cliente GenAI não foi inicializado.")
        st.stop()

    st.header("1. Defina o Conteúdo do Roteiro")
    tema = st.text_input("Tema Bíblico Específico:", placeholder="Ex: A história de Davi e Golias e suas lições de coragem")
    objetivo = st.text_input(
        "Objetivo Principal/Mensagem Chave (O Quê e o Porquê):",
        value="Que podemos aprender com as lições dos outros ou Que Deus sempre perdoa e podemos recomeçar (relevante pois todos erram)",
        placeholder="Ex: Inspirar fé através da perseverança de Jó"
    )
    num_palavras = st.number_input(
        "Número aproximado de palavras para o roteiro:",
        min_value=200, max_value=10000, value=1000, step=100,
        help="Um roteiro de 1000 palavras tem aproximadamente 7-8 minutos de narração."
    )

    if "roteiro_inicial" not in st.session_state:
        st.session_state.roteiro_inicial = ""
    if "meta" not in st.session_state:
        st.session_state.meta = ""
    if "roteiro_revisado" not in st.session_state:
        st.session_state.roteiro_revisado = ""

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📝 Gerar Roteiro Inicial e Metadados", type="primary", use_container_width=True):
            if not tema.strip():
                st.error("Por favor, preencha o tema bíblico.")
            elif not objetivo.strip():
                st.error("Por favor, preencha o objetivo principal.")
            else:
                try:
                    with st.spinner("Gerando roteiro inicial... Por favor, aguarde."):
                        st.session_state.roteiro_inicial = generate_initial_script(client, model_name, tema, objetivo, num_palavras)
                    st.success("Roteiro inicial gerado!")

                    with st.spinner("Gerando títulos, descrição e prompt de thumbnail..."):
                        palavras_roteiro = st.session_state.roteiro_inicial.split()
                        roteiro_curto_para_meta = " ".join(palavras_roteiro[:1500])
                        st.session_state.meta = generate_titles_and_description(client, model_name, roteiro_curto_para_meta)
                    st.success("Metadados gerados!")
                    st.session_state.roteiro_revisado = ""

                except RuntimeError as e:
                    st.error(f"Ocorreu um erro: {e}")
                except Exception as e:
                    st.error(f"Ocorreu um erro inesperado: {e}")
    with col2:
        if st.session_state.roteiro_inicial:
            if st.button("🔄 Revisar Roteiro Inicial", use_container_width=True):
                if not st.session_state.roteiro_inicial.strip():
                    st.warning("Gere um roteiro inicial primeiro para poder revisá-lo.")
                else:
                    try:
                        with st.spinner("Revisando roteiro... Por favor, aguarde."):
                            st.session_state.roteiro_revisado = revise_script(client, model_name, st.session_state.roteiro_inicial, num_palavras)
                        st.success("Roteiro revisado com sucesso!")
                    except RuntimeError as e:
                        st.error(f"Ocorreu um erro durante a revisão: {e}")
                    except Exception as e:
                        st.error(f"Ocorreu um erro inesperado durante a revisão: {e}")

    st.markdown("---")
    st.header("Resultados Gerados")

    tab_inicial, tab_meta, tab_revisado = st.tabs(["📜 Roteiro Inicial", "📊 Metadados", "✍️ Roteiro Revisado"])

    with tab_inicial:
        if st.session_state.roteiro_inicial:
            st.subheader("Roteiro Inicial Gerado")
            st.text_area("Roteiro Inicial:", st.session_state.roteiro_inicial, height=400, key="text_area_inicial")
            st.download_button(
                label="📥 Baixar Roteiro Inicial",
                data=st.session_state.roteiro_inicial,
                file_name=f"roteiro_inicial_{tema[:20].replace(' ','_') if tema else 'sem_tema'}.txt",
                mime="text/plain"
            )
        else:
            st.info("Clique em 'Gerar Roteiro Inicial e Metadados' para começar.")

    with tab_meta:
        if st.session_state.meta:
            st.subheader("Títulos, Descrição e Prompt de Thumbnail")
            st.text_area("Metadados:", st.session_state.meta, height=400, key="text_area_meta")
            st.download_button(
                label="📥 Baixar Metadados",
                data=st.session_state.meta,
                file_name=f"metadados_{tema[:20].replace(' ','_') if tema else 'sem_tema'}.txt",
                mime="text/plain"
            )
        else:
            st.info("Metadados serão gerados junto com o roteiro inicial.")

    with tab_revisado:
        if st.session_state.roteiro_revisado:
            st.subheader("Roteiro Revisado")
            st.text_area("Roteiro Revisado:", st.session_state.roteiro_revisado, height=400, key="text_area_revisado")
            st.download_button(
                label="📥 Baixar Roteiro Revisado",
                data=st.session_state.roteiro_revisado,
                file_name=f"roteiro_revisado_{tema[:20].replace(' ','_') if tema else 'sem_tema'}.txt",
                mime="text/plain"
            )
        elif st.session_state.roteiro_inicial:
            st.info("Clique em 'Revisar Roteiro Inicial' se desejar uma versão aprimorada.")
        else:
            st.info("Gere um roteiro inicial primeiro. A opção de revisão aparecerá em seguida.")


if __name__ == "__main__":
    main()


