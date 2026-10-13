### Sistema de Reconhecimento Facial
Este será um sistema de reconhecimento facial desenvolvido com Machine 
Learning e segundo a abordagem Spec-Driven Development.

**Problema**: Os problemas são os seguintes: 
1. Dada a imagem de uma pessoa, detectar (via modelo treinado por ML) se ela 
pertence a um certo grupo de pessoas, e, se sim, qual delas está na imagem.
 
 - Montar a amostra de dados (público-privada).

 - Decidir qual MODELO de IA será desenvolvido para a detecção.

 - Treinar o modelo adequadamente.

2. Dadas algumas imagens de uma pessoa, adicioná-la ao grupo de pessoas que 
podem ser reconhecidas.

3. Dado o identificador de uma pessoa, retirá-la do grupo de pessoas que podem
ser reconhecidas.

**Requisitos**:
* Requisitos Funcionais:
  - [ ] A
  - [ ] B
  - [ ] C

* Requisitos Técnicos:
  - [ ] A
  - [ ] B
  - [ ] C

**Especificação**: AFAZER.

**Planejamento**: AFAZER.

**Implementação**: AFAZER.

**Testes**: AFAZER.

**Revisão**: AFAZER.
##Estratégias a serem investigadas

Podem ser comparadas, entre outras:
* Modelo pré-treinado sem fine-tuning
Modelo pré-treinado > Embeddings > Reconhecimento

* Fine-tuning parcial
Parte da rede permanece congelada enquanto as últimas camadas são atualizadas.

* Fine-tuning completo
Os parâmetros da rede são atualizados durante o treinamento.

## Estratégias de comparação

Podem ser utilizadas:

* distância Euclidiana;

* similaridade de cosseno;

* k-NN;

* SVM;

* protótipos de classe;

* outros classificadores.

## Funções de perda

Podem ser investigadas:

* Cross-Entropy;

* Contrastive Loss;

* Triplet Loss;

* ArcFace Loss;

* outras técnicas de Metric Learning.

