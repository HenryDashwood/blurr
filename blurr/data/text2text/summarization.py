# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/01zc_data-text2text-summarization.ipynb (unless otherwise specified).

__all__ = ['HF_SummarizationInput', 'HF_SummarizationBeforeBatchTransform']

# Cell
import ast
from functools import reduce

import torch
from transformers import *
from fastai.text.all import *

from ...utils import *
from ..core import *
from .core import *

logging.set_verbosity_error()

# Cell
class HF_SummarizationInput(HF_BaseInput): pass

# Cell
class HF_SummarizationBeforeBatchTransform(HF_BeforeBatchTransform):

    def __init__(self, hf_arch, hf_tokenizer, max_length=None, padding=True, truncation=True,
                 is_split_into_words=False, n_tok_inps=2, ignore_token_id=CrossEntropyLossFlat().ignore_index,
                 tok_kwargs={}, **kwargs):

        super().__init__(hf_arch, hf_tokenizer, max_length=max_length, padding=padding, truncation=truncation,
                         is_split_into_words=is_split_into_words, n_tok_inps=n_tok_inps,
                         tok_kwargs=tok_kwargs.copy(), **kwargs)

        self.ignore_token_id = ignore_token_id

    def encodes(self, samples):
        samples = super().encodes(samples)
        if (len(samples[0]) == 1): return samples

        updated_samples = []
        for s in samples:
            trg_input_ids = s[1]['input_ids']

            if (self.hf_arch in ['t5', 'pegasus']):
                # see: https://github.com/huggingface/transformers/issues/7986#issuecomment-714938591
                trg_input_ids = F.pad(trg_input_ids, pad=(1,0), value=self.hf_tokenizer.pad_token_id)[:-1]

            s[0]['decoder_input_ids'] = trg_input_ids[:-1].clone()
            s[0]['labels'] = trg_input_ids[1:].clone()
            s[0]['labels'][s[0]['labels'] == self.hf_tokenizer.pad_token_id] = self.ignore_token_id

            targ_ids = s[0]['labels'].clone()

            updated_samples.append((s[0], targ_ids))

        return updated_samples

# Cell
@typedispatch
def show_batch(x:HF_SummarizationInput, y, samples, dataloaders, ctxs=None, max_n=6,
               input_trunc_at=None, target_trunc_at=None, **kwargs):

    before_batch_tfm = dataloaders.before_batch[0]
    hf_tokenizer = before_batch_tfm.hf_tokenizer
    ignore_token_id = before_batch_tfm.ignore_token_id

    res = L([ (hf_tokenizer.decode(s[0], skip_special_tokens=True)[:input_trunc_at],
               hf_tokenizer.decode(s[1][s[1] != ignore_token_id], skip_special_tokens=True)[:target_trunc_at])
             for s in samples ])

    display_df(pd.DataFrame(res, columns=['text', 'target'])[:max_n])
    return ctxs