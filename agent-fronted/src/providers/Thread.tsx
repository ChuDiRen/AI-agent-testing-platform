import { validate } from "uuid";
import { getApiKey } from "@/lib/api-key";
import { Thread } from "@langchain/langgraph-sdk";
import { useQueryState } from "nuqs";
import {
  createContext,
  useContext,
  ReactNode,
  useCallback,
  useState,
  Dispatch,
  SetStateAction,
} from "react";
import { createClient } from "./client";

interface ThreadContextType {
  getThreads: () => Promise<Thread[]>; // 获取线程列表
  threads: Thread[]; // 线程列表
  setThreads: Dispatch<SetStateAction<Thread[]>>; // 设置线程列表
  threadsLoading: boolean; // 加载状态
  setThreadsLoading: Dispatch<SetStateAction<boolean>>; // 设置加载状态
  deleteThread: (threadId: string) => Promise<void>; // 删除单个线程
  deleteThreads: (threadIds: string[]) => Promise<void>; // 批量删除线程
}

const ThreadContext = createContext<ThreadContextType | undefined>(undefined);

function getThreadSearchMetadata(
  assistantId: string,
): { graph_id: string } | { assistant_id: string } {
  if (validate(assistantId)) {
    return { assistant_id: assistantId };
  } else {
    return { graph_id: assistantId };
  }
}

export function ThreadProvider({ children }: { children: ReactNode }) {
  const [apiUrl] = useQueryState("apiUrl");
  const [assistantId] = useQueryState("assistantId");
  const [threads, setThreads] = useState<Thread[]>([]);
  const [threadsLoading, setThreadsLoading] = useState(false);

  const getThreads = useCallback(async (): Promise<Thread[]> => {
    if (!apiUrl || !assistantId) return [];
    const client = createClient(apiUrl, getApiKey() ?? undefined);

    const threads = await client.threads.search({
      metadata: {
        ...getThreadSearchMetadata(assistantId),
      },
      limit: 100,
    });

    return threads;
  }, [apiUrl, assistantId]);

  // 删除单个线程
  const deleteThread = useCallback(
    async (threadId: string): Promise<void> => {
      if (!apiUrl) throw new Error("缺少 API URL");
      const client = createClient(apiUrl, getApiKey() ?? undefined);

      await client.threads.delete(threadId);

      // 从本地状态中移除
      setThreads((prev) => prev.filter((t) => t.thread_id !== threadId));
    },
    [apiUrl],
  );

  // 批量删除线程
  const deleteThreads = useCallback(
    async (threadIds: string[]): Promise<void> => {
      if (!apiUrl) throw new Error("缺少 API URL");
      const client = createClient(apiUrl, getApiKey() ?? undefined);

      // 并发删除所有线程
      await Promise.all(threadIds.map((id) => client.threads.delete(id)));

      // 从本地状态中移除
      setThreads((prev) =>
        prev.filter((t) => !threadIds.includes(t.thread_id)),
      );
    },
    [apiUrl],
  );

  const value = {
    getThreads,
    threads,
    setThreads,
    threadsLoading,
    setThreadsLoading,
    deleteThread,
    deleteThreads,
  };

  return (
    <ThreadContext.Provider value={value}>{children}</ThreadContext.Provider>
  );
}

export function useThreads() {
  const context = useContext(ThreadContext);
  if (context === undefined) {
    throw new Error("useThreads must be used within a ThreadProvider");
  }
  return context;
}
