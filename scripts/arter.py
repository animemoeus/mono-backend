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

    # Get movies without embeddings
    movies_without_embeddings = Movie.objects.filter(embedding__isnull=True).order_by("-id")
    movies_with_embeddings = Movie.objects.filter(embedding__isnull=False).count()

    total_movies = len(movies_without_embeddings) + movies_with_embeddings
    processed_count = 0
    batch_size = 50

    print(
        f"Found {len(movies_without_embeddings)} movies without embeddings, {movies_with_embeddings} already have embeddings"
    )

    # Process movies in batches
    for i in range(0, len(movies_without_embeddings), batch_size):
        batch_movies = movies_without_embeddings[i : i + batch_size]

        # Prepare text descriptions for batch
        batch_texts = []
        for movie in batch_movies:
            movie_text = f"Movie: {movie.title}, Description: {movie.description}, Release Date: {movie.release_date}, Rating: {movie.rating}, Genres: {[genre.name for genre in movie.genre.all()]}, Talents: {[talent.name for talent in movie.talent.all()]}, Original Language: {movie.original_language}"
            batch_texts.append(movie_text)

        print(f"Processing batch {i // batch_size + 1}: {len(batch_movies)} movies")

        try:
            # Get embeddings for entire batch in single API call
            batch_embeddings = openai.get_embeddings_batch(batch_texts)

            # Assign embeddings to movies
            for movie, embedding in zip(batch_movies, batch_embeddings):
                movie.embedding = embedding

            # Bulk update database
            Movie.objects.bulk_update(batch_movies, ["embedding"])
            processed_count += len(batch_movies)

            print(f"Successfully processed batch of {len(batch_movies)} movies")

        except Exception as e:
            print(f"Batch processing failed: {e}")
            print("Falling back to individual processing for this batch...")

            # Fallback: process individually
            for movie in batch_movies:
                try:
                    movie_text = f"Movie: {movie.title}, Description: {movie.description}, Release Date: {movie.release_date}, Rating: {movie.rating}, Genres: {[genre.name for genre in movie.genre.all()]}, Talents: {[talent.name for talent in movie.talent.all()]}, Original Language: {movie.original_language}"
                    movie.embedding = openai.get_embedding(movie_text)
                    movie.save()
                    processed_count += 1
                    print(f"Individual processing: {movie.title}")
                except Exception as individual_error:
                    print(f"Failed to process {movie.title}: {individual_error}")

    print(f"Completed! Processed: {processed_count}, Skipped: {movies_with_embeddings}, Total: {total_movies}")
