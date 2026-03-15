/**
 * Centralized TanStack Query key management.
 * Prevents key collisions and enables targeted invalidation.
 */

export const queryKeys = {
  auth: {
    me: ["auth", "me"] as const,
  },
  projects: {
    all: ["projects"] as const,
    list: (filters?: Record<string, string>) =>
      ["projects", "list", filters] as const,
    detail: (id: string) => ["projects", id] as const,
  },
  applications: {
    all: ["applications"] as const,
    byProject: (projectId: string) =>
      ["applications", "project", projectId] as const,
    mine: ["applications", "mine"] as const,
  },
  reviews: {
    pending: ["reviews", "pending"] as const,
  },
  sponsors: {
    mySupports: ["sponsors", "my-supports"] as const,
  },
  credentials: {
    mine: ["credentials", "mine"] as const,
  },
  dashboard: {
    overview: ["dashboard", "overview"] as const,
    tasks: ["dashboard", "tasks"] as const,
  },
} as const;
