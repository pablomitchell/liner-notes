import torch
from transformers import BertTokenizer, EncoderDecoderModel


tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
#model = EncoderDecoderModel.from_encoder_decoder_pretrained('bert-base-uncased', 'bert-base-uncased')
model = EncoderDecoderModel.from_encoder_decoder_pretrained('bert-base-uncased', 'gpt2-large')

input = """2016 chateau pontet canet  bordeaux"""
encoder_input_ids = tokenizer(input, return_tensors='pt').input_ids




# output = """well you already know how i feel about 2016. if you are looking for investment grade top-end association bottles look no further the 2016 pontet-canet is absolutely breathtaking. powerful ample and racy in the glass the 2016 is one of the most exquisitely well-balanced young pontet-canets i can remember tasting. savory high-toned aromatics and brisk mineral notes lend energy and delineation as this vivid wonderfully alive wine opens up in the glass. the flavors are dark and incisive but it is the wine's total sense of harmony that is most compelling. all of the elements are simply in the right place. the 2016 is tremendous. it's as simple as that. as is often the case pontet-canet is one of the most singular wines in bordeaux. alfred tesseron could have chosen to play things safe when he took over the management of the estate in the mid-1990s. instead he chose a very different path. no proprietor in bordeaux has taken more risks over the last two decades than alfred tesseron. a commitment to biodynamic farming sustainability across the entire estate more broadly and the adoption of new concepts for bordeaux such as aging a portion of the wine in terra cotta set pontet-canet apart from other properties in pauillac and the left bank. not surprisingly the wine is also starkly different from the wines of neighboring estates. 2022 to 2066. amazing 2016 chateau pontet canet 750ml bordeaux - 149.70 usd"""
# decoder_input_ids = tokenizer(output, return_tensors="pt").input_ids

