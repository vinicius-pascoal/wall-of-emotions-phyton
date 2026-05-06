# Expression Wall - Py-Feat

Versão em Python do jogo inspirado em **Hole in the Wall**, usando webcam e **Py-Feat** para detectar expressões faciais.

Nesta versão, o jogador precisa fazer a expressão facial sorteada antes que a parede chegue ao final da tela.

## Expressões usadas

| Alvo no jogo | Emoção usada no Py-Feat |
|---|---|
| Smile / Sorria | `happiness` |
| Disgust / Nojo | `disgust` |
| Surprise / Surpresa | `surprise` |
| Neutral / Neutro | estado interno, não sorteado |

## Mecânicas implementadas

- **Menu principal** com opções de jogar ou calibrar.
- Sorteio de expressão alvo por rodada.
- Parede se aproximando visualmente.
- Validação por threshold da emoção alvo.
- A emoção alvo não precisa ser a maior absoluta; basta passar do threshold.
- Pausa da rodada quando não há rosto detectado.
- Score, vidas, tempo, combo e número da rodada.
- Tela de game over.
- **Modo de treinamento para calibração de expressões.**
- Reinício com `R`.
- Debug das emoções com `D`.
- Sair com `ESC`.

## Requisitos recomendados

- Python 3.11 (recomendado e testado). Python 3.10 ou 3.12 podem funcionar, mas 3.11 é a versão recomendada para evitar problemas de compatibilidade com dependências nativas.
- Webcam funcional.
- Boa iluminação no rosto.
- Internet na primeira execução, pois o Py-Feat pode baixar modelos automaticamente.

## Instalação manual

Use preferencialmente o Python 3.11. No Windows recomenda-se o `py` launcher; no Linux/macOS use `python3.11` se disponível.

```bash
# Windows (recomendado)
py -3.11 -m venv .venv

# Linux/macOS (se tiver python3.11 instalado)
python3.11 -m venv .venv
```

### Windows

```bash
# Ative o virtualenv criado com o Python 3.11
.venv\Scripts\Activate.ps1    # PowerShell
# ou
.venv\Scripts\activate       # cmd

python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
python main.py
```

### Linux/macOS

```bash
# Ative o virtualenv criado com python3.11
source .venv/bin/activate

python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
python main.py
```

## Execução automática

### Windows

Dê dois cliques em:

```txt
run_windows.bat
```

### Linux/macOS

```bash
chmod +x run_linux_mac.sh
./run_linux_mac.sh
```

## Comandos do jogo

| Tecla | Ação |
|---|---|
| **↑ ↓** | Navegar no menu |
| **ENTER / SPACE** | Selecionar opção do menu |
| **T** | Entrar no modo de treinamento (durante o jogo) |
| **D** | Mostrar/ocultar debug das emoções |
| **R** | Reiniciar depois do game over (volta ao menu) |
| **ESC** | Voltar ao menu / Sair |

## � Menu Principal

Ao iniciar o jogo, você verá o **menu principal** com duas opções:

### 1. 🎮 JOGAR
Inicia o jogo normal. Faça as expressões sorteadas antes que a parede chegue ao final da tela.

### 2. ⚙️ CALIBRAR  
Entra no **modo de treinamento** para otimizar a detecção de expressões com sua webcam e ambiente.

**Dica:** Se a precisão está baixa, faça o treinamento primeiro! Pode melhorar muito.

O **modo de treinamento** ajuda a melhorar a precisão da detecção calibrando os thresholds com suas expressões específicas.

### Como usar:

1. **Inicie o jogo e pressione `T`** para entrar no modo de treinamento
2. **Pressione `SPACE`** para começar
3. **O jogo pedirá para fazer cada expressão por ~3 segundos:**
   - Smile / Sorria
   - Disgust / Nojo
   - Surprise / Surpresa
4. **Após coletar amostras**, o sistema recomendará thresholds otimizados
5. **Pressione `SPACE` para salvar** ou `ESC` para descartar

Os thresholds personalizados são salvos em `.training_data.json` e usados automaticamente nas próximas execuções.

### Por que fazer treinamento?

- Cada webcam/iluminação é diferente
- Expressões faciais variam por pessoa
- Thresholds personalizados **aumentam significativamente a precisão**
- O treinamento leva apenas ~15 segundos!

## Escolher outra webcam

Se a webcam padrão não abrir:

```bash
python main.py --camera 1
```

ou:

```bash
python main.py --camera 2
```

## Ajustar frequência de detecção

O Py-Feat é mais pesado que detectores simples. Por padrão, a inferência roda a cada `0.8s`.

Para tentar uma resposta mais rápida:

```bash
python main.py --interval 0.5
```

Se o jogo travar ou ficar pesado:

```bash
python main.py --interval 1.0
```

## Ajustar thresholds

Os thresholds ficam em:

```txt
src/config.py
```

Valores iniciais:

```python
THRESHOLDS = {
    "happiness": 0.55,
    "disgust": 0.35,
    "surprise": 0.45,
    "neutral": 0.45,
}
```

Se uma expressão estiver difícil de acertar, reduza o valor dela.

Exemplo:

```python
"disgust": 0.25
```

## Estrutura do projeto

```txt
hole_in_the_wall_pyfeat/
├── main.py
├── requirements.txt
├── run_windows.bat
├── run_linux_mac.sh
├── README.md
├── src/
│   ├── config.py
│   ├── expression_target.py
│   ├── expression_reader.py
│   ├── game_manager.py
│   ├── hud.py
│   └── wall.py
└── assets/
    ├── fonts/
    └── sounds/
```

## Possíveis problemas

### A câmera não abre

Feche Discord, Teams, Zoom, navegador ou qualquer app usando a webcam.

Depois tente:

```bash
python main.py --camera 1
```

### Py-Feat demora muito na primeira execução

É esperado. A primeira execução pode baixar os modelos de detecção.

### O jogo está pesado

Aumente o intervalo de inferência:

```bash
python main.py --interval 1.2
```

### Instalação do Py-Feat falha no macOS com chip Apple Silicon

Tente instalar o PyTables antes:

```bash
pip install git+https://github.com/PyTables/PyTables.git
pip install -r requirements.txt
```

ou use conda:

```bash
conda install pytables
pip install -r requirements.txt
```

## Próximas melhorias recomendadas

- Menu inicial.
- Sons de acerto/erro.
- Recorde local em JSON.
- Tela de calibração de expressões.
- Assets visuais para a parede.
- Modo treino sem vidas.
- Ranking por pontuação.
- Partículas e animações de feedback.
