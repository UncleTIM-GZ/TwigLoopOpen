/**
 * TypeScript types matching core-api Pydantic schemas.
 * TODO: Auto-generate from OpenAPI spec in CI.
 */

// === API Envelope ===

export interface ApiResponse<T> {
  success: boolean;
  data: T | null;
  error: string | null;
  meta: Record<string, unknown> | null;
}

export interface PaginatedMeta {
  total: number;
  page: number;
  limit: number;
  has_next: boolean;
}

// === Auth ===

export interface AuthResponse {
  account_id: string;
  actor_id: string;
  access_token: string;
  refresh_token: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  display_name: string;
  entry_intent?: "founder" | "collaborator" | "both";
}

export interface LoginRequest {
  email: string;
  password: string;
}

// === User ===

export interface AccountInfo {
  account_id: string;
  email: string;
}

export interface ActorInfo {
  actor_id: string;
  display_name: string;
  actor_type: string;
  bio: string | null;
  availability: string | null;
  is_founder: boolean;
  is_collaborator: boolean;
  is_reviewer: boolean;
  is_sponsor: boolean;
  profile_status: string;
  level: string;
}

export interface MeResponse {
  account: AccountInfo;
  actor: ActorInfo;
}

export interface UpdateProfileRequest {
  display_name?: string;
  bio?: string;
  availability?: string;
}

// === Project ===

export interface ProjectResponse {
  project_id: string;
  founder_actor_id: string;
  project_type: "general" | "public_benefit" | "recruitment";
  founder_type: string;
  title: string;
  summary: string;
  target_users: string | null;
  current_stage: string;
  min_start_step: string | null;
  status: string;
  needs_human_reviewer: boolean;
  human_review_status: string;
  has_reward: boolean;
  has_sponsor: boolean;
  created_via: string;
  created_at: string;
  updated_at: string;
}

export interface CreateProjectRequest {
  project_type: "general" | "public_benefit" | "recruitment";
  founder_type: "ordinary" | "help_seeker" | "contributor";
  title: string;
  summary: string;
  target_users?: string;
  current_stage?: string;
  min_start_step?: string;
  created_via?: "web" | "mcp";
}

// === Work Package ===

export interface WorkPackageResponse {
  work_package_id: string;
  project_id: string;
  title: string;
  description: string | null;
  status: string;
  sort_order: number;
  created_at: string;
}

// === Task Card ===

export interface TaskCardResponse {
  task_id: string;
  work_package_id: string;
  title: string;
  task_type: string;
  goal: string;
  input_conditions: string | null;
  output_spec: string;
  completion_criteria: string;
  main_role: string;
  risk_level: string;
  status: string;
  ewu: number;
  rwu: number | null;
  swu: number | null;
  has_reward: boolean;
  created_at: string;
}

// === Application ===

export interface ApplicationResponse {
  application_id: string;
  project_id: string;
  actor_id: string;
  seat_preference: string;
  intended_role: string;
  motivation: string | null;
  availability: string | null;
  status: string;
  created_at: string;
  reviewed_at: string | null;
}

export interface CreateApplicationRequest {
  seat_preference: "growth" | "formal";
  intended_role: string;
  motivation?: string;
  availability?: string;
}

// === Seat ===

export interface SeatResponse {
  seat_id: string;
  project_id: string;
  actor_id: string | null;
  seat_type: string;
  role_needed: string;
  status: string;
  reward_enabled: boolean;
  created_at: string;
}

// === Review ===

export interface ReviewResponse {
  project_id: string;
  reviewer_actor_id: string;
  decision: string;
  feedback: string | null;
  created_at: string;
}

export interface SubmitReviewRequest {
  decision: "passed" | "needs_revision" | "rejected";
  feedback?: string;
}

// === Sponsor Support ===

export interface SupportResponse {
  support_id: string;
  project_id: string;
  sponsor_actor_id: string;
  support_type: string;
  amount: number | null;
  status: string;
  created_at: string;
}

export interface CreateSupportRequest {
  project_id: string;
  support_type: "financial" | "resource" | "mentorship";
  amount?: number;
}
