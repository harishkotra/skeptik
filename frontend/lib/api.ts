import { Article, Status } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function fetchJSON<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { next: { revalidate: 60 } });
  if (!response.ok) {
    const body = await response.text();
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
