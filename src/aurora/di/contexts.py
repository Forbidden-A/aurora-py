"""Linkd DI contexts."""

from __future__ import annotations

import linkd


class Contexts:
    MESSAGE = linkd.global_context_registry.register("aurora.contexts.message")
