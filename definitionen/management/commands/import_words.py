import json
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.dateparse import parse_datetime

from definitionen.models import Definition, Word

DEFAULT_FILE = Path(settings.BASE_DIR) / "fixtures" / "new_words.json"


class Command(BaseCommand):
    help = (
        "Imports AI-written words and definitions from a JSON file (flagged ai_generated). "
        "Entries whose word already has a definition with the same content are skipped, "
        "so the command can be run repeatedly (locally and on the live site)."
    )

    def add_arguments(self, parser):
        parser.add_argument("file", nargs="?", default=str(DEFAULT_FILE))
        parser.add_argument("--author", default="anonym", help="username of the author (default: anonym)")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        path = Path(options["file"])
        if not path.exists():
            raise CommandError(f"File not found: {path}")

        try:
            author = User.objects.get(username=options["author"])
        except User.DoesNotExist:
            raise CommandError(f"User '{options['author']}' does not exist")

        entries = json.loads(path.read_text(encoding="utf-8"))
        created_words = created_defs = skipped = 0

        with transaction.atomic():
            for entry in entries:
                title = entry["title"].strip()
                key = title.lower()

                word = Word.objects.filter(word=key).first()
                if word is None:
                    word = Word.objects.create(word=key, display_title=entry.get("display_title", title))
                    created_words += 1

                if Definition.objects.filter(word=word, content=entry["content"]).exists():
                    skipped += 1
                    continue

                definition = Definition.objects.create(
                    title=title,
                    content=entry["content"],
                    example=entry["example"],
                    author=author,
                    word=word,
                    ai_generated=True,
                )
                # date_posted uses auto_now_add, so an explicit date has to be set afterwards
                if entry.get("date_posted"):
                    Definition.objects.filter(pk=definition.pk).update(date_posted=parse_datetime(entry["date_posted"]))
                created_defs += 1

            if options["dry_run"]:
                transaction.set_rollback(True)

        prefix = "[dry run] " if options["dry_run"] else ""
        self.stdout.write(self.style.SUCCESS(
            f"{prefix}{created_words} new words, {created_defs} new definitions, {skipped} skipped"
        ))
