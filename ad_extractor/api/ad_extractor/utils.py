from pathlib import Path
from typing import Dict, Optional

from api.ad_extractor.ad_extractors import ADExtractorFactory, OpenAIADExtractor
from api.ad_extractor.document_extractors import PDFExtractorFactory
from api.schema import ADDocument


async def get_output_directory(base_dir: Path) -> Path:
    """
        Get directory where to save processed AD documents.
    """
    output_directory = base_dir / "output"
    output_directory.mkdir(exist_ok=True)
    return output_directory


async def save_ad_document(
        ad_document: ADDocument, 
        output_directory: Path
) -> Path:
    """
        Save the ADDocument as a JSON file in the specified output directory.
    """
    output_path = output_directory / f"{ad_document.ad_id}_parsed.json"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(ad_document.model_dump_json(indent=4))
    return output_path


async def process_and_save_ad(
    text: str,
    ad_extractor: ADExtractorFactory,
    output_directory: Path
) -> Optional[ADDocument]:
    """
        Process one extracted text to create an ADDocument and save it.
    """
    ad_document = await ad_extractor.extract_ad(text)
    
    if not ad_document:
        return None
    
    await save_ad_document(ad_document, output_directory)
    return ad_document


async def bulk_process_ads(
    extracted_texts: Dict[str, str],
    ad_extractor: ADExtractorFactory,
    output_directory: Path
) -> Optional[Dict[str, ADDocument]]:
    """
        Process and save multiple AD texts to ADDocument instances.
    """
    ad_documents = {}
    
    for text in extracted_texts.values():
        ad_document = await process_and_save_ad(text, ad_extractor, output_directory)
        if ad_document:
            ad_documents[ad_document.ad_id] = ad_document
    
    if not ad_documents:
        return None

    return ad_documents
