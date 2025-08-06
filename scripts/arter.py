from backend.utils import openai
from cinematch.models import Movie


def run():
    x = openai.get_embedding("Hello, world!")
    print(len(x))

    batch_data = ["Hello, world!", "Goodbye, world!"]
    batch_x = openai.get_embeddings_batch(batch_data)
    print(len(batch_x))
    print(len(batch_x[0]))
    print(len(batch_x[1]))

    movies = Movie.objects.all().order_by("-id")
    total_movies = movies[:200].count()
    processed_count = 0
    skipped_count = 0

    for movie in movies[:200]:
        m = f"Movie: {movie.title}, Description: {movie.description}, Release Date: {movie.release_date}, Rating: {movie.rating}, Genres: {[genre.name for genre in movie.genre.all()]}, Talents: {[talent.name for talent in movie.talent.all()]}, Original Language: {movie.original_language}"

        if movie.embedding is not None:
            print(f"Embedding already exists for movie: {movie.title}")
            skipped_count += 1
            continue

        print(f"Generating embedding for movie: {movie.title}")
        openai_embedding = openai.get_embedding(m)
        movie.embedding = openai_embedding
        movie.save()
        processed_count += 1

    print(f"Completed! Processed: {processed_count}, Skipped: {skipped_count}, Total: {total_movies}")
