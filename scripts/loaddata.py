"""
Django runscript to load movie data from CSV into cinematch models.

Usage: python manage.py runscript loaddata
"""

import csv
import os
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.db import transaction

from cinematch.models import Genre, Movie, Talent


def run():
    """Main function executed by django-extensions runscript."""
    csv_path = os.path.join(settings.BASE_DIR, "scripts", "cinematch", "imdb_movies.csv")

    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return

    print(f"Loading movie data from: {csv_path}")

    # Statistics counters
    stats = {
        "movies_created": 0,
        "movies_updated": 0,
        "genres_created": 0,
        "talents_created": 0,
        "rows_processed": 0,
        "rows_skipped": 0,
        "errors": [],
    }

    with open(csv_path, encoding="utf-8") as csvfile:
        # Detect delimiter and read CSV
        sample = csvfile.read(1024)
        csvfile.seek(0)
        sniffer = csv.Sniffer()
        delimiter = sniffer.sniff(sample).delimiter

        reader = csv.DictReader(csvfile, delimiter=delimiter)

        with transaction.atomic():
            for row_num, row in enumerate(reader, start=2):  # Start at 2 for header
                try:
                    process_movie_row(row, stats)
                    stats["rows_processed"] += 1

                    # Progress indicator
                    if stats["rows_processed"] % 50 == 0:
                        print(f"Processed {stats['rows_processed']} movies...")

                except Exception as e:
                    stats["rows_skipped"] += 1
                    stats["errors"].append(f"Row {row_num}: {str(e)}")
                    print(f"Skipping row {row_num}: {str(e)}")
                    continue

    # Print final statistics
    print_statistics(stats)


def process_movie_row(row, stats):
    """Process a single CSV row and create/update movie data."""

    # Extract and validate basic movie data
    title = row.get("names", "").strip()
    if not title:
        raise ValueError("Missing movie title")

    # Parse release date
    date_str = row.get("date_x", "").strip()
    if not date_str:
        raise ValueError("Missing release date")

    try:
        # Parse MM/dd/yyyy format
        release_date = datetime.strptime(date_str, "%m/%d/%Y").date()
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}")

    # Parse rating
    score_str = row.get("score", "").strip()
    if score_str:
        try:
            rating = Decimal(str(score_str))
            # Ensure rating is within reasonable bounds
            if rating < 0 or rating > 10:
                rating = None
        except (InvalidOperation, ValueError):
            rating = None
    else:
        rating = None

    # Other fields
    description = row.get("overview", "").strip() or None
    original_language = row.get("orig_lang", "").strip() or None

    # Create or get movie
    movie, created = Movie.objects.get_or_create(
        title=title,
        release_date=release_date,
        defaults={
            "description": description,
            "rating": rating or Decimal("0.0"),
            "original_language": original_language,
        },
    )

    if created:
        stats["movies_created"] += 1
    else:
        # Update existing movie with new data
        updated = False
        if description and not movie.description:
            movie.description = description
            updated = True
        if rating and movie.rating == Decimal("0.0"):
            movie.rating = rating
            updated = True
        if original_language and not movie.original_language:
            movie.original_language = original_language
            updated = True

        if updated:
            movie.save()
            stats["movies_updated"] += 1

    # Process genres
    genre_str = row.get("genre", "").strip()
    if genre_str:
        genre_names = [g.strip() for g in genre_str.split(",") if g.strip()]
        for genre_name in genre_names:
            genre, created = Genre.objects.get_or_create(name=genre_name)
            if created:
                stats["genres_created"] += 1
            movie.genre.add(genre)

    # Process crew/talents
    crew_str = row.get("crew", "").strip()
    if crew_str:
        # Parse crew field which contains actor names separated by commas
        # Format appears to be: "Actor Name, Character Name, Actor Name, Character Name, ..."
        crew_parts = [part.strip() for part in crew_str.split(",") if part.strip()]

        # Extract actor names using simple heuristics
        # This filters out character names and other non-actor entries
        actor_names = []
        for part in crew_parts:
            # Skip parts that look like character names (contain certain patterns)
            if not any(pattern in part.lower() for pattern in ["(voice)", "voice)", "(", "character"]):
                # Take names that look like person names (contain spaces or are short)
                if " " in part or len(part.split()) == 1:
                    actor_names.append(part)

        # Limit to first 10 actors to avoid too much noise
        for actor_name in actor_names[:10]:
            if len(actor_name) > 2:  # Basic validation
                talent, created = Talent.objects.get_or_create(name=actor_name)
                if created:
                    stats["talents_created"] += 1
                movie.talent.add(talent)


def print_statistics(stats):
    """Print final loading statistics."""
    print("\n" + "=" * 50)
    print("MOVIE DATA LOADING COMPLETE")
    print("=" * 50)
    print(f"Rows processed: {stats['rows_processed']}")
    print(f"Rows skipped: {stats['rows_skipped']}")
    print(f"Movies created: {stats['movies_created']}")
    print(f"Movies updated: {stats['movies_updated']}")
    print(f"Genres created: {stats['genres_created']}")
    print(f"Talents created: {stats['talents_created']}")

    if stats["errors"]:
        print(f"\nErrors encountered: {len(stats['errors'])}")
        print("First 5 errors:")
        for error in stats["errors"][:5]:
            print(f"  - {error}")

        if len(stats["errors"]) > 5:
            print(f"  ... and {len(stats['errors']) - 5} more errors")

    print("=" * 50)
