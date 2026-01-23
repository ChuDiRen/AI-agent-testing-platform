export interface ApiParameter {
  name: string;
  in: 'query' | 'header' | 'path' | 'cookie';
  required: boolean;
  type: string;
  description?: string;
}

export type ApiParameterRecord = ApiParameter & { key: string };

interface SchemaProperty {
  type: string;
  description?: string;
  example?: unknown;
}

export interface ApiSchema {
  type: string;
  properties?: Record<string, SchemaProperty>;
  required?: string[];
  example?: unknown;
}

export interface ApiResponse {
  status: number;
  description: string;
  schema?: ApiSchema;
}

export interface ApiEndpoint {
  id: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  path: string;
  summary: string;
  description?: string;
  lastUpdated: string;
  parameters?: ApiParameter[];
  requestBody?: ApiSchema;
  responses?: ApiResponse[];
}

export interface ApiTag {
  id: string;
  name: string;
  endpoints: ApiEndpoint[];
}

export interface ApiVersion {
  id: string;
  version: string;
  tags: ApiTag[];
}

export interface ApiService {
  id: string;
  name: string;
  versions: ApiVersion[];
}

