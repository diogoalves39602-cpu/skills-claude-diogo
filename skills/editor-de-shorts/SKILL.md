---
name: editor-de-shorts
description: Cria e edita vídeos curtos verticais (YouTube Shorts, Reels, TikTok) de curiosidades narradas, do roteiro ao MP4 final, com imagens livres, imagens de reação engraçadas (estilo meme), roteiro com humor e palavrões, narração, música de fundo, legendas karaokê e título/descrição/hashtags. Use quando o Diogo pedir para criar, editar ou melhorar um vídeo, short ou reels.
---

# Editor de Shorts

Fluxo e ferramentas usados no primeiro Short do Diogo (água-viva imortal, out/2026), que ele aprovou ("ficou muito bom"). Responda sempre em português.

## O que o Diogo gosta (aplique sem ele precisar pedir)

- **Ritmo dinâmico**: sem pausas longas, narração rápida e cortes frequentes. Ele achou "morto" quando havia uma imagem só por frase.
- **Uma imagem para cada fala importante**, trocando na palavra exata. Exemplos que ele mesmo sugeriu: "um estudante" → foto de estudante; "anos 80 na Itália" → foto que lembre a época e o lugar; "imagina a cara dele" → alguém surpreso. Ilustre o literal e o engraçado: "vira lanche" → um sanduíche; "malandra demais" → cachorro de óculos escuros. Meta: trocar de imagem a cada 2 ou 3 s.
- **Narração engraçada, com alguns palavrões** ("porra", "foda-se", "caralho"), em tom de zoeira. Avise que palavrão logo no começo pode reduzir a monetização.
- **Música de fundo baixa**, para não ficar só a voz. A música abaixa sozinha quando a voz fala.
- **Imagens da espécie, pessoa ou objeto certo** quando o assunto é algo específico. Ele cobrou isso. Se só existir uma foto livre, faça vários enquadramentos dela (aberto, médio, close, retrato).
- **Voz humana**: ele prefere gerar a narração no Google AI Studio (Generate Speech). A geração lá exige vincular uma chave de API paga (sem ela, dá erro 403). Ele mesmo gera e baixa o .wav, e você monta. Até lá, use o edge-tts como rascunho.
- **No final**, entregue o título, a descrição e as hashtags escritos na resposta e num .txt, com os créditos das imagens.
- **Entrega na pasta Downloads** (`C:\Users\diogo\Downloads\<Projeto>\`), porque a pasta Vídeos é bloqueada pelo Controlled Folder Access. Mande o arquivo com SendUserFile e, se ele não achar, abra o Explorador com reveal_path.

## Imagens engraçadas: o tempero de meme

Foi o que fez o Diogo dizer "ficou muito bom". O vídeo só com fotos científicas parecia "morto"; as imagens de reação deram vida a ele.

### Regras que funcionaram

1. **Ilustre o literal da frase, não o assunto.** "Vira lanche" → um sanduíche de pasta de amendoim, e não um peixe comendo uma água-viva. A imagem fora de contexto é a piada.
2. **Ponha uma reação na exclamação.** Logo depois de um palavrão ou de um "imagina a cara dele", mostre um rosto reagindo: bebê espantado no "caralho, ela rejuvenesceu!", gatinho assustado no "que bicho estranho da porra".
3. **Faça a imagem comentar a fala.** O bebê espantado no "rejuvenesceu" funciona em dois níveis: é a cara de susto e é um bebê, ou seja, alguém que rejuvenesceu. Procure essas coincidências.
4. **Bicho fazendo cara de gente rende mais que pessoa.** Gato surpreso e cachorro de óculos escuros são mais engraçados que fotos de pessoas, e é mais fácil achar fotos livres deles.
5. **Dê voz ao bicho e mostre o personagem.** Se o roteiro tem "ela pensa: foda-se", entra um boneco dando de ombros. Personificar o animal com fala de gente é metade da graça; a imagem completa a outra metade.
6. **Use comparação de tamanho com o corpo.** "Menor que a sua unha" → close de uma mão. Escala no corpo humano prende quem está assistindo.
7. **Represente época e lugar com um objeto da época.** Não existe foto livre da cena real ("estudante na Itália nos anos 80")? Monte em sequência: foto de estudante dos anos 80 → carro da época (Fiat Panda 1988) → a cidade de verdade (Rapallo). O cérebro de quem assiste junta as três.
8. **Desenho e vetor funcionam como emoji gigante.** O boneco laranja CC0 ficou ótimo em tela cheia, e desenhos não têm problema de direito de imagem de pessoas.
9. **A piada é curta.** A imagem da piada fica 0,7–2 s, entra com zoom-soco, flash e whoosh, e já sai. Se demorar, perde a graça.
10. **Alterne sério e piada.** Foto científica → piada → foto científica. Cerca de uma piada visual a cada 5–8 s. Mantenha a informação certa (espécie certa, fatos certos), porque a graça vem por cima de um vídeo confiável.

### Roteiro que já nasce engraçado

A imagem engraçada precisa de uma frase que dê gancho. Truques que funcionaram no roteiro:
- **Gancho com comparação absurda e palavrão**: "Esse bichinho aqui é menor que a porra da sua unha... e ele simplesmente não morre de velhice."
- **Pensamento do bicho em voz de gente**: "Ela pensa: foda-se... e volta a ser bebê."
- **Comparação do dia a dia** para explicar a ciência: "É tipo uma borboleta virar lagarta de novo!"
- **Imaginar a reação de alguém**: "Imagina a cara dele: caralho, ela rejuvenesceu!"
- **Fecho seco depois do fato**, curto e de uma ou duas palavras: "Já era. Vira lanche." / "Malandra demais." / "Que bicho estranho da porra."
- **Exagero de três**: "e ela faz isso de novo, e de novo, e de novo."

Cada fecho seco e cada exclamação é um ponto para uma imagem de reação (veja as regras acima). Escreva o roteiro já marcando essas palavras, porque elas viram as `tomadas` do JSON.

### Como achar a imagem

Para cada frase do roteiro, pergunte:
- **Qual é a palavra concreta?** (lanche, unha, bebê, estudante)
- **Qual emoção a frase pede?** (susto, desdém, malandragem)
- **Existe um bicho fazendo essa cara?**

Busque pelo substantivo concreto em inglês no `buscar_commons.py`.

| Tipo de fala | Imagem que funcionou | Termo de busca que achou |
|---|---|---|
| Susto, "como assim?", bizarro | gatinho com cara de susto | `surprised face` |
| "Caralho!", choque, descoberta | bebê de boca aberta | `surprised face` |
| "Foda-se", "tanto faz", desistir | boneco laranja dando de ombros (vetor CC0) | `shrugging man` |
| Malandro, esperto, de boa | cachorro de óculos escuros | `dog sunglasses` |
| Ser comido, "já era", fome | sanduíche | `sandwich` |
| Predador com fome | peixe de boca aberta | `fish open mouth` |
| Renascer, voltar a ser jovem | bebê rindo | `baby laughing` |
| Velhice | idoso sorrindo (CC0) | `elderly man portrait smiling` |
| Tamanho minúsculo | mão em close | `Opposable thumbs` |
| "Nem tem cérebro" / "nem coração" | ilustração do cérebro / modelo de coração | `human brain`, `anatomical heart model` |
| Pessoa de uma época | estudante dos anos 80 | `university student 1980s` |
| Época / país | carro icônico da época, cidade real | `Fiat Panda 1980`, nome da cidade |
| "Cientistas descobriram" | equipe em laboratório (CC0) | `scientists laboratory` |

**Buscas que não funcionaram** (evite): `fingernail close-up` (trouxe conteúdo adulto), `Italy 1980s street`, `confused man face` e `shocked man face` (só pinturas antigas e livros digitalizados). Para emoções, busque bicho ou bebê em vez de "man face".

**Ideias ainda não testadas** para os próximos vídeos (confira licença e qualidade antes):
- gato bocejando → tédio
- cachorro inclinando a cabeça → confusão
- coruja encarando → desconfiança
- estátua com a mão na testa → facepalm
- caveira → morte
- troféu → recorde
- explosão → algo exagerado

### Banco de reações pronto

Em `banco_imagens/` há 14 imagens já aprovadas (1800 px, licença livre): gato surpreso, bebê espantado, boneco dando de ombros, bebê rindo, idoso sorrindo, cachorro de óculos, sanduíche, peixe de boca aberta, mão em close, cérebro, coração, estudante dos anos 80, Fiat Panda 1988 e cientistas no laboratório.

- O `banco.json` diz quando usar cada uma, quem é o autor e qual é a licença.
- Para usar, copie a imagem para a pasta `imgs` do projeto e **ponha o crédito no .txt de descrição**. As licenças CC BY e CC BY-SA exigem.
- Não repita a mesma reação em vídeos seguidos do canal, para não cansar. Varie e aumente o banco com as novas que funcionarem.

## Ferramentas (já instaladas no PC)

- ffmpeg 9 com NVENC (`h264_nvenc`). Rode **um render por vez**: renders em paralelo já travaram o PC.
- Python 3.12 com `edge-tts`, `pillow`, `numpy` e `faster-whisper`.
- `scripts/build_short.py`: o motor de montagem. Lê um `projeto.json` e gera um MP4 1080×1920 a 30 fps.
- `scripts/transcrever.py`: gera o `words.json` (tempo de cada palavra) a partir de uma narração pronta.
- `scripts/buscar_commons.py "termo1" "termo2"`: busca imagens livres no Wikimedia Commons, já tirando licenças NC e GFDL.
- `exemplo/agua_viva_imortal.json`: o projeto aprovado. Use como modelo.

## Passo a passo

1. **Roteiro** (~60–75 s, ~11 cenas): gancho forte na 1ª frase, 5–6 curiosidades numeradas, CTA no final com pergunta ("comenta aí e se inscreve"). Confira os fatos. Cada cena tem `imagem`, `texto` e `etiqueta` (tag amarela no topo, ex.: "#1 ELA VOLTA A SER BEBÊ").
2. **Imagens**: busque com `buscar_commons.py`. Prefira CC0, domínio público, CC BY e CC BY-SA, e evite NC (o vídeo pode ser monetizado). Baixe pela API `imageinfo` com `iiurlwidth=2000`, salve o autor e a licença, e espere 2–3 s entre as requisições.
   - O Commons devolve **429** se você buscar rápido demais; use User-Agent com contato e repita com pausa.
   - Buscas genéricas ("fingernail", "close-up") trazem **conteúdo adulto**. Leia os títulos e descarte antes de baixar.
   - Monte uma folha de contato (miniaturas + nome) e **olhe** antes de usar. Descarte as ruins.
   - PNG → converta para JPG com fundo branco. Aplique `exif_transpose`. Reduza para no máximo 2600 px.
3. **Tomadas** (`tomadas` no JSON): para cada cena, uma lista `[imagem, palavra_do_roteiro]`, em que a imagem entra quando essa palavra é dita (`null` = início da cena). As palavras são procuradas em ordem dentro da cena.
4. **Foco** (`foco`): `{imagem: [x, y]}` em frações, para imagens cujo assunto não está no centro (ex.: pessoa no canto). Confira no quadro renderizado.
5. **Narração**:
   - Rascunho: `python build_short.py projeto.json saida.mp4` (edge-tts, `pt-BR-AntonioNeural`, `+22%`).
   - Voz humana: coloque o .wav numa pasta própria, rode `python transcrever.py pasta/voz.wav` e depois `python build_short.py projeto.json saida.mp4 pasta/voz.wav`. O script alinha o roteiro à transcrição (difflib) e interpola as palavras que não casarem.
   - No AI Studio funcionou: voz **Mako** ("energetic and colorful") com o estilo "Narrador brasileiro de YouTube Shorts, muito animado e engraçado, tom de zoeira e espanto, ritmo rápido e dinâmico, sem pausas longas." Não digite `<` no texto, porque abre o menu de tags.
6. **Conferir antes de entregar**:
   - Extraia quadros no meio das tomadas (`select=eq(n\,N)` + `tile`) e veja se a imagem bate com a legenda e se nada fica cortado.
   - Volume entre -14 e -16 LUFS (`-af ebur128`).
   - Compare a transcrição com o roteiro e avise de palavras que a voz pode ter falado errado (ex.: "volta a ser bebê" soou como "volta a se beber").
   - Você não escuta o áudio: diga isso ao Diogo e peça para ele ouvir.

## Estilo visual do motor

Fundo desfocado e escurecido + imagem central com faixas amarelas (ou tela cheia para imagens em retrato) · Ken Burns com zoom-soco na entrada de cada tomada · flash branco e "whoosh" sintetizado nos cortes (mais forte na troca de cena) · legenda karaokê de até 3 palavras em Segoe UI Bold maiúsculo, palavra atual em amarelo, em y=1620 · etiqueta amarela no topo · barra de progresso amarela no topo · música lo-fi sintetizada em numpy (Am-F-C-G, 104 bpm), sem direitos autorais.

## Armadilhas já resolvidas

- `faster-whisper` com caminho de arquivo quebra no PyAV novo (`metadata_errors`): passe um array numpy decodificado pelo ffmpeg (o `transcrever.py` já faz isso).
- No Windows, salve e leia JSON sempre com `encoding="utf-8"`. Senão, sai em cp1252 e os acentos quebram.
- O terminal mostra acentos como `�`; é só exibição.
- Legenda em cima da faixa amarela: a imagem central vai até y≈1488, então a legenda fica em y=1620.

## Animações desenhadas por código (`@nome`)

O Diogo pediu "animaçãozinha, não só fotos". O motor aceita tomadas animadas:
- No `projeto.json`, `"animacoes": "animacoes.py"` aponta para um módulo do projeto com `frame(nome, lt, dur, t)` → PIL RGB 1080×1920 e, opcional, `sfx(nome, sr, dur)` → np.array (sino de round, explosão etc.).
- Use `"@nome"` no lugar da imagem (em `imagem` ou nas `tomadas`). A etiqueta, a legenda, o flash e a barra de progresso continuam por cima. Deixe livre o topo (até y≈280) e a faixa da legenda (y≈1480–1750).
- Modelo pronto: `exemplo/batalha_animacoes.py` (personagens Tardi e Medusa, VS, round com sino, placar animado, termômetro, foguete, confete) e `exemplo/batalha_tardigrado_agua_viva.json`.
- Antes de renderizar, gere folhas de contato com 4 instantes de cada animação e olhe; teste também todos os `sfx` com durações curtas e longas (um buffer curto já derrubou o render no fim).
- Âncoras das tomadas: a voz sintética junta número com a palavra anterior ("Em 2007" vira um token). Não ancore em palavra colada em número. Se a âncora falhar, o motor agora diz a cena, a palavra e a lista de palavras disponíveis.
