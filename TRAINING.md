# 🎓 Modo de Treinamento - Guia Completo

## O que é o Modo de Treinamento?

O **modo de treinamento** é uma ferramenta para calibrar o reconhecimento de expressões faciais de acordo com:
- Sua webcam específica
- Sua iluminação
- Suas expressões faciais pessoais
- Seu ambiente

## Por que fazer treinamento?

Cada ambiente é diferente:
- 🎥 **Webcams variam**: baixa resolução, boa resolução, diferentes ângulos
- 💡 **Iluminação muda**: luz natural, artificial, pouca luz, etc.
- 👤 **Expressões são pessoais**: intensidade, rapidez, estilo de rosto
- 🏠 **Ambiente diferente**: escritório, sala, cozinha, etc.

Sem calibração, o modelo padrão pode ter taxa de erro alta (30-50% ou mais).

**Com treinamento, você pode melhorar a precisão em até 30-40%!**

## Como usar

### Passo 1: Iniciar o Modo de Treinamento

```
1. Execute o jogo normalmente
2. Pressione "T" (de Training)
3. Você verá a tela do modo de treinamento
```

### Passo 2: Ler as Instruções

Você verá:
```
MODO DE TREINAMENTO
Treinaremos com suas expressões específicas

SPACE para começar | ESC para sair
```

### Passo 3: Começar o Treinamento

```
Pressione SPACE para iniciar
```

### Passo 4: Fazer Expressões

Para cada expressão (Smile, Disgust, Surprise), o jogo vai:

1. **Contar regressivamente** (3s): Prepare-se
2. **Registrar** (3s): Faça a expressão e MANTENHA-A
3. **Próxima expressão**: Repita

#### 💡 Dicas para cada expressão:

**😊 Smile (Sorria)**
- Sorria naturalmente (não force demais)
- Mostre os dentes levemente
- Duração: mantenha por 3 segundos

**😖 Disgust (Nojo)**
- Faça uma careta
- Franzir a testa, enrugar o nariz
- Abaixar os cantos da boca
- Duração: mantenha por 3 segundos

**😲 Surprise (Surpresa)**
- Abra os olhos bem
- Levante as sobrancelhas
- Abra a boca um pouco
- Duração: mantenha por 3 segundos

### Passo 5: Revisar Resultados

Após coletar amostras, você verá:

```
✓ CALIBRAÇÃO CONCLUÍDA!

Thresholds recomendados:
happiness: 0.47
disgust: 0.30
surprise: 0.38
```

Estes são **valores otimizados para você**!

### Passo 6: Salvar ou Descartar

```
SPACE: salvar | ESC: descartar
```

- **Pressione SPACE** para salvar os thresholds personalizados
- **Pressione ESC** para descartar e usar valores padrão

## Onde são salvos os dados?

Os dados são salvos em **`.training_data.json`** na raiz do projeto.

Exemplo:
```json
{
  "thresholds": {
    "happiness": 0.47,
    "disgust": 0.30,
    "surprise": 0.38,
    "neutral": 0.45
  },
  "sessions": [
    {
      "target": "smile",
      "average_scores": { ... },
      "num_samples": 45
    },
    ...
  ]
}
```

## Quando treinar novamente?

Retreine se:
- 📍 **Mudou de lugar** (diferente iluminação)
- 🎥 **Mudou de câmera** (outra webcam)
- 👨 **Outra pessoa vai usar** (expressões diferentes)
- 📱 **A precisão caiu** (algo mudou no ambiente)

## Dúvidas Frequentes

### P: Posso fazer treinamento múltiplas vezes?
**R:** Sim! Cada treinamento substitui o anterior. Use o mais recente.

### P: E se eu não fizer treinamento?
**R:** O jogo usa os thresholds padrão. Pode funcionar, mas a precisão pode ser menor.

### P: Quanto tempo leva?
**R:** ~15 segundos no total. Muito rápido!

### P: E se não conseguir fazer a expressão bem?
**R:** Tudo bem! Faça da forma mais natural para você. O sistema calcula a média.

### P: Posso deletar `.training_data.json`?
**R:** Sim. O jogo voltará a usar os thresholds padrão automaticamente.

### P: Os dados são compartilhados?
**R:** Não! Ficam apenas no seu computador.

## Resultado Esperado

Antes do treinamento:
```
Teste rápido: acerta 2 de 5 expressões (40%)
```

Depois do treinamento:
```
Teste rápido: acerta 4 de 5 expressões (80%)
```

## Próximos Passos

Depois de treinar, **volte ao jogo principal** e veja como fica!

A precisão deve melhorar **significativamente**.

---

**Bom treinamento! 🚀**
