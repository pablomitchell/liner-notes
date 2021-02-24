import torch
from datasets import load_dataset, load_metric
from transformers import BertTokenizer, EncoderDecoderModel
from transformers import Seq2SeqTrainer, Seq2SeqTrainingArguments


tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
tokenizer.bos_token = tokenizer.cls_token
tokenizer.eos_token = tokenizer.sep_token

csv_file = '../data/garagiste_wine_clean.csv'
val_data = load_dataset('csv', data_files=csv_file, split='train[90%:]')
train_data = load_dataset('csv', data_files=csv_file, split='train[:90%]')
print(val_data)
print(train_data)

batch_size = 16  # 4 but change to 16 for full training
encoder_max_length = 128
decoder_max_length = 2048
device = 'cuda' if torch.cuda.is_available() else 'cpu'


def process_data_to_model_inputs(batch):
    # tokenize the inputs and labels
    tok_params = {
        'padding': 'max_length',
        'truncation': True,
        'max_length': encoder_max_length,
    }
    inputs = tokenizer(batch['name'], **tok_params)
    outputs = tokenizer(batch['note'], **tok_params)

    batch['input_ids'] = inputs.input_ids
    batch['attention_mask'] = inputs.attention_mask
    batch['decoder_input_ids'] = outputs.input_ids
    batch['decoder_attention_mask'] = outputs.attention_mask
    batch['labels'] = outputs.input_ids.copy()

    # because BERT automatically shifts the labels, the labels correspond exactly to `decoder_input_ids`.
    # We have to make sure that the PAD token is ignored
    batch['labels'] = [
        [-100 if token == tokenizer.pad_token_id else token for token in labels] for labels in batch['labels']
    ]

    return batch


# only use 32 training examples for notebook - COMMENT LINE FOR FULL TRAINING
# train_data = train_data.select(range(32))

train_data = train_data.map(
    process_data_to_model_inputs,
    batched=True,
    batch_size=batch_size,
    remove_columns=['name', 'note'],
)
train_data.set_format(
    type='torch',
    columns=['input_ids', 'attention_mask', 'decoder_input_ids', 'decoder_attention_mask', 'labels'],
)

# only use 16 training examples for notebook - DELETE LINE FOR FULL TRAINING
# val_data = val_data.select(range(16))

val_data = val_data.map(
    process_data_to_model_inputs,
    batched=True,
    batch_size=batch_size,
    remove_columns=['name', 'note'],
)
val_data.set_format(
    type='torch',
    columns=['input_ids', 'attention_mask', 'decoder_input_ids', 'decoder_attention_mask', 'labels'],
)

ed_model = EncoderDecoderModel.from_encoder_decoder_pretrained('bert-base-uncased', 'bert-base-uncased')

# set special tokens
ed_model.config.decoder_start_token_id = tokenizer.bos_token_id
ed_model.config.eos_token_id = tokenizer.eos_token_id
ed_model.config.pad_token_id = tokenizer.pad_token_id

# sensible parameters for beam search
ed_model.config.vocab_size = ed_model.config.decoder.vocab_size
ed_model.config.max_length = 142
ed_model.config.min_length = 56
ed_model.config.no_repeat_ngram_size = 3
ed_model.config.early_stopping = True
ed_model.config.length_penalty = 2.0
ed_model.config.num_beams = 4


# load rouge for validation
rouge = load_metric('rouge')


def compute_metrics(pred):
    labels_ids = pred.label_ids
    pred_ids = pred.predictions

    # all unnecessary tokens are removed
    pred_str = tokenizer.batch_decode(pred_ids, skip_special_tokens=True)
    labels_ids[labels_ids == -100] = tokenizer.pad_token_id
    label_str = tokenizer.batch_decode(labels_ids, skip_special_tokens=True)

    rouge_output = rouge.compute(predictions=pred_str, references=label_str, rouge_types=['rouge2'])['rouge2'].mid

    return {
        'rouge2_precision': round(rouge_output.precision, 4),
        'rouge2_recall': round(rouge_output.recall, 4),
        'rouge2_fmeasure': round(rouge_output.fmeasure, 4),
    }


# set training arguments - these params are not really tuned, feel free to change
training_args = Seq2SeqTrainingArguments(
    output_dir='./',
    evaluation_strategy='steps',
    per_device_train_batch_size=batch_size,
    per_device_eval_batch_size=batch_size,
    predict_with_generate=True,
    logging_steps=20,  # 2 or set to 1000 for full training
    save_steps=160,  # 16 or set to 500 for full training
    eval_steps=40,  # 4 or set to 8000 for full training
    warmup_steps=10,  # 1 or set to 2000 for full training
    max_steps=160,  # 16 or comment for full training
    overwrite_output_dir=True,
    save_total_limit=3,
    fp16=torch.cuda.is_available(),
)

# instantiate trainer
trainer = Seq2SeqTrainer(
    model=ed_model,
    tokenizer=tokenizer,
    args=training_args,
    compute_metrics=compute_metrics,
    train_dataset=train_data,
    eval_dataset=val_data,
)
trainer.train()
