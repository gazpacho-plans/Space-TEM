import json
import logging
import logging.handlers
import os
import functools
from pathlib import Path
from typing import Any, Dict, Optional

import discord


class JsonFormatter(logging.Formatter):
	def format(self, record: logging.LogRecord) -> str:
		payload: Dict[str, Any] = {
			"ts": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S%z"),
			"level": record.levelname,
			"logger": record.name,
			"msg": record.getMessage(),
		}
		if record.exc_info:
			payload["exc_info"] = self.formatException(record.exc_info)
		ctx = getattr(record, "ctx", None)
		if isinstance(ctx, dict):
			# Merge a shallow context map into the payload
			for key, value in ctx.items():
				if value is not None:
					payload[key] = value
		return json.dumps(payload, ensure_ascii=False)


def setup_logging() -> None:
	# Levels
	console_level = os.getenv("LOG_LEVEL_CONSOLE", "INFO").upper()
	file_level = os.getenv("LOG_LEVEL_FILE", "DEBUG").upper()
	log_file = os.getenv("LOG_FILE", "utils/logs/debug.log")
	console_json = os.getenv("LOG_JSON_CONSOLE", "0") in {"1", "true", "True"}

	# Handlers
	console_handler = logging.StreamHandler()
	if console_json:
		console_handler.setFormatter(JsonFormatter())
	else:
		console_handler.setFormatter(logging.Formatter("%(levelname)s: %(name)s: %(message)s"))
	console_handler.setLevel(console_level)

	# Ensure log directory exists
	Path(log_file).parent.mkdir(parents=True, exist_ok=True)
	file_handler = logging.handlers.RotatingFileHandler(
		log_file, maxBytes=10_000_000, backupCount=5, encoding="utf-8"
	)
	file_handler.setFormatter(JsonFormatter())
	file_handler.setLevel(file_level)

	root = logging.getLogger()
	root.handlers.clear()
	root.addHandler(console_handler)
	root.addHandler(file_handler)
	# Allow all records through; handlers apply their own level filtering
	root.setLevel("DEBUG")

	# Quiet noisy third-party libs on console by default
	logging.getLogger("discord").setLevel(os.getenv("LOG_LEVEL_DISCORD", "WARNING").upper())
	logging.getLogger("aiohttp").setLevel(os.getenv("LOG_LEVEL_AIOHTTP", "WARNING").upper())


def get_logger(name: Optional[str] = None) -> logging.Logger:
	return logging.getLogger(name or "space_tem")


def ctx_from_interaction(interaction: discord.Interaction) -> Dict[str, Any]:
	user = getattr(interaction, "user", None)
	guild = getattr(interaction, "guild", None)
	channel = getattr(interaction, "channel", None)
	command = getattr(interaction, "command", None)
	return {
		"interaction_id": getattr(interaction, "id", None),
		"user_id": getattr(user, "id", None),
		"guild_id": getattr(guild, "id", None),
		"channel_id": getattr(channel, "id", None),
		"command": getattr(command, "qualified_name", None),
	}


def with_command_logging(fn):
	"""Decorator for app command callbacks to log start/end and exceptions."""
	@functools.wraps(fn)
	async def _inner(self, interaction: discord.Interaction, *args, **kwargs):
		logger = get_logger("space_tem.cmd")
		ctx = ctx_from_interaction(interaction)
		logger.info("command_start", extra={"ctx": ctx})
		try:
			return await fn(self, interaction, *args, **kwargs)
		except Exception:
			logger.exception("command_error", extra={"ctx": ctx})
			raise
		finally:
			logger.info("command_end", extra={"ctx": ctx})
	return _inner


