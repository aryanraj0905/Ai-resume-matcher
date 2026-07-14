import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 60000,
});

/**
 * Normalize any axios error into a short, user-friendly message.
 * The embedding model can take a few seconds to warm up on the very first
 * request, so timeouts get a distinct, reassuring message.
 */
export function getFriendlyErrorMessage(error) {
  if (axios.isCancel(error)) {
    return "The request was cancelled.";
  }

  if (error.code === "ECONNABORTED") {
    return "The server is taking longer than expected (it may be warming up the AI model). Please try again in a moment.";
  }

  if (!error.response) {
    return "Couldn't reach the server. Make sure the backend is running and try again.";
  }

  const detail = error.response.data?.detail;

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail) && detail.length > 0) {
    return detail[0].msg || "The request was invalid. Please check your input.";
  }

  if (error.response.status >= 500) {
    return "Something went wrong on our end. Please try again shortly.";
  }

  return "Something went wrong. Please try again.";
}

export async function uploadResume(file, { signal } = {}) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await apiClient.post("/resume/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    signal,
  });

  return response.data;
}

export async function matchResumeToJob({ resumeId, description }, { signal } = {}) {
  const response = await apiClient.post(
    "/job/match",
    { resume_id: resumeId, description },
    { signal }
  );

  return response.data;
}
