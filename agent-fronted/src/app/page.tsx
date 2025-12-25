"use client";

import dynamic from "next/dynamic";
import { StreamProvider } from "@/providers/Stream";
import { ThreadProvider } from "@/providers/Thread";
import { ArtifactProvider } from "@/features/thread/artifact";
import { Toaster } from "@/components/ui/sonner";
import React from "react";

import { ThreadSkeleton } from "@/features/thread/skeleton";

const Thread = dynamic(() => import("@/features/thread").then((mod) => mod.Thread), {
  loading: () => <ThreadSkeleton />,
});

export default function DemoPage(): React.ReactNode {
  return (
    <React.Suspense fallback={<ThreadSkeleton />}>
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
