// src/components/HistoryPage.tsx
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Header } from './Header';
import { Card, CardContent } from './ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Button } from './ui/button';
import { Loader2, AlertCircle } from 'lucide-react';
import { analysisService } from '../services/analysisService';
import { gardenService } from '../services/gardenService';
import { useApiRequest } from '../hooks/useApiRequest';

interface AnalysisHistoryItem {
  id: number;
  tree_id: number | null;
  garden_id: number | null;
  garden_name: string;
  fruit_type: string;
  harvest_date: string;
  fruit_count: number;
  confidence: number;
  processing_time: number;
  image_url: string | null;
  created_at: string;
}

export function HistoryPage() {
  const navigate = useNavigate();
  const [history, setHistory] = useState<AnalysisHistoryItem[]>([]);
  const [selectedGarden, setSelectedGarden] = useState<string>('all');
  const [gardens, setGardens] = useState<{ id: number; name: string }[]>([]);
  
  const historyRequest = useApiRequest<any>();
  const gardensRequest = useApiRequest<any>();
  
  useEffect(() => {
    loadGardens();
    loadHistory();
  }, []);
  
  const loadGardens = async () => {
    try {
      const data = await gardensRequest.execute(() => gardenService.getAllGardens());
      setGardens(data);
    } catch (error) {
      console.error('Ошибка загрузки садов:', error);
    }
  };
  
  const loadHistory = async () => {
    try {
      const gardenId = selectedGarden !== 'all' ? parseInt(selectedGarden) : undefined;
      const data = await historyRequest.execute(() => 
        analysisService.getAnalysisHistory(gardenId, undefined, 50)
      );
      setHistory(data.analyses || []);
    } catch (error) {
      console.error('Ошибка загрузки истории:', error);
    }
  };
  
  useEffect(() => {
    loadHistory();
  }, [selectedGarden]);
  
  const getFruitIcon = (fruitType: string): string => {
    switch (fruitType?.toLowerCase()) {
      case 'apple': return '🍎';
      case 'pear': return '🍐';
      case 'cherry': return '🍒';
      case 'plum': return '🟣';
      default: return '🌳';
    }
  };
  
  const formatConfidence = (confidence: number): string => {
    return `${Math.round((confidence || 0) * 100)}%`;
  };
  
  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 0.95) return 'text-green-600';
    if (confidence >= 0.9) return 'text-blue-600';
    return 'text-amber-600';
  };
  
  const isLoading = historyRequest.loading || gardensRequest.loading;
  const hasError = historyRequest.error;
  
  return (
    <div className="min-h-screen bg-background">
      <Header isLoggedIn userName=" " />
      
      <main className="container mx-auto px-6 py-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-3xl mb-4 flex items-center gap-2">
            <span className="text-2xl">📋</span>
            ИСТОРИЯ АНАЛИЗОВ
          </h1>
          
          <div className="flex gap-4">
            <div className="flex items-center gap-2">
              <span className="text-muted-foreground">Фильтры:</span>
              <Select value={selectedGarden} onValueChange={setSelectedGarden}>
                <SelectTrigger className="w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Все сады</SelectItem>
                  {gardens.map(garden => (
                    <SelectItem key={garden.id} value={garden.id.toString()}>
                      {garden.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>
        
        {/* Статус загрузки */}
        {isLoading && (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="size-8 animate-spin text-muted-foreground" />
          </div>
        )}
        
        {/* Ошибка */}
        {hasError && (
          <div className="flex items-center gap-3 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
            <AlertCircle className="size-5" />
            <span>Не удалось загрузить историю анализов. Попробуйте позже.</span>
          </div>
        )}
        
        {/* История */}
        {!isLoading && !hasError && (
          <>
            {history.length === 0 ? (
              <div className="text-center py-16">
                <p className="text-muted-foreground text-lg mb-4">
                  У вас пока нет выполненных анализов
                </p>
                <Button onClick={() => navigate('/analysis')}>
                  Загрузить первое фото
                </Button>
              </div>
            ) : (
              <>
                <div className="space-y-4 mb-8">
                  {history.map((item) => (
                    <Card key={item.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="pt-6">
                        <div className="flex gap-6 flex-col sm:flex-row">
                          {/* Изображение с LAZY LOADING */}
                          {item.image_url && (
                            <div className="w-full sm:w-48 h-32 flex-shrink-0 bg-gray-100 rounded-lg overflow-hidden">
                              <img 
                                src={item.image_url} 
                                alt={`Анализ урожая ${item.fruit_type} в ${item.garden_name} от ${item.harvest_date}`}
                                loading="lazy"  // ← LAZY LOADING
                                className="size-full object-cover hover:scale-105 transition-transform duration-300"
                                onError={(e) => {
                                  // Запасной вариант при ошибке загрузки
                                  (e.target as HTMLImageElement).src = '/placeholder-image.jpg';
                                }}
                              />
                            </div>
                          )}
                          
                          {/* Детали */}
                          <div className="flex-1">
                            <div className="flex items-start justify-between flex-wrap gap-2 mb-3">
                              <div>
                                <div className="flex items-center gap-2 flex-wrap mb-2">
                                  <span className="text-xl">📅</span>
                                  <span className="text-muted-foreground">{item.harvest_date}</span>
                                  <span className="mx-2">|</span>
                                  <span className="text-xl">{getFruitIcon(item.fruit_type)}</span>
                                  <span className="font-medium">{item.garden_name}</span>
                                  <span className="mx-2">|</span>
                                  <span className="text-sm text-muted-foreground">
                                    {item.tree_id ? `Дерево #${item.tree_id}` : 'Общий анализ'}
                                  </span>
                                </div>
                                
                                <div className="flex items-center gap-6 flex-wrap">
                                  <div className="flex items-center gap-2">
                                    <span className="text-xl">🎯</span>
                                    <span className="text-primary text-xl font-semibold">
                                      {item.fruit_count} {item.fruit_type === 'apple' ? 'яблок' : 
                                        item.fruit_type === 'pear' ? 'груш' : 
                                        item.fruit_type === 'cherry' ? 'вишен' : 'плодов'}
                                    </span>
                                  </div>
                                  
                                  <div className="flex items-center gap-2">
                                    <span className="text-xl">✅</span>
                                    <span className={`font-medium ${getConfidenceColor(item.confidence)}`}>
                                      {formatConfidence(item.confidence)} точность
                                    </span>
                                  </div>
                                </div>
                              </div>
                            </div>
                            
                            <div className="flex items-center gap-6 text-muted-foreground flex-wrap">
                              <div className="flex items-center gap-2">
                                <span>⏱</span>
                                <span>{item.processing_time?.toFixed(1) || '?'} сек</span>
                              </div>
                              
                              <div className="flex items-center gap-2">
                                <span>🔬</span>
                                <span>ID: {item.id}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
                
                {/* Статистика */}
                <Card className="bg-secondary/10">
                  <CardContent className="pt-6 text-center">
                    <p className="text-lg">
                      Статистика: <span className="text-primary font-semibold">{history.length} анализов</span> | 
                      <span className="text-primary font-semibold ml-2">
                        {formatConfidence(history.reduce((sum, item) => sum + (item.confidence || 0), 0) / history.length)} средняя точность
                      </span>
                    </p>
                  </CardContent>
                </Card>
              </>
            )}
          </>
        )}
      </main>
    </div>
  );
}