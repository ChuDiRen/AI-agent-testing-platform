import { Skeleton } from "@/components/ui/skeleton";

export function ThreadSkeleton() {
  return (
    <div className="flex h-screen w-full overflow-hidden bg-background">
      {/* Sidebar Skeleton */}
      <div className="hidden lg:flex h-full w-[300px] border-r bg-muted/30 p-4 flex-col gap-4">
        <Skeleton className="h-8 w-3/4" />
        <div className="space-y-3 mt-4">
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
        </div>
      </div>

      {/* Main Content Skeleton */}
      <div className="flex-1 flex flex-col h-full">
        {/* Header Skeleton */}
        <div className="h-[60px] border-b flex items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <Skeleton className="h-8 w-8 rounded-md" />
            <Skeleton className="h-6 w-32" />
          </div>
          <div className="flex items-center gap-2">
            <Skeleton className="h-8 w-8 rounded-md" />
            <Skeleton className="h-8 w-8 rounded-md" />
          </div>
        </div>

        {/* Messages Skeleton */}
        <div className="flex-1 p-4 space-y-6 overflow-hidden">
            <div className="flex flex-col gap-2 max-w-3xl mx-auto w-full mt-10">
                 <div className="flex gap-4">
                    <Skeleton className="h-10 w-10 rounded-full flex-shrink-0" />
                    <div className="space-y-2 flex-1">
                        <Skeleton className="h-4 w-1/4" />
                        <Skeleton className="h-20 w-3/4" />
                    </div>
                 </div>
                 
                 <div className="flex gap-4 flex-row-reverse">
                    <Skeleton className="h-10 w-10 rounded-full flex-shrink-0" />
                    <div className="space-y-2 flex-1 flex flex-col items-end">
                        <Skeleton className="h-4 w-1/4" />
                        <Skeleton className="h-12 w-1/2" />
                    </div>
                 </div>
            </div>
        </div>

        {/* Input Skeleton */}
        <div className="p-4 border-t">
          <div className="max-w-3xl mx-auto w-full">
            <Skeleton className="h-[50px] w-full rounded-xl" />
          </div>
        </div>
      </div>
    </div>
  );
}
