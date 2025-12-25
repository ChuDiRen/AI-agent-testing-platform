import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { PanelRightOpen, PanelRightClose, SquarePen, Settings } from "lucide-react";
import { LangGraphLogoSVG } from "@/components/icons/langgraph";
import { TooltipIconButton } from "../tooltip-icon-button";
import { AgentSwitchButton } from "@/components/agent-selector";
import { useI18n } from "@/hooks/useI18n";

interface ThreadHeaderProps {
  chatHistoryOpen: boolean;
  setChatHistoryOpen: (open: boolean | ((prev: boolean) => boolean)) => void;
  isLargeScreen: boolean;
  chatStarted: boolean;
  setThreadId: (id: string | null) => void;
  currentAgentId: string;
  openAgentSelector: () => void;
  openSettings: () => void;
}

export function ThreadHeader({
  chatHistoryOpen,
  setChatHistoryOpen,
  isLargeScreen,
  chatStarted,
  setThreadId,
  currentAgentId,
  openAgentSelector,
  openSettings,
}: ThreadHeaderProps) {
  const { t } = useI18n();

  return (
    <div className="absolute top-0 left-0 right-0 z-20 flex items-center justify-between gap-3 p-3 bg-background/80 backdrop-blur-md border-b">
      <div className="flex items-center gap-2">
        {(!chatHistoryOpen || !isLargeScreen) && (
          <Button
            variant="ghost"
            size="icon"
            className="h-9 w-9 text-muted-foreground hover:text-foreground"
            onClick={() => setChatHistoryOpen((p) => !p)}
          >
            {chatHistoryOpen ? (
              <PanelRightOpen className="size-5" />
            ) : (
              <PanelRightClose className="size-5" />
            )}
          </Button>
        )}

        {chatStarted && (
          <motion.button
            className="flex cursor-pointer items-center gap-2 px-2 py-1 rounded-md hover:bg-muted/50 transition-colors"
            onClick={() => setThreadId(null)}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <LangGraphLogoSVG width={24} height={24} />
            <span className="text-lg font-semibold tracking-tight hidden sm:inline-block">
              {t("app.title")}
            </span>
          </motion.button>
        )}
      </div>

      <div className="flex items-center gap-2">
        <AgentSwitchButton
          currentAgentId={currentAgentId}
          onClick={openAgentSelector}
        />

        <div className="h-4 w-px bg-border mx-1" />

        <TooltipIconButton
          tooltip={t("thread.newThread")}
          variant="ghost"
          size="icon"
          className="h-9 w-9 text-muted-foreground hover:text-foreground"
          onClick={() => setThreadId(null)}
        >
          <SquarePen className="size-5" />
        </TooltipIconButton>

        <TooltipIconButton
          tooltip={t("settings.title")}
          variant="ghost"
          size="icon"
          className="h-9 w-9 text-muted-foreground hover:text-foreground"
          onClick={openSettings}
        >
          <Settings className="size-5" />
        </TooltipIconButton>
      </div>
    </div>
  );
}
