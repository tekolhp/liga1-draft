#!/usr/bin/env python3
"""Download the provided URLs and compress them into a web-friendly format."""

from __future__ import annotations

import argparse
import logging
from io import BytesIO
from pathlib import Path
from typing import Iterable, Sequence, Tuple

import requests
from PIL import Image

IMAGE_SOURCES: Sequence[Tuple[str, str]] = (
    ("MAGDLENA", "https://i.postimg.cc/sg7D42jC/MAGDLENA.png"),
    ("ABRAAO", "https://i.postimg.cc/k5zTwVVf/ABRAAO.png"),
    ("ALEX", "https://i.postimg.cc/jjmMvWwT/ALEX.png"),
    ("ALEX_B", "https://i.postimg.cc/gJhN7YRB/ALEX_B.png"),
    ("ANDREJR", "https://i.postimg.cc/q7zm8c7g/ANDREJR.png"),
    ("ARANHA", "https://i.postimg.cc/DZGBN2LV/ARANHA.png"),
    ("BAHIA", "https://i.postimg.cc/Xq0QSTkv/BAHIA.png"),
    ("BARBA", "https://i.postimg.cc/MH8d2hmV/BARBA.png"),
    ("BILEU", "https://i.postimg.cc/tJH2QLNY/BILEU.png"),
    ("BONINI", "https://i.postimg.cc/BbWVgmYr/BONINI.png"),
    ("BRUNO", "https://i.postimg.cc/8PcZvQzS/BRUNO.png"),
    ("CARIOCA", "https://i.postimg.cc/fy4rK826/CARIOCA.png"),
    ("CARTOLA", "https://i.postimg.cc/wMKGVw4z/CARTOLA.png"),
    ("NATAN", "https://i.postimg.cc/0yr0zpZS/NATAN.png"),
    ("CL", "https://i.postimg.cc/wMKGVwf4/CL.png"),
    ("CORUJA", "https://i.postimg.cc/tJhmmFw8/CORUJA.png"),
    ("CRISTIANO", "https://i.postimg.cc/65kyj0WB/CRISTIANO.png"),
    ("DG", "https://i.postimg.cc/fyxggY1N/DG.png"),
    ("DIEGO", "https://i.postimg.cc/C5j66b9q/DIEGO.png"),
    ("DIEGO_H", "https://i.postimg.cc/44tMdTy5/DIEGO_H.png"),
    ("DVD", "https://i.postimg.cc/v89jBdTv/DVD.png"),
    ("EVERTON", "https://i.postimg.cc/h4xwjqvs/EVERTON.png"),
    ("FABIANO", "https://i.postimg.cc/zD0d3X56/FABIANO.png"),
    ("FABINHO", "https://i.postimg.cc/9F0L95Q5/FABINHO.png"),
    ("FERNANDO", "https://i.postimg.cc/PrJSDs5h/FERNANDO.png"),
    ("GABRIEL_C", "https://i.postimg.cc/Kvj0TS8m/GABRIEL_C.png"),
    ("GABRIEL_N", "https://i.postimg.cc/FszTS5Hs/GABRIEL_N.png"),
    ("GABRIEL", "https://i.postimg.cc/kXGTS3g4/GABRIEL.png"),
    ("GAGA", "https://i.postimg.cc/Kvj0TS84/GAGA.png"),
    ("GUTE", "https://i.postimg.cc/fTy8dnRV/GUTE.png"),
    ("HELCINHO", "https://i.postimg.cc/6pyp2hS3/HELCINHO.png"),
    ("IHURI", "https://i.postimg.cc/5262YmG2/IHURI.png"),
    ("ITALO", "https://i.postimg.cc/t4Y4ZzfC/ITALO.png"),
    ("JACKSON", "https://i.postimg.cc/CLvKx2vR/JACKSON.png"),
    ("JEFAO", "https://i.postimg.cc/RZNZ6T8J/JEFAO.png"),
    ("JOAN", "https://i.postimg.cc/bwWNQtcR/JOAN.png"),
    ("JOAO", "https://i.postimg.cc/GmVhkywf/JOAO.png"),
    ("JONATHAN", "https://i.postimg.cc/K8wvnMSC/JONATHAN.png"),
    ("JOTTA", "https://i.postimg.cc/0yF2pwRX/JOTTA.png"),
    ("JUNINHO", "https://i.postimg.cc/T3FYrDvM/JUNINHO.png"),
    ("JUNIOR", "https://i.postimg.cc/d0CQnVJt/JUNIOR.png"),
    ("KLEVSON", "https://i.postimg.cc/XYd7kvjN/KLEVSON.png"),
    ("LEOZINHO", "https://i.postimg.cc/vZfHtmYG/LEOZINHO.png"),
    ("2S", "https://i.postimg.cc/jSbC9fk4/2S.png"),
    ("MAGRAO", "https://i.postimg.cc/MpVKmG6K/MAGRAO.png"),
    ("MALHEIRO", "https://i.postimg.cc/R0mCszhC/MALHEIRO.png"),
    ("MARCELO", "https://i.postimg.cc/wBzxfdM1/MARCELO.png"),
    ("MARCIO", "https://i.postimg.cc/k5CM1dGv/MARCIO.png"),
    ("MARLLON", "https://i.postimg.cc/9F6r8pmX/MARLLON.png"),
    ("MATHEUS", "https://i.postimg.cc/GpR371tJ/MATHEUS.png"),
    ("MOREIRA", "https://i.postimg.cc/cJW19NCT/MOREIRA.png"),
    ("NELSON", "https://i.postimg.cc/dVZP8N96/NELSON.png"),
    ("NEVES", "https://i.postimg.cc/jdFYnYyW/NEVES.png"),
    ("OBINA", "https://i.postimg.cc/htQW9Z0b/OBINA.png"),
    ("OZIEL", "https://i.postimg.cc/fRSnxqv7/OZIEL.png"),
    ("PHILL", "https://i.postimg.cc/K83Snp5q/PHILL.png"),
    ("PQD", "https://i.postimg.cc/9F6r8pmF/PQD.png"),
    ("RAFAEL", "https://i.postimg.cc/bJTKz7zv/RAFAEL.png"),
    ("RANGEL", "https://i.postimg.cc/BbnRtm6Z/RANGEL.png"),
    ("RAPHAEL", "https://i.postimg.cc/vTZCD0B6/RAPHAEL.png"),
    ("RAPHAEL_D", "https://i.postimg.cc/YScc8NXP/RAPHAEL_D.png"),
    ("REGIO", "https://i.postimg.cc/sxHqW5QZ/REGIO.png"),
    ("RENATO", "https://i.postimg.cc/8P2DnVcX/RENATO.png"),
    ("RODRIGUES", "https://i.postimg.cc/8P2DnVc2/RODRIGUES.png"),
    ("RONALDO", "https://i.postimg.cc/fRYk69ys/RONALDO.png"),
    ("SAPAO", "https://i.postimg.cc/ZKGZDh0k/SAPAO.png"),
    ("SILLAS", "https://i.postimg.cc/WbBjfPzS/SILLAS.png"),
    ("TANA", "https://i.postimg.cc/2SnYsXBR/TANA.png"),
    ("TAPINHA", "https://i.postimg.cc/cLfWp584/TAPINHA.png"),
    ("TETEU", "https://i.postimg.cc/P51HgF85/TETEU.png"),
    ("TH", "https://i.postimg.cc/VkXwxHbs/TH.png"),
    ("THIAGUINHO", "https://i.postimg.cc/Mp1wCrjv/THIAGUINHO.png"),
    ("TRINDADE", "https://i.postimg.cc/vmMybLWv/TRINDADE.png"),
    ("BERNARDO", "https://i.postimg.cc/W3ZXy2g3/BERNARDO.png"),
    ("V_MARIN", "https://i.postimg.cc/mrR4BNQh/V_MARIN.png"),
    ("WENDEL", "https://i.postimg.cc/zf5N8Sn0/WENDEL.png"),
    ("YAGO", "https://i.postimg.cc/mrR4BNQM/YAGO.png"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download every named image and save a compressed version for the web.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("web-images"),
        help="Directory where the compressed images will be stored (created automatically).",
    )
    parser.add_argument(
        "--format",
        choices=("webp", "jpeg", "png"),
        default="webp",
        help="Target format for the compressed assets.",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=80,
        help="Compression quality for WebP/JPEG (ignored for PNG).",
    )
    parser.add_argument(
        "--max-width",
        type=int,
        default=1600,
        help="Downscale width when the source exceeds this value.",
    )
    parser.add_argument(
        "--max-height",
        type=int,
        default=1600,
        help="Downscale height when the source exceeds this value.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Redownload and recompress even when the target file already exists.",
    )
    return parser.parse_args()


def sanitize_name(raw: str) -> str:
    pieces = []
    for char in raw.lower():
        if char.isalnum():
            pieces.append(char)
        elif pieces and pieces[-1] != "-":
            pieces.append("-")
    sanitized = "".join(pieces).strip("-")
    return sanitized or "image"


def download_and_compress(
    target_dir: Path, fmt: str, quality: int, max_width: int, max_height: int, force: bool
) -> None:
    session = requests.Session()
    target_dir.mkdir(parents=True, exist_ok=True)

    for label, url in IMAGE_SOURCES:
        slug = sanitize_name(label)
        destination = target_dir / f"{slug}.{fmt}"
        if destination.exists() and not force:
            logging.info("Skipping %s (already exists at %s).", label, destination)
            continue

        logging.info("Downloading %s from %s", label, url)
        response = session.get(url, timeout=30)
        response.raise_for_status()

        with Image.open(BytesIO(response.content)) as img:
            if img.mode == "P":
                img = img.convert("RGBA")

            if max_width or max_height:
                target_size = (
                    max_width or img.width,
                    max_height or img.height,
                )
                img.thumbnail(target_size, Image.LANCZOS)

            save_kwargs = {}
            if fmt in {"jpeg", "webp"} and img.mode == "RGBA":
                alpha = img.split()[-1]
                background = Image.new("RGBA", img.size, (255, 255, 255, 0))
                background.paste(img, mask=alpha)
                img = background

            if fmt in {"jpeg", "webp"}:
                save_kwargs["quality"] = quality
                if fmt == "jpeg":
                    img = img.convert("RGB")

            if fmt == "webp":
                save_kwargs.setdefault("method", 6)

            img.save(destination, fmt.upper(), **save_kwargs)
            logging.info("Saved %s", destination)


def main() -> int:
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    download_and_compress(
        target_dir=args.output_dir,
        fmt=args.format,
        quality=args.quality,
        max_width=args.max_width,
        max_height=args.max_height,
        force=args.force,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

