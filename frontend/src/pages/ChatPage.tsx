import { useState, useRef, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Layout,
  Menu,
  Input,
  Button,
  Typography,
  Spin,
  Space,
  Empty,
  Popconfirm,
  message as antMessage,
} from "antd";
import {
  SendOutlined,
  PlusOutlined,
  DeleteOutlined,
  MessageOutlined,
} from "@ant-design/icons";
import ChatBubble from "../components/ChatBubble";
import { useAuthStore } from "../stores/authStore";
import api from "../api/client";

const { Sider, Content } = Layout;
const { Title, Text } = Typography;

interface SessionItem {
  id: number;
  title: string | null;
  created_at: string;
}

interface ChatSource {
  text_id: number;
  juan_num: number;
  chunk_text: string;
  score: number;
}

interface ChatMessage {
  id: number;
  role: "user" | "assistant";
  content: string;
  sources: ChatSource[] | null;
  created_at: string;
}

interface SessionDetail {
  id: number;
  title: string | null;
  messages: ChatMessage[];
}

// Local message for immediate display before server response
interface LocalMessage {
  role: "user" | "assistant";
  content: string;
  sources?: ChatSource[] | null;
}

export default function ChatPage() {
  const queryClient = useQueryClient();
  const { user } = useAuthStore();
  const isLoggedIn = !!user;

  const [activeSession, setActiveSession] = useState<number | null>(null);
  const [inputValue, setInputValue] = useState("");
  const [localMessages, setLocalMessages] = useState<LocalMessage[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Only fetch sessions if logged in
  const { data: sessions } = useQuery<SessionItem[]>({
    queryKey: ["chatSessions"],
    queryFn: async () => (await api.get("/chat/sessions")).data,
    enabled: isLoggedIn,
    retry: false,
  });

  const { data: sessionDetail, isLoading: detailLoading } = useQuery<SessionDetail>({
    queryKey: ["chatSession", activeSession],
    queryFn: async () => (await api.get(`/chat/sessions/${activeSession}`)).data,
    enabled: isLoggedIn && !!activeSession,
    retry: false,
  });

  const sendMutation = useMutation({
    mutationFn: (params: { message: string; session_id: number | null }) =>
      api.post("/chat", params, { timeout: 60000 }),
    onSuccess: (resp) => {
      const data = resp.data;
      const sessionId = data.session_id;
      setActiveSession(sessionId);
      setInputValue("");

      if (isLoggedIn) {
        // Server will become source of truth — clear local messages
        // so we don't duplicate once sessionDetail refreshes.
        setLocalMessages([]);
        queryClient.invalidateQueries({ queryKey: ["chatSessions"] });
        queryClient.invalidateQueries({ queryKey: ["chatSession", sessionId] });
      } else {
        // Anonymous: no server session fetch, keep local messages
        setLocalMessages((prev) => [
          ...prev,
          { role: "assistant", content: data.message, sources: data.sources },
        ]);
      }
    },
    onError: () => {
      antMessage.error("发送失败，请稍后重试");
      // Remove the optimistic user message
      setLocalMessages((prev) => prev.slice(0, -1));
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (sessionId: number) => api.delete(`/chat/sessions/${sessionId}`),
    onSuccess: () => {
      setActiveSession(null);
      setLocalMessages([]);
      queryClient.invalidateQueries({ queryKey: ["chatSessions"] });
    },
  });

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [localMessages, sessionDetail?.messages]);

  // When switching sessions, clear local messages
  useEffect(() => {
    setLocalMessages([]);
  }, [activeSession]);

  const handleSend = () => {
    if (!inputValue.trim() || sendMutation.isPending) return;

    // Add user message to local display immediately
    setLocalMessages((prev) => [...prev, { role: "user", content: inputValue }]);

    sendMutation.mutate({ message: inputValue, session_id: activeSession });
  };

  // Combine server messages with local messages.
  // Server history is the source of truth for persisted messages;
  // local messages are appended for the current editing round.
  const serverMessages: LocalMessage[] =
    sessionDetail?.messages?.map((m) => ({
      role: m.role,
      content: m.content,
      sources: m.sources,
    })) ?? [];

  const displayMessages: LocalMessage[] =
    serverMessages.length > 0
      ? [...serverMessages, ...localMessages]
      : localMessages;

  return (
    <div style={{ maxWidth: 1200, margin: "16px auto", height: "calc(100vh - 180px)" }}>
      <Layout style={{ height: "100%", background: "#fff", borderRadius: 8, overflow: "hidden" }}>
        <Sider width={260} style={{ background: "#fafafa", borderRight: "1px solid #f0f0f0" }}>
          <div style={{ padding: 12 }}>
            <Button
              type="dashed"
              block
              icon={<PlusOutlined />}
              onClick={() => {
                setActiveSession(null);
                setLocalMessages([]);
              }}
            >
              新对话
            </Button>
          </div>
          {isLoggedIn && (
            <Menu
              mode="inline"
              selectedKeys={activeSession ? [String(activeSession)] : []}
              style={{ border: "none", background: "transparent" }}
              items={
                sessions?.map((s) => ({
                  key: String(s.id),
                  icon: <MessageOutlined />,
                  label: (
                    <Space style={{ width: "100%", justifyContent: "space-between" }}>
                      <Text ellipsis style={{ maxWidth: 150 }}>
                        {s.title || "新对话"}
                      </Text>
                      <Popconfirm
                        title="确认删除此会话？"
                        onConfirm={(e) => {
                          e?.stopPropagation();
                          deleteMutation.mutate(s.id);
                        }}
                        onCancel={(e) => e?.stopPropagation()}
                      >
                        <DeleteOutlined
                          style={{ fontSize: 12, color: "#999" }}
                          onClick={(e) => e.stopPropagation()}
                        />
                      </Popconfirm>
                    </Space>
                  ),
                  onClick: () => setActiveSession(s.id),
                })) ?? []
              }
            />
          )}
          {!isLoggedIn && (
            <div style={{ padding: "12px 16px", color: "#999", fontSize: 12 }}>
              登录后可保存对话历史
            </div>
          )}
        </Sider>
        <Content style={{ display: "flex", flexDirection: "column" }}>
          <div style={{ padding: "12px 16px", borderBottom: "1px solid #f0f0f0" }}>
            <Title level={5} style={{ margin: 0 }}>
              {sessionDetail?.title || "AI 佛典问答"}
            </Title>
          </div>

          <div style={{ flex: 1, overflow: "auto", padding: 16 }}>
            {detailLoading ? (
              <div style={{ textAlign: "center", padding: 40 }}>
                <Spin />
              </div>
            ) : displayMessages.length > 0 ? (
              displayMessages.map((msg, i) => (
                <ChatBubble
                  key={i}
                  role={msg.role as "user" | "assistant"}
                  content={msg.content}
                  sources={msg.sources}
                />
              ))
            ) : (
              <Empty
                description="输入问题开始佛典智能问答"
                style={{ marginTop: 80 }}
              />
            )}
            {sendMutation.isPending && (
              <div style={{ textAlign: "center", padding: 16 }}>
                <Spin tip="AI 思考中..." />
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div style={{ padding: "12px 16px", borderTop: "1px solid #f0f0f0" }}>
            <Space.Compact style={{ width: "100%" }}>
              <Input
                placeholder="请输入关于佛典的问题..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onPressEnter={handleSend}
                disabled={sendMutation.isPending}
              />
              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={handleSend}
                loading={sendMutation.isPending}
              >
                发送
              </Button>
            </Space.Compact>
          </div>
        </Content>
      </Layout>
    </div>
  );
}
