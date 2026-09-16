from transformers import GenerationConfig

gen_config = GenerationConfig(
    max_length=60,
    min_length=20,
    num_beams=10,
    length_penalty=0.65,
    no_repeat_ngram_size=3,
    encoder_no_repeat_ngram_size=3,
    forced_eos_token_id=2
)

gen_config.save_pretrained("D:/Download/HugginFace/VenusChatbot/Venus_project/static/sauv_config")
