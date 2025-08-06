from backend.utils import openai


def run():
    x = openai.get_embedding("Hello, world!")
    print(len(x))

    batch_data = ["Hello, world!", "Goodbye, world!"]
    batch_x = openai.get_embeddings_batch(batch_data)
    print(len(batch_x))
    print(len(batch_x[0]))
    print(len(batch_x[1]))
