# XLConvosumm-bot
## Concerning models
### Introduction

Conversation, discussion - A sequence of sentences whose semantics implies the presence of a **subject** of discussion, main **theses** on the matter and **premises** to the theses. These are three main entities summarizer has to consider, for it to make conversation summary short, but informative.
I have not met any dataset, except [Convosumm](https://github.com/Yale-LILY/ConvoSumm), that would provide a similar decomposition of chat polemics in summarization. In addition, other popular datasets, despite their size, mostly contains short and oversimplified messages. While size of the input sequence in Convosumm even require to extend model's positional encodings for it to grasp all data points. And the last problem - most of my chat polemics are in russian language.

So there are three motivational problems:
1. Longer than usual input context required.
2. More complex summary structure.
3. Cross language inference.

### Expirementing

Based on the article by the creators of Convosumm, SOTA result was achieved by fine-tuning BART language model (LM) pre-trained on CNN-DM, which outperformed T5 (probably due to the specifics of BART’s pre-training task).

I assumed that initializing LM with weights of fine-tuned models on similar task datasets (XSum, samsum) could improve convergence. The hypothesis did not hold up in practice, and it was not possible to escape from the local minima of the original tasks:

**Expirements**
| Model | Wandb Logs |
| --- | --- |
| [facebook/bart-large-cnn](https://huggingface.co/facebook/bart-large-cnn) | [Click](https://wandb.ai/remeris/Convosumm-Models-comparison/runs/dfdt7k6a)|
| [facebook/bart-large-xsum](https://huggingface.co/facebook/bart-large-cnn) | [Click](https://wandb.ai/remeris/Convosumm-Models-comparison/runs/afbi9efy)|
| [kabita-choudhary/finetuned-bart-for-conversation-summary](https://huggingface.co/facebook/bart-large-cnn) | [Click](https://wandb.ai/remeris/Convosumm-Models-comparison/runs/sw9vwayl) |
| [lidiya/bart-large-xsum-samsum](https://huggingface.co/facebook/bart-large-cnn) | [Click](https://wandb.ai/remeris/Convosumm-Models-comparison/runs/t2szthnp)|

After choosing pre-trained model and successefuly testing it's ability to learn extended positional encodings, next problem was to adapt it to russian language. Initial thought was to translate dataset using the GoogleTranslate API and fine-tune multi-language LM as it was done in [mbart_ruDialogSum](https://huggingface.co/Kirili4ik/mbart_ruDialogSum) and [d0rj/rut5-base-summ](https://huggingface.co/d0rj/rut5-base-summ). So two models were fine-tuned but results appeared to be quite poor, models converged, but metrics weren't improving and inference produced only gibberish. Main cause of quality loss - dataset auto-translation.

**Expirements**
| Model | Wandb Logs |
| --- | --- |
| [IlyaGusev/mbart_ru_sum_gazeta](https://huggingface.co/IlyaGusev/mbart_ru_sum_gazeta) | [Click](https://wandb.ai/remeris/Convosumm-Models-comparison/runs/dn5wjcv4)|
| [d0rj/rut5-base-summ](https://huggingface.co/d0rj/rut5-base-summ) | [Click](https://wandb.ai/remeris/Convosumm-Models-comparison/runs/og2mm25e)|

### Final solution
Considering everything mentioned above, the final hypothesis was as follows: in a resource-limited environment [facebook/bart-large-cnn](https://huggingface.co/facebook/bart-large-cnn) with extended positional encodings fine-tuned on Convosumm will produce the best possible result. Pre and post translation of text sequences with an English LM inference in between will have less negative impact on the overall quality of the output, rather than blunt translation of the whole Convosumm dataset and training russian LM on it.

Hyper-parameters and context extention method are taken from the original [dataset article](https://arxiv.org/pdf/2106.00829.pdf) and [general article](https://arxiv.org/pdf/2010.12836.pdf) on LM fine-tuning on abstract summarization.

**Final results**
| Model | Wandb Logs |
| --- | --- |
| [Remeris/BART-CNN-Convosumm](https://huggingface.co/Remeris/BART-CNN-Convosumm) | [Click](https://wandb.ai/remeris/BART-CNN-Convosumm/runs/68syxthd)|

## Concerning bots