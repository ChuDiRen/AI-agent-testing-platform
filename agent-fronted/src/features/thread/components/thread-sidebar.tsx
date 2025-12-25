import { motion } from "framer-motion";
import ThreadHistory from "../history";

interface ThreadSidebarProps {
  isOpen: boolean;
  isLargeScreen: boolean;
}

export function ThreadSidebar({ isOpen, isLargeScreen }: ThreadSidebarProps) {
  return (
    <div className="relative hidden lg:flex h-full">
      <motion.div
        className="relative z-20 h-full overflow-hidden border-r bg-muted/30 backdrop-blur-xl"
        style={{ width: 300 }}
        animate={
          isLargeScreen
            ? { x: isOpen ? 0 : -300 }
            : { x: isOpen ? 0 : -300 }
        }
        initial={{ x: -300 }}
        transition={
          isLargeScreen
            ? { type: "spring", stiffness: 300, damping: 30 }
            : { duration: 0 }
        }
      >
        <div className="relative h-full" style={{ width: 300 }}>
          <ThreadHistory />
        </div>
      </motion.div>
    </div>
  );
}
