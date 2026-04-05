import { apiClient } from './apiClient';

export interface WeatherData {
  temperature: number;
  feels_like: number;
  humidity: number;
  description: string;
  icon: string;
  wind_speed: number;
}

export const weatherService = {
  getGardenWeather: async (gardenId: number, lat: number, lon: number): Promise<WeatherData> => {
    return apiClient.get(`/weather/garden/${gardenId}?lat=${lat}&lon=${lon}`);
  },
};