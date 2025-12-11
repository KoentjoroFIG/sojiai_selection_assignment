import json
from pathlib import Path
from typing import Dict
from api.schema import ADDocument


async def load_parsed_ads(output_dir: Path) -> Dict[str, ADDocument]:
    ads = {}
    for json_file in output_dir.glob("*_parsed.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            ad = ADDocument.model_validate(data)
            ads[ad.ad_id] = ad
    return ads