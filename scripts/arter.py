from cinematch.models import Movie  # noqa: INP001
from core.utils import openai


def run():
    x = openai.get_embedding("Hello, world!")
    print(len(x))  # noqa: T201

    batch_data = ["Hello, world!", "Goodbye, world!"]
    batch_x = openai.get_embeddings_batch(batch_data)
    print(len(batch_x))  # noqa: T201
    print(len(batch_x[0]))  # noqa: T201
    print(len(batch_x[1]))  # noqa: T201

    # Get movies without embeddings
    movies_without_embeddings = Movie.objects.filter(embedding__isnull=True).order_by(
        "-id"
    )
    movies_with_embeddings = Movie.objects.filter(embedding__isnull=False).count()

    total_movies = len(movies_without_embeddings) + movies_with_embeddings
    processed_count = 0
    batch_size = 50

    print(  # noqa: T201
        f"Found {len(movies_without_embeddings)} movies without embeddings, {movies_with_embeddings} already have embeddings",  # noqa: E501
    )

    # Process movies in batches
    for i in range(0, len(movies_without_embeddings), batch_size):
        batch_movies = movies_without_embeddings[i : i + batch_size]

        # Prepare text descriptions for batch
        batch_texts = []
        for movie in batch_movies:
            movie_text = f"Movie: {movie.title}, Description: {movie.description}, Release Date: {movie.release_date}, Rating: {movie.rating}, Genres: {[genre.name for genre in movie.genre.all()]}, Talents: {[talent.name for talent in movie.talent.all()]}, Original Language: {movie.original_language}"  # noqa: E501
            batch_texts.append(movie_text)

        print(f"Processing batch {i // batch_size + 1}: {len(batch_movies)} movies")  # noqa: T201

        try:
            # Get embeddings for entire batch in single API call
            batch_embeddings = openai.get_embeddings_batch(batch_texts)

            # Assign embeddings to movies
            for movie, embedding in zip(batch_movies, batch_embeddings):  # noqa: B905
                movie.embedding = embedding

            # Bulk update database
            Movie.objects.bulk_update(batch_movies, ["embedding"])
            processed_count += len(batch_movies)

            print(f"Successfully processed batch of {len(batch_movies)} movies")  # noqa: T201

        except Exception as e:  # noqa: BLE001
            print(f"Batch processing failed: {e}")  # noqa: T201
            print("Falling back to individual processing for this batch...")  # noqa: T201

            # Fallback: process individually
            for movie in batch_movies:
                try:
                    movie_text = f"Movie: {movie.title}, Description: {movie.description}, Release Date: {movie.release_date}, Rating: {movie.rating}, Genres: {[genre.name for genre in movie.genre.all()]}, Talents: {[talent.name for talent in movie.talent.all()]}, Original Language: {movie.original_language}"  # noqa: E501
                    movie.embedding = openai.get_embedding(movie_text)
                    movie.save()
                    processed_count += 1
                    print(f"Individual processing: {movie.title}")  # noqa: T201
                except Exception as individual_error:  # noqa: BLE001
                    print(f"Failed to process {movie.title}: {individual_error}")  # noqa: T201

    print(  # noqa: T201
        f"Completed! Processed: {processed_count}, Skipped: {movies_with_embeddings}, Total: {total_movies}"  # noqa: E501
    )
