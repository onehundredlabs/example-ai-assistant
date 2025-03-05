import { Assistant } from "@/components/custom/assistant";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  component: App,
});

function App() {
  return (
    <div className="container p-10 h-full">
      <Assistant />
    </div>
  );
}
