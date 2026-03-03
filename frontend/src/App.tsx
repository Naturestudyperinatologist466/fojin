import { lazy, Suspense } from "react";
import { Routes, Route } from "react-router-dom";
import { Spin } from "antd";
import Layout from "./components/Layout";
import HomePage from "./pages/HomePage";
import SearchPage from "./pages/SearchPage";
import TextDetailPage from "./pages/TextDetailPage";

const SourcesPage = lazy(() => import("./pages/SourcesPage"));
const LoginPage = lazy(() => import("./pages/LoginPage"));
const ReaderPage = lazy(() => import("./pages/ReaderPage"));
const ProfilePage = lazy(() => import("./pages/ProfilePage"));
const ParallelReaderPage = lazy(() => import("./pages/ParallelReaderPage"));
const KnowledgeGraphPage = lazy(() => import("./pages/KnowledgeGraphPage"));
const ManuscriptViewerPage = lazy(() => import("./pages/ManuscriptViewerPage"));
const ChatPage = lazy(() => import("./pages/ChatPage"));
const ExportsPage = lazy(() => import("./pages/ExportsPage"));
const DianjinBrowserPage = lazy(() => import("./pages/DianjinBrowserPage"));

function Loading() {
  return (
    <div style={{ textAlign: "center", padding: 80 }}>
      <Spin size="large" />
    </div>
  );
}

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/texts/:id" element={<TextDetailPage />} />
          <Route path="/sources" element={<SourcesPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/read/:textId" element={<ReaderPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/parallel/:textId" element={<ParallelReaderPage />} />
          <Route path="/kg" element={<KnowledgeGraphPage />} />
          <Route path="/manuscripts/:textId" element={<ManuscriptViewerPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/exports" element={<ExportsPage />} />
          <Route path="/dianjin" element={<DianjinBrowserPage />} />
        </Route>
      </Routes>
    </Suspense>
  );
}

export default App;
