import { useQuery } from '@tanstack/react-query';
import { weatherService, WeatherData } from '../services/weatherService';
import { Loader2, CloudRain, Wind } from 'lucide-react';

interface GardenWeatherProps {
  gardenId: number;
  lat: number;
  lon: number;
}

export function GardenWeather({ gardenId, lat, lon }: GardenWeatherProps) {
  const { data, isLoading, error } = useQuery<WeatherData>({
    queryKey: ['weather', gardenId, lat, lon],
    queryFn: () => weatherService.getGardenWeather(gardenId, lat, lon),
    staleTime: 30 * 60 * 1000, // 30 минут
    retry: 1,
  });

  if (isLoading) return <div className="flex items-center gap-2"><Loader2 className="animate-spin size-4" /> Загрузка погоды...</div>;
  if (error) return <div className="text-amber-600">⚠️ Погода временно недоступна</div>;
  if (!data) return null;

  return (
    <div className="bg-blue-50 p-3 rounded-lg flex items-center gap-3">
      <img 
        src={`https://openweathermap.org/img/wn/${data.icon}@2x.png`} 
        alt={data.description}
        loading="lazy"
        className="size-10"
      />
      <div>
        <div className="font-semibold">{Math.round(data.temperature)}°C, {data.description}</div>
        <div className="text-sm text-gray-600 flex gap-3">
          <span>💧 {data.humidity}%</span>
          <span><Wind className="inline size-3" /> {Math.round(data.wind_speed)} м/с</span>
        </div>
      </div>
    </div>
  );
}