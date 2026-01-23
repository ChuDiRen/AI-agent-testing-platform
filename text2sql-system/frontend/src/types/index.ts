// WebSocket message types
export interface WebSocketMessage {
  query: string;
}

export interface WebSocketResponse {
  source: 'query_analyzer' | 'sql_generator' | 'sql_explainer' | 'sql_executor' | 'visualization_recommender' | 'system';
  content: string;
  is_final: boolean;
  result?: QueryResult;
  error?: string;
}

export interface QueryResult {
  analysis?: any;
  sql?: string;
  explanation?: string;
  data?: any[];
  statistics?: {
    execution_time: number;
    row_count: number;
    column_count: number;
  };
  visualization?: VisualizationConfig;
}

export interface VisualizationConfig {
  chart_type: 'bar' | 'line' | 'pie' | 'scatter' | 'table';
  title: string;
  x_axis?: string;
  y_axis?: string;
  series?: Array<{
    name: string;
    data: any[];
  }>;
  options: any;
}

// Component props
export interface QueryInputProps {
  onQuery: (query: string) => void;
  isProcessing: boolean;
  disabled?: boolean;
}

export interface OutputRegionProps {
  title: string;
  content: string;
  type: 'markdown' | 'code' | 'json' | 'table';
  loading?: boolean;
  error?: string;
}

export interface VisualizationProps {
  config: VisualizationConfig;
  data?: any[];
}

export interface WebSocketClientProps {
  url: string;
  onMessage: (message: WebSocketResponse) => void;
  onError?: (error: Event) => void;
  onOpen?: () => void;
  onClose?: () => void;
}

// Query state
export interface QueryState {
  id: string;
  query: string;
  status: 'idle' | 'processing' | 'completed' | 'error';
  results: {
    analysis?: string;
    sql?: string;
    explanation?: string;
    data?: any[];
    visualization?: VisualizationConfig;
    statistics?: {
      execution_time: number;
      row_count: number;
      column_count: number;
    };
  };
  error?: string;
  timestamp: number;
}

// App state
export interface AppState {
  currentQuery: QueryState | null;
  queryHistory: QueryState[];
  connectionStatus: 'disconnected' | 'connecting' | 'connected' | 'error';
}
