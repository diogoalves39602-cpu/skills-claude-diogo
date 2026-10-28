# Skills do Claude do Diogo

Todas as skills que eu uso no Claude Code, prontas para instalar.

## Instalar (Windows)

1. Baixe este repositório (botão verde **Code → Download ZIP**, ou `git clone`).
2. Abra a pasta e rode no PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\instalar.ps1
```

Isso copia tudo de `skills\` para `%USERPROFILE%\.claude\skills\`. Feche e abra o Claude de novo para ele carregar as skills.

No Mac/Linux: `cp -r skills/* ~/.claude/skills/`

## O que tem aqui

| Skill | O que faz | Origem |
|---|---|---|
| `editor-de-shorts` | Cria Shorts/Reels/TikTok narrados, do roteiro ao MP4 | Feita por nós |
| `maestro` | Escolhe a melhor skill para cada tarefa (`/maestro`) | Feita por nós |
| `ego-browser` | Automação de navegador | citrolabs/ego-lite |
| `find-skills` | Acha e instala skills novas | vercel-labs/skills |
| `security-audit` | Revisão de segurança de código | cloudflare/security-audit-skill |
| `slopmonster` | Tira "cara de IA" de textos | ItsssssJack/SlopMonster (MIT) |
| `playwright-cli` | Testes e automação com Playwright | Playwright |
| `reverse-engineer-anything` | Engenharia reversa com REA (precisa do servidor REA) | REA |

## Plugins (instalar à parte)

Também uso estes plugins. Dentro do Claude Code, rode:

```
/plugin marketplace add addyosmani/agent-skills
/plugin marketplace add Jakeschincariol/arena-skill
/plugin marketplace add rehan-remade/universal-modder
```

Depois `/plugin` e instale `agent-skills`, `arena-skill` e `universal-modder`.

## Requisitos do editor-de-shorts

- ffmpeg (eu uso com GPU NVIDIA / NVENC; sem NVIDIA, troque `h264_nvenc` por `libx264` em `scripts/build_short.py`)
- Python 3.12 com: `pip install edge-tts pillow numpy faster-whisper`

**Atenção:** a skill foi escrita para mim. Ela fala "o Diogo gosta de…", usa a pasta `C:\Users\diogo\Downloads` e tem meu e-mail no User-Agent de `scripts/buscar_commons.py`. Troque pelo seu nome, pasta e e-mail em `SKILL.md` e nesse script (ou peça ao Claude: "adapte a skill editor-de-shorts para mim").

As imagens em `banco_imagens/` vêm do Wikimedia Commons; autor e licença de cada uma estão em `banco.json`.
