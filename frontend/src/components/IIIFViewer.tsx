import { useEffect, useRef } from "react";
import OpenSeadragon from "openseadragon";

interface IIIFViewerProps {
  manifestUrl: string;
  width?: string;
  height?: string;
}

export default function IIIFViewer({ manifestUrl, width = "100%", height = "600px" }: IIIFViewerProps) {
  const viewerRef = useRef<HTMLDivElement>(null);
  const osdRef = useRef<OpenSeadragon.Viewer | null>(null);

  useEffect(() => {
    if (!viewerRef.current) return;

    // Destroy previous viewer
    if (osdRef.current) {
      osdRef.current.destroy();
    }

    osdRef.current = OpenSeadragon({
      element: viewerRef.current,
      prefixUrl: "https://cdn.jsdelivr.net/npm/openseadragon@4.1/build/openseadragon/images/",
      sequenceMode: true,
      showNavigator: true,
      navigatorPosition: "BOTTOM_RIGHT",
      showRotationControl: true,
      showFullPageControl: true,
      tileSources: [manifestUrl],
    });

    return () => {
      if (osdRef.current) {
        osdRef.current.destroy();
        osdRef.current = null;
      }
    };
  }, [manifestUrl]);

  return (
    <div
      ref={viewerRef}
      style={{
        width,
        height,
        border: "1px solid #d9d9d9",
        borderRadius: 8,
        background: "#1a1a1a",
      }}
    />
  );
}
