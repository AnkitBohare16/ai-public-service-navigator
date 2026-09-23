"use client";

import { useState } from "react";

import { checkBackendHealth } from "../lib/api";

export default function Home() {
  const [backendStatus, setBackendStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

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

  return (
    <main className="min-h-screen bg-gray-50 px-6 py-12">
      <div className="mx-auto max-w-4xl">
        <div className="rounded-2xl bg-white p-8 shadow-sm">
          <h1 className="text-3xl font-bold text-gray-900">
            AI Public-Service Information Navigator
          </h1>

          <p className="mt-3 text-gray-600">
            Find public-service information from authoritative sources.
          </p>

          <div className="mt-8 rounded-xl border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900">
              Ask a question
            </h2>

            <p className="mt-2 text-sm text-gray-500">
              For example: “What documents do I need to update my address?”
            </p>

            <div className="mt-5 flex gap-3">
              <input
                type="text"
                placeholder="Ask about a public service..."
                className="flex-1 rounded-lg border border-gray-300 px-4 py-3 outline-none focus:border-gray-500"
              />

              <button className="rounded-lg bg-black px-5 py-3 font-medium text-white">
                Search
              </button>
            </div>
          </div>

          <div className="mt-6 rounded-xl border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="font-semibold text-gray-900">
                  Backend Status
                </h2>

                <p className="mt-1 text-sm text-gray-500">
                  Connection to the FastAPI backend.
                </p>
              </div>

              <button
                onClick={handleHealthCheck}
                disabled={loading}
                className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium hover:bg-gray-50 disabled:opacity-50"
              >
                {loading ? "Checking..." : "Check"}
              </button>
            </div>

            {backendStatus && (
              <div className="mt-4 rounded-lg bg-gray-50 p-4 text-sm">
                Backend response:{" "}
                <span className="font-semibold">{backendStatus}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}