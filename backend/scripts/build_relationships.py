#!/usr/bin/env python3
"""
Run Relationship Builder - selective mode
"""

import asyncio
import sys
import os
import argparse
import logging


BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../.."
    )
)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.database import get_db
from backend.graph.services.relationship_builder import RelationshipBuilder


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


async def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--type",
        choices=[
            "all",
            "shared_package",
            "vendor_similarity",
            "method_similarity",
            "financial_similarity"
        ],
        default="all"
    )

    args = parser.parse_args()


    async for db in get_db():

        builder = RelationshipBuilder(db)


        results = {}


        if args.type == "all":

            results = await builder.build_all_relationships()


        elif args.type == "shared_package":

            results["shared_package"] = (
                await builder._build_shared_package()
            )


        elif args.type == "vendor_similarity":

            results["vendor_similarity"] = (
                await builder._build_vendor_similarity()
            )


        elif args.type == "method_similarity":

            results["method_similarity"] = (
                await builder._build_method_similarity()
            )


        elif args.type == "financial_similarity":

            results["financial_similarity"] = (
                await builder._build_financial_similarity()
            )


        logger.info("\n📊 RESULTS")

        for key,value in results.items():
            logger.info(
                f"  {key}: {value}"
            )


if __name__ == "__main__":
    asyncio.run(main())