import { createFileRoute } from "@tanstack/react-router";
import { AIChat } from "@/components/Chat";

// @ts-ignore
export const Route = createFileRoute("/_layout/chat")({
  component: ChatPage,
});

function ChatPage() {
  return (
    <div className="p-4 h-screen flex flex-col">
      <div className="mb-4">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
          AI Assistant
        </h1>
        <p className="text-slate-600 dark:text-slate-400 mt-1">
          Chat with AI to calculate routes and get information
        </p>
      </div>
      <div className="flex-1">
        <AIChat />
      </div>
    </div>
  );
}


