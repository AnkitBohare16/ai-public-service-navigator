# Evaluation

## Overview

The AI Public-Service Information Navigator includes an evaluation layer to verify that the retrieval and reliability pipeline behaves correctly for both supported and unsupported questions.

The evaluation focuses on two important behaviors:

1. Supported questions should retrieve relevant official evidence and achieve sufficient reliability.
2. Unsupported questions should not be treated as reliable, even when the user asks for specific procedures, fees, or requirements that are not present in the indexed source.

The evaluation does not call the LLM. It evaluates the retrieval, citation, and reliability layers deterministically.

## Evaluation Flow

```text
Evaluation Cases
       |
       v
RetrievalService
       |
       v
CitationService
       |
       v
ReliabilityService
       |
       v
Evaluation Result