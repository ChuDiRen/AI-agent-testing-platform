import React from 'react';
import { Thread } from './components/thread';
import { StreamProvider } from './providers/Stream';
import { ThreadProvider } from './providers/Thread';
import { ArtifactProvider } from './components/thread/artifact';
import { Toaster } from './components/ui/sonner';
import { I18nProvider } from './contexts/I18nContext';

// Agent Chat React 主应用
export default function AgentChatApp() {
  return (
    <React.Suspense fallback={<div className="flex items-center justify-center h-screen">加载中...</div>}>
      <I18nProvider>
        <Toaster />
        <ThreadProvider>
          <StreamProvider>
            <ArtifactProvider>
              <Thread />
            </ArtifactProvider>
          </StreamProvider>
        </ThreadProvider>
      </I18nProvider>
    </React.Suspense>
  );
}

