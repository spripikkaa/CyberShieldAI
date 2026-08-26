import { ApiError, API_BASE, parseErrorDetail } from "./client";
import type { PredictResponse } from "../types/scan";

export { ApiError };

export async function predictUrl(
  url: string,
  userId?: string,
): Promise<PredictResponse> {
  const params = new URLSearchParams({ url });
  if (userId) {
    params.set("user_id", userId);
  }

  const response = await fetch(`${API_BASE}/predict?${params.toString()}`);

  if (!response.ok) {
    throw new ApiError(await parseErrorDetail(response), response.status);
  }

  return (await response.json()) as PredictResponse;
}
