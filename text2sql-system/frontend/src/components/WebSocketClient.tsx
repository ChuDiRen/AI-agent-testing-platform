'use client';

import React, { useEffect, useRef, useState } from 'react';
import { getWebSocketClient } from '@/lib/websocket';
import { WebSocketClientProps, WebSocketResponse } from '@/types';

export default function WebSocketClient({
  url,
  onMessage,
  onError,
  onOpen,
  onClose,
}: WebSocketClientProps) {
  const wsClientRef = useRef(getWebSocketClient(url));
  const [status, setStatus] = useState<'disconnected' | 'connecting' | 'connected' | 'error'>('disconnected');

  useEffect(() => {
    const client = wsClientRef.current;

    // Connect to WebSocket
    setStatus('connecting');
    client.connect(
      // onMessage
      (message: WebSocketResponse) => {
        onMessage(message);
        setStatus('connected');
      },
      // onError
      (error) => {
        console.error('WebSocket error:', error);
        setStatus('error');
        onError?.(error);
      },
      // onOpen
      () => {
        console.log('WebSocket connection opened');
        setStatus('connected');
        onOpen?.();
      },
      // onClose
      () => {
        console.log('WebSocket connection closed');
        setStatus('disconnected');
        onClose?.();
      }
    );

    // Cleanup on unmount
    return () => {
      client.disconnect();
    };
  }, [url, onMessage, onError, onOpen, onClose]);

  // This component doesn't render anything visible
  // It's a hidden component that manages WebSocket connection
  return null;
}

export function useWebSocket(url: string) {
  const wsClientRef = useRef(getWebSocketClient(url));
  const [status, setStatus] = useState<'disconnected' | 'connecting' | 'connected' | 'error'>('disconnected');

  const sendMessage = useRef((query: string) => {
    wsClientRef.current.send({ query });
  });

  const connect = useRef((
    onMessage: (message: WebSocketResponse) => void,
    onError?: (error: Event) => void,
    onOpen?: () => void,
    onClose?: () => void
  ) => {
    setStatus('connecting');
    wsClientRef.current.connect(
      (message: WebSocketResponse) => {
        onMessage(message);
        setStatus('connected');
      },
      (error) => {
        console.error('WebSocket error:', error);
        setStatus('error');
        onError?.(error);
      },
      () => {
        console.log('WebSocket connection opened');
        setStatus('connected');
        onOpen?.();
      },
      () => {
        console.log('WebSocket connection closed');
        setStatus('disconnected');
        onClose?.();
      }
    );
  });

  const disconnect = useRef(() => {
    wsClientRef.current.disconnect();
  });

  return {
    status,
    sendMessage: sendMessage.current,
    connect: connect.current,
    disconnect: disconnect.current,
  };
}
