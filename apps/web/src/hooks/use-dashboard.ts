"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { queryKeys } from "@/lib/query-keys";
import type { ApiResponse, ApplicationResponse, TaskCardResponse } from "@/types/api";

export function useMyTasks() {
  return useQuery({
    queryKey: queryKeys.dashboard.tasks,
    queryFn: () =>
      apiClient<ApiResponse<TaskCardResponse[]>>("/api/v1/me/tasks"),
    retry: false,
  });
}

export function useMyApplications() {
  return useQuery({
    queryKey: queryKeys.applications.mine,
    queryFn: () =>
      apiClient<ApiResponse<ApplicationResponse[]>>("/api/v1/me/applications"),
    retry: false,
  });
}
