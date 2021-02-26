import torch
from datasets import load_dataset, load_metric
from transformers import BertTokenizer, EncoderDecoderModel


batch_size = 64  # 16 or change to 64 for full evaluation
encoder_max_length = 128
decoder_max_length = 512
device = 'cuda' if torch.cuda.is_available() else 'cpu'

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
ed_model = EncoderDecoderModel.from_pretrained('./checkpoint-1500')
ed_model.to(device)

csv_file = '../data/foo.csv'
test_data = load_dataset(
    'csv',
    data_files=csv_file,
    split='train',
)
# only use 16 training examples for notebook - COMMENT LINE FOR FULL TRAINING
#test_data = test_data.select(range(16))
test_data = test_data.select(range(3))


# load rouge for validation
rouge = load_metric('rouge')


# map data correctly
def generate_description(batch):
    # Tokenizer will automatically set [BOS] <text> [EOS]
    # cut off at BERT max length
    inputs = tokenizer(batch['name'], padding='max_length', truncation=True,
                       max_length=encoder_max_length, return_tensors='pt')
    input_ids = inputs.input_ids.to(device)
    attention_mask = inputs.attention_mask.to(device)

    outputs = ed_model.generate(input_ids, attention_mask=attention_mask)

    # all special tokens including will be removed
    output_str = tokenizer.batch_decode(outputs, skip_special_tokens=True)

    batch['pred'] = output_str

    return batch


#results = test_data.map(generate_description, batched=True, batch_size=batch_size, remove_columns=['name'])
results = test_data.map(generate_description, batched=True, batch_size=batch_size)
name_str = results['name']
note_str = results['note']
pred_str = results['pred']

rouge_output = rouge.compute(predictions=pred_str, references=note_str, rouge_types=['rouge2'])['rouge2'].mid
print(rouge_output)
print()

for name, note in zip(name_str, pred_str):
    print(name)
    print()
    print(note)
    print('-'*45)

