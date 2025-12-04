"use client";

import dynamic from "next/dynamic";
import { StreamProvider } from "@/providers/Stream";
import { ThreadProvider } from "@/providers/Thread";
import { ArtifactProvider } from "@/features/thread/artifact";
import { Toaster } from "@/components/ui/sonner";
import React from "react";

const Thread = dynamic(() => import("@/features/thread").then((mod) => mod.Thread), {
  loading: () => <div className="flex h-screen w-full items-center justify-center">Loading...</div>,
});


export default function DemoPage(): React.ReactNode {
  return (
    <React.Suspense fallback={<div>加载中...</div>}>
      <Toaster />
      <ThreadProvider>
        <StreamProvider>
          <ArtifactProvider>
            <Thread />
          </ArtifactProvider>
        </StreamProvider>
      </ThreadProvider>
    </React.Suspense>
  );
}
