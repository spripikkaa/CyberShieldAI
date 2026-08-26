import { apiPost } from "./client";
import type { LoginRequest, RegisterRequest, User } from "../types/user";

export async function registerUser(payload: RegisterRequest): Promise<User> {
  return apiPost<User>("/users/register", payload);
}

export async function loginUser(payload: LoginRequest): Promise<User> {
  return apiPost<User>("/users/login", payload);
}
