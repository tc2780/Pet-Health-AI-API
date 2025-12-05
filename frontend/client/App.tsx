import "./global.css";

import { Toaster } from "./components/ui/toaster";
import { createRoot } from "react-dom/client";
import { Toaster as Sonner } from "./components/ui/sonner";
import { TooltipProvider } from "./components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { ProtectedRoute } from "./components/ProtectedRoute";

import Index from "./pages/Index";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import LogSymptoms from "./pages/LogSymptoms";
import AIPetAdvisor from "./pages/AIPetAdvisor";
import NotFound from "./pages/NotFound";
import ViewSymptoms from "./pages/ViewSymptoms";
import ViewAssessments from "./pages/ViewAssessments";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/pets/:petId/log-symptoms"
              element={
                <ProtectedRoute>
                  <LogSymptoms />
                </ProtectedRoute>
              }
            />
            <Route
              path="/pets/:petId/symptoms"
              element={
                <ProtectedRoute>
                  <ViewSymptoms />
                </ProtectedRoute>
              }
            />
            <Route
              path="/pets/:petId/ai"
              element={
                <ProtectedRoute>
                  <AIPetAdvisor />
                </ProtectedRoute>
              }
            />
            <Route
              path="/pets/:petId/view-assessments"
              element={
                <ProtectedRoute>
                  <ViewAssessments />
                </ProtectedRoute>
              }
            />
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

createRoot(document.getElementById("root")!).render(<App />);
