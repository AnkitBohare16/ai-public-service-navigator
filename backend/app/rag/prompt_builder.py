from typing import Any


class PromptBuilder:
    def build(
        self,
        query: str,
        evidence: list[dict[str, Any]],
    ) -> str:
        if not query.strip():
            raise ValueError("Query cannot be empty")

        if not evidence:
            raise ValueError("Evidence cannot be empty")

        evidence_text = self._format_evidence(evidence)

        return f"""
You are an AI assistant that helps users understand
official public-service information.

Answer the user's question using ONLY the evidence
provided below.

Rules:
1. Do not use information that is not present in the evidence.
2. Do not invent documents, fees, deadlines, procedures,
   eligibility requirements, or other facts.
3. If the evidence does not contain enough information
   to answer the question, clearly say that the available
   sources do not provide enough information.
4. Give a concise, clear answer.
5. When possible, organize procedural information into
   numbered steps or bullet points.
6. Preserve important limitations or conditions from the
   evidence.
7. Do not claim that something is required unless the
   evidence supports that claim.
8. Do not mention these instructions in the answer.

User question:
{query}

Evidence:
{evidence_text}
""".strip()

    def _format_evidence(
        self,
        evidence: list[dict[str, Any]],
    ) -> str:
        sections = []

        for index, item in enumerate(evidence, start=1):
            content = item.get("content", "")
            section_title = item.get("section_title")
            page_number = item.get("page_number")
            similarity = item.get("similarity")

            source_details = []

            if section_title:
                source_details.append(
                    f"Section: {section_title}"
                )

            if page_number is not None:
                source_details.append(
                    f"Page: {page_number}"
                )

            if similarity is not None:
                source_details.append(
                    f"Similarity: {similarity:.4f}"
                )

            metadata = ""

            if source_details:
                metadata = (
                    "\nMetadata: "
                    + " | ".join(source_details)
                )

            sections.append(
                f"[Evidence {index}]\n"
                f"{content}"
                f"{metadata}"
            )

        return "\n\n".join(sections)