// English language pack
import { Translations } from "./zh-CN";

export const en: Translations = {
  // App metadata
  app: {
    title: "Agent Chat",
    description: "Agent Chat UX by LangChain",
  },

  // Common text
  common: {
    loading: "Loading...",
    cancel: "Cancel",
    confirm: "Confirm",
    delete: "Delete",
    edit: "Edit",
    save: "Save",
    send: "Send",
    copy: "Copy",
    copied: "Copied",
    refresh: "Refresh",
    submit: "Submit",
    close: "Close",
    search: "Search",
    select: "Select",
    continue: "Continue",
  },

  // Thread related
  thread: {
    history: "Thread History",
    newThread: "New thread",
    delete: "Delete",
    deleteConfirm: "Are you sure you want to delete this chat?",
    deleteMultipleConfirm: "Are you sure you want to delete these {count} chats?",
    deleteSuccess: "Deleted successfully",
    deleteFailed: "Failed to delete",
    batchDelete: "Batch Delete",
    batchMode: "Batch Mode",
    cancelBatch: "Cancel Batch",
    deleteSelected: "Delete Selected",
    selectAll: "Select All",
    unselectAll: "Unselect All",
    noThreads: "No threads",
    threadId: "Thread ID",
    copyThreadId: "Copy thread ID",
  },

  // Message related
  message: {
    typeMessage: "Type your message...",
    scrollToBottom: "Scroll to bottom",
    copyContent: "Copy content",
    cancelEdit: "Cancel edit",
    regenerate: "Refresh",
  },

  // Tool calls
  toolCall: {
    hide: "Hide Tool Calls",
    show: "Show Tool Calls",
  },

  // File upload
  upload: {
    title: "Upload PDF or Image",
    dragDrop: "Drag and drop files here",
    or: "or",
    browse: "Browse files",
    uploading: "Uploading...",
    uploadSuccess: "Upload successful",
    uploadFailed: "Upload failed",
  },

  // Config form
  config: {
    welcome: "Welcome to Agent Chat! Before you get started, you need to enter the URL of the deployment and the assistant / graph ID.",
    deploymentUrl: "Deployment URL",
    deploymentUrlDesc: "This is the URL of your LangGraph deployment. Can be a local, or production deployment.",
    assistantId: "Assistant / Graph ID",
    assistantIdDesc: "This is the ID of the graph (can be the graph name), or assistant to fetch threads from, and invoke when actions are taken.",
    apiKey: "LangSmith API Key",
    apiKeyDesc: "This is NOT required if using a local LangGraph server. This value is stored in your browser's local storage and is only used to authenticate requests sent to your LangGraph server.",
    apiKeyPlaceholder: "lsv2_pt_...",
    required: "*",
  },

  // Error messages
  error: {
    general: "An error occurred. Please try again.",
    connectionFailed: "Failed to connect to LangGraph server",
    connectionFailedDesc: "Please ensure your graph is running at {url} and your API key is correctly set (if connecting to a deployed graph).",
    invalidInput: "Invalid input",
    networkError: "Network error",
    unknownError: "Unknown error",
  },

  // GitHub link
  github: {
    openRepo: "Open GitHub repo",
  },
};

