"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function DocumentsPage() {
  const [orderId, setOrderId] = useState<string | null>(null);
  const [docs, setDocs] = useState<Awaited<ReturnType<typeof api.documents>> | null>(null);
  const [docType, setDocType] = useState("passport");
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = (oid: string) => api.documents(oid).then(setDocs);

  useEffect(() => {
    api
      .orders()
      .then((orders) => {
        if (orders.length === 0) throw new Error("No orders yet.");
        setOrderId(orders[0].id);
        return refresh(orders[0].id);
      })
      .catch((e) => setError(e.message));
  }, []);

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault();
    if (!file || !orderId) return;
    setUploading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const token = window.localStorage.getItem("token");
      const res = await fetch(
        `${API_URL}/api/documents/${orderId}/upload?doc_type=${docType}`,
        { method: "POST", headers: { Authorization: `Bearer ${token}` }, body: formData }
      );
      if (!res.ok) throw new Error((await res.json()).detail || "Upload failed.");
      await refresh(orderId);
      setFile(null);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setUploading(false);
    }
  }

  async function handleDownload(id: string, fileName: string) {
    const token = window.localStorage.getItem("token");
    const res = await fetch(`${API_URL}/api/documents/${id}/download`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) {
      setError("Couldn't download that file.");
      return;
    }
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = fileName;
    a.click();
    window.URL.revokeObjectURL(url);
  }

  return (
    <div>
      <h1 className="font-display text-2xl text-paper mb-8">Documents</h1>
      {error && <p className="text-mist text-sm mb-4">{error}</p>}

      {orderId && (
        <form onSubmit={handleUpload} className="border border-line rounded-sm p-4 mb-8 flex flex-wrap gap-3 items-center">
          <select
            value={docType}
            onChange={(e) => setDocType(e.target.value)}
            className="bg-ink-raised border border-line text-paper text-sm rounded-sm px-3 py-2"
          >
            <option value="passport">Passport</option>
            <option value="address_proof">Address Proof</option>
            <option value="business_info">Business Information</option>
          </select>
          <input
            type="file"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="text-sm text-mist"
          />
          <button
            type="submit"
            disabled={!file || uploading}
            className="bg-brass text-ink text-sm font-medium px-4 py-2 rounded-sm disabled:opacity-50"
          >
            {uploading ? "Uploading…" : "Upload"}
          </button>
        </form>
      )}

      <div className="space-y-2">
        {docs?.map((d) => (
          <div key={d.id} className="flex justify-between items-center border-b border-line pb-2">
            <div>
              <p className="text-paper text-sm">{d.file_name}</p>
              <p className="text-mist text-xs capitalize">{d.type.replace("_", " ")}</p>
            </div>
            <button
              onClick={() => handleDownload(d.id, d.file_name)}
              className="text-brass text-xs font-mono"
            >
              Download
            </button>
          </div>
        ))}
        {docs?.length === 0 && <p className="text-mist text-sm">No documents uploaded yet.</p>}
      </div>
    </div>
  );
}
