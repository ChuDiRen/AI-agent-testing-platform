import { motion } from "framer-motion";
import ThreadHistory from "../history";

interface ThreadSidebarProps {
  isOpen: boolean;
  isLargeScreen: boolean;
}

export function ThreadSidebar({ isOpen, isLargeScreen }: ThreadSidebarProps) {
  return (
    <motion.div
      initial={false}
      animate={{ width: isOpen && isLargeScreen ? 300 : 0 }}
      transition={{
        type: "spring",
        stiffness: 300,
        damping: 30,
      }}
      className="hidden lg:flex h-full border-r bg-muted/30 backdrop-blur-xl overflow-hidden flex-shrink-0"
    >
      <div className="w-[300px] h-full">
        <ThreadHistory />
      </div>
    </motion.div>
  );
}
