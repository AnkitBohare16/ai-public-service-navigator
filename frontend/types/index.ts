export interface SearchResult {
  chunk_id: string;
  document_version_id: string;
  content: string;
  section_title: string | null;
  page_number: number | null;
  similarity: number;
}

export interface Citation {
  chunk_id: string;
  document_version_id: string;
  organization: string;
  source_title: string;
  url: string;
  is_official: boolean;
  document_version: number;
  retrieved_at: string;
  freshness_status: string;
  age_days: number | null;
  section_title: string | null;
  page_number: number | null;
  similarity: number;
}

export interface Reliability {
  status: string;
  score: number;
  reason: string;
}

export interface ChatResponse {
  query: string;
  answer: string;
  evidence: SearchResult[];
  citations: Citation[];
  reliability: Reliability;
}