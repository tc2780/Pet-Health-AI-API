import { CheckCircle, AlertCircle } from "lucide-react";

interface ResponseDisplayProps {
  error?: string;
  response?: string;
  isSuccess: boolean;
}

export function ResponseDisplay({
  error,
  response,
  isSuccess,
}: ResponseDisplayProps) {
  if (error) {
    return (
      <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-md">
        <div className="flex items-start gap-2">
          <AlertCircle className="h-4 w-4 text-red-600 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-sm font-semibold text-red-800">Error</p>
            <p className="text-xs text-red-700 mt-1 font-mono">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (isSuccess && response) {
    return (
      <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-md">
        <div className="flex items-center gap-2 mb-2">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <p className="text-sm font-semibold text-green-800">
            Success - Response
          </p>
        </div>
        <pre className="text-xs bg-white text-slate-800 p-2 rounded border border-green-100 overflow-auto max-h-48">
          {response}
        </pre>
      </div>
    );
  }

  return null;
}
