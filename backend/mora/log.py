# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import logging

from . import config


def init():
    logging.getLogger("urllib3").setLevel(logging.INFO)

    log_level = config.get_settings().os2mo_log_level
    logger = logging.getLogger()

    logger.setLevel(log_level)
    logger.setLevel(min(logger.getEffectiveLevel(), logging.INFO))

    log_format = logging.Formatter(
        "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
    )

    stdout_log_handler = logging.StreamHandler()
    stdout_log_handler.setFormatter(log_format)
    stdout_log_handler.setLevel(log_level)  # this can be higher
    logger.addHandler(stdout_log_handler)
