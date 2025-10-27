import { Button } from "@/components/ui/button";
import { useThreads } from "@/providers/Thread";
import { Thread } from "@langchain/langgraph-sdk";
import { useEffect, useState } from "react";

import { getContentString } from "../utils";
import { useQueryState, parseAsBoolean } from "nuqs";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Skeleton } from "@/components/ui/skeleton";
import { PanelRightOpen, PanelRightClose, Trash2, List } from "lucide-react";
import { useMediaQuery } from "@/hooks/useMediaQuery";
import { useI18n } from "@/hooks/useI18n";
import { Checkbox } from "@/components/ui/checkbox";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { toast } from "sonner";

function ThreadList({
  threads,
  onThreadClick,
  batchMode,
  selectedThreads,
  onToggleSelect,
  onDeleteSingle,
}: {
  threads: Thread[];
  onThreadClick?: (threadId: string) => void;
  batchMode: boolean;
  selectedThreads: Set<string>;
  onToggleSelect: (threadId: string) => void;
  onDeleteSingle: (threadId: string) => void;
}) {
  const [threadId, setThreadId] = useQueryState("threadId");

  return (
    <div className="flex h-full w-full flex-col items-start justify-start gap-2 overflow-y-scroll [&::-webkit-scrollbar]:w-1.5 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-gray-300 [&::-webkit-scrollbar-track]:bg-transparent">
      {threads.map((t) => {
        let itemText = t.thread_id;
        if (
          typeof t.values === "object" &&
          t.values &&
          "messages" in t.values &&
          Array.isArray(t.values.messages) &&
          t.values.messages?.length > 0
        ) {
          const firstMessage = t.values.messages[0];
          itemText = getContentString(firstMessage.content);
        }
        return (
          <div
            key={t.thread_id}
            className="group relative w-full px-1"
          >
            <div className="flex items-center gap-2">
              {batchMode && (
                <Checkbox
                  checked={selectedThreads.has(t.thread_id)}
                  onCheckedChange={() => onToggleSelect(t.thread_id)}
                />
              )}
              <Button
                variant="ghost"
                className="flex-1 items-start justify-start text-left font-normal"
                onClick={(e) => {
                  e.preventDefault();
                  if (batchMode) {
                    onToggleSelect(t.thread_id);
                  } else {
                    onThreadClick?.(t.thread_id);
                    if (t.thread_id === threadId) return;
                    setThreadId(t.thread_id);
                  }
                }}
              >
                <p className="truncate text-ellipsis">{itemText}</p>
              </Button>
              {!batchMode && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteSingle(t.thread_id);
                  }}
                  className="absolute right-2 opacity-0 transition-opacity group-hover:opacity-100"
                >
                  <Trash2 className="h-4 w-4 text-red-500 hover:text-red-700" />
                </button>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function ThreadHistoryLoading() {
  return (
    <div className="flex h-full w-full flex-col items-start justify-start gap-2 overflow-y-scroll [&::-webkit-scrollbar]:w-1.5 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-gray-300 [&::-webkit-scrollbar-track]:bg-transparent">
      {Array.from({ length: 30 }).map((_, i) => (
        <Skeleton
          key={`skeleton-${i}`}
          className="h-10 w-[280px]"
        />
      ))}
    </div>
  );
}

export default function ThreadHistory() {
  const { t } = useI18n();
  const isLargeScreen = useMediaQuery("(min-width: 1024px)");
  const [chatHistoryOpen, setChatHistoryOpen] = useQueryState(
    "chatHistoryOpen",
    parseAsBoolean.withDefault(false),
  );
  const [threadId] = useQueryState("threadId");

  const {
    getThreads,
    threads,
    setThreads,
    threadsLoading,
    setThreadsLoading,
    deleteThread,
    deleteThreads,
  } = useThreads();

  const [batchMode, setBatchMode] = useState(false);
  const [selectedThreads, setSelectedThreads] = useState<Set<string>>(
    new Set(),
  );
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<{
    type: "single" | "batch";
    threadIds: string[];
  } | null>(null);

  useEffect(() => {
    if (typeof window === "undefined") return;
    setThreadsLoading(true);
    getThreads()
      .then(setThreads)
      .catch((err) => console.error("获取线程列表失败:", err))
      .finally(() => setThreadsLoading(false));
  }, []);

  // 切换选中状态
  const handleToggleSelect = (tid: string) => {
    setSelectedThreads((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(tid)) {
        newSet.delete(tid);
      } else {
        newSet.add(tid);
      }
      return newSet;
    });
  };

  // 单个删除
  const handleDeleteSingle = (tid: string) => {
    setDeleteTarget({ type: "single", threadIds: [tid] });
    setDeleteDialogOpen(true);
  };

  // 批量删除
  const handleDeleteBatch = () => {
    if (selectedThreads.size === 0) return;
    setDeleteTarget({
      type: "batch",
      threadIds: Array.from(selectedThreads),
    });
    setDeleteDialogOpen(true);
  };

  // 确认删除
  const handleConfirmDelete = async () => {
    if (!deleteTarget) return;

    try {
      if (deleteTarget.type === "single") {
        await deleteThread(deleteTarget.threadIds[0]);
        toast.success(t("thread.deleteSuccess"));
      } else {
        await deleteThreads(deleteTarget.threadIds);
        toast.success(t("thread.deleteSuccess"));
      }

      // 清空选中状态
      setSelectedThreads(new Set());
      setDeleteDialogOpen(false);
      setDeleteTarget(null);
    } catch (error) {
      console.error("删除失败:", error);
      toast.error(t("thread.deleteFailed"));
    }
  };

  // 切换批量模式
  const handleToggleBatchMode = () => {
    setBatchMode(!batchMode);
    if (!batchMode) {
      setSelectedThreads(new Set());
    }
  };

  return (
    <>
      <div className="shadow-inner-right hidden h-screen w-[300px] shrink-0 flex-col items-start justify-start gap-6 border-r-[1px] border-slate-300 lg:flex">
        <div className="flex w-full flex-col gap-3 px-4 pt-1.5">
          <div className="flex w-full items-center justify-between">
            <Button
              className="hover:bg-gray-100"
              variant="ghost"
              onClick={() => setChatHistoryOpen((p) => !p)}
            >
              {chatHistoryOpen ? (
                <PanelRightOpen className="size-5" />
              ) : (
                <PanelRightClose className="size-5" />
              )}
            </Button>
            <h1 className="text-xl font-semibold tracking-tight">
              {t("thread.history")}
            </h1>
          </div>
          <div className="flex w-full items-center justify-between gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleToggleBatchMode}
              className="flex-1"
            >
              {batchMode ? (
                <>
                  <List className="mr-2 h-4 w-4" />
                  {t("thread.cancelBatch")}
                </>
              ) : (
                <>
                  <Trash2 className="mr-2 h-4 w-4" />
                  {t("thread.batchDelete")}
                </>
              )}
            </Button>
            {batchMode && (
              <Button
                variant="destructive"
                size="sm"
                onClick={handleDeleteBatch}
                disabled={selectedThreads.size === 0}
              >
                {t("thread.deleteSelected")} ({selectedThreads.size})
              </Button>
            )}
          </div>
        </div>
        {threadsLoading ? (
          <ThreadHistoryLoading />
        ) : (
          <ThreadList
            threads={threads}
            batchMode={batchMode}
            selectedThreads={selectedThreads}
            onToggleSelect={handleToggleSelect}
            onDeleteSingle={handleDeleteSingle}
          />
        )}
      </div>
      <div className="lg:hidden">
        <Sheet
          open={!!chatHistoryOpen && !isLargeScreen}
          onOpenChange={(open) => {
            if (isLargeScreen) return;
            setChatHistoryOpen(open);
          }}
        >
          <SheetContent
            side="left"
            className="flex flex-col lg:hidden"
          >
            <SheetHeader>
              <SheetTitle>{t("thread.history")}</SheetTitle>
            </SheetHeader>
            <div className="flex flex-col gap-3 pb-4">
              <Button
                variant="outline"
                size="sm"
                onClick={handleToggleBatchMode}
              >
                {batchMode ? (
                  <>
                    <List className="mr-2 h-4 w-4" />
                    {t("thread.cancelBatch")}
                  </>
                ) : (
                  <>
                    <Trash2 className="mr-2 h-4 w-4" />
                    {t("thread.batchDelete")}
                  </>
                )}
              </Button>
              {batchMode && (
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={handleDeleteBatch}
                  disabled={selectedThreads.size === 0}
                >
                  {t("thread.deleteSelected")} ({selectedThreads.size})
                </Button>
              )}
            </div>
            <ThreadList
              threads={threads}
              onThreadClick={() => setChatHistoryOpen((o) => !o)}
              batchMode={batchMode}
              selectedThreads={selectedThreads}
              onToggleSelect={handleToggleSelect}
              onDeleteSingle={handleDeleteSingle}
            />
          </SheetContent>
        </Sheet>
      </div>

      {/* 删除确认对话框 */}
      <AlertDialog
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>{t("common.confirm")}</AlertDialogTitle>
            <AlertDialogDescription>
              {deleteTarget?.type === "single"
                ? t("thread.deleteConfirm")
                : t("thread.deleteMultipleConfirm", {
                    count: deleteTarget?.threadIds.length || 0,
                  })}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>{t("common.cancel")}</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleConfirmDelete}
              className="bg-red-600 hover:bg-red-700"
            >
              {t("common.delete")}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
