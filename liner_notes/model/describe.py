import torch
from transformers import BertTokenizer, EncoderDecoderModel


input_str = '1999 chevillon nuit saints georges villages france'

encoder_max_length = 128
device = 'cuda' if torch.cuda.is_available() else 'cpu'

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
ed_model = EncoderDecoderModel.from_pretrained('./checkpoint-500')
ed_model.to(device)

inputs = tokenizer(input_str, padding='max_length', truncation=True,
                   max_length=encoder_max_length, return_tensors='pt')
input_ids = inputs.input_ids.to(device)
attention_mask = inputs.attention_mask.to(device)
outputs = ed_model.generate(input_ids, attention_mask=attention_mask)
output_str = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]

print(f'NAME\n{input_str}')
print()
print(f'DESCRIPTION\n{output_str}')