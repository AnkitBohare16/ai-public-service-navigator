"use client";

import { useState } from "react";

import { askChat, checkBackendHealth } from "../lib/api";
import type { ChatResponse } from "../types";

export default function Home() {
  const [backendStatus, setBackendStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const [query, setQuery] = useState("");
  const [chatResponse, setChatResponse] = useState<ChatResponse | null>(null);
  const [chatLoading, setChatLoading] = useState(false);
  const [chatError, setChatError] = useState<string | null>(null);

  async function handleHealthCheck() {
    setLoading(true);

    try {
      const result = await checkBackendHealth();
      setBackendStatus(result.status);
    } catch {
      setBackendStatus("error");
    } finally {
      setLoading(false);
    }
  }

  async function handleChat() {
    if (!query.trim()) {
      return;
    }

    setChatLoading(true);
    setChatError(null);

    try {
      const result = await askChat(query);
      setChatResponse(result);
    } catch {
      setChatError("Unable to get an answer. Please try again.");
      setChatResponse(null);
    } finally {
      setChatLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-gray-100 px-6 py-12 text-gray-900">
      <div className="mx-auto max-w-4xl">
        <div className="rounded-2xl bg-white p-8 shadow-md">
          <h1 className="text-3xl font-bold text-gray-900">
            AI Public-Service Information Navigator
          </h1>

          <p className="mt-3 text-gray-600">
            Find public-service information from authoritative sources.
          </p>

          {/* Chat Section */}
          <div className="mt-8 rounded-xl border border-gray-300 bg-gray-50 p-6">
            <h2 className="text-lg font-semibold text-gray-900">
              Ask a question
            </h2>

            <p className="mt-2 text-sm text-gray-600">
              For example: “What documents do I need to update my address?”
            </p>

            <div className="mt-5 flex gap-3">
              <input
                type="text"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    handleChat();
                  }
                }}
                placeholder="Ask about a public service..."
                className="flex-1 rounded-lg border border-gray-400 bg-white px-4 py-3 text-gray-900 placeholder-gray-500 outline-none transition focus:border-gray-700 focus:ring-2 focus:ring-gray-200"
              />

              <button
                onClick={handleChat}
                disabled={chatLoading || !query.trim()}
                className="rounded-lg bg-gray-900 px-5 py-3 font-medium text-white transition hover:bg-gray-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {chatLoading ? "Searching..." : "Search"}
              </button>
            </div>

            {chatError && (
              <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                {chatError}
              </div>
            )}
          </div>

          {/* Answer Section */}
          {chatResponse && (
            <div className="mt-6 rounded-xl border border-gray-300 bg-white p-6 shadow-sm">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">
                  Answer
                </h2>

                <span className="rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-700">
                  AI-generated from retrieved sources
                </span>
              </div>

              <div className="mt-5 rounded-lg bg-gray-50 p-5">
                <p className="whitespace-pre-wrap leading-7 text-gray-800">
                  {chatResponse.answer}
                </p>
              </div>

              {/* Sources Section */}
              <div className="mt-6">
                <h3 className="text-base font-semibold text-gray-900">
                  Sources
                </h3>

                <div className="mt-3 space-y-3">
                  {chatResponse.citations.map((citation) => (
                    <div
                      key={citation.chunk_id}
                      className="rounded-lg border border-gray-200 bg-gray-50 p-4"
                    >
                      <div className="flex flex-wrap items-center gap-2">
                        <h4 className="font-medium text-gray-900">
                          {citation.source_title}
                        </h4>

                        {citation.is_official && (
                          <span className="rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-800">
                            Official source
                          </span>
                        )}

                        <span
                          className={`rounded-full px-2 py-1 text-xs font-medium ${
                            citation.freshness_status === "fresh"
                              ? "bg-green-100 text-green-800"
                              : citation.freshness_status === "aging"
                                ? "bg-yellow-100 text-yellow-800"
                                : "bg-red-100 text-red-800"
                          }`}
                        >
                          {citation.freshness_status}
                        </span>
                      </div>

                      <p className="mt-2 text-sm text-gray-600">
                        Organization: {citation.organization}
                      </p>

                      <p className="mt-1 text-sm text-gray-600">
                        Document version: {citation.document_version}
                      </p>

                      {citation.section_title && (
                        <p className="mt-1 text-sm text-gray-600">
                          Section: {citation.section_title}
                        </p>
                      )}

                      {citation.page_number !== null && (
                        <p className="mt-1 text-sm text-gray-600">
                          Page: {citation.page_number}
                        </p>
                      )}

                      {citation.age_days !== null && (
                        <p className="mt-1 text-sm text-gray-600">
                          Retrieved approximately{" "}
                          {citation.age_days.toFixed(1)} days ago
                        </p>
                      )}

                      <a
                        href={citation.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="mt-3 inline-block text-sm font-medium text-blue-700 hover:underline"
                      >
                        View source
                      </a>
                    </div>
                  ))}
                </div>
              </div>

              {/* Reliability Section */}
              <div className="mt-6 rounded-lg border border-gray-200 bg-gray-50 p-5">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-gray-900">
                    Reliability
                  </h3>

                  <span
                    className={`rounded-full px-3 py-1 text-sm font-semibold ${
                      chatResponse.reliability.status === "high"
                        ? "bg-green-100 text-green-800"
                        : chatResponse.reliability.status === "medium"
                          ? "bg-yellow-100 text-yellow-800"
                          : "bg-red-100 text-red-800"
                    }`}
                  >
                    {chatResponse.reliability.status}
                  </span>
                </div>

                <p className="mt-3 text-2xl font-bold text-gray-900">
                  {(chatResponse.reliability.score * 100).toFixed(1)}%
                </p>

                <p className="mt-2 text-sm leading-6 text-gray-600">
                  {chatResponse.reliability.reason}
                </p>
              </div>
            </div>
          )}

          {/* Backend Status */}
          <div className="mt-6 rounded-xl border border-gray-300 bg-gray-50 p-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="font-semibold text-gray-900">
                  Backend Status
                </h2>

                <p className="mt-1 text-sm text-gray-600">
                  Connection to the FastAPI backend.
                </p>
              </div>

              <button
                onClick={handleHealthCheck}
                disabled={loading}
                className="rounded-lg border border-gray-400 bg-white px-4 py-2 text-sm font-medium text-gray-800 transition hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading ? "Checking..." : "Check"}
              </button>
            </div>

            {backendStatus && (
              <div
                className={`mt-4 rounded-lg border p-4 text-sm ${
                  backendStatus === "ok"
                    ? "border-green-200 bg-green-50 text-green-800"
                    : "border-red-200 bg-red-50 text-red-800"
                }`}
              >
                <p>
                  Backend:{" "}
                  <span className="font-semibold">
                    {backendStatus === "ok"
                      ? "Connected"
                      : "Unavailable"}
                  </span>
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}