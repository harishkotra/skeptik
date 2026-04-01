import { Article, Status } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function fetchJSON<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { cache: "no-store" });
  if (!response.ok) {
    const body = await response.text();
    const contentType = response.headers.get("content-type") ?? "";
    if (contentType.includes("text/html")) {
      throw new Error(`Backend returned ${response.status} ${response.statusText}. Check the backend host and logs.`);
    }
    throw new Error(body || `API request failed for ${path}`);
  }
  return response.json() as Promise<T>;
}

export async function getArticles(): Promise<Article[]> {
  return fetchJSON<Article[]>("/api/articles");
}

export async function getArticle(slug: string): Promise<Article> {
  return fetchJSON<Article>(`/api/articles/${slug}`);
}

export async function getStatus(): Promise<Status> {
  return fetchJSON<Status>("/api/status");
}
