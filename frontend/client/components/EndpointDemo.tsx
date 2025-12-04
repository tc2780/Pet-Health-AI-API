import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ResponseDisplay } from "@/components/ResponseDisplay";
import { Loader2, Code2, ChevronDown, ChevronUp } from "lucide-react";

interface EndpointDemoProps {
  title: string;
  description: string;
  endpoint: string;
  method?: "GET" | "POST" | "PUT" | "DELETE";
}

export function EndpointDemo({
  title,
  description,
  endpoint,
  method = "GET",
}: EndpointDemoProps) {
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<string>("");
  const [error, setError] = useState<string>("");
  const [success, setSuccess] = useState(false);
  const [requestBody, setRequestBody] = useState<string>("");
  const [showBody, setShowBody] = useState(false);

  const handleBodyKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Tab") {
      e.preventDefault();
      const textarea = e.currentTarget;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const newValue =
        requestBody.substring(0, start) + "  " + requestBody.substring(end);
      setRequestBody(newValue);

      setTimeout(() => {
        textarea.selectionStart = textarea.selectionEnd = start + 2;
      }, 0);
    }
  };

  const callEndpoint = async () => {
    setLoading(true);
    setError("");
    setResponse("");
    setSuccess(false);

    try {
      const fetchOptions: RequestInit = {
        method: method,
        headers: {
          "Content-Type": "application/json",
        },
      };

      if (requestBody.trim()) {
        try {
          const parsedBody = JSON.parse(requestBody);
          fetchOptions.body = JSON.stringify(parsedBody);
        } catch (parseErr) {
          throw new Error(
            "Invalid JSON in request body: " +
              (parseErr instanceof Error ? parseErr.message : "Unknown error")
          );
        }
      }

      const res = await fetch(endpoint, fetchOptions);

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }

      const data = await res.json();
      setResponse(JSON.stringify(data, null, 2));
      setSuccess(true);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Unknown error occurred";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="flex flex-col h-full hover:shadow-lg transition-shadow">
      <CardHeader>
        <CardTitle className="text-lg">{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
        <div className="mt-3 flex items-center gap-2">
          <span className="inline-block bg-blue-100 text-blue-800 text-xs font-semibold px-2 py-1 rounded">
            {method}
          </span>
          <code className="text-xs bg-slate-100 text-slate-700 px-2 py-1 rounded flex-1 overflow-auto">
            {endpoint}
          </code>
        </div>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col gap-4">
        <div>
          <button
            onClick={() => setShowBody(!showBody)}
            className="flex items-center gap-2 text-sm font-medium text-slate-700 hover:text-slate-900 mb-2 w-full"
          >
            {showBody ? (
              <ChevronUp className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
            Request Body (JSON)
            {requestBody.trim() && (
              <span className="ml-auto text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
                Body added
              </span>
            )}
          </button>
          {showBody && (
            <textarea
              value={requestBody}
              onChange={(e) => setRequestBody(e.target.value)}
              onKeyDown={handleBodyKeyDown}
              placeholder='{"key": "value"}'
              className="w-full h-32 p-3 text-xs font-mono bg-slate-50 border border-slate-200 rounded text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              spellCheck="false"
            />
          )}
        </div>

        <Button
          onClick={callEndpoint}
          disabled={loading}
          className="w-full gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Calling...
            </>
          ) : (
            <>
              <Code2 className="h-4 w-4" />
              Call Endpoint
            </>
          )}
        </Button>

        <ResponseDisplay
          error={error}
          response={response}
          isSuccess={success}
        />
      </CardContent>
    </Card>
  );
}
