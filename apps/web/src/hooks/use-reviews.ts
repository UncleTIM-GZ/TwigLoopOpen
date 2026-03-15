"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { queryKeys } from "@/lib/query-keys";
import type {
  ApiResponse,
  ReviewResponse,
  SubmitReviewRequest,
} from "@/types/api";

export function usePendingReviews() {
  return useQuery({
    queryKey: queryKeys.reviews.pending,
    queryFn: () =>
      apiClient<ApiResponse<ReviewResponse[]>>("/api/v1/reviews/pending"),
  });
}

export function useSubmitReview(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SubmitReviewRequest) =>
      apiClient<ApiResponse<ReviewResponse>>(
        `/api/v1/reviews/${projectId}/submit`,
        {
          method: "POST",
          body: JSON.stringify(data),
        },
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.reviews.pending });
    },
  });
}
