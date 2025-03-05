import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormMessage,
} from "@/components/ui/form";
import { Textarea } from "@/components/ui/textarea";
import Cal, { getCalApi } from "@calcom/embed-react";
import { useEffect, useState } from "react";
import { useMutation } from "@tanstack/react-query";

const formSchema = z.object({
  question: z.string(),
});

interface Message {
  content: string;
  isUser?: boolean;
}

export const Assistant = () => {
  const [messages, setMessages] = useState<Message[]>([]);

  const { mutate: sendMessage, isPending } = useMutation({
    mutationFn: async (text: string) => {
      const response = await fetch("http://localhost:8000/schedules", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text }),
      });
      return response.json();
    },
    onSuccess: (data) => {
      console.log("data", data);
      const newMessages = data.messages.map(
        (msg: { content: string; type: string }) => ({
          content: msg.content,
          isUser: msg.type === "human",
        })
      );
      setMessages(newMessages);
    },
  });

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      question: "",
    },
  });

  const onSubmit = (values: z.infer<typeof formSchema>) => {
    setMessages((prev) => [
      ...prev,
      { content: values.question, isUser: true },
    ]);
    sendMessage(values.question);
    form.reset();
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      form.handleSubmit(onSubmit)();
    }
  };

  useEffect(() => {
    (async function () {
      const cal = await getCalApi({ namespace: "coding-lesson" });
      cal("ui", { hideEventTypeDetails: false, layout: "month_view" });
    })();
  }, []);

  return (
    <div className="flex flex-col h-full">
      <h1 className="text-2xl text-center mt-5 font-bold">
        Book the coding lesson!
      </h1>

      <div className="mt-5">
        <Cal
          namespace="coding-lesson"
          calLink="patrik-braborec-46zriu/coding-lesson"
          style={{ width: "100%", height: "100%", overflow: "scroll" }}
          config={{ layout: "month_view" }}
          className="rounded-3xl"
        />
      </div>

      <div className="w-full flex items-center justify-center gap-5 mt-5">
        <div className="w-1/2 h-0.5 bg-neutral-800" />
        <h2 className="text-center text-neutral-800 uppercase font-bold">
          or ask me anything
        </h2>
        <div className="w-1/2 h-0.5 bg-neutral-800" />
      </div>

      <div className="flex flex-col justify-between h-full">
        {messages.length > 0 && (
          <div className="mt-5 space-y-4 overflow-y-auto p-4 rounded-lg">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg ${message.isUser ? "bg-blue-100 ml-auto max-w-[80%]" : "bg-white max-w-[80%]"}`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
              </div>
            ))}
            {isPending && (
              <div className="p-3 rounded-lg bg-white max-w-[80%]">
                <p className="whitespace-pre-wrap">
                  <span className="inline-block animate-pulse">.</span>
                  <span className="inline-block animate-pulse delay-150">
                    .
                  </span>
                  <span className="inline-block animate-pulse delay-300">
                    .
                  </span>
                </p>
              </div>
            )}
          </div>
        )}

        <div className="mt-5">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
              <FormField
                control={form.control}
                name="question"
                render={({ field }) => (
                  <FormItem>
                    <FormControl>
                      <Textarea
                        placeholder="Ask any questions about your schedule, or schedule your next appointment."
                        className="resize-none min-h-40 bg-white rounded-3xl p-5"
                        onKeyDown={handleKeyDown}
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </form>
          </Form>
        </div>
      </div>
    </div>
  );
};
