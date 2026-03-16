"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { queryKeys } from "@/lib/query-keys";
import type {
  ApiResponse,
  ProjectResponse,
  WorkPackageResponse,
  SeatResponse,
} from "@/types/api";

export function useProjects(filters?: Record<string, string>) {
  const params = new URLSearchParams(filters);
  const qs = params.toString() ? `?${params.toString()}` : "";

  return useQuery({
    queryKey: queryKeys.projects.list(filters),
    queryFn: () =>
      apiClient<ApiResponse<ProjectResponse[]>>(`/api/v1/projects/${qs}`),
  });
}

export function useProject(id: string) {
  return useQuery({
    queryKey: queryKeys.projects.detail(id),
    queryFn: () =>
      apiClient<ApiResponse<ProjectResponse>>(`/api/v1/projects/${id}`),
    enabled: !!id,
  });
}

export function useWorkPackages(projectId: string) {
  return useQuery({
    queryKey: ["work-packages", projectId],
    queryFn: () =>
      apiClient<ApiResponse<WorkPackageResponse[]>>(
        `/api/v1/projects/${projectId}/work-packages`,
      ),
    enabled: !!projectId,
  });
}

export function useSeats(projectId: string) {
  return useQuery({
    queryKey: ["seats", projectId],
    queryFn: () =>
      apiClient<ApiResponse<SeatResponse[]>>(
        `/api/v1/projects/${projectId}/seats`,
      ),
    enabled: !!projectId,
  });
}
