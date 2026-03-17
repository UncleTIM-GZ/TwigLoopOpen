"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { apiClient } from "@/lib/api-client";
import { logout as authLogout, setTokens } from "@/lib/auth";
import { queryKeys } from "@/lib/query-keys";
import type {
  ApiResponse,
  AuthResponse,
  LoginRequest,
  MeResponse,
  RegisterRequest,
} from "@/types/api";

export function useMe() {
  return useQuery({
    queryKey: queryKeys.auth.me,
    queryFn: () => apiClient<ApiResponse<MeResponse>>("/api/v1/me"),
    retry: false,
  });
}

export function useRegister() {
  const router = useRouter();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: RegisterRequest) =>
      apiClient<ApiResponse<AuthResponse>>("/api/v1/auth/register", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: (res) => {
      if (res.data) {
        setTokens(res.data.access_token, res.data.refresh_token);
        queryClient.invalidateQueries({ queryKey: queryKeys.auth.me });
        router.push("/dashboard");
      }
    },
  });
}

export function useLogin() {
  const router = useRouter();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: LoginRequest) =>
      apiClient<ApiResponse<AuthResponse>>("/api/v1/auth/login", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: (res) => {
      if (res.data) {
        setTokens(res.data.access_token, res.data.refresh_token);
        queryClient.invalidateQueries({ queryKey: queryKeys.auth.me });
        router.push("/dashboard");
      }
    },
  });
}

export interface UpdateProfileData {
  display_name?: string;
  bio?: string;
  availability?: string;
  skills?: string[];
  interested_project_types?: string[];
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateProfileData) =>
      apiClient<ApiResponse<unknown>>("/api/v1/me", {
        method: "PATCH",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.auth.me });
    },
  });
}

export interface CredentialResponse {
  credential_id: string;
  credential_type: string;
  status: string;
  issued_at: string;
  task_id: string | null;
  holder_actor_id: string;
  credential_version: number;
  revoked_at: string | null;
  superseded_by: string | null;
}

export function useMyCredentials() {
  return useQuery({
    queryKey: queryKeys.credentials.mine,
    queryFn: () =>
      apiClient<ApiResponse<CredentialResponse[]>>("/api/v1/me/credentials"),
    retry: false,
  });
}

export function useLogout() {
  const router = useRouter();
  const queryClient = useQueryClient();

  return async () => {
    await authLogout();
    queryClient.clear();
    router.push("/");
  };
}
