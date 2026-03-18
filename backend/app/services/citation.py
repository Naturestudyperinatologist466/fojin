from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import TextNotFoundError
from app.models.text import BuddhistText
from app.schemas.citation import CitationResponse


async def generate_citation(
    session: AsyncSession, text_id: int, style: str = "chicago"
) -> CitationResponse:
    result = await session.execute(select(BuddhistText).where(BuddhistText.id == text_id))
    text = result.scalar_one_or_none()
    if text is None:
        raise TextNotFoundError(text_id=text_id)

    title = text.title_zh
    translator = text.translator or "佚名"
    dynasty = text.dynasty or ""
    cbeta_id = text.cbeta_id

    if style == "chicago":
        citation = (
            f"《{title}》，{dynasty}{translator}译。"
            f"CBETA 电子佛典集成，编号 {cbeta_id}。"
            f"佛津 FoJin 数字平台。"
        )
    elif style == "apa":
        citation = (
            f"{translator} (译). ({dynasty}). "
            f"《{title}》 ({cbeta_id}). "
            f"CBETA 电子佛典集成. 佛津 FoJin."
        )
    elif style == "mla":
        citation = (
            f"{translator}, 译. 《{title}》. "
            f"CBETA 电子佛典集成, {cbeta_id}. "
            f"佛津 FoJin."
        )
    elif style == "harvard":
        citation = (
            f"{translator} (译) ({dynasty}) "
            f"《{title}》. {cbeta_id}. "
            f"CBETA 电子佛典集成. 佛津 FoJin."
        )
    else:
        citation = f"《{title}》，{dynasty}{translator}译，CBETA {cbeta_id}。"

    return CitationResponse(
        text_id=text_id,
        title=title,
        style=style,
        citation=citation,
    )
