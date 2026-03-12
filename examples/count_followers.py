"""Minimal example of running profile counting followers."""

import logging
import os

from contriboo import ContribooClient, ContribooSettings

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    settings = ContribooSettings(github_token=os.getenv("GITHUB_TOKEN"))
    client = ContribooClient(settings=settings)

    username = "octocat"

    result = client.profile.count_followers(
        username=username,
    )
    print(result)
