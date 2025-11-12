from pathlib import Path

from django.conf import settings
from django.test.runner import DiscoverRunner


class RootDiscoverRunner(DiscoverRunner):
    """Extends Django discovery to include top-level ``tests`` package."""

    def build_suite(self, test_labels=None, extra_tests=None, **kwargs):
        suite = super().build_suite(test_labels, extra_tests, **kwargs)
        if not test_labels:
            extra_dir = (Path(settings.BASE_DIR).parent / "tests").resolve()
            if extra_dir.exists():
                suite.addTests(
                    self.test_loader.discover(
                        start_dir=str(extra_dir),
                        pattern=self.pattern,
                        top_level_dir=str(extra_dir.parent),
                    )
                )
        return suite
