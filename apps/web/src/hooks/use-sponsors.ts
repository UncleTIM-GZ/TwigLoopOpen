"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { queryKeys } from "@/lib/query-keys";
import type {
  ApiResponse,
  CreateSupportRequest,
  SupportResponse,
} from "@/types/api";

export function useMySupports() {
  return useQuery({
    queryKey: queryKeys.sponsors.mySupports,
    queryFn: () =>
      apiClient<ApiResponse<SupportResponse[]>>(
        "/api/v1/sponsors/my-supports",
      ),
  });
}

export function useCreateSupport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateSupportRequest) =>
      apiClient<ApiResponse<SupportResponse>>("/api/v1/sponsors/support", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.sponsors.mySupports,
      });
    },
  });
}
