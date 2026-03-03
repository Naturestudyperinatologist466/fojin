import { useState, useEffect } from "react";
import { Button, message } from "antd";
import { HeartOutlined, HeartFilled } from "@ant-design/icons";
import { useAuthStore } from "../stores/authStore";
import { addBookmark, removeBookmark, checkBookmark } from "../api/client";

interface BookmarkButtonProps {
  textId: number;
}

export default function BookmarkButton({ textId }: BookmarkButtonProps) {
  const user = useAuthStore((s) => s.user);
  const [bookmarked, setBookmarked] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!user) return;
    checkBookmark(textId).then(setBookmarked).catch(() => {});
  }, [user, textId]);

  if (!user) return null;

  const toggle = async () => {
    setLoading(true);
    try {
      if (bookmarked) {
        await removeBookmark(textId);
        setBookmarked(false);
        message.success("已取消收藏");
      } else {
        await addBookmark(textId);
        setBookmarked(true);
        message.success("已收藏");
      }
    } catch (err: any) {
      message.error(err.response?.data?.detail || "操作失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button
      type="text"
      icon={bookmarked ? <HeartFilled style={{ color: "#ff4d4f" }} /> : <HeartOutlined />}
      loading={loading}
      onClick={toggle}
    >
      {bookmarked ? "已收藏" : "收藏"}
    </Button>
  );
}
