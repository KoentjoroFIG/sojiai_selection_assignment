from fastapi import APIRouter
from pathlib import Path

from api.ad_extractor.schema import ADExtractionResponse
from api.ad_extractor.ad_extractors import ADExtractorFactory, OpenAIADExtractor
from api.ad_extractor.document_extractors import PDFExtractorFactory
from api.ad_extractor.utils import (
    get_output_directory,
    process_and_save_ad,
    bulk_process_ads
)
from config.config import settings

router = APIRouter()


@router.post(
        "/extraction_test",
        description="Run extraction test based on assignment specifications",
        tags=["Assignment"]
    )
async def extraction_test() -> ADExtractionResponse:
    pdf_extractor = PDFExtractorFactory()
    ad_extractor = ADExtractorFactory(
        extractor_strategy=OpenAIADExtractor(api_key=settings.LLM_API_KEY.get_secret_value(), base_url=settings.BASE_URL)
    )

    base_dir = Path(__file__).parent.parent.parent.parent
    pdf_directory = base_dir / "ad_docs"
    output_directory = get_output_directory(base_dir)
    
    extracted_texts = pdf_extractor.bulk_extract(pdf_directory)
    ad_documents = bulk_process_ads(extracted_texts, ad_extractor, output_directory)
    
    if not ad_documents:
        return ADExtractionResponse(status="failure")

    extracted_ads = []
    for ad_doc in ad_documents.values():
        extracted_ads.append(ad_doc)

    return ADExtractionResponse(
        status="success",
        extracted_ads=extracted_ads
    )


@router.post(
        "/path/{pdf_path}",
        description="Extract ADs from single pdf path"
    )
async def extract_ad_from_path(pdf_path: str) -> ADExtractionResponse:
    pdf_extractor = PDFExtractorFactory()
    ad_extractor = ADExtractorFactory(
        extractor_strategy=OpenAIADExtractor(api_key=settings.LLM_API_KEY.get_secret_value(), base_url=settings.BASE_URL)
    )

    base_dir = Path(__file__).parent.parent.parent.parent
    output_directory = get_output_directory(base_dir)
    
    extracted_text = pdf_extractor.extract_text(pdf_path)
    filename = Path(pdf_path).stem
    ad_document = process_and_save_ad(extracted_text, filename, ad_extractor, output_directory)

    if not ad_document:
        return ADExtractionResponse(status="failure")
    
    return ADExtractionResponse(
        status="success",
        extracted_ads=[ad_document]
    )

@router.post(
    "/directory/{pdf_directory}",
    description="Extract ADs from all PDF files in a specified directory"
)
async def extract_ads_from_directory(pdf_directory: str) -> ADExtractionResponse:
    pdf_extractor = PDFExtractorFactory()
    ad_extractor = ADExtractorFactory(
        extractor_strategy=OpenAIADExtractor(api_key=settings.LLM_API_KEY.get_secret_value(), base_url=settings.BASE_URL)
    )

    base_dir = Path(__file__).parent.parent.parent.parent
    output_directory = get_output_directory(base_dir)
    
    extracted_texts = pdf_extractor.bulk_extract(pdf_directory)
    ad_documents = bulk_process_ads(extracted_texts, ad_extractor, output_directory)
    
    if not ad_documents:
        return ADExtractionResponse(status="failure")
    
    extracted_ads = []
    for ad_doc in ad_documents.values():
        extracted_ads.append(ad_doc)
    
    return ADExtractionResponse(
        status="success",
        extracted_ads=extracted_ads
    )


@router.get(
        "/read_all",
        description="Read all existing extracted AD JSON files"
    )
async def list_all_extracted_ads() -> ADExtractionResponse:
    base_dir = Path(__file__).parent.parent.parent.parent
    output_directory = get_output_directory(base_dir)
    
    extracted_ads = []
    for json_file in output_directory.glob("*_parsed.json"):
        import json
        with open(json_file, "r", encoding="utf-8") as f:
            ad_data = json.load(f)
            extracted_ads.append(ad_data)

    if extracted_ads == []:
        return ADExtractionResponse(status="No files found")
        
    
    return ADExtractionResponse(
        status="success",
        extracted_ads=extracted_ads
    )