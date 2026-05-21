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
\
# Instalação recomendada (passo-a-passo)
pip install --upgrade pip setuptools wheel
# Instala as dependências principais listadas no requirements
pip install -r requirements.txt

# Se houver problemas com o Py-Feat / torch, instale estas versões testadas (CPU)
pip install torch==2.4.1+cpu torchvision==0.19.1+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html
pip install numpy==1.23.5 scipy==1.13.1
pip install py-feat==0.6.2

# Execute o jogo usando o Python do .venv
.venv\Scripts\python.exe main.py
```

### Linux/macOS

```bash
# Ative o virtualenv criado com python3.11
source .venv/bin/activate

python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Se houver problemas com o Py-Feat / torch (Apple Silicon ou incompatibilidades), siga as instruções específicas do PyTorch
# e do Py-Feat. Para CPUs Intel/macOS padrão, instale:
pip install numpy==1.23.5 scipy==1.13.1 py-feat==0.6.2

python3 -m pip install --upgrade pip
python3 main.py
```

## Instalação detalhada / resolução de dependências (Py-Feat)

O Py-Feat depende de `torch`/`torchvision` e de versões compatíveis de `numpy` e `scipy`. Se durante `import feat` você vir erros como "cannot import name 'read_video' from 'torchvision.io'" ou mensagens sobre DLLs, tente alinhar as versões do `torch` e `torchvision` conforme abaixo.

Windows (CPU) — comandos testados nesta base:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install --upgrade pip setuptools wheel
pip install torch==2.4.1+cpu torchvision==0.19.1+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html
pip install numpy==1.23.5 scipy==1.13.1
pip install py-feat==0.6.2
pip install opencv-python pygame-ce pandas matplotlib
```

Observações:
- Se você usa GPU/CUDA, instale a versão do `torch`/`torchvision` adequada ao seu CUDA seguindo as instruções oficiais do PyTorch.
- Em Macs com Apple Silicon pode ser necessário compilar ou usar wheels específicos (ver documentação do PyTables/Py-Feat). Em caso de dificuldades, considere usar uma environment baseada em `conda`.

## Verificando o Py-Feat

Para testar rapidamente se o `py-feat` foi instalado corretamente:

```bash
.venv\Scripts\python.exe -c "import feat; print('py-feat', feat.__version__)"
```

No jogo, o HUD exibe o nome do detector (por exemplo `feat.Detector`) e, em caso de falha, a primeira linha do erro de carregamento. Também é possível pressionar `P` durante a execução para tentar recarregar o detector em tempo de execução.

## Solução de problemas comuns

- Erro ao importar `feat` (ex.: "cannot import name 'read_video' from 'torchvision.io'"): verifique se `torch` e `torchvision` são compatíveis. Reinstale conforme "Instalação detalhada".
- Erro do tipo "Can't call numpy() on Tensor that requires grad": instale as versões recomendadas de `torch`/`torchvision` e garanta que o detector esteja sendo chamado em modo de inferência — esta versão do jogo já faz isso.
- `ImportError` / DLL load failed no Windows: verifique o Microsoft Visual C++ Redistributable e use o Python do `.venv` (veja `run_windows.bat`).
- Py-Feat demora na primeira execução: é normal — modelos são baixados/compilados. Aguarde alguns minutos na primeira inicialização.

## Treinamento / calibração

Use o modo de treinamento no jogo (`T`) para calibrar thresholds personalizados. As recomendações são salvas em `.training_data.json` na raiz do projeto e aplicadas automaticamente nas próximas execuções.

## Verificar/alterar câmera e intervalo de inferência

```bash
python main.py --camera 1
python main.py --interval 0.5
```

## Execução direta (alternativa)

Para garantir que o Python correto do virtualenv seja usado no Windows:

```powershell
.venv\Scripts\python.exe main.py
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
