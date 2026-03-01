import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import HomePage from "./pages/HomePage";
import SearchPage from "./pages/SearchPage";
import TextDetailPage from "./pages/TextDetailPage";

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/texts/:id" element={<TextDetailPage />} />
      </Route>
    </Routes>
  );
}

export default App;
