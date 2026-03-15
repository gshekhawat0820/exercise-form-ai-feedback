import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface AnalyzeResponse {
  feedback: string;
  frames_analyzed: number;
  timestamp: string;
}

export interface ErrorResponse {
  detail: string;
}

export class ApiClient {
  private client;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      timeout: 60000, // 60 seconds for video processing
      headers: {
        Accept: "application/json",
      },
    });
  }

  /**
   * Analyze exercise form from a video file
   */
  async analyzeVideo(file: File): Promise<AnalyzeResponse> {
    const formData = new FormData();
    formData.append("video", file);

    try {
      const response = await this.client.post<AnalyzeResponse>(
        "/api/v1/analyze",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        },
      );
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        const errorData = error.response.data as ErrorResponse;
        throw new Error(errorData.detail || "Failed to analyze video");
      }
      throw new Error("Network error. Please check your connection.");
    }
  }

  /**
   * Analyze exercise form from base64 encoded frames
   */
  async analyzeFrames(frames: string[]): Promise<AnalyzeResponse> {
    try {
      const response = await this.client.post<AnalyzeResponse>(
        "/api/v1/analyze",
        { frames },
        {
          headers: {
            "Content-Type": "application/json",
          },
        },
      );
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        const errorData = error.response.data as ErrorResponse;
        throw new Error(errorData.detail || "Failed to analyze frames");
      }
      throw new Error("Network error. Please check your connection.");
    }
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<boolean> {
    try {
      await this.client.get("/health");
      return true;
    } catch {
      return false;
    }
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
