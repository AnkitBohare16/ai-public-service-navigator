# AI Public-Service Information Navigator

An AI-powered system that helps users navigate public-service information using authoritative sources.

## Overview

The system retrieves information from official government/public-service sources and provides:

- Required documents
- Application procedures
- Fees
- Deadlines
- Eligibility requirements
- Source citations
- Source freshness information
- Warnings when authoritative information is insufficient or conflicting

## Architecture

The application consists of:

- Next.js frontend
- FastAPI backend
- PostgreSQL + pgvector
- Document ingestion pipeline
- Retrieval and reranking
- LLM-based answer generation
- Citation and source verification
- Freshness and reliability checks

## Project Structure

```text
backend/       Backend API and AI/RAG pipeline
frontend/      Web application
data/          Documents and processed data
docs/          Technical documentation
scripts/       Utility and evaluation scripts
.github/       CI/CD workflows