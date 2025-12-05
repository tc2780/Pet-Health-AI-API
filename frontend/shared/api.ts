/**
 * Shared code between client and server
 * Useful to share types between client and server
 * and/or small pure JS functions that can be used on both client and server
 */

/**
 * Example response type for /api/demo
 */
export interface DemoResponse {
  message: string;
}

/**
 * Authentication types
 */
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

export interface AuthResponse {
  id: string;
  email: string;
  name: string;
  access_token: string;
}

/**
 * Pet types
 */
export interface Pet {
  id: string;
  userId: string;
  name: string;
  species: string;
  breed?: string;
  age?: number;
  createdAt: string;
}

export interface CreatePetRequest {
  name: string;
  species: string;
  breed?: string;
  age?: number;
}

/**
 * Symptom types
 */
export interface Symptom {
  id: string;
  petId: string;
  symptom: string;
  severity: "mild" | "moderate" | "severe";
  date: string;
  notes?: string;
  description?: string;
  observed_at?: string;
  duration_hours?: number;
}

export interface LogSymptomRequest {
  petId: string;
  symptoms: SymptomEntry[];
  notes?: string;
}

export interface SymptomEntry {
  symptom: string;
  severity: "mild" | "moderate" | "severe";
}

/**
 * AI Query types
 */
export interface AIQueryRequest {
  petId: string;
  symptoms: string[];
  petInfo: {
    name: string;
    species: string;
    breed?: string;
    age?: number;
  };
}

export interface AIQueryResponse {
  response: string;
  suggestions?: string[];
}
